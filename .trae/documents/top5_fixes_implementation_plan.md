# Top 5 Recommended Fixes — Implementation Plan

## Repository Research

### Architecture Overview
- **Backend**: FastAPI (Python) + SQLAlchemy + Alembic migrations + Supabase (Postgres + Auth)
- **Frontend**: Next.js 15+ (App Router) + TypeScript + React + Tailwind + custom UI components
- **API Prefix**: `/api/v1` (configured in settings, applied in [main.py](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/main.py#L26))
- **Router pattern**: Per-domain routers in `backend/app/api/*_routes.py`, aggregated via [routes.py](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/api/routes.py)

### Research Conclusions vs User's 5 Items

| # | User Claim | Actual State (After Research) |
|---|---|---|
| 1 | "9 missing routers" | **All 19 routers ARE already registered** in [routes.py](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/api/routes.py#L54-L93). The only non-router `.py` files in `api/` are `routes.py` (aggregator) and `docs.py` (OpenAPI helper). **No action needed here.** |
| 2 | "Add parent/student roles to RBAC" | **Roles DO exist** in [auth.py L239-240](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/core/auth.py#L239-L240) with permission lists. What's MISSING: backend endpoints that parent/student roles actually call, plus `/auth/parent-login`. |
| 3 | "Create /bus-routes + /bus-stops endpoints" | **transport_routes.py EXISTS and IS registered**, but under prefix `/transport` → `/transport/bus-routes`, `/transport/bus-stops`. Frontend [bus-routes/page.tsx](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/frontend/app/settings/bus-routes/page.tsx#L41) calls the WRONG paths: `/bus-routes`, `/bus-stops` (no prefix). Fix = add prefix-less alias routes on backend. |
| 4 | "Build parent/student dashboard UIs" | Parent dashboard UI EXISTS at [dashboard/parent/page.tsx](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/frontend/app/dashboard/parent/page.tsx) but calls 4 NON-EXISTENT backend endpoints. Parent login redirects to STAFF `/parents` page. **Student dashboard UI does NOT exist.** Student login redirects to STAFF `/students` page. |
| 5 | "Run SQL schema migrations" | Only **1 alembic migration** exists (initial schema) covering ~12 tables. 26 `*_schema.sql` files define 20+ additional tables NOT in alembic. CRITICAL missing tables: `user_roles` (used by auth.py for role lookup!), `bus_routes`, `bus_stops`, `student_transport`, `vehicles`, `fee_structures`, `message_templates`, `student_attendance`, `student_assignments`, `lost_leads`, `receipts`, `calendar_events`, `reminders`. |

## Files and Modules to Change

### Backend
- `backend/app/api/routes.py` — Add `/auth/parent-login` endpoint + parent portal grouped routes
- `backend/app/api/transport_routes.py` — Add prefix-less alias routes (`/bus-routes`, `/bus-stops`) for frontend compatibility
- `backend/app/core/auth.py` — Verify role coverage; ensure parent/student role-scoped endpoints work
- Backend: Create parent portal endpoints (4 routes: `/parent/children`, `/parent/invoices`, `/parent/payments`, `/parent/communications`) — inline in `routes.py` or new `parent_portal_routes.py`

### Frontend
- `frontend/app/parent-login/page.tsx` — Fix redirect: `/parents` → `/dashboard/parent`
- `frontend/app/student-login/page.tsx` — Fix redirect: `/students` → `/dashboard/student`
- `frontend/app/dashboard/student/page.tsx` — **NEW**: Create student dashboard UI (similar layout to parent dashboard)
- `frontend/app/settings/bus-routes/page.tsx` — Optionally fix URL paths (safer: fix on backend)

### Database / Migrations
- `backend/alembic/versions/` — Generate second alembic migration for missing tables, OR
- Supabase SQL Editor — Apply combined SQL from all 26 `*_schema.sql` files in dependency order

## Implementation Steps

### Step 1: Fix Transport Endpoint Path Mismatch (Item #3 corrected)
**File**: [transport_routes.py](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/api/transport_routes.py)
- Create a second `APIRouter` instance **without** a prefix
- Register the same bus-route and bus-stop handler functions under both `/transport/bus-routes` AND `/bus-routes` paths
- Do the same for `/transport/bus-stops` → `/bus-stops`
- Keep student-transport and vehicles only under `/transport/*` (they are not called by the existing frontend bus-routes page)

### Step 2: Create Parent Portal Backend Endpoints + Auth Endpoint (Items #2 + #4 backend)
**Files**: [routes.py](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/api/routes.py)
1. Add `POST /auth/parent-login` endpoint:
   - Reuses `authenticate_user()` from auth.py
   - After successful auth, validates that the returned user.role IS `"parent"`
   - Raises 403 if role doesn't match (prevents staff from using parent login page)
   - Returns same `AuthResponse` shape as regular login
   
2. Add grouped parent-scope endpoints:
   - `GET /parent/children` — Look up current_user (parent role enforced). Find family(ies) via `parents.primary_contact_id=user.id` or email match, then return students joined via `family_id`. Include `student_id`, `full_name`, `class`, `grade`, `date_of_birth`, `admission_number`.
   - `GET /parent/invoices` — For same family student IDs, return invoices from Supabase `invoices` table (fields: `id`, `invoice_number`, `amount_due`, `amount_paid`, `status`, `due_date`, `student_name`)
   - `GET /parent/payments` — Same student_ids filter on `payments` JOIN invoices (fields: `id`, `amount`, `paid_at`, `payment_method`, `payment_reference`, `description`)
   - `GET /parent/communications` — Query `message_logs` where recipient = parent email or family-linked broadcast sent through messaging; return `id`, `subject`, `body`, `sent_at`, `channel`

### Step 3: Fix Login Redirects + Build Student Dashboard UI (Item #4 frontend)
**Files**:
- [parent-login/page.tsx](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/frontend/app/parent-login/page.tsx#L43) — change redirect: `router.push("/parents")` → `router.push("/dashboard/parent")`
- [student-login/page.tsx](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/frontend/app/student-login/page.tsx#L48) — change redirect: `router.push("/students")` → `router.push("/dashboard/student")`
- **NEW** `frontend/app/dashboard/student/page.tsx`:
  - Reuse `AppShell`, `KpiGrid`, `Card`, `Badge`, `SectionTitle`, `LoadingPanel` from existing components
  - Fetch from student-scope endpoints (reuse existing `/students/{student_id}` + `/lifecycle/*` patterns, or add new `/student/*` scope endpoints that scope to current user via `students.user_id = auth_user.id`)
  - Dashboard sections to include:
    1. KPI grid: Attendance (present/absent ratio), Assignments pending, GPA/grades summary, Notices count
    2. "My Profile" card — own student info (name, class, DOB, admission_no)
    3. "Attendance" recent 5 days (from `student_attendance`)
    4. "Assignments" card — list upcoming + completed (from `student_assignments`)
    5. Quick actions: View Timetable, Report Issue (ticket), Contact Teacher

### Step 4: Apply SQL Schema Migrations (Item #5)
Approach: Since the project uses Supabase (not local SQLite for production) and most `.sql` files use Postgres-specific syntax (`UUID`, `gen_random_uuid()`, `JSONB`, `auth.users` references):

1. **First, check alembic current state**:
   - `cd backend && alembic current`
   - `cd backend && alembic upgrade head` (to ensure the 1 initial migration is applied)

2. **For Supabase**: Combine and execute all 26 `*_schema.sql` files in the Supabase SQL Editor in this dependency order:
   1. `supabase_schema.sql` (core tables: schools, roles, users, families, parents, classes, students, leads)
   2. `school_multi_tenant_schema.sql`
   3. `user_administration_schema.sql` → creates `user_roles` table (CRITICAL for auth.py!)
   4. `class_structure_schema.sql`
   5. `term_session_schema.sql`
   6. `student_lifecycle_schema.sql`
   7. `receipts_schema.sql`
   8. `debtors_schema.sql`
   9. `bulk_billing_schema.sql`
   10. `extended_fields_schema.sql`
   11. `calendar_schema.sql`
   12. `reminders_schema.sql`, `reminder_queue_schema.sql`
   13. `messaging_integration_schema.sql` → creates `message_templates`
   14. `activity_audit_schema.sql`
   15. `frontdesk_schema.sql`
   16. `helpdesk_enhancements_schema.sql`
   17. `lost_lead_schema.sql`
   18. `workload_schema.sql`
   19. `analytics_schema.sql`, `predictive_analytics_schema.sql`
   20. `session_tracking_schema.sql`
   21. `email_verification_schema.sql`
   22. `parent_student_portal_schema.sql` → adds `student_attendance`, `student_assignments`, student `user_id`/`email` columns

3. **For local dev SQLite**: SQLite doesn't support all Postgres features. Use `backend/edudrive.db` as-is for basic local testing. Document that full feature parity requires Supabase connection.

### Step 5: RBAC Endpoint Verification (Item #2 follow-up)
No changes needed to [auth.py](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/core/auth.py#L232-L241) role_permissions dict — parent + student are present. Verify:
- Parent endpoint handlers use `require_role("parent")` or `require_any_role(["parent", "school_admin"])` where appropriate
- Student dashboard endpoints use `require_role("student")`
- `has_permission()` is called where fine-grained checks are needed (e.g., `students:view-own`, `tickets:view-own`)

## Dependencies and Considerations

1. **Supabase Connection Required**: Most database writes go to the `supabase.table()` client, NOT the SQLAlchemy models. The 26 SQL files reference `auth.users` (Supabase Auth table) — these only work when connected to a real Supabase project.
2. **user_roles table is CRITICAL**: [auth.py L49](file:///C:/Users/USER/Documents/XAMMP%20NEW/htdocs/EduDrive%20CRM/backend/app/core/auth.py#L49) queries `user_roles` on EVERY login. If this table doesn't exist, every login will fall back to default `school_admin` role. **Priority: apply user_administration_schema.sql first.**
3. **Parent ↔ Student Link Logic**: There is no direct `primary_contact_parent_id` column on `families` matching the Supabase auth user ID. The link must be built by: matching parent email → `parents.email` → `parents.family_id` → `students.family_id`. Alternative: add `user_id` column to `parents` table (mirrors the `students.user_id` pattern in parent_student_portal_schema.sql).
4. **SQLite ↔ Postgres Divergence**: Alembic migration uses String(36) IDs; `.sql` files use native Postgres UUID. SQLite local dev will not match production Supabase. Set `.env` `SUPABASE_URL`/`SUPABASE_KEY` correctly for meaningful testing.
5. **Student Auth Link**: `parent_student_portal_schema.sql` adds `students.user_id REFERENCES auth.users(id)`. This column is required for student-scope endpoints to map the logged-in auth user to a student record.

## Validation

After each step, verify:

**Step 1 (Transport routes):**
- Start backend: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
- `curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/v1/bus-routes` → 200 [] (empty, no 404)
- `curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/v1/bus-stops` → 200 []
- Also: `/api/v1/transport/bus-routes` still returns same result (regression check)

**Step 2 (Parent endpoints + auth):**
- `curl -X POST http://127.0.0.1:8000/api/v1/auth/parent-login -H "Content-Type: application/json" -d '{"email":"parent1@edudrive.demo","password":"Parent@123"}'` → returns user with role="parent" (after users created in Supabase)
- Staff login to `/auth/parent-login` → should get 403
- `GET /parent/children` with parent token → returns children array (even empty = OK)
- `GET /parent/invoices` → 200
- `GET /parent/payments` → 200
- `GET /parent/communications` → 200

**Step 3 (Frontend dashboards + redirects):**
- Start frontend: `cd frontend && npm run dev`
- Navigate to `/parent-login` → enter credentials → lands on `/dashboard/parent` (NOT `/parents`)
- Navigate to `/student-login` → enter credentials → lands on `/dashboard/student` (NOT `/students`)
- Student dashboard page renders: KPI grid visible, no 404, fetch calls resolve
- Parent dashboard fetch calls to `/parent/*` no longer return 404 in browser Network tab

**Step 4 (SQL migrations):**
- Supabase SQL Editor → run each script → check "Success, no rows affected" or row counts
- `SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;` → should now list ~35+ tables including `user_roles`, `bus_routes`, `bus_stops`, `student_transport`, `vehicles`, `fee_structures`, `message_templates`, `student_attendance`, `student_assignments`, `lost_leads`, `receipts`, `reminders`, `calendar_events`
- Verify `user_roles` table exists: `SELECT COUNT(*) FROM user_roles;`

**Step 5 (RBAC verification):**
- Test each parent endpoint with a student token → should get 403
- Test each student endpoint with a parent token → should get 403
- Existing staff endpoints (e.g., `/leads`) with parent token → should get 403 (permission denied)

## Risks

| Risk | Handling / Fallback |
|---|---|
| `user_roles` table missing on Supabase → all logins default to `school_admin` role | **Apply `user_administration_schema.sql` FIRST** before any other validation. Without it, parent/student roles cannot be assigned or looked up. |
| Alembic migration fails on SQLite (Postgres syntax in .sql) | Use Supabase SQL Editor for .sql files. Only run `alembic upgrade head` for the single migration on local SQLite. Do NOT attempt to convert .sql files to SQLite — too divergent. |
| Parent auth user ID ↔ parents record link cannot be established | Add a `user_id UUID REFERENCES auth.users(id)` column to `parents` table (mirroring `students.user_id`). Include this in the combined SQL. |
| Frontend transport page still 404 after alias routes added | Confirm API_URL env var on frontend matches `http://127.0.0.1:8000/api/v1` and that backend includes the `/api/v1` prefix correctly. |
| Login redirects still land on /parents or /students (browser cached redirect) | Hard refresh (Ctrl+Shift+R), clear localStorage test tokens, test in incognito window. |
| Supabase Auth users for parent/student not created → cannot test parent/student login | Follow instructions in `parent_student_portal_schema.sql` to create demo users in Supabase Auth Dashboard first. Passwords: Parent@123 / Student@123 |
