-- Complete Parent User Creation Script for Supabase
-- This script creates the parent user in Supabase Auth and links all tables
-- IMPORTANT: You must first create the user in Supabase Auth via the dashboard
-- Then run this script to link the user to your custom tables

-- Step 1: Get the Supabase Auth user ID from the dashboard
-- The user ID from Supabase Auth: 7788b872-8a1b-4dfb-b03f-0311ce0b2082

DO $$
DECLARE
    v_school_id UUID;
    v_parent_role_id UUID;
    v_user_id UUID := '7788b872-8a1b-4dfb-b03f-0311ce0b2082'; -- Supabase Auth User ID
    v_email TEXT := 'parent3@edudrive.demo';
BEGIN
    -- Get school
    SELECT id INTO v_school_id FROM schools WHERE slug = 'demo-school' LIMIT 1;
    
    IF v_school_id IS NULL THEN
        RAISE EXCEPTION 'School not found';
    END IF;
    
    -- Get or create parent role
    SELECT id INTO v_parent_role_id FROM roles WHERE school_id = v_school_id AND name = 'parent' LIMIT 1;
    
    IF v_parent_role_id IS NULL THEN
        INSERT INTO roles (school_id, name, permissions)
        VALUES (v_school_id, 'parent', ARRAY['view_children', 'view_invoices', 'create_tickets', 'view_tickets'])
        RETURNING id INTO v_parent_role_id;
    END IF;
    
    -- Delete existing user record if exists
    DELETE FROM users WHERE email = v_email;
    
    -- Delete existing role mapping if exists
    DELETE FROM user_roles WHERE user_id = v_user_id;
    
    -- Insert user with Supabase Auth ID
    INSERT INTO users (id, school_id, role_id, full_name, email, password_hash, status)
    VALUES (
        v_user_id,
        v_school_id,
        v_parent_role_id,
        'Demo Parent',
        v_email,
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m', -- bcrypt hash for 'password123'
        'active'
    );
    
    -- Verify user was inserted
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = v_user_id) THEN
        RAISE EXCEPTION 'Failed to insert user with ID %', v_user_id;
    END IF;
    
    RAISE NOTICE 'User inserted successfully with ID: %', v_user_id;
    
    -- Insert user role mapping
    INSERT INTO user_roles (user_id, role, school_id)
    VALUES (v_user_id, 'parent', v_school_id);
    
    RAISE NOTICE 'Parent user setup complete';
    RAISE NOTICE 'User ID: %', v_user_id;
    RAISE NOTICE 'Email: %', v_email;
    RAISE NOTICE 'Login credentials: parent3@edudrive.demo / password123';
END $$;

-- Verify the setup
SELECT u.id, u.full_name, u.email, r.name as role_name, s.name as school_name
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN schools s ON u.school_id = s.id
WHERE u.email = 'parent3@edudrive.demo';
