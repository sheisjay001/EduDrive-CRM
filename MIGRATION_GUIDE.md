# SQL Schema Migration Guide for EduDrive CRM

## Overview
This guide explains how to apply the 24 SQL schema files to your Supabase database. Since direct programmatic execution is not available via the Supabase REST API, you'll need to execute these files manually in the Supabase SQL Editor.

## Prerequisites
- Access to Supabase Dashboard (https://supabase.com/dashboard)
- Project: `zdnxmgevzhaqksgllyzg`
- Appropriate permissions to execute SQL

## Execution Steps

### Step 1: Access SQL Editor
1. Go to https://supabase.com/dashboard
2. Select your project (`zdnxmgevzhaqksgllyzg`)
3. Navigate to **SQL Editor** in the left sidebar
4. Click **"New Query"** to create a new SQL editor tab

### Step 2: Execute Schema Files in Order

Execute the following SQL files in this exact order to avoid dependency issues:

#### **Phase 1: Core Base Schema (Must Execute First)**
1. `supabase_schema.sql` - Base tables (schools, users, roles, students, etc.)

#### **Phase 2: Core Extensions**
2. `activity_audit_schema.sql` - Activity logging
3. `analytics_schema.sql` - Lead conversion metrics and analytics
4. `class_structure_schema.sql` - Class organization
5. `email_verification_schema.sql` - Email verification system
6. `extended_fields_schema.sql` - Custom field extensions

#### **Phase 3: Financial & Billing**
7. `bulk_billing_schema.sql` - Bulk billing operations
8. `debtors_schema.sql` - Debt management
9. `receipts_schema.sql` - Payment receipts

#### **Phase 4: Communication & Messaging**
10. `messaging_integration_schema.sql` - Messaging system
11. `reminders_schema.sql` - Reminder system
12. `reminder_queue_schema.sql` - Reminder queue management

#### **Phase 5: Admissions & CRM**
13. `calendar_schema.sql` - Calendar and scheduling
14. `frontdesk_schema.sql` - Front desk operations
15. `helpdesk_enhancements_schema.sql` - Helpdesk ticketing
16. `lost_lead_schema.sql` - Lost lead tracking
17. `parent_student_portal_schema.sql` - Parent/student portal
18. `student_lifecycle_schema.sql` - Student lifecycle management

#### **Phase 6: Advanced Features**
19. `predictive_analytics_schema.sql` - Predictive analytics
20. `session_tracking_schema.sql` - Session tracking
21. `school_multi_tenant_schema.sql` - Multi-tenancy support
22. `term_session_schema.sql` - Term/session management
23. `user_administration_schema.sql` - User administration
24. `workload_schema.sql` - Staff workload tracking

### Step 3: How to Execute Each File

For each schema file:
1. Open the file in your code editor
2. Copy the entire SQL content
3. Paste it into the Supabase SQL Editor
4. Click **"Run"** (or press `Ctrl+Enter`)
5. Wait for execution to complete
6. Check for any error messages in the bottom panel
7. If successful, proceed to the next file

### Step 4: Verification

After executing all files, verify the schema was applied correctly:

#### Check Tables Exist
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

#### Check Functions/RPCs Exist
```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;
```

#### Check Views Exist
```sql
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public'
ORDER BY table_name;
```

## Troubleshooting

### Common Issues

**Issue: "relation already exists"**
- **Solution**: The table was already created. This is usually safe unless you need to recreate it with a different schema.

**Issue: "function already exists"**
- **Solution**: The SQL files use `CREATE OR REPLACE FUNCTION` which should handle this automatically.

**Issue: Foreign key constraint errors**
- **Solution**: Ensure you're executing files in the correct order. Dependent tables must be created before tables that reference them.

**Issue: Permission denied**
- **Solution**: Ensure you're using the service role key or have appropriate database permissions.

## Alternative: Using psql CLI

If you have PostgreSQL command-line tools installed, you can execute files directly:

```bash
# Set your database password
set PGPASSWORD=Soteria2003@

# Execute individual files
psql -h db.zdnxmgevzhaqksgllyzg.supabase.co -p 5432 -U postgres -d postgres -f supabase_schema.sql
psql -h db.zdnxmgevzhaqksgllyzg.supabase.co -p 5432 -U postgres -d postgres -f activity_audit_schema.sql
# ... continue for all files
```

Or execute all at once:
```bash
for file in *_schema.sql; do
    echo "Executing $file..."
    psql -h db.zdnxmgevzhaqksgllyzg.supabase.co -p 5432 -U postgres -d postgres -f "$file"
done
```

## Summary

- **Total schema files**: 24
- **Execution method**: Manual via Supabase SQL Editor (recommended) or psql CLI
- **Estimated time**: 15-30 minutes
- **Verification**: Run the provided SQL queries to confirm all tables/functions were created

## Next Steps After Migration

1. **Verify data integrity**: Check that all tables have the expected columns
2. **Test API endpoints**: Ensure your backend can connect and query the new schema
3. **Update alembic**: If you want to track these migrations in alembic, create migration files that match the SQL
4. **Seed initial data**: Run any seed scripts to populate reference data (roles, permissions, etc.)
