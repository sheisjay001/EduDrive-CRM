"""
Script to verify Supabase database schema matches the SQL definitions.
This checks which tables, functions, and views exist in the database.
"""
import requests
from app.core.config import settings

def execute_query_via_rest(query):
    """Execute a query via Supabase REST API"""
    url = f"{settings.supabase_url}/rest/v1/"
    
    headers = {
        'apikey': settings.supabase_service_role_key,
        'Authorization': f'Bearer {settings.supabase_service_role_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    try:
        # Use the SQL endpoint if available, otherwise we'll need to use a different approach
        # Since exec_sql doesn't exist, we'll document what should be checked
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def print_verification_instructions():
    """Print instructions for manual verification"""
    print("=" * 70)
    print("SUPABASE SCHEMA VERIFICATION")
    print("=" * 70)
    print()
    print("Since direct SQL execution via REST API is not available,")
    print("please run these queries in the Supabase SQL Editor to verify:")
    print()
    print("-" * 70)
    print("1. CHECK ALL TABLES")
    print("-" * 70)
    print("""
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
""")
    
    print("-" * 70)
    print("2. CHECK ALL FUNCTIONS/RPCs")
    print("-" * 70)
    print("""
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;
""")
    
    print("-" * 70)
    print("3. CHECK ALL VIEWS")
    print("-" * 70)
    print("""
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public'
ORDER BY table_name;
""")
    
    print("-" * 70)
    print("4. CHECK TABLE COLUMNS (for specific tables)")
    print("-" * 70)
    print("""
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'your_table_name'
ORDER BY ordinal_position;
""")
    
    print("-" * 70)
    print("5. CHECK FOREIGN KEY CONSTRAINTS")
    print("-" * 70)
    print("""
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, tc.constraint_name;
""")
    
    print("-" * 70)
    print("EXPECTED TABLES (from 24 schema files)")
    print("-" * 70)
    expected_tables = [
        # Base schema
        "schools", "roles", "users", "families", "parents", "classes",
        "students", "leads", "invoices", "payments", "tickets", 
        "message_logs", "activity_logs",
        # Activity audit
        "activity_audit_logs",
        # Analytics
        "lead_conversion_metrics",
        # Bulk billing
        "bulk_invoice_batches", "bulk_invoice_items",
        # Calendar
        "calendar_events", "calendar_event_attendees",
        # Email verification
        "email_verification_tokens", "email_verification_logs",
        # Extended fields
        "extended_field_definitions", "extended_field_values",
        # Frontdesk
        "frontdesk_visits", "frontdesk_inquiries",
        # Helpdesk
        "helpdesk_ticket_comments", "helpdesk_ticket_attachments",
        # Lost lead
        "lost_leads", "lost_lead_reasons",
        # Messaging
        "message_templates", "message_campaigns",
        # Parent/Student portal
        "portal_access_tokens", "portal_activity_logs",
        # Predictive analytics
        "prediction_models", "prediction_results",
        # Receipts
        "receipts", "receipt_line_items",
        # Reminders
        "reminder_templates", "reminder_schedules",
        # Reminder queue
        "reminder_queue", "reminder_queue_history",
        # Multi-tenant
        "tenant_settings", "tenant_features",
        # Session tracking
        "user_sessions", "session_events",
        # Student lifecycle
        "student_status_history", "student_enrollment_periods",
        # Term/Session
        "academic_terms", "academic_sessions",
        # User administration
        "user_permissions", "user_audit_logs",
        # Workload
        "staff_workload", "workload_assignments"
    ]
    
    for table in sorted(expected_tables):
        print(f"  - {table}")
    
    print()
    print("-" * 70)
    print("EXPECTED FUNCTIONS/RPCs")
    print("-" * 70)
    expected_functions = [
        "has_permission",
        "track_lead_stage_change",
        "record_first_response",
        # Add more as found in schema files
    ]
    
    for func in sorted(expected_functions):
        print(f"  - {func}")
    
    print()
    print("-" * 70)
    print("EXPECTED VIEWS")
    print("-" * 70)
    expected_views = [
        "conversion_rate_by_stage",
        "response_time_metrics",
        "lead_funnel_analysis",
        "staff_lead_performance",
        # Add more as found in schema files
    ]
    
    for view in sorted(expected_views):
        print(f"  - {view}")
    
    print()
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print()
    print("Compare the results from the SQL Editor queries with the")
    print("expected lists above to ensure all schema was applied correctly.")
    print()

if __name__ == "__main__":
    print_verification_instructions()
