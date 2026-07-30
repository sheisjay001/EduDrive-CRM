-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schools table
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    school_type VARCHAR(50) DEFAULT 'Secondary',
    primary_color VARCHAR(20) DEFAULT '#14213D',
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles table with permissions
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(80) NOT NULL,
    permissions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(30) DEFAULT 'active',
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Families table
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    household_name VARCHAR(150) NOT NULL,
    billing_contact_parent_id UUID,
    status VARCHAR(30) DEFAULT 'active',
    notes TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Parents table
CREATE TABLE parents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    relationship VARCHAR(50) DEFAULT 'Parent',
    email VARCHAR(150),
    phone VARCHAR(30),
    preferred_channel VARCHAR(30) DEFAULT 'email',
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Classes table
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    arm VARCHAR(10),
    level_group VARCHAR(50),
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Students table
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    lead_id UUID,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    admission_no VARCHAR(50) UNIQUE,
    gender VARCHAR(20),
    date_of_birth TIMESTAMP WITH TIME ZONE,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leads table
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    parent_name VARCHAR(150) NOT NULL,
    parent_phone VARCHAR(30) NOT NULL,
    parent_email VARCHAR(150),
    source VARCHAR(50) NOT NULL,
    stage VARCHAR(50) DEFAULT 'new',
    interested_class VARCHAR(50),
    follow_up_at TIMESTAMP WITH TIME ZONE,
    notes TEXT DEFAULT '',
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoices table
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) UNIQUE,
    term VARCHAR(50) NOT NULL,
    amount_due DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(30) DEFAULT 'issued',
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(50) NOT NULL,
    provider_reference VARCHAR(100),
    paid_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tickets table
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    family_id UUID REFERENCES families(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES parents(id) ON DELETE CASCADE,
    assignee_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    subject VARCHAR(200) NOT NULL,
    priority VARCHAR(30) DEFAULT 'Medium',
    status VARCHAR(30) DEFAULT 'open',
    sla_due_at TIMESTAMP WITH TIME ZONE,
    description TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Message logs table
CREATE TABLE message_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    channel VARCHAR(30) NOT NULL,
    recipient VARCHAR(150) NOT NULL,
    subject VARCHAR(200),
    body TEXT NOT NULL,
    delivery_status VARCHAR(30) DEFAULT 'queued',
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activity logs table
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    user_id UUID,
    entity_type VARCHAR(80) NOT NULL,
    entity_id UUID,
    action VARCHAR(120) NOT NULL,
    meta_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_school_id ON users(school_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_leads_school_id ON leads(school_id);
CREATE INDEX idx_leads_stage ON leads(stage);
CREATE INDEX idx_students_school_id ON students(school_id);
CREATE INDEX idx_students_family_id ON students(family_id);
CREATE INDEX idx_invoices_school_id ON invoices(school_id);
CREATE INDEX idx_invoices_student_id ON invoices(student_id);
CREATE INDEX idx_tickets_school_id ON tickets(school_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_families_school_id ON families(school_id);

-- Row Level Security (RLS) policies
ALTER TABLE schools ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE families ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;

-- Insert default roles with permissions
INSERT INTO roles (id, school_id, name, permissions) VALUES
-- Super Admin: Full access to everything
(
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    'super_admin',
    '["*"]'::jsonb
),
-- School Admin: Full access to their school
(
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    'school_admin',
    '["dashboard:*", "admissions:*", "finance:*", "helpdesk:*", "staff:*", "reports:*", "settings:*"]'::jsonb
),
-- Admissions Officer: Leads, tours, parent inquiries
(
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    'admissions_officer',
    '["dashboard:view", "admissions:*", "leads:*", "parents:view"]'::jsonb
),
-- Bursar/Accounts Manager: Finance, payments, invoices
(
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    'bursar',
    '["dashboard:view", "finance:*", "invoices:*", "payments:*", "students:view"]'::jsonb
),
-- Teacher/Class Supervisor: Attendance, behavior, academic notes
(
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    'teacher',
    '["dashboard:view", "students:*", "attendance:*", "behavior:*", "academic:*", "parents:view"]'::jsonb
),
-- Helpdesk Officer: Tickets, parent support
(
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    'helpdesk_officer',
    '["dashboard:view", "helpdesk:*", "tickets:*", "parents:view"]'::jsonb
);

-- Create a function to check if user has specific permission
CREATE OR REPLACE FUNCTION has_permission(user_id UUID, required_permission TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_role_id UUID;
    role_permissions JSONB;
BEGIN
    SELECT role_id INTO user_role_id FROM users WHERE id = user_id;
    
    IF user_role_id IS NULL THEN
        RETURN FALSE;
    END IF;
    
    SELECT permissions INTO role_permissions FROM roles WHERE id = user_role_id;
    
    IF role_permissions IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Check for wildcard permission
    IF role_permissions ? '*' THEN
        RETURN TRUE;
    END IF;
    
    -- Check for specific permission
    RETURN role_permissions ? required_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
