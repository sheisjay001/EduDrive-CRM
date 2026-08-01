-- Parent and Student Portal Schema and Demo Data
-- This script creates tables and demo users for parent and student portals

-- ============================================
-- TABLE CREATION
-- ============================================

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
BEGIN
    SELECT id INTO school_id FROM schools LIMIT 1;
    
    IF school_id IS NULL THEN
        RAISE NOTICE 'No school found. Please create a school first.';
    ELSE
        -- Parent User 1 Role Assignment
        INSERT INTO user_roles (user_id, role, school_id, created_at)
        VALUES (
            'a1b2c3d4-e5f6-7890-abcd-ef1234567890', -- parent1@edudrive.demo (replace with actual user_id)
            'parent',
            school_id,
            NOW()
        ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
        
        -- Parent User 2 Role Assignment
        INSERT INTO user_roles (user_id, role, school_id, created_at)
        VALUES (
            'b2c3d4e5-f6a7-8901-bcde-f12345678901', -- parent2@edudrive.demo (replace with actual user_id)
            'parent',
            school_id,
            NOW()
        ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
        
        -- Student User 1 Role Assignment
        INSERT INTO user_roles (user_id, role, school_id, created_at)
        VALUES (
            'c3d4e5f6-a7b8-9012-cdef-123456789012', -- student1@edudrive.demo (replace with actual user_id)
            'student',
            school_id,
            NOW()
        ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
        
        -- Student User 2 Role Assignment
        INSERT INTO user_roles (user_id, role, school_id, created_at)
        VALUES (
            'd4e5f6a7-b8c9-0123-def0-234567890123', -- student2@edudrive.demo (replace with actual user_id)
            'student',
            school_id,
            NOW()
        ) ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role, school_id = EXCLUDED.school_id;
        
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
    demo_student1_id UUID := 'c3d4e5f6-a7b8-9012-cdef-123456789012';
    demo_student2_id UUID := 'd4e5f6a7-b8c9-0123-def0-234567890123';
BEGIN
    SELECT id INTO school_id FROM schools LIMIT 1;
    
    IF school_id IS NOT NULL THEN
        -- Sample Student Attendance Records
        INSERT INTO student_attendance (student_id, date, status, notes, recorded_by, school_id)
        VALUES
            (demo_student1_id, CURRENT_DATE - INTERVAL '5 days', 'present', NULL, demo_student1_id, school_id),
            (demo_student1_id, CURRENT_DATE - INTERVAL '4 days', 'present', NULL, demo_student1_id, school_id),
            (demo_student1_id, CURRENT_DATE - INTERVAL '3 days', 'late', 'Arrived 15 minutes late', demo_student1_id, school_id),
            (demo_student1_id, CURRENT_DATE - INTERVAL '2 days', 'present', NULL, demo_student1_id, school_id),
            (demo_student1_id, CURRENT_DATE - INTERVAL '1 day', 'absent', 'Sick leave', demo_student1_id, school_id),
            (demo_student2_id, CURRENT_DATE - INTERVAL '5 days', 'present', NULL, demo_student2_id, school_id),
            (demo_student2_id, CURRENT_DATE - INTERVAL '4 days', 'present', NULL, demo_student2_id, school_id),
            (demo_student2_id, CURRENT_DATE - INTERVAL '3 days', 'present', NULL, demo_student2_id, school_id),
            (demo_student2_id, CURRENT_DATE - INTERVAL '2 days', 'excused', 'Medical appointment', demo_student2_id, school_id),
            (demo_student2_id, CURRENT_DATE - INTERVAL '1 day', 'present', NULL, demo_student2_id, school_id)
        ON CONFLICT DO NOTHING;
        
        -- Sample Student Assignments
        INSERT INTO student_assignments (student_id, title, description, subject, due_date, status, assigned_by, school_id)
        VALUES
            (demo_student1_id, 'Math Homework Chapter 5', 'Complete exercises 1-20 from Chapter 5', 'Mathematics', CURRENT_DATE + INTERVAL '3 days', 'pending', demo_student1_id, school_id),
            (demo_student1_id, 'Science Project', 'Create a presentation on renewable energy', 'Science', CURRENT_DATE + INTERVAL '7 days', 'in_progress', demo_student1_id, school_id),
            (demo_student1_id, 'English Essay', 'Write a 500-word essay on climate change', 'English', CURRENT_DATE - INTERVAL '2 days', 'completed', demo_student1_id, school_id),
            (demo_student2_id, 'History Report', 'Research and write about World War II', 'History', CURRENT_DATE + INTERVAL '5 days', 'pending', demo_student2_id, school_id),
            (demo_student2_id, 'Math Quiz Preparation', 'Study for upcoming algebra quiz', 'Mathematics', CURRENT_DATE + INTERVAL '2 days', 'in_progress', demo_student2_id, school_id),
            (demo_student2_id, 'Geography Map Assignment', 'Label countries on world map', 'Geography', CURRENT_DATE - INTERVAL '1 day', 'completed', demo_student2_id, school_id)
        ON CONFLICT DO NOTHING;
        
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
    s.name as student_name,
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
    s.name as student_name,
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

STEP 2: Get User IDs
Run this query to get the actual user IDs:
SELECT id, email FROM auth.users WHERE email LIKE '%@edudrive.demo';

STEP 3: Update User IDs in this script
Replace the placeholder user IDs in the role assignment section with the actual IDs from step 2.

STEP 4: Run this script in Supabase SQL Editor
Execute the entire script to create tables and assign roles.

STEP 5: Test Login
- Parent Login: /parent-login
- Student Login: /student-login
*/
