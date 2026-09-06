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

-- Step 4: Delete existing user and role mapping, then insert both in single transaction
DO $$
DECLARE
    v_school_id UUID;
    v_parent_role_id UUID;
    v_user_id UUID := '7788b872-8a1b-4dfb-b03f-0311ce0b2082';
BEGIN
    -- Get school ID
    SELECT id INTO v_school_id FROM schools WHERE slug = 'demo-school' LIMIT 1;
    IF v_school_id IS NULL THEN
        RAISE EXCEPTION 'School not found';
    END IF;
    
    -- Get parent role ID
    SELECT id INTO v_parent_role_id FROM roles WHERE name = 'parent' AND school_id = v_school_id LIMIT 1;
    IF v_parent_role_id IS NULL THEN
        RAISE EXCEPTION 'Parent role not found';
    END IF;
    
    -- Delete existing user
    DELETE FROM users WHERE email = 'parent3@edudrive.demo';
    
    -- Delete existing role mapping
    DELETE FROM user_roles WHERE user_id = v_user_id;
    
    -- Insert user
    INSERT INTO users (id, school_id, role_id, full_name, email, password_hash, status)
    VALUES (
        v_user_id,
        v_school_id,
        v_parent_role_id,
        'Demo Parent',
        'parent3@edudrive.demo',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m',
        'active'
    );
    
    RAISE NOTICE 'User inserted successfully with ID: %', v_user_id;
    
    -- Verify user exists immediately
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = v_user_id) THEN
        RAISE EXCEPTION 'User verification failed immediately after insert';
    END IF;
    
    RAISE NOTICE 'User verified in database';
    
    -- Insert role mapping in same transaction
    INSERT INTO user_roles (user_id, role, school_id)
    VALUES (v_user_id, 'parent', v_school_id);
    
    RAISE NOTICE 'Role mapping inserted successfully';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RAISE;
END $$;

-- Step 5: Re-enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- Step 6: Verify the complete setup
SELECT u.id, u.full_name, u.email, r.name as role_name, s.name as school_name
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN schools s ON u.school_id = s.id
WHERE u.email = 'parent3@edudrive.demo';
