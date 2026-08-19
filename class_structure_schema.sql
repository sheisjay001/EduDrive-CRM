-- Class Structure Configuration Schema
-- Configure classes, subjects, and teacher assignments

-- Drop tables if they exist
DROP TABLE IF EXISTS class_subjects CASCADE;
DROP TABLE IF EXISTS class_enrollments CASCADE;
DROP TABLE IF EXISTS classes CASCADE;

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_name VARCHAR(100) NOT NULL, -- 'JSS 1', 'SS 2', 'Grade 5'
    class_code VARCHAR(20) UNIQUE NOT NULL, -- 'JSS1', 'SS2', 'G5'
    class_level VARCHAR(50) NOT NULL, -- 'junior_secondary', 'senior_secondary', 'primary'
    section VARCHAR(50), -- 'A', 'B', 'C' for multiple sections
    capacity INTEGER DEFAULT 40,
    current_enrollment INTEGER DEFAULT 0,
    class_teacher_id UUID REFERENCES users(id) ON DELETE SET NULL,
    class_teacher_name VARCHAR(255),
    academic_session_id UUID REFERENCES academic_sessions(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for classes
CREATE INDEX IF NOT EXISTS idx_classes_class_code ON classes(class_code);
CREATE INDEX IF NOT EXISTS idx_classes_class_level ON classes(class_level);
CREATE INDEX IF NOT EXISTS idx_classes_academic_session_id ON classes(academic_session_id);
CREATE INDEX IF NOT EXISTS idx_classes_school_id ON classes(school_id);
CREATE INDEX IF NOT EXISTS idx_classes_is_active ON classes(is_active);

-- Class subjects table
CREATE TABLE IF NOT EXISTS class_subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(50),
    teacher_id UUID REFERENCES users(id) ON DELETE SET NULL,
    teacher_name VARCHAR(255),
    periods_per_week INTEGER DEFAULT 5,
    is_core_subject BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(class_id, subject_name)
);

-- Indexes for class subjects
CREATE INDEX IF NOT EXISTS idx_class_subjects_class_id ON class_subjects(class_id);
CREATE INDEX IF NOT EXISTS idx_class_subjects_teacher_id ON class_subjects(teacher_id);
CREATE INDEX IF NOT EXISTS idx_class_subjects_school_id ON class_subjects(school_id);

-- Class enrollments table
CREATE TABLE IF NOT EXISTS class_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    term_id UUID REFERENCES academic_terms(id) ON DELETE SET NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    enrollment_status VARCHAR(20) DEFAULT 'active', -- 'active', 'transferred', 'withdrawn', 'promoted', 'retained'
    promotion_status VARCHAR(20), -- 'promoted', 'retained', 'pending'
    previous_class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    next_class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    academic_performance JSONB,
    conduct_score VARCHAR(10),
    remarks TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, class_id, term_id)
);

-- Indexes for class enrollments
CREATE INDEX IF NOT EXISTS idx_class_enrollments_student_id ON class_enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_class_enrollments_class_id ON class_enrollments(class_id);
CREATE INDEX IF NOT EXISTS idx_class_enrollments_term_id ON class_enrollments(term_id);
CREATE INDEX IF NOT EXISTS idx_class_enrollments_school_id ON class_enrollments(school_id);

-- Function to create class
CREATE OR REPLACE FUNCTION create_class(
    p_class_name VARCHAR(100),
    p_class_code VARCHAR(20),
    p_class_level VARCHAR(50),
    p_section VARCHAR(50),
    p_capacity INTEGER,
    p_class_teacher_id UUID,
    p_class_teacher_name VARCHAR(255),
    p_academic_session_id UUID,
    p_description TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_class_id UUID;
BEGIN
    INSERT INTO classes (
        class_name, class_code, class_level, section, capacity,
        class_teacher_id, class_teacher_name, academic_session_id,
        description, school_id
    ) VALUES (
        p_class_name, p_class_code, p_class_level, p_section, p_capacity,
        p_class_teacher_id, p_class_teacher_name, p_academic_session_id,
        p_description, p_school_id
    ) RETURNING id INTO v_class_id;
    
    RETURN v_class_id;
END;
$$ LANGUAGE plpgsql;

-- Function to add subject to class
CREATE OR REPLACE FUNCTION add_class_subject(
    p_class_id UUID,
    p_subject_name VARCHAR(100),
    p_subject_code VARCHAR(50),
    p_teacher_id UUID,
    p_teacher_name VARCHAR(255),
    p_periods_per_week INTEGER,
    p_is_core_subject BOOLEAN,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_subject_id UUID;
BEGIN
    INSERT INTO class_subjects (
        class_id, subject_name, subject_code, teacher_id, teacher_name,
        periods_per_week, is_core_subject, school_id
    ) VALUES (
        p_class_id, p_subject_name, p_subject_code, p_teacher_id, p_teacher_name,
        p_periods_per_week, p_is_core_subject, p_school_id
    ) RETURNING id INTO v_subject_id;
    
    -- Update class enrollment count if teacher assigned
    IF p_teacher_id IS NOT NULL THEN
        -- Could add teacher workload tracking here
    END IF;
    
    RETURN v_subject_id;
END;
$$ LANGUAGE plpgsql;

-- Function to enroll student in class
CREATE OR REPLACE FUNCTION enroll_student_in_class(
    p_student_id UUID,
    p_class_id UUID,
    p_term_id UUID,
    p_previous_class_id UUID,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_enrollment_id UUID;
BEGIN
    INSERT INTO class_enrollments (
        student_id, class_id, term_id, previous_class_id, school_id
    ) VALUES (
        p_student_id, p_class_id, p_term_id, p_previous_class_id, p_school_id
    ) RETURNING id INTO v_enrollment_id;
    
    -- Update class enrollment count
    UPDATE classes
    SET current_enrollment = current_enrollment + 1
    WHERE id = p_class_id;
    
    -- Update student's class
    UPDATE students
    SET class_id = p_class_id
    WHERE id = p_student_id;
    
    RETURN v_enrollment_id;
END;
$$ LANGUAGE plpgsql;

-- Function to promote students
CREATE OR REPLACE FUNCTION promote_students(
    p_class_id UUID,
    p_next_class_id UUID,
    p_term_id UUID,
    p_school_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_promoted_count INTEGER;
BEGIN
    -- Update enrollments
    UPDATE class_enrollments
    SET 
        enrollment_status = 'promoted',
        next_class_id = p_next_class_id,
        updated_at = NOW()
    WHERE class_id = p_class_id
    AND enrollment_status = 'active';
    
    GET DIAGNOSTICS v_promoted_count = ROW_COUNT;
    
    -- Create new enrollments for promoted students
    INSERT INTO class_enrollments (student_id, class_id, term_id, previous_class_id, school_id)
    SELECT student_id, p_next_class_id, p_term_id, p_class_id, p_school_id
    FROM class_enrollments
    WHERE class_id = p_class_id
    AND enrollment_status = 'promoted'
    AND NOT EXISTS (
        SELECT 1 FROM class_enrollments ce2
        WHERE ce2.student_id = class_enrollments.student_id
        AND ce2.class_id = p_next_class_id
        AND ce2.term_id = p_term_id
    );
    
    -- Update enrollment counts
    UPDATE classes
    SET current_enrollment = current_enrollment - v_promoted_count
    WHERE id = p_class_id;
    
    UPDATE classes
    SET current_enrollment = current_enrollment + v_promoted_count
    WHERE id = p_next_class_id;
    
    RETURN v_promoted_count;
END;
$$ LANGUAGE plpgsql;

-- Views for class management
CREATE OR REPLACE VIEW class_structure AS
SELECT 
    c.id,
    c.class_name,
    c.class_code,
    c.class_level,
    c.section,
    c.capacity,
    c.current_enrollment,
    ROUND((c.current_enrollment::DECIMAL / NULLIF(c.capacity, 0)) * 100, 2) as enrollment_percentage,
    c.class_teacher_name,
    c.academic_session_id,
    s.session_name,
    COUNT(cs.id) as total_subjects,
    COUNT(cs.id) FILTER (WHERE cs.is_core_subject = true) as core_subjects,
    COUNT(ce.id) as enrolled_students
FROM classes c
LEFT JOIN academic_sessions s ON c.academic_session_id = s.id
LEFT JOIN class_subjects cs ON c.id = cs.class_id AND cs.is_active = true
LEFT JOIN class_enrollments ce ON c.id = ce.class_id AND ce.enrollment_status = 'active'
WHERE c.is_active = true
GROUP BY c.id, c.class_name, c.class_code, c.class_level, c.section, c.capacity,
         c.current_enrollment, c.class_teacher_name, c.academic_session_id, s.session_name
ORDER BY c.class_level, c.class_code;

CREATE OR REPLACE VIEW teacher_subject_load AS
SELECT 
    cs.teacher_id,
    cs.teacher_name,
    COUNT(DISTINCT cs.class_id) as classes_assigned,
    COUNT(*) as total_subjects,
    SUM(cs.periods_per_week) as total_periods_per_week,
    STRING_AGG(DISTINCT c.class_name, ', ') as assigned_classes
FROM class_subjects cs
JOIN classes c ON cs.class_id = c.id
WHERE cs.teacher_id IS NOT NULL
AND cs.is_active = true
GROUP BY cs.teacher_id, cs.teacher_name
ORDER BY total_periods_per_week DESC;

CREATE OR REPLACE VIEW student_class_history AS
SELECT 
    ce.student_id,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    c.class_name,
    c.class_code,
    t.term_name,
    t.term_code,
    s.session_name,
    ce.enrollment_date,
    ce.enrollment_status,
    ce.promotion_status,
    ce.academic_performance,
    ce.conduct_score
FROM class_enrollments ce
JOIN students s ON ce.student_id = s.id
JOIN classes c ON ce.class_id = c.id
JOIN academic_terms t ON ce.term_id = t.id
JOIN academic_sessions s ON t.session_id = s.id
ORDER BY ce.enrollment_date DESC;
