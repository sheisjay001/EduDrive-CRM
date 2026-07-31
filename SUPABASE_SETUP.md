# Supabase Integration & Role-Based Access Control Setup

## Overview
This document summarizes the Supabase integration and role-based access control (RBAC) implementation for EduDrive CRM.

## What Was Implemented

### 1. Supabase Client Setup (Frontend)
- Installed `@supabase/supabase-js` package
- Created Supabase client configuration in `frontend/lib/supabase.ts`
- Updated auth storage (`frontend/services/auth-storage.ts`) to work with Supabase sessions
- Modified API client (`frontend/services/api-client.ts`) to use Supabase authentication

### 2. Database Schema (Backend)
- Created comprehensive Supabase schema in `backend/supabase_schema.sql`
- Schema includes all tables: schools, roles, users, families, parents, students, classes, leads, invoices, payments, tickets, message_logs, activity_logs
- Added Row Level Security (RLS) policies
- Created permission checking function in PostgreSQL

### 3. Role-Based Access Control (Backend)
- Added `teacher` role to the system with appropriate permissions
- Implemented `has_permission()` function in `backend/app/core/auth.py`
- Updated all API routes with permission checks:
  - `dashboard:view` - Dashboard access
  - `leads:view/create/update` - Admissions management
  - `students:view` - Student records
  - `finance:view` - Financial data
  - `tickets:view` - Helpdesk tickets
  - `staff:view` - Staff management
  - `reports:view` - Reports access
  - `settings:view` - Settings access
  - `messaging:view` - Messaging system
  - `families:view` - Family records
  - `parents:view` - Parent records

### 4. Role Permissions

| Role | Permissions |
|------|-------------|
| **super_admin** | Full access (`*`) - Proprietor/Board level |
| **school_admin** | Dashboard, admissions, finance, helpdesk, staff, reports, settings |
| **admissions_officer** | Dashboard, admissions, leads, parents view |
| **bursar** | Dashboard, finance, invoices, payments, students view |
| **teacher** | Dashboard, students, attendance, behavior, academic, parents view |
| **helpdesk_officer** | Dashboard, helpdesk, tickets, parents view |

## Next Steps to Complete Integration

### 1. Set Up Supabase Database
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the schema from `backend/supabase_schema.sql`
4. This will create all tables, indexes, and RLS policies

### 2. Configure Supabase Environment Variables
Add these to your Render environment variables:

**Frontend:**
- `NEXT_PUBLIC_SUPABASE_URL` = `https://zdnxmgevzhaqksgllyzg.supabase.co`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` = `sb_publishable_00MK4XHG1p9HS21WHfa9Fw_jXKxO4n2`
- `NEXT_PUBLIC_API_URL` = `https://edudrive-crm.onrender.com/api/v1`

**Backend:**
- `SUPABASE_URL` = `https://zdnxmgevzhaqksgllyzg.supabase.co`
- `SUPABASE_SERVICE_ROLE_KEY` = (Get from Supabase dashboard → Settings → API)

### 3. Update Backend to Use Supabase
The backend currently uses SQLite. To fully migrate to Supabase:

1. Install Supabase Python client:
```bash
cd backend
pip install supabase
```

2. Update database connection in `backend/app/database/session.py` to use Supabase instead of SQLite

3. Update repositories to use Supabase client instead of SQLAlchemy

### 4. Seed Initial Data
Run the seed script to create initial users with different roles:
```bash
cd backend
python seed_db.py
```

### 5. Test Authentication Flow
1. Test login with different user roles
2. Verify permission checks work correctly
3. Test that users can only access their permitted resources

## Current Status

✅ **Completed:**
- Supabase client setup in frontend
- Database schema design
- Role-based permission system
- Permission checks on all API routes
- Teacher role implementation

⏳ **Pending:**
- Supabase database creation (run SQL schema)
- Backend migration to use Supabase instead of SQLite
- Environment variable configuration on Render
- Testing with actual Supabase authentication

## Important Notes

1. **Hybrid Authentication:** The current implementation uses Supabase for authentication while the backend still uses SQLite. This is a transitional state.

2. **Permission System:** The permission system is implemented in the backend and checks are enforced on all sensitive endpoints.

3. **Teacher Role:** The teacher role has been added with permissions for student management, attendance, behavior tracking, and academic notes.

4. **Row Level Security:** RLS policies are defined in the schema but need to be properly configured in Supabase after database creation.

## Testing Checklist

- [ ] Create Supabase database using schema
- [ ] Configure environment variables
- [ ] Test login with Supabase
- [ ] Test role-based access for each role
- [ ] Verify permission enforcement on all endpoints
- [ ] Test teacher-specific features (attendance, behavior, academic notes)
- [ ] Deploy updated backend to Render
- [ ] Deploy updated frontend to Render
