-- Demo Users SQL Script for EduDrive CRM
-- This script creates demo users with all different roles for testing

-- Drop user_roles table if it exists to recreate with proper constraints
DROP TABLE IF EXISTS user_roles;

-- Create user_roles table
CREATE TABLE user_roles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- First, check if a school exists and get its ID
DO $$
DECLARE
    school_id UUID;
BEGIN
    -- Try to get an existing school
    SELECT id INTO school_id FROM schools LIMIT 1;
    
    -- If no school exists, create one
    IF school_id IS NULL THEN
        INSERT INTO schools (id, name, slug, school_type, primary_color, status, created_at)
        VALUES (
            gen_random_uuid(),
            'Demo School',
            'demo-school',
            'Secondary',
            '#3B82F6',
            'active',
            NOW()
        )
        RETURNING id INTO school_id;
        
        RAISE NOTICE 'Created demo school with ID: %', school_id;
    ELSE
        RAISE NOTICE 'Using existing school with ID: %', school_id;
    END IF;
    
    -- Store the school ID in a temporary table for use in subsequent statements
    CREATE TEMP TABLE IF NOT EXISTS temp_school_id (id UUID);
    TRUNCATE temp_school_id;
    INSERT INTO temp_school_id VALUES (school_id);
END $$;

-- Create demo users in Supabase Auth
-- Note: These users will need to be created via Supabase Dashboard or API
-- The passwords below are for demo purposes only

-- User 1: Super Admin
-- Email: superadmin@edudrive.demo
-- Password: Super@123
-- Role: super_admin

-- User 2: School Admin  
-- Email: schooladmin@edudrive.demo
-- Password: School@123
-- Role: school_admin

-- User 3: Admissions Officer
-- Email: admissions@edudrive.demo
-- Password: Admissions@123
-- Role: admissions_officer

-- User 4: Bursar
-- Email: bursar@edudrive.demo
-- Password: Bursar@123
-- Role: bursar

-- User 5: Teacher
-- Email: teacher@edudrive.demo
-- Password: Teacher@123
-- Role: teacher

-- User 6: Helpdesk Officer
-- Email: helpdesk@edudrive.demo
-- Password: Helpdesk@123
-- Role: helpdesk_officer

-- After creating users in Supabase Auth Dashboard, run this to assign roles:
-- Replace the user_ids below with the actual IDs from auth.users table

-- Get the school ID from temp table
DO $$
DECLARE
    school_id UUID;
BEGIN
    SELECT id INTO school_id FROM temp_school_id LIMIT 1;
    
    -- Insert user roles (replace user_ids with actual IDs from auth.users)
    -- You can get user_ids from: SELECT id, email FROM auth.users;
    
    -- Super Admin
    INSERT INTO user_roles (user_id, role, school_id, created_at)
    VALUES (
        '81a5dc62-d7bf-4159-aa8f-2433f3e06cab', -- superadmin@edudrive.demo
        'super_admin',
        school_id,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
    
    -- School Admin
    INSERT INTO user_roles (user_id, role, school_id, created_at)
    VALUES (
        '851d53d9-4b22-406e-aa89-ec10772635ec', -- schooladmin@edudrive.demo
        'school_admin',
        school_id,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
    
    -- Admissions Officer
    INSERT INTO user_roles (user_id, role, school_id, created_at)
    VALUES (
        'c8d19ed5-3033-4559-bd86-1a4cd05d697c', -- admissions@edudrive.demo
        'admissions_officer',
        school_id,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
    
    -- Bursar
    INSERT INTO user_roles (user_id, role, school_id, created_at)
    VALUES (
        'd78d66d0-cd75-4111-a8d1-aa3da1459d5e', -- bursar@edudrive.demo
        'bursar',
        school_id,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
    
    -- Teacher
    INSERT INTO user_roles (user_id, role, school_id, created_at)
    VALUES (
        '58f0c47c-7d71-42c1-98fb-0eda9f913f9d', -- teacher@edudrive.demo
        'teacher',
        school_id,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
    
    -- Helpdesk Officer
    INSERT INTO user_roles (user_id, role, school_id, created_at)
    VALUES (
        '8b337ea5-b324-4995-ba3f-1732e266d26c', -- helpdesk@edudrive.demo
        'helpdesk_officer',
        school_id,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
    
    RAISE NOTICE 'User roles have been assigned. School ID: %', school_id;
END $$;

-- Query to verify user roles
SELECT 
    u.id,
    u.email,
    u.raw_user_meta_data->>'full_name' as full_name,
    ur.role,
    ur.school_id
FROM auth.users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
WHERE u.email LIKE '%@edudrive.demo'
ORDER BY ur.role;

-- Clean up temp table
DROP TABLE IF EXISTS temp_school_id;
