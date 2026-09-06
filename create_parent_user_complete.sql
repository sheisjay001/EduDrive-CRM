-- Complete Parent User Creation Script for Supabase
-- This script creates the parent user in Supabase Auth and links all tables
-- IMPORTANT: You must first create the user in Supabase Auth via the dashboard
-- Then run this script to link the user to your custom tables

-- Step 1: Get the Supabase Auth user ID from the dashboard
-- The user ID from Supabase Auth: 7788b872-8a1b-4dfb-b03f-0311ce0b2082

-- Step 1: Get school ID (run this first and note the ID)
SELECT id as school_id FROM schools WHERE slug = 'demo-school' LIMIT 1;

-- Step 2: Get or create parent role (run this and note the ID)
-- If no result, run the insert below
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

-- Step 3: Delete existing user record
DELETE FROM users WHERE email = 'parent3@edudrive.demo';

-- Step 4: Insert user with Supabase Auth ID
INSERT INTO users (id, school_id, role_id, full_name, email, password_hash, status)
SELECT 
    '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid,
    (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1),
    (SELECT id FROM roles WHERE name = 'parent' AND school_id = (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1) LIMIT 1),
    'Demo Parent',
    'parent3@edudrive.demo',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m',
    'active';

-- Step 5: Verify user was inserted
SELECT id, full_name, email FROM users WHERE id = '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid;

-- Step 6: Delete existing role mapping
DELETE FROM user_roles WHERE user_id = '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid;

-- Step 7: Insert user role mapping
-- First check if user exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid) THEN
        RAISE EXCEPTION 'User does not exist in users table';
    END IF;
    
    INSERT INTO user_roles (user_id, role, school_id)
    SELECT 
        '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid,
        'parent',
        (SELECT id FROM schools WHERE slug = 'demo-school' LIMIT 1);
        
    RAISE NOTICE 'Role mapping inserted successfully';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error inserting role mapping: %', SQLERRM;
        RAISE;
END $$;

-- Step 8: Verify the complete setup
SELECT u.id, u.full_name, u.email, r.name as role_name, s.name as school_name
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN schools s ON u.school_id = s.id
WHERE u.email = 'parent3@edudrive.demo';
