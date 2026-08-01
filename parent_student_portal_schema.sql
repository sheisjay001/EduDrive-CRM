-- Parent and Student Portal Schema and Demo Data
-- This script creates tables and demo users for parent and student portals

-- ============================================
-- TABLE CREATION
-- ============================================

-- Add user_id column to students table if it doesn't exist
DO $$
BEGIN
    -- Add user_id column to students table if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'students' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE students ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added user_id column to students table';
    END IF;
    
    -- Add email column to students table if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'students' AND column_name = 'email'
    ) THEN
        ALTER TABLE students ADD COLUMN email VARCHAR(150);
        RAISE NOTICE 'Added email column to students table';
    END IF;
    
    -- Add enrollment_date column to students table if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'students' AND column_name = 'enrollment_date'
    ) THEN
        ALTER TABLE students ADD COLUMN enrollment_date DATE;
        RAISE NOTICE 'Added enrollment_date column to students table';
    END IF;
END $$;

-- Student Attendance Table
CREATE TABLE IF NOT EXISTS student_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    notes TEXT,
    recorded_by UUID REFERENCES auth.users(id),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for student_attendance
CREATE INDEX IF NOT EXISTS idx_student_attendance_student_id ON student_attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_student_attendance_date ON student_attendance(date);
CREATE INDEX IF NOT EXISTS idx_student_attendance_school_id ON student_attendance(school_id);

-- Student Assignments Table
CREATE TABLE IF NOT EXISTS student_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    due_date DATE,
    assigned_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    grade VARCHAR(10),
    feedback TEXT,
    assigned_by UUID REFERENCES auth.users(id),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for student_assignments
CREATE INDEX IF NOT EXISTS idx_student_assignments_student_id ON student_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_student_assignments_status ON student_assignments(status);
CREATE INDEX IF NOT EXISTS idx_student_assignments_school_id ON student_assignments(school_id);

-- ============================================
-- DEMO PARENT USERS
-- ============================================

-- Parent User 1
-- Email: parent1@edudrive.demo
-- Password: Parent@123
-- Role: parent

-- Parent User 2  
-- Email: parent2@edudrive.demo
-- Password: Parent@123
-- Role: parent

-- ============================================
-- DEMO STUDENT USERS
-- ============================================

-- Student User 1
-- Email: student1@edudrive.demo
-- Password: Student@123
-- Role: student

-- Student User 2
-- Email: student2@edudrive.demo
-- Password: Student@123
-- Role: student

-- ============================================
-- ROLE ASSIGNMENTS FOR PARENTS AND STUDENTS
-- ============================================

-- Get school ID for role assignments
DO $$
DECLARE
    school_id UUID;
    parent1_id UUID;
    parent2_id UUID;
    student1_id UUID;
    student2_id UUID;
BEGIN
    SELECT id INTO school_id FROM schools LIMIT 1;
    
    IF school_id IS NULL THEN
        RAISE NOTICE 'No school found. Please create a school first.';
    ELSE
        -- Get actual user IDs from auth.users table
        SELECT id INTO parent1_id FROM auth.users WHERE email = 'parent1@edudrive.demo' LIMIT 1;
        SELECT id INTO parent2_id FROM auth.users WHERE email = 'parent2@edudrive.demo' LIMIT 1;
        SELECT id INTO student1_id FROM auth.users WHERE email = 'student1@edudrive.demo' LIMIT 1;
        SELECT id INTO student2_id FROM auth.users WHERE email = 'student2@edudrive.demo' LIMIT 1;
        
        -- Only assign roles if users exist
        IF parent1_id IS NOT NULL THEN
            INSERT INTO user_roles (user_id, role, school_id, created_at)
            VALUES (parent1_id, 'parent', school_id, NOW())
            ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
            RAISE NOTICE 'Assigned parent role to parent1@edudrive.demo';
        ELSE
            RAISE NOTICE 'User parent1@edudrive.demo not found. Please create user first in Supabase Dashboard.';
        END IF;
        
        IF parent2_id IS NOT NULL THEN
            INSERT INTO user_roles (user_id, role, school_id, created_at)
            VALUES (parent2_id, 'parent', school_id, NOW())
            ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
            RAISE NOTICE 'Assigned parent role to parent2@edudrive.demo';
        ELSE
            RAISE NOTICE 'User parent2@edudrive.demo not found. Please create user first in Supabase Dashboard.';
        END IF;
        
        IF student1_id IS NOT NULL THEN
            INSERT INTO user_roles (user_id, role, school_id, created_at)
            VALUES (student1_id, 'student', school_id, NOW())
            ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
            RAISE NOTICE 'Assigned student role to student1@edudrive.demo';
        ELSE
            RAISE NOTICE 'User student1@edudrive.demo not found. Please create user first in Supabase Dashboard.';
        END IF;
        
        IF student2_id IS NOT NULL THEN
            INSERT INTO user_roles (user_id, role, school_id, created_at)
            VALUES (student2_id, 'student', school_id, NOW())
            ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
            RAISE NOTICE 'Assigned student role to student2@edudrive.demo';
        ELSE
            RAISE NOTICE 'User student2@edudrive.demo not found. Please create user first in Supabase Dashboard.';
        END IF;
        
        RAISE NOTICE 'Parent and student roles assigned. School ID: %', school_id;
    END IF;
END $$;

-- ============================================
-- SAMPLE DATA FOR TESTING
-- ============================================

-- Get school ID and demo student IDs for sample data
DO $$
DECLARE
    school_id UUID;
    student1_auth_id UUID;
    student2_auth_id UUID;
    student1_record_id UUID;
    student2_record_id UUID;
BEGIN
    SELECT id INTO school_id FROM schools LIMIT 1;
    SELECT id INTO student1_auth_id FROM auth.users WHERE email = 'student1@edudrive.demo' LIMIT 1;
    SELECT id INTO student2_auth_id FROM auth.users WHERE email = 'student2@edudrive.demo' LIMIT 1;
    
    IF school_id IS NOT NULL THEN
        -- Only insert sample data if students exist in auth.users
        IF student1_auth_id IS NOT NULL THEN
            -- Check if student record exists in students table by email
            SELECT id INTO student1_record_id FROM students WHERE email = 'student1@edudrive.demo' LIMIT 1;
            
            -- If no student record exists, create one using existing columns
            IF student1_record_id IS NULL THEN
                INSERT INTO students (id, school_id, first_name, last_name, email, status, created_at)
                VALUES (gen_random_uuid(), school_id, 'Michael', 'Student', 'student1@edudrive.demo', 'active', NOW())
                RETURNING id INTO student1_record_id;
                RAISE NOTICE 'Created student record for student1@edudrive.demo';
            END IF;
            
            -- Sample Student Attendance Records for Student 1
            INSERT INTO student_attendance (student_id, date, status, notes, recorded_by, school_id)
            VALUES
                (student1_record_id, CURRENT_DATE - INTERVAL '5 days', 'present', NULL, student1_auth_id, school_id),
                (student1_record_id, CURRENT_DATE - INTERVAL '4 days', 'present', NULL, student1_auth_id, school_id),
                (student1_record_id, CURRENT_DATE - INTERVAL '3 days', 'late', 'Arrived 15 minutes late', student1_auth_id, school_id),
                (student1_record_id, CURRENT_DATE - INTERVAL '2 days', 'present', NULL, student1_auth_id, school_id),
                (student1_record_id, CURRENT_DATE - INTERVAL '1 day', 'absent', 'Sick leave', student1_auth_id, school_id)
            ON CONFLICT DO NOTHING;
            
            -- Sample Student Assignments for Student 1
            INSERT INTO student_assignments (student_id, title, description, subject, due_date, status, assigned_by, school_id)
            VALUES
                (student1_record_id, 'Math Homework Chapter 5', 'Complete exercises 1-20 from Chapter 5', 'Mathematics', CURRENT_DATE + INTERVAL '3 days', 'pending', student1_auth_id, school_id),
                (student1_record_id, 'Science Project', 'Create a presentation on renewable energy', 'Science', CURRENT_DATE + INTERVAL '7 days', 'in_progress', student1_auth_id, school_id),
                (student1_record_id, 'English Essay', 'Write a 500-word essay on climate change', 'English', CURRENT_DATE - INTERVAL '2 days', 'completed', student1_auth_id, school_id)
            ON CONFLICT DO NOTHING;
            
            RAISE NOTICE 'Sample data inserted for student1@edudrive.demo';
        END IF;
        
        IF student2_auth_id IS NOT NULL THEN
            -- Check if student record exists in students table by email
            SELECT id INTO student2_record_id FROM students WHERE email = 'student2@edudrive.demo' LIMIT 1;
            
            -- If no student record exists, create one using existing columns
            IF student2_record_id IS NULL THEN
                INSERT INTO students (id, school_id, first_name, last_name, email, status, created_at)
                VALUES (gen_random_uuid(), school_id, 'Sarah', 'Student', 'student2@edudrive.demo', 'active', NOW())
                RETURNING id INTO student2_record_id;
                RAISE NOTICE 'Created student record for student2@edudrive.demo';
            END IF;
            
            -- Sample Student Attendance Records for Student 2
            INSERT INTO student_attendance (student_id, date, status, notes, recorded_by, school_id)
            VALUES
                (student2_record_id, CURRENT_DATE - INTERVAL '5 days', 'present', NULL, student2_auth_id, school_id),
                (student2_record_id, CURRENT_DATE - INTERVAL '4 days', 'present', NULL, student2_auth_id, school_id),
                (student2_record_id, CURRENT_DATE - INTERVAL '3 days', 'present', NULL, student2_auth_id, school_id),
                (student2_record_id, CURRENT_DATE - INTERVAL '2 days', 'excused', 'Medical appointment', student2_auth_id, school_id),
                (student2_record_id, CURRENT_DATE - INTERVAL '1 day', 'present', NULL, student2_auth_id, school_id)
            ON CONFLICT DO NOTHING;
            
            -- Sample Student Assignments for Student 2
            INSERT INTO student_assignments (student_id, title, description, subject, due_date, status, assigned_by, school_id)
            VALUES
                (student2_record_id, 'History Report', 'Research and write about World War II', 'History', CURRENT_DATE + INTERVAL '5 days', 'pending', student2_auth_id, school_id),
                (student2_record_id, 'Math Quiz Preparation', 'Study for upcoming algebra quiz', 'Mathematics', CURRENT_DATE + INTERVAL '2 days', 'in_progress', student2_auth_id, school_id),
                (student2_record_id, 'Geography Map Assignment', 'Label countries on world map', 'Geography', CURRENT_DATE - INTERVAL '1 day', 'completed', student2_auth_id, school_id)
            ON CONFLICT DO NOTHING;
            
            RAISE NOTICE 'Sample data inserted for student2@edudrive.demo';
        END IF;
        
        RAISE NOTICE 'Sample data inserted for parent and student portals';
    END IF;
END $$;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify parent and student roles
SELECT 
    u.id,
    u.email,
    u.raw_user_meta_data->>'full_name' as full_name,
    ur.role,
    ur.school_id
FROM auth.users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
WHERE ur.role IN ('parent', 'student')
ORDER BY ur.role, u.email;

-- Verify student attendance records
SELECT 
    sa.id,
    sa.student_id,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    sa.date,
    sa.status,
    sa.notes,
    sa.recorded_at
FROM student_attendance sa
LEFT JOIN students s ON sa.student_id = s.id
ORDER BY sa.date DESC;

-- Verify student assignments
SELECT 
    sa.id,
    sa.student_id,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    sa.title,
    sa.subject,
    sa.due_date,
    sa.status,
    sa.grade
FROM student_assignments sa
LEFT JOIN students s ON sa.student_id = s.id
ORDER BY sa.due_date;

-- ============================================
-- INSTRUCTIONS FOR CREATING USERS IN SUPABASE
-- ============================================

/*
STEP 1: Create Users in Supabase Auth Dashboard
1. Go to Supabase Dashboard > Authentication > Users
2. Create the following users:

PARENT USERS:
- Email: parent1@edudrive.demo
  Password: Parent@123
  User Metadata: {"full_name": "John Parent"}

- Email: parent2@edudrive.demo  
  Password: Parent@123
  User Metadata: {"full_name": "Jane Parent"}

STUDENT USERS:
- Email: student1@edudrive.demo
  Password: Student@123
  User Metadata: {"full_name": "Michael Student"}

- Email: student2@edudrive.demo
  Password: Student@123
  User Metadata: {"full_name": "Sarah Student"}

STEP 2: Run this script in Supabase SQL Editor
The script now automatically fetches user IDs from auth.users table, so no manual ID replacement is needed.

STEP 3: Verify Results
Check the notice messages to confirm:
- Tables were created successfully
- Roles were assigned to existing users
- Sample data was inserted

STEP 4: Test Login
- Parent Login: /parent-login
- Student Login: /student-login

NOTE: If users don't exist, the script will skip role assignment and show helpful notices.
*/
