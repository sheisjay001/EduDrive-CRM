-- Student Lifecycle Log Schema
-- Tracks student progress, disciplinary records, and fee payment history term-by-term

DROP TABLE IF EXISTS student_lifecycle_logs CASCADE;

CREATE TABLE student_lifecycle_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    log_type VARCHAR(50) NOT NULL, -- 'academic', 'disciplinary', 'medical', 'attendance', 'achievement', 'fee_payment'
    term VARCHAR(50) NOT NULL, -- 'Term 1 2024/2025', etc.
    academic_year VARCHAR(20) NOT NULL, -- '2024/2025'
    
    -- Academic records
    subject VARCHAR(100),
    grade VARCHAR(10),
    score DECIMAL(5,2),
    teacher_comments TEXT,
    
    -- Disciplinary records
    incident_type VARCHAR(100),
    incident_date DATE,
    severity VARCHAR(20), -- 'minor', 'moderate', 'major', 'severe'
    action_taken TEXT,
    resolved BOOLEAN DEFAULT false,
    resolution_date DATE,
    
    -- Medical records
    medical_condition VARCHAR(255),
    treatment TEXT,
    doctor_name VARCHAR(255),
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_date DATE,
    
    -- Attendance records
    attendance_date DATE,
    attendance_status VARCHAR(20), -- 'present', 'absent', 'late', 'excused'
    absence_reason TEXT,
    
    -- Achievements
    achievement_type VARCHAR(100),
    achievement_date DATE,
    description TEXT,
    award_level VARCHAR(50), -- 'school', 'regional', 'national', 'international'
    
    -- Fee payment records
    fee_type VARCHAR(50),
    amount_paid DECIMAL(10,2),
    payment_date DATE,
    payment_method VARCHAR(50),
    term_balance DECIMAL(10,2),
    
    -- General fields
    notes TEXT,
    recorded_by UUID,
    recorded_by_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Indexes for lifecycle queries
CREATE INDEX IF NOT EXISTS idx_lifecycle_student_id ON student_lifecycle_logs(student_id);
CREATE INDEX IF NOT EXISTS idx_lifecycle_log_type ON student_lifecycle_logs(log_type);
CREATE INDEX IF NOT EXISTS idx_lifecycle_term ON student_lifecycle_logs(term);
CREATE INDEX IF NOT EXISTS idx_lifecycle_academic_year ON student_lifecycle_logs(academic_year);
CREATE INDEX IF NOT EXISTS idx_lifecycle_incident_date ON student_lifecycle_logs(incident_date);
CREATE INDEX IF NOT EXISTS idx_lifecycle_school_id ON student_lifecycle_logs(school_id);

-- Student term summary (aggregated view)
CREATE OR REPLACE VIEW student_term_summary AS
SELECT 
    student_id,
    term,
    academic_year,
    log_type,
    COUNT(*) as record_count,
    MAX(created_at) as last_updated
FROM student_lifecycle_logs
GROUP BY student_id, term, academic_year, log_type;

-- Disciplinary records view
CREATE OR REPLACE VIEW disciplinary_records AS
SELECT 
    id,
    student_id,
    term,
    academic_year,
    incident_type,
    incident_date,
    severity,
    action_taken,
    resolved,
    resolution_date,
    notes,
    recorded_by_name,
    created_at
FROM student_lifecycle_logs
WHERE log_type = 'disciplinary'
ORDER BY incident_date DESC;

-- Academic performance view
CREATE OR REPLACE VIEW academic_performance AS
SELECT 
    student_id,
    term,
    academic_year,
    subject,
    AVG(CASE WHEN score IS NOT NULL THEN score END) as average_score,
    COUNT(*) as assessment_count,
    MAX(created_at) as last_updated
FROM student_lifecycle_logs
WHERE log_type = 'academic'
GROUP BY student_id, term, academic_year, subject;

-- Function to add lifecycle log entry
CREATE OR REPLACE FUNCTION add_lifecycle_log(
    p_student_id UUID,
    p_log_type VARCHAR(50),
    p_term VARCHAR(50),
    p_academic_year VARCHAR(50),
    p_subject VARCHAR(100),
    p_grade VARCHAR(10),
    p_score DECIMAL,
    p_teacher_comments TEXT,
    p_incident_type VARCHAR(100),
    p_incident_date DATE,
    p_severity VARCHAR(20),
    p_action_taken TEXT,
    p_resolved BOOLEAN,
    p_resolution_date DATE,
    p_medical_condition VARCHAR(255),
    p_treatment TEXT,
    p_doctor_name VARCHAR(255),
    p_follow_up_required BOOLEAN,
    p_follow_up_date DATE,
    p_attendance_date DATE,
    p_attendance_status VARCHAR(20),
    p_absence_reason TEXT,
    p_achievement_type VARCHAR(100),
    p_achievement_date DATE,
    p_description TEXT,
    p_award_level VARCHAR(50),
    p_fee_type VARCHAR(50),
    p_amount_paid DECIMAL,
    p_payment_date DATE,
    p_payment_method VARCHAR(50),
    p_term_balance DECIMAL,
    p_notes TEXT,
    p_recorded_by UUID,
    p_recorded_by_name VARCHAR(255),
    p_school_id UUID
)
RETURNS UUID AS $$
BEGIN
    INSERT INTO student_lifecycle_logs (
        student_id, log_type, term, academic_year,
        subject, grade, score, teacher_comments,
        incident_type, incident_date, severity, action_taken, resolved, resolution_date,
        medical_condition, treatment, doctor_name, follow_up_required, follow_up_date,
        attendance_date, attendance_status, absence_reason,
        achievement_type, achievement_date, description, award_level,
        fee_type, amount_paid, payment_date, payment_method, term_balance,
        notes, recorded_by, recorded_by_name, school_id
    )
    VALUES (
        p_student_id, p_log_type, p_term, p_academic_year,
        p_subject, p_grade, p_score, p_teacher_comments,
        p_incident_type, p_incident_date, p_severity, p_action_taken, p_resolved, p_resolution_date,
        p_medical_condition, p_treatment, p_doctor_name, p_follow_up_required, p_follow_up_date,
        p_attendance_date, p_attendance_status, p_absence_reason,
        p_achievement_type, p_achievement_date, p_description, p_award_level,
        p_fee_type, p_amount_paid, p_payment_date, p_payment_method, p_term_balance,
        p_notes, p_recorded_by, p_recorded_by_name, p_school_id
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;
