-- Topaz Integration Schema for EduDrive CRM (PostgreSQL)
-- This schema adds CBT, Scratch Card PINs, Timetables, and enhanced functionality

-- Create custom ENUM types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exam_status') THEN
        CREATE TYPE exam_status AS ENUM ('active', 'inactive', 'archived');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'correct_option') THEN
        CREATE TYPE correct_option AS ENUM ('a', 'b', 'c', 'd');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pin_status') THEN
        CREATE TYPE pin_status AS ENUM ('unused', 'used', 'blocked');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'timetable_type') THEN
        CREATE TYPE timetable_type AS ENUM ('exam', 'class', 'general');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'target_audience') THEN
        CREATE TYPE target_audience AS ENUM ('all', 'student', 'teacher', 'parent', 'admin');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attendance_status') THEN
        CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'late');
    END IF;
END $$;

-- CBT Exams Table
CREATE TABLE IF NOT EXISTS cbt_exams (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    class VARCHAR(100) NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    status exam_status DEFAULT 'active',
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for cbt_exams
DROP TRIGGER IF EXISTS update_cbt_exams_updated_at ON cbt_exams;
CREATE TRIGGER update_cbt_exams_updated_at
    BEFORE UPDATE ON cbt_exams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- CBT Questions Table
CREATE TABLE IF NOT EXISTS cbt_questions (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_option correct_option NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES cbt_exams(id) ON DELETE CASCADE
);

-- CBT Results Table
CREATE TABLE IF NOT EXISTS cbt_results (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    student_id UUID NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES cbt_exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE (exam_id, student_id)
);

-- Scratch Card PINs Table
CREATE TABLE IF NOT EXISTS pins (
    id SERIAL PRIMARY KEY,
    pin_code VARCHAR(12) NOT NULL UNIQUE,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    status pin_status DEFAULT 'unused',
    student_id UUID,
    usage_count INTEGER DEFAULT 0,
    max_usage INTEGER DEFAULT 5,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

-- Timetables Table
CREATE TABLE IF NOT EXISTS timetables (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    type timetable_type DEFAULT 'class',
    class VARCHAR(100) DEFAULT 'all',
    session VARCHAR(50) NOT NULL,
    term VARCHAR(50) NOT NULL,
    uploaded_by UUID,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Enhanced Notifications Table (if not exists)
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    target_audience target_audience DEFAULT 'all',
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Enhanced Results Table (create if not exists, then add columns)
DO $$
BEGIN
    -- Create results table if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'results') THEN
        CREATE TABLE results (
            id SERIAL PRIMARY KEY,
            student_id UUID NOT NULL,
            subject VARCHAR(255) NOT NULL,
            score NUMERIC(5,2) DEFAULT 0,
            term VARCHAR(50),
            session VARCHAR(50),
            ca_score NUMERIC(5,2) DEFAULT 0,
            exam_score NUMERIC(5,2) DEFAULT 0,
            uploaded_by UUID,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
        );
    ELSE
        -- Add columns if they don't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'results' AND column_name = 'ca_score'
        ) THEN
            ALTER TABLE results ADD COLUMN ca_score NUMERIC(5,2) DEFAULT 0;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'results' AND column_name = 'exam_score'
        ) THEN
            ALTER TABLE results ADD COLUMN exam_score NUMERIC(5,2) DEFAULT 0;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'results' AND column_name = 'uploaded_by'
        ) THEN
            ALTER TABLE results ADD COLUMN uploaded_by UUID;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'results' AND column_name = 'uploaded_at'
        ) THEN
            ALTER TABLE results ADD COLUMN uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END IF;
END $$;

-- Add foreign key for results if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_results_uploader'
    ) THEN
        ALTER TABLE results 
        ADD CONSTRAINT fk_results_uploader 
        FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Teacher Attendance Management Table
CREATE TABLE IF NOT EXISTS teacher_attendance (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL,
    teacher_id UUID NOT NULL,
    date DATE NOT NULL,
    status attendance_status DEFAULT 'present',
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (student_id, teacher_id, date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cbt_exams_class ON cbt_exams(class);
CREATE INDEX IF NOT EXISTS idx_cbt_exams_status ON cbt_exams(status);
CREATE INDEX IF NOT EXISTS idx_cbt_questions_exam ON cbt_questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_cbt_results_student ON cbt_results(student_id);
CREATE INDEX IF NOT EXISTS idx_cbt_results_exam ON cbt_results(exam_id);
CREATE INDEX IF NOT EXISTS idx_pins_code ON pins(pin_code);
CREATE INDEX IF NOT EXISTS idx_pins_serial ON pins(serial_number);
CREATE INDEX IF NOT EXISTS idx_pins_status ON pins(status);
CREATE INDEX IF NOT EXISTS idx_timetables_class ON timetables(class);
CREATE INDEX IF NOT EXISTS idx_timetables_session ON timetables(session);
CREATE INDEX IF NOT EXISTS idx_notifications_audience ON notifications(target_audience);
CREATE INDEX IF NOT EXISTS idx_teacher_attendance_date ON teacher_attendance(date);
CREATE INDEX IF NOT EXISTS idx_teacher_attendance_teacher ON teacher_attendance(teacher_id);
