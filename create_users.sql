-- Create users in Supabase Auth and assign roles
-- Run this in Supabase SQL Editor

-- IMPORTANT: First create users in Supabase Auth Dashboard with these credentials:
-- admin@greenfieldcollege.ng / Admin@123
-- admissions@greenfieldcollege.ng / Admissions@123
-- bursar@greenfieldcollege.ng / Bursar@123
-- teacher@greenfieldcollege.ng / Teacher@123

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user_roles table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    school_id UUID DEFAULT uuid_generate_v4(),
    role VARCHAR(50) NOT NULL DEFAULT 'school_admin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Check if schools table has any data
SELECT * FROM schools LIMIT 5;

-- If no school exists, you need to create one manually in Supabase Dashboard
-- Go to Table Editor → schools → Insert row and create a school

-- Assign roles to users using existing school
-- Super Admin - Full system access
INSERT INTO user_roles (user_id, school_id, role)
SELECT
    (SELECT id FROM auth.users WHERE email = 'admin@greenfieldcollege.ng' LIMIT 1),
    (SELECT id FROM schools LIMIT 1),
    'super_admin'
WHERE NOT EXISTS (
    SELECT 1 FROM user_roles
    WHERE user_id = (SELECT id FROM auth.users WHERE email = 'admin@greenfieldcollege.ng' LIMIT 1)
);

-- Admissions Officer - Leads, tours, parent inquiries, pipeline management
INSERT INTO user_roles (user_id, school_id, role)
SELECT
    (SELECT id FROM auth.users WHERE email = 'admissions@greenfieldcollege.ng' LIMIT 1),
    (SELECT id FROM schools LIMIT 1),
    'admissions_officer'
WHERE NOT EXISTS (
    SELECT 1 FROM user_roles
    WHERE user_id = (SELECT id FROM auth.users WHERE email = 'admissions@greenfieldcollege.ng' LIMIT 1)
);

-- Bursar - Fee statuses, payments, invoices, payment reminders
INSERT INTO user_roles (user_id, school_id, role)
SELECT
    (SELECT id FROM auth.users WHERE email = 'bursar@greenfieldcollege.ng' LIMIT 1),
    (SELECT id FROM schools LIMIT 1),
    'bursar'
WHERE NOT EXISTS (
    SELECT 1 FROM user_roles
    WHERE user_id = (SELECT id FROM auth.users WHERE email = 'bursar@greenfieldcollege.ng' LIMIT 1)
);

-- Teacher - Student attendance, behavior notes, academic notes, parent notifications
INSERT INTO user_roles (user_id, school_id, role)
SELECT
    (SELECT id FROM auth.users WHERE email = 'teacher@greenfieldcollege.ng' LIMIT 1),
    (SELECT id FROM schools LIMIT 1),
    'teacher'
WHERE NOT EXISTS (
    SELECT 1 FROM user_roles
    WHERE user_id = (SELECT id FROM auth.users WHERE email = 'teacher@greenfieldcollege.ng' LIMIT 1)
);

-- Verify the setup
SELECT
    u.id,
    u.email,
    u.email_confirmed_at,
    ur.role,
    s.name as school_name
FROM auth.users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN schools s ON ur.school_id = s.id
WHERE u.email IN (
    'admin@greenfieldcollege.ng',
    'admissions@greenfieldcollege.ng',
    'bursar@greenfieldcollege.ng',
    'teacher@greenfieldcollege.ng'
);
