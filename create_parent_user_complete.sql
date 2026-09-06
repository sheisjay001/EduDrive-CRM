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

-- Step 4: Insert user with Supabase Auth ID - SEPARATE TRANSACTION
-- Run ONLY this step first and verify it succeeds
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
    
    -- Insert user ONLY - no role mapping
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
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error inserting user: %', SQLERRM;
        RAISE;
END $$;

-- Step 5: Verify user exists - RUN THIS AFTER STEP 4 SUCCEEDS
SELECT id, full_name, email, school_id, role_id FROM users WHERE id = '7788b872-8a1b-4dfb-b03f-0311ce0b2082'::uuid;

-- Step 6: Insert role mapping - RUN THIS ONLY AFTER STEP 5 SHOWS THE USER EXISTS
DO $$
DECLARE
    v_school_id UUID;
    v_user_id UUID := '7788b872-8a1b-4dfb-b03f-0311ce0b2082';
BEGIN
    -- Get school ID
    SELECT id INTO v_school_id FROM schools WHERE slug = 'demo-school' LIMIT 1;
    
    -- Delete existing role mapping
    DELETE FROM user_roles WHERE user_id = v_user_id;
    
    -- Insert role mapping
    INSERT INTO user_roles (user_id, role, school_id)
    VALUES (v_user_id, 'parent', v_school_id);
    
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
