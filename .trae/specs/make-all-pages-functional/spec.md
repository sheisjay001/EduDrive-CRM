# EduDrive CRM - Make All Pages and Buttons Functional

## Overview
- **Summary**: Audit the entire EduDrive CRM frontend (all 40+ pages) and backend API to identify and fix every page, button, form, and data fetch that is currently non-functional, uses static/hardcoded data without API integration, or has UI controls with no event handlers.
- **Purpose**: The CRM has many pages with beautiful static UI but missing event handlers, broken data fetching, and UI elements that do nothing when clicked. This makes the product feel like a prototype rather than a working system. The goal is to make every visible interactive element perform a real action backed by API calls.
- **Target Users**: All 8 user roles: super_admin, school_admin, admissions_officer, bursar, teacher, helpdesk_officer, parent, student.

## Goals
1. Every visible button, link, and form control across the app triggers a real action when clicked.
2. Every list/table page fetches real data from the backend API instead of showing empty/hardcoded lists.
3. All CRUD actions (Create, Read, Update, Delete) complete their full cycle: mutate state → call API → refresh list → show user feedback.
4. Backend API endpoints exist for every action the frontend initiates; missing endpoints are added.
5. TypeScript validation passes with `npx tsc --noEmit` in the frontend directory.
6. No new `alert()` calls; use a proper notification/toast pattern (or minimally keep alerts only if no toast library exists, but prefer inline feedback).

## Non-Goals
- Do NOT redesign any UI layouts or change visual styling (colors, spacing, fonts).
- Do NOT introduce new npm dependencies unless absolutely required; reuse existing patterns.
- Do NOT implement payment gateway webhooks (marked TODO).
- Do NOT add new pages or modules beyond what already exists in the file tree.
- Do NOT implement 3D scene, advanced charting libraries, or new visualizations beyond existing TrendPanel.
- Do NOT rewrite entire pages into different patterns; surgically fix what is broken and add what is missing.

## Background & Context
- Project stack: Next.js App Router (frontend) + FastAPI (backend) + Supabase (database).
- Auth: 8 roles enforced via `middleware.ts` (server) and `RouteGuard` HOC (client). Tokens stored in localStorage with `edudrive_` prefix and synced to cookies.
- Frontend data patterns: `@tanstack/react-query` via hooks in `use-crm-query.ts`, with fallback to raw `fetch()` in some pages. API client in `api-client.ts` wraps token refresh logic.
- Backend data patterns: Most GET list endpoints return `demo_data.*()` mock data. Supabase is used for mutations (POST/PATCH/DELETE) only.
- Current known gaps (from audit of representative pages):
  1. `/students` page never fetches data (state stays `[]`), no Add Student form, role typo in permission check.
  2. `/dashboard/school-admin` CBT exam buttons (Create/Edit/Play/Delete) have no handlers.
  3. `/messaging` "Create Notification" button does nothing; notification Delete buttons do nothing; static notification list.
  4. `/settings` Generate PINs button does nothing; PIN Lock/Delete buttons do nothing; static PIN list; form field key mapping bug.
  5. AppShell sidebar "Open Daily Brief" button has no handler.
  6. AppShell header "7 alerts" bell button has no handler.
  7. Backend missing endpoints: `DELETE /students/{id}`, `POST /students`, `POST /students/import/csv` (frontend calls it, backend needs implementation), `PATCH /settings`, CBT exam CRUD, Notifications CRUD, PIN CRUD.
  8. All subpages (e.g. `/finance/payments`, `/finance/debtors`, `/admissions/calendar`, `/reminders`, `/frontdesk`, `/activity`, `/analytics`, `/staff/administration`, `/staff/workload`, `/settings/classes`, `/settings/terms`, `/settings/bus-routes`, all `[id]/page.tsx` detail pages) need to be audited and fixed where broken.

## Functional Requirements
- **FR-1 (Students Page)**: `/students` page must fetch real student list via `useStudentsQuery()`, populate the DataTable, render Add Student form on toggle, submit create to backend, support inline edit + save, support delete with confirmation, and refresh list after every mutation. Fix role typo (`admission_officer` → `admissions_officer`).
- **FR-2 (CBT Exams Dashboard)**: `/dashboard/school-admin` CBT section must: wire Create Exam button to open a form/dialog, call backend to create/list exams, wire Edit/Play/Delete buttons to real actions, refresh list.
- **FR-3 (Messaging Notifications)**: `/messaging` page must: wire "Create Notification" to show form + submit to backend, wire each notification Delete button, fetch real notification list from backend (not hardcoded array), refresh after create/delete.
- **FR-4 (Settings PINs)**: `/settings` page must: wire "Generate PINs" to backend call, wire PIN Lock/Delete buttons, fetch real PIN list from backend, fix form field key mapping so settings edit form correctly maps group item labels to formData keys, refresh after each mutation.
- **FR-5 (AppShell Sidebar/HUD Buttons)**: Wire AppShell sidebar "Open Daily Brief" button and header "7 alerts" bell button to real actions (open a dialog, navigate, or show content — use existing pattern that is most natural).
- **FR-6 (Backend Student Endpoints)**: Add `POST /students` (create), `DELETE /students/{student_id}`, and `POST /students/import/csv` backend endpoints using Supabase, with proper RBAC guards.
- **FR-7 (Backend Settings PATCH)**: Add `PATCH /settings` endpoint to persist school settings (branding, payment keys, channel configs) to Supabase `schools` table `settings` JSON column with RBAC.
- **FR-8 (Backend CBT Exam Endpoints)**: Add GET/POST/PATCH/DELETE for `/cbt/exams` CRUD with RBAC, using Supabase `cbt_exams` table (create schema if needed).
- **FR-9 (Backend Notifications Endpoints)**: Add GET/POST/DELETE for `/notifications` CRUD with RBAC using Supabase `notifications` table.
- **FR-10 (Backend PIN Endpoints)**: Add POST `/pins/generate`, GET `/pins`, PATCH `/pins/{pin_id}/lock`, DELETE `/pins/{pin_id}` with RBAC using Supabase `scratch_card_pins` table.
- **FR-11 (Subpages Audit & Fix)**: Audit every remaining page file under `frontend/app/**/page.tsx` (payments, debtors, calendar, reminders, frontdesk, activity, analytics, staff/admin, staff/workload, settings/classes, settings/terms, settings/bus-routes, messaging/broadcasts, messaging/templates, admissions/lost-leads, all `[id]/page.tsx` detail pages) and fix: missing data fetches, static/hardcoded lists, buttons with no handlers, broken form submits, missing CRUD actions.
- **FR-12 (CRUD Feedback)**: Every Create/Update/Delete action must provide user-visible feedback (success or error) and refresh the displayed data; no silent failures.
- **FR-13 (Consistent API Client usage)**: Where pages use raw `fetch(...)` + `getAccessToken()` inline, prefer to add a wrapper method into `api-client.ts` and call it, so token refresh flow is consistently applied (don't break pages that work with raw fetch, but for new/updated mutations use the api-client pattern or ensure 401 handling).

## Non-Functional Requirements
- **NFR-1 (Type Safety)**: `npx tsc --noEmit` in `frontend` folder exits 0 after all changes.
- **NFR-2 (No Hydration Issues)**: All `localStorage` reads in React use lazy `useState(() => ...)` initializers or `useEffect` to avoid Next.js SSR/hydration warnings.
- **NFR-3 (useSearchParams + Suspense)**: Any component using `useSearchParams()` that is modified must remain inside a `<Suspense>` boundary (existing pages already wrap this, do not break).
- **NFR-4 (Auth Token Refresh)**: All backend API calls from the frontend must eventually flow through code that handles 401 + token refresh; for raw `fetch()` calls, keep or add the 401 logic inline, or use `api-client.request()`.
- **NFR-5 (Project conventions)**: Continue using `cn()`, `Badge` tones (`good`/`warn`/`danger`/`neutral`), the dark indigo + gold theme, and existing UI primitives (Button, Card, DataTable, SectionTitle, LoadingPanel, TrendPanel, KpiGrid).
- **NFR-6 (Safe Redirects)**: Any login flow with `?redirect=` continues to use `SAFE_REDIRECT_RE` regex validation pattern.

## Constraints
- **Technical**: Backend must use FastAPI + Supabase `supabase.table(...).{insert,update,delete,select}()` patterns matching existing code in `routes.py`. Frontend is Next.js 15 App Router with `"use client"` directive on all the pages being changed.
- **Business**: Role checks on backend endpoints use `require_any_role([...])` and `require_role(...)` from `app.core.auth`. On the frontend, role checks via `getUser()` + `includes()` pattern.
- **Dependencies**: Do NOT add new npm packages. If new tables are needed, write raw Supabase SQL queries or create the table via Supabase client (create if not exists pattern is not required; the backend insert will error if tables are missing, so document tables that need to exist in notes, but actual SQL creation via Supabase dashboard is expected to be handled separately).
- **Environment**: API URL is read from `NEXT_PUBLIC_API_URL` or falls back to `http://127.0.0.1:8000/api/v1`.

## Assumptions
- Demo data fallback (`demo_data.get_*()`) is acceptable for GET endpoints when Supabase tables are empty, ensuring the UI always shows something for testing purposes.
- Supabase tables that don't yet exist (e.g., `cbt_exams`, `notifications`, `scratch_card_pins`) will be created manually or via migrations; backend insert code attempts to write to them and will surface standard 500 errors if missing. This is acceptable — fixing the endpoints to use correct table names and columns is in scope; table creation SQL is out of scope unless the schema file already exists (many schema SQL files exist in `backend/*.sql`, check them first).
- Existing 40+ remaining sub-pages will have issues of varying severity; each will be audited during implementation and fixed with the smallest surgical change that makes them functional.

## Acceptance Criteria

### AC-1: Students page CRUD fully wired
- **Type**: `rule`
- **Given**: User is logged in as school_admin, admissions_officer, bursar, teacher, parent, or student
- **When**: User navigates to `/students`
- **Then**: (1) DataTable is populated from `useStudentsQuery()` (not empty array by default), (2) Add Student button shows a form with at least first_name, last_name fields, submitting calls `POST /students` via api-client and refreshes list, (3) inline Edit button switches row to inputs, Save calls PATCH endpoint and refreshes, Delete confirms and calls DELETE then refreshes, (4) role check uses correct `admissions_officer` string.
- **Pass Condition**: Manually click through add/edit/delete or inspect code to verify every button has an onClick that calls API + refetch, and the initial students array comes from the query hook.
- **Evidence**: Source diff of `students/page.tsx` showing `useStudentsQuery()` call, state wired to `data.students`, Add Student form rendered with submit handler, api-client methods invoked, plus tsc output with 0 errors.

### AC-2: School admin CBT exam buttons all functional
- **Type**: `rule`
- **Given**: User logged in as school_admin or super_admin on `/dashboard/school-admin`
- **When**: User clicks Create Exam, then Edit, Play, or Delete on an exam row
- **Then**: (1) Create Exam opens a dialog/form with at least title, student_class, duration_minutes fields and submits to backend, refreshes list, (2) Edit opens inline or dialog edit, save calls PATCH, (3) Play navigates or opens exam experience (minimally an alert or status update with confirmation message if actual test engine is out of scope), (4) Delete confirms and calls DELETE then refreshes.
- **Pass Condition**: All 4 CBT action buttons have onClick handlers that result in an API call or an explicit documented action + list refresh where applicable.
- **Evidence**: Source diff of `dashboard/school-admin/page.tsx` + new api-client methods + backend `/cbt/exams` endpoints.

### AC-3: Messaging page notifications section functional
- **Type**: `rule`
- **Given**: User on `/messaging` with create permissions (school_admin, super_admin)
- **When**: User clicks "Create Notification" and fills/submits form, or clicks Delete on any notification
- **Then**: (1) "Create Notification" button onClick opens a form (inline or dialog) with title/audience/channel fields, submit calls POST `/notifications`, refreshes list, (2) Each static notification card's Delete button calls DELETE `/notifications/{id}` and refreshes, (3) the notification list comes from API GET `/notifications` instead of hardcoded array.
- **Pass Condition**: Create button and all Delete buttons have onClick handlers calling API via api-client and triggering a refetch or state update; list is rendered from backend response.
- **Evidence**: Source diff of `messaging/page.tsx` + new `useNotificationsQuery` hook or inline fetch + backend notifications endpoints.

### AC-4: Settings page PINs section functional + edit form key mapping fixed
- **Type**: `rule`
- **Given**: School admin on `/settings`
- **When**: User clicks Generate PINs, or Lock/Delete on a PIN row, or edits school branding/payment settings and saves
- **Then**: (1) "Generate PINs" button calls POST `/pins/generate` (with quantity/batch form or defaults) and refreshes PIN list, (2) PIN Lock button calls PATCH `/pins/{id}/lock` (toggle status between unused/blocked), (3) PIN Delete button confirms and calls DELETE then refreshes, (4) PIN list is fetched from GET `/pins` backend instead of hardcoded array, (5) the settings edit form correctly maps each group item label (e.g., "Paystack Public Key") to the camelCase or snake_case key used in formData so typed values appear back in correct inputs on submit, and `handleSave` sends correct JSON body matching backend PATCH `/settings` schema.
- **Pass Condition**: Generate, Lock, Delete all have onClick handlers with API calls; settings edit form survives roundtrip (click Edit → change "Name" → Save → value persisted via API). Key mapping no longer uses label-derived guesswork that fails on spaces/casing.
- **Evidence**: Source diff of `settings/page.tsx` + backend PATCH `/settings` + PIN endpoints.

### AC-5: AppShell "Open Daily Brief" and "7 alerts" buttons wired
- **Type**: `rule`
- **Given**: Authenticated user on any AppShell-wrapped page
- **When**: User clicks "Open Daily Brief" sidebar card CTA or the header "7 alerts" Bell button
- **Then**: Both buttons trigger an action. Acceptable actions: (a) navigate to a relevant page (e.g., `/activity` for daily brief, `/reminders` for alerts); OR (b) open an informational dialog/showAlert-like UI populated with a list of items from an existing query. Must NOT be a no-op onClick.
- **Pass Condition**: Both buttons have a non-empty onClick handler resulting in navigation or visible state change.
- **Evidence**: Source diff of `app-shell.tsx` showing two handler functions assigned.

### AC-6: Backend CRUD endpoints added for student create/delete/import-CSV, settings PATCH, CBT, notifications, PINs
- **Type**: `rule`
- **Given**: Backend server running with authenticated request
- **When**: Frontend calls each new endpoint with valid payload + auth token
- **Then**: Endpoint exists (not 404), validates RBAC, writes to or reads from correct Supabase table, returns 2xx on success and 4xx/5xx on error. Specifically: `POST /students`, `DELETE /students/{id}`, `POST /students/import/csv`, `PATCH /settings`, `GET/POST/PATCH/DELETE /cbt/exams[/id]`, `GET/POST/DELETE /notifications[/id]`, `POST /pins/generate`, `GET /pins`, `PATCH /pins/{id}/lock`, `DELETE /pins/{id}`.
- **Pass Condition**: All 15+ endpoint verbs listed above are defined in `routes.py` (or included router files) with guards and Supabase interaction (demo_data fallback for GETs is OK; mutations must hit Supabase).
- **Evidence**: Source diff of `backend/app/api/routes.py` or new included routers, showing the routes + guard decorators + supabase.table calls.

### AC-7: All remaining sub-pages are functional (audit and fix)
- **Type**: `rubric`
- **Dimension**: Completeness and correctness of sub-pages audit pass
- **Scale**: 1-5
- **Anchors**: 1 = No sub-pages examined beyond the 4 main ones; 3 = Top 8 high-traffic sub-pages examined and top obvious fixes applied (data fetch wired, action buttons have handlers); 5 = Every page file in `frontend/app/**/page.tsx` was opened, scanned for: missing data fetches (empty state used where a query hook exists), hardcoded static lists of cards/rows that should come from backend, buttons missing onClick, broken form submits, missing delete/edit wiring; all findings are fixed surgically; at minimum every list page uses its corresponding `use*Query()` hook from `use-crm-query.ts` (or adds one if missing) instead of empty state.
- **Pass Threshold**: >= 4
- **Evidence**: Per-page summary in task completion evidence; grep of `frontend/app/**/page.tsx` shows no instances of empty `useState([])` patterns when a corresponding `use*Query()` hook exists (except intentional fallbacks while loading).

### AC-8: TypeScript passes with zero errors
- **Type**: `rule`
- **Given**: Frontend codebase after all changes
- **When**: `cd frontend && npx tsc --noEmit` is executed
- **Then**: Process exits with code 0 and no "error TS" lines in output.
- **Pass Condition**: `tsc --noEmit` returns 0.
- **Evidence**: Last tsc run command output attached to final task.

## Open Questions
- [ ] None currently. Scope defined as "fix everything broken found during audit" with surgical changes per the constraints above.
