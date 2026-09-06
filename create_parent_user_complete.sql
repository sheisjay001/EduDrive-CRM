-- Complete Parent User Creation Script for Supabase
-- This script creates the parent user in Supabase Auth and links all tables
-- IMPORTANT: Run this in Supabase SQL Editor

-- Step 1: Disable RLS on users and user_roles tables temporarily
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;

-- Step 2: Get school ID
SELECT id as school_id FROM schools WHERE slug = 'demo-school' LIMIT 1;

-- Step 3: Get or create parent role
INSERT INTO roles (school_id, name, permissions)
SELECT 
    (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1),
    'parent',
    '["view_children", "view_invoices", "create_tickets", "view_tickets"]'::jsonb
WHERE NOT EXISTS (
    SELECT 1 FROM roles 
    WHERE school_id = (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1)
    AND name = 'parent'
)
RETURNING id as parent_role_id;

-- Step 4: Delete existing user record
DELETE FROM users WHERE email = 'parent3@edudrive.demo';

-- Step 5: Insert user with Supabase Auth ID
INSERT INTO users (id, school_id, role_id, full_name, email, password_hash, status)
SELECT 
    '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid,
    (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1),
    (SELECT id FROM roles WHERE name = 'parent' AND school_id = (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1) LIMIT 1),
    'Demo Parent',
    'parent3@edudrive.demo',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m',
    'active';

-- Step 6: Verify user was inserted
SELECT id, full_name, email FROM users WHERE id = '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid;

-- Step 7: Delete existing role mapping
DELETE FROM user_roles WHERE user_id = '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid;

-- Step 8: Insert user role mapping
INSERT INTO user_roles (user_id, role, school_id)
SELECT 
    '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid,
    'parent',
    (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1);

-- Step 9: Re-enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- Step 10: Verify the complete setup
SELECT u.id, u.full_name, u.email, r.name as role_name, s.name as school_name
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN schools s ON u.school_id = s.id
WHERE u.email = 'parent3@edudrive.demo';
