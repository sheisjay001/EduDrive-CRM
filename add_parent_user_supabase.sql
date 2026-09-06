-- Add Parent User to Supabase Database
-- Run this in the Supabase SQL Editor

-- First, get the school ID (adjust the school name if needed)
DO $$
DECLARE
    v_school_id UUID;
    v_parent_role_id UUID;
    v_parent_user_id UUID;
BEGIN
    -- Get or create school
    SELECT id INTO v_school_id FROM schools WHERE slug = 'demo-school' LIMIT 1;
    
    IF v_school_id IS NULL THEN
        -- Create demo school if it doesn't exist
        INSERT INTO schools (name, slug, school_type, primary_color)
        VALUES ('Demo School', 'demo-school', 'Secondary', '#14213D')
        RETURNING id INTO v_school_id;
        RAISE NOTICE 'Created demo school';
    ELSE
        RAISE NOTICE 'Found existing school with ID: %', v_school_id;
    END IF;
    
    -- Get or create parent role
    SELECT id INTO v_parent_role_id FROM roles WHERE school_id = v_school_id AND name = 'parent' LIMIT 1;
    
    IF v_parent_role_id IS NULL THEN
        -- Create parent role
        INSERT INTO roles (school_id, name, permissions)
        VALUES (v_school_id, 'parent', ARRAY['view_children', 'view_invoices', 'create_tickets', 'view_tickets'])
        RETURNING id INTO v_parent_role_id;
        RAISE NOTICE 'Created parent role';
    ELSE
        RAISE NOTICE 'Found existing parent role with ID: %', v_parent_role_id;
    END IF;
    
    -- Check if parent user already exists
    SELECT id INTO v_parent_user_id FROM users WHERE email = 'parent3@edudrive.demo' LIMIT 1;
    
    IF v_parent_user_id IS NOT NULL THEN
        RAISE NOTICE 'Parent user already exists with ID: %', v_parent_user_id;
    ELSE
        -- Create parent user
        -- Note: You need to generate a proper password hash. 
        -- For 'password123', the bcrypt hash is: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m
        INSERT INTO users (school_id, role_id, full_name, email, password_hash, status)
        VALUES (
            v_school_id,
            v_parent_role_id,
            'Demo Parent',
            'parent3@edudrive.demo',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW9iW5J5q6m',
            'active'
        )
        RETURNING id INTO v_parent_user_id;
        RAISE NOTICE 'Created parent user with ID: %', v_parent_user_id;
    END IF;
    
    RAISE NOTICE 'Parent user setup complete';
    RAISE NOTICE 'Login credentials: parent3@edudrive.demo / password123';
END $$;

-- Verify the user was created
SELECT id, full_name, email, role_id, status 
FROM users 
WHERE email = 'parent3@edudrive.demo';
