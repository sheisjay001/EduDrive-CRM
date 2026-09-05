# EduDrive CRM - Make All Pages Functional - Implementation Plan

## Task 1: Add missing backend CRUD endpoints (students, settings, CBT, notifications, PINs)
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None (backend endpoints are prerequisite for frontend wiring)
- **Description**:
  - Add `POST /students` (create student record in Supabase `students` table; required fields: first_name, last_name; optional: admission_no, gender, date_of_birth, class_id, family_id; guarded by require_any_role school_admin/admissions_officer)
  - Add `DELETE /students/{student_id}` (RBAC school_admin only; delete + school_id scope)
  - Add `POST /students/import/csv` (parse CSV file, create rows in `students`, return count; guarded by school_admin) — keep simple implementation matching what api-client expects.
  - Add `PATCH /settings` endpoint that merges incoming JSON into `schools.settings` or `schools` table columns by school_id (RBAC school_admin only)
  - Add `/cbt/exams` CRUD: GET list, POST create, PATCH by id, DELETE by id — use Supabase `cbt_exams` table, guarded by school_admin
  - Add `/notifications` CRUD: GET list, POST create, DELETE by id — use Supabase `notifications` table, guarded by school_admin/admissions_officer
  - Add `/pins` endpoints: GET list, POST `/pins/generate` (batch), PATCH `/pins/{id}/lock` (toggle status), DELETE by id — use Supabase `scratch_card_pins` table, guarded by school_admin
  - Ensure all new endpoints follow the `routes.py` style: Depends guards, demo_data fallback for GET reads where appropriate, supabase.table for mutations.
  - Add corresponding wrapper methods to `frontend/services/api-client.ts` for every new endpoint (so frontend can use `apiClient.*` instead of raw fetch). Specifically add: `createStudent`, `deleteStudent` (PATCH update exists already), `createCbtExam`, `updateCbtExam`, `deleteCbtExam`, `getCbtExams`, `createNotification`, `deleteNotification`, `getNotifications`, `generatePins`, `getPins`, `lockPin`, `deletePin`, `updateSettings`. Also add/update the `importStudentsCSV` already exists in api-client — keep or confirm correct path.
- **Acceptance Criteria Addressed**: AC-6 (rule), and prerequisites for AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-1.1: Each new endpoint is defined in backend routes with a guard; grep `routes.py` and included routers for all 15+ verb paths. Evidence: diff of `routes.py` / new routers plus api-client.ts.
  - `rule` TR-1.2: `api-client.ts` contains new wrapper methods for all new endpoints, calling `request<T>(...)` with correct verbs, token included, paths matching backend. Evidence: file diff.
  - `rule` TR-1.3: Running backend and calling `GET /cbt/exams`, `GET /notifications`, `GET /pins` each return a list (possibly empty or demo fallback) instead of 404. Evidence: curl commands or unit tests if runnable.

## Task 2: Wire AppShell sidebar "Open Daily Brief" and header "7 alerts" buttons
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - In `app-shell.tsx`, add `handleOpenDailyBrief()` — most natural: `router.push('/activity')` since Activity page is the daily operations log.
  - Add `handleOpenAlerts()` — most natural: `router.push('/reminders')` since Reminders page tracks schedule and alerts, OR if an inline dropdown dialog is easier, a simple confirm dialog listing alerts count. Navigation is preferred.
  - Wire `onClick` on both buttons to the handlers.
- **Acceptance Criteria Addressed**: AC-5 (rule)
- **Test Requirements**:
  - `rule` TR-2.1: Both buttons have non-empty `onClick` prop assigned to a handler that causes navigation or a visible state change. Evidence: `grep -n "Open Daily Brief\|7 alerts" app-shell.tsx` source context shows onClick.

## Task 3: Fix Students page — fetch real data, add Add Student form, wire CRUD
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1 (needs student create/delete endpoints + apiClient methods)
- **Description**:
  - Replace the hardcoded `useState([])` for `students` with `const { data, isLoading, refetch } = useStudentsQuery();` and render `data.students` or equivalent in the DataTable rows.
  - Fix role typo: `admission_officer` → `admissions_officer`.
  - Implement Add Student form (currently showAddForm toggles to nothing visible). Render inline form fields: first_name, last_name, gender, date_of_birth, class_id, family_id (all text inputs for simplicity). Submit calls `apiClient.createStudent()` then `refetch()` + reset form + hide.
  - Ensure Edit/Delete calls `await apiClient.updateStudent(...)` and `await apiClient.deleteStudent(...)` then `refetch()` — currently they call apiClient but don't call `refetch` to reload the query hook's cache; add `refetch()` after each save/delete.
  - Show user feedback after each mutation (can use existing `alert(...)` pattern or inline success/error text).
- **Acceptance Criteria Addressed**: AC-1 (rule), contributes to AC-7 (rubric)
- **Test Requirements**:
  - `rule` TR-3.1: `useStudentsQuery` hook is used, `data.students` or equivalent is passed to DataTable rows (not local empty array). Evidence: source diff.
  - `rule` TR-3.2: Role string `admissions_officer` used (not `admission_officer`). Evidence: grep.
  - `rule` TR-3.3: Add Student form inputs actually render when showAddForm=true, submit button onClick calls a create handler. Evidence: source diff of form rendering block.
  - `rule` TR-3.4: Every mutation (create/save-edit/delete) calls `refetch()` or an equivalent cache invalidation after success. Evidence: source inspection of the 3 handler functions.

## Task 4: Wire School Admin dashboard CBT exam section Create/Edit/Play/Delete buttons
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1 (CBT endpoints + apiClient methods)
- **Description**:
  - Replace existing direct `fetch` for exams with a clean wrapper: either use `apiClient.getCbtExams()` in a useEffect with cancellation guard, OR add `useCbtExamsQuery` in use-crm-query.ts and use it here. Keep pattern consistent with rest of page.
  - Wire "Create Exam" button (setShowCreateDialog(true)): implement a simple inline form section or modal dialog with title, student_class, duration_minutes, status inputs. Submit calls apiClient.createCbtExam then refreshes exams list.
  - Wire Edit button: switch the exam row into inline editable inputs (title, duration, status). Save button calls apiClient.updateCbtExam then refreshes.
  - Wire Play button: minimal working behavior is fine — e.g., set exam status to "active" + confirm alert message "Starting exam: {title}" or navigate to a placeholder CBT page if one exists (check routes). Since no CBT detail page exists in app tree, set status to active via API and show a toast/alert: "Exam {title} is now active".
  - Wire Delete button: confirm → apiClient.deleteCbtExam → refresh list.
- **Acceptance Criteria Addressed**: AC-2 (rule)
- **Test Requirements**:
  - `rule` TR-4.1: All 4 CBT action button onClick handlers are non-empty and call corresponding apiClient methods + refetch. Evidence: diff of school-admin/page.tsx handlers.
  - `rule` TR-4.2: Creating an exam via the new form adds a row to the exams list after submit (calls API + updates state). Evidence: source inspection of create handler.

## Task 5: Wire Messaging page Notifications section (Create, Delete, dynamic list)
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1 (notifications endpoints + apiClient methods)
- **Description**:
  - Add `useNotificationsQuery` hook in `use-crm-query.ts` using `apiClient.getNotifications()`.
  - In messaging/page.tsx: fetch notifications with this hook and replace the hardcoded `[{Mid-term, Fee Reminder, Staff Meeting}].map(...)` with `data.notifications.map(...)` (with fallback while loading).
  - Wire "Create Notification" button: onClick toggles an inline form (title, audience, channel/message fields). Submit calls `apiClient.createNotification(addFormData)` → `refetch()` → reset form.
  - Wire each notification's Delete button onClick to `apiClient.deleteNotification(id)` → confirm → `refetch()`.
  - Add a local `addFormData` useState for the new notification form.
- **Acceptance Criteria Addressed**: AC-3 (rule)
- **Test Requirements**:
  - `rule` TR-5.1: Notification list rendered from the query hook (not hardcoded array). Evidence: grep `useNotificationsQuery` in page source and map call uses `data.notifications` or similar.
  - `rule` TR-5.2: "Create Notification" has onClick that shows form and submit handler calls create API + refetch. Evidence: handler code diff.
  - `rule` TR-5.3: Each notification Delete button calls delete API then refetches. Evidence: onClick lambda in the map.

## Task 6: Fix Settings page (PINs section buttons, dynamic list, edit form key mapping)
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1 (PIN endpoints + updateSettings + apiClient methods)
- **Description**:
  - Add `usePinsQuery` hook in `use-crm-query.ts` using `apiClient.getPins()`.
  - Fetch PINs with this hook and replace the hardcoded 3-PIN static array with `data.pins.map(...)`.
  - Wire "Generate PINs" button onClick: add an inline input for quantity (default 10), and submit calls `apiClient.generatePins({ batch_size: quantity })` → `refetch()`.
  - Wire each PIN's Lock button onClick to `apiClient.lockPin(pin.id)` → `refetch()`.
  - Wire each PIN's Delete button onClick to confirm → `apiClient.deletePin(pin.id)` → `refetch()`.
  - **Fix the edit form key mapping bug**: The current code derives formData keys from `item.label.toLowerCase().replace(/ /g, "_")` which produces "paystack_public_key" (snake) but state uses "paystack_public_key" (already snake, works for some but not consistent). Replace this with a hardcoded label→key map that explicitly maps each group item label (e.g., "Name", "Primary Color", "Paystack Public Key") to its corresponding formData key (e.g., "name", "primary_color", "paystack_public_key") — keep exact set in sync with the demo_data settings structure.
  - Wire `handleSave` to use `apiClient.updateSettings(formData)` instead of raw fetch, and ensure `refetch()` updates the display.
- **Acceptance Criteria Addressed**: AC-4 (rule)
- **Test Requirements**:
  - `rule` TR-6.1: PIN section Generate, Lock, Delete all have onClick handlers with API calls and refetch. Evidence: code diff of handlers.
  - `rule` TR-6.2: PIN list from API (not hardcoded). Evidence: grep `usePinsQuery` and map over `data.pins`.
  - `rule` TR-6.3: Edit form key mapping uses an explicit label→key map (not label-guessing transform). Evidence: explicit `Record<string,string>` map in source, not `.toLowerCase().replace()`.
  - `rule` TR-6.4: Settings Save calls apiClient.updateSettings and success triggers refetch so values update on screen. Evidence: handler diff.

## Task 7: Audit ALL remaining pages under frontend/app/**/page.tsx — find and fix broken interactions
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None (can run in parallel conceptually, but after Task 1 for API surfaces)
- **Description**:
  - Enumerate every page.tsx file in `frontend/app/**/` (full list):
    1. `app/page.tsx` — landing page
    2. `app/[schoolSlug]/layout.tsx` — school slug layout
    3. `app/activity/page.tsx`
    4. `app/admissions/page.tsx` (already examined, works but double-check)
    5. `app/admissions/[leadId]/page.tsx`
    6. `app/admissions/calendar/page.tsx`
    7. `app/admissions/leads/[leadId]/page.tsx`
    8. `app/admissions/lost-leads/page.tsx`
    9. `app/analytics/page.tsx`
    10. `app/dashboard/page.tsx` (examined)
    11. All 8 `app/dashboard/*/page.tsx` (super-admin, admissions, bursar, helpdesk, parent, school-admin, student, teacher)
    12. `app/families/page.tsx` (examined)
    13. `app/families/[familyId]/page.tsx`
    14. `app/finance/page.tsx` (examined)
    15. `app/finance/debtors/page.tsx`
    16. `app/finance/fee-structures/page.tsx`
    17. `app/finance/invoices/[invoiceId]/page.tsx`
    18. `app/finance/payments/page.tsx`
    19. `app/forgot-password/page.tsx`
    20. `app/frontdesk/page.tsx`
    21. `app/helpdesk/page.tsx` (examined)
    22. `app/helpdesk/[ticketId]/page.tsx`
    23. `app/login/page.tsx` (examined)
    24. `app/messaging/page.tsx` (examined)
    25. `app/messaging/broadcasts/page.tsx`
    26. `app/messaging/templates/page.tsx`
    27. `app/parent-login/page.tsx`
    28. `app/parents/page.tsx` (examined)
    29. `app/parents/[parentId]/page.tsx`
    30. `app/reminders/page.tsx`
    31. `app/reports/page.tsx` (examined)
    32. `app/reset-password/page.tsx`
    33. `app/settings/page.tsx` (examined)
    34. `app/settings/bus-routes/page.tsx`
    35. `app/settings/classes/page.tsx`
    36. `app/settings/terms/page.tsx`
    37. `app/signup/page.tsx`
    38. `app/staff/page.tsx`
    39. `app/staff/administration/page.tsx`
    40. `app/staff/workload/page.tsx`
    41. `app/student-login/page.tsx`
    42. `app/students/page.tsx` (covered in Task 3)
    43. `app/students/[studentId]/page.tsx`
    44. `app/students/[studentId]/lifecycle/page.tsx`
  - For EACH file: open and read, look for and fix:
    A. **Static empty list patterns**: Is a DataTable/Card list populated from a `useState([])` when a corresponding `useXxxQuery()` hook exists? Wire it up.
    B. **Buttons with no onClick handler or `onClick={() => {}}`**: For every `<Button>` without a meaningful onClick, add a sensible handler (navigation link → use `asChild` + `<Link>` pattern; actions → call appropriate apiClient method + give feedback; if truly a placeholder for a future feature, at minimum show a `confirm("Feature coming soon")` style alert so the button visibly does something instead of feeling dead).
    C. **Broken forms**: Any form input without onChange or submit without handler.
    D. **DataTable rows mapped to empty array because the right query hook exists but wasn't called**.
    E. **Missing refetch()** after a mutation (common in already-implemented pages that don't trigger list refresh).
  - Specifically known pages to scrutinize hard:
    - `finance/payments`, `finance/debtors`, `finance/fee-structures`: look for Add Payment/Add Fee Structure buttons; make sure submit buttons call api + refresh.
    - `staff/administration`, `staff/workload`: Add Staff/Invite buttons; wire.
    - `settings/classes`, `settings/terms`, `settings/bus-routes`: Add Class/Term/Route buttons if present, wire.
    - `messaging/broadcasts`: Send Broadcast button wiring.
    - `messaging/templates`: Add/Edit template buttons.
    - All `[id]/page.tsx` detail pages: ensure Edit/Save/Delete buttons on detail screens are wired and call corresponding apiClient methods with redirect back to list on delete.
    - `forgot-password`, `reset-password`, `signup`, `parent-login`, `student-login`: Make sure submit buttons actually call the auth APIs. Parent and Student login pages already exist in routes.py (`/auth/parent-login` exists, need to check if frontend pages use the right endpoint).
    - `landing page.tsx`: Link buttons to /login or appropriate place.
- **Acceptance Criteria Addressed**: AC-7 (rubric)
- **Test Requirements**:
  - `rubric` TR-7.1: Sub-page audit completeness. Scale 1-5. Anchors: 1 = <10 pages checked; 3 = >25 pages checked with major pages fixed; 5 = All ~45 page.tsx files opened individually, every instance of pattern A-E above found and fixed where fixable without introducing new dependencies. Threshold >= 4. Evidence: per-file findings log in Completion Evidence (a list of files changed + specific fixes applied per file).
  - `rule` TR-7.2: Every `<Button>` in the codebase that is NOT a pure navigation link (asChild Link) MUST have an onClick that either routes, opens a dialog, calls an API, shows an explicit "coming soon" alert, or invokes a visibly observable action. Evidence: grep of compiled output or search showing zero `<Button>` elements with onClick={noop/empty/undefined} that are not asChild-wrapped Links.

## Task 8: TypeScript validation pass
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Tasks 1-7 (all code changes must be done first)
- **Description**:
  - Run `cd frontend && npx tsc --noEmit`.
  - Fix every TS error that surfaces. Likely culprits:
    - New apiClient methods missing from interface/types (check crm.ts types for response types if used).
    - Form state keys not aligning with type definitions — add appropriate Record typing or loosen.
    - Response shape mismatches from new endpoints (add fallback types or cast safely).
  - Repeat until clean 0-exit.
- **Acceptance Criteria Addressed**: AC-8 (rule)
- **Test Requirements**:
  - `rule` TR-8.1: Final `tsc --noEmit` stdout has zero "error TS" lines and exit code is 0. Evidence: attach full terminal output to completion evidence.
