-- Term/Session Setup Schema
-- Configure academic terms and sessions for the school

-- Drop tables if they exist
DROP TABLE IF EXISTS academic_sessions CASCADE;
DROP TABLE IF EXISTS academic_terms CASCADE;
DROP TABLE IF EXISTS term_dates CASCADE;

-- Academic sessions table (e.g., 2024-2025)
CREATE TABLE IF NOT EXISTS academic_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name VARCHAR(100) NOT NULL, -- '2024-2025'
    session_code VARCHAR(20) UNIQUE NOT NULL, -- '2024-25'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for academic sessions
CREATE INDEX IF NOT EXISTS idx_academic_sessions_session_code ON academic_sessions(session_code);
CREATE INDEX IF NOT EXISTS idx_academic_sessions_is_current ON academic_sessions(is_current);
CREATE INDEX IF NOT EXISTS idx_academic_sessions_school_id ON academic_sessions(school_id);

-- Academic terms table (e.g., First Term, Second Term)
CREATE TABLE IF NOT EXISTS academic_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES academic_sessions(id) ON DELETE CASCADE,
    term_name VARCHAR(100) NOT NULL, -- 'First Term', 'Second Term', 'Third Term'
    term_code VARCHAR(20) NOT NULL, -- 'TERM1', 'TERM2', 'TERM3'
    term_order INTEGER NOT NULL, -- 1, 2, 3
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    fee_structure_id UUID REFERENCES fee_structures(id) ON DELETE SET NULL,
    description TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, term_code)
);

-- Indexes for academic terms
CREATE INDEX IF NOT EXISTS idx_academic_terms_session_id ON academic_terms(session_id);
CREATE INDEX IF NOT EXISTS idx_academic_terms_term_code ON academic_terms(term_code);
CREATE INDEX IF NOT EXISTS idx_academic_terms_is_current ON academic_terms(is_current);
CREATE INDEX IF NOT EXISTS idx_academic_terms_school_id ON academic_terms(school_id);

-- Term-specific important dates
CREATE TABLE IF NOT EXISTS term_dates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term_id UUID REFERENCES academic_terms(id) ON DELETE CASCADE,
    date_type VARCHAR(50) NOT NULL, -- 'mid_term_break', 'exam_start', 'exam_end', 'holiday_start', 'holiday_end', 'report_day'
    date_name VARCHAR(255) NOT NULL,
    date_value DATE NOT NULL,
    is_school_day BOOLEAN DEFAULT true,
    notes TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for term dates
CREATE INDEX IF NOT EXISTS idx_term_dates_term_id ON term_dates(term_id);
CREATE INDEX IF NOT EXISTS idx_term_dates_date_type ON term_dates(date_type);
CREATE INDEX IF NOT EXISTS idx_term_dates_date_value ON term_dates(date_value);
CREATE INDEX IF NOT EXISTS idx_term_dates_school_id ON term_dates(school_id);

-- Function to create academic session
CREATE OR REPLACE FUNCTION create_academic_session(
    p_session_name VARCHAR(100),
    p_session_code VARCHAR(20),
    p_start_date DATE,
    p_end_date DATE,
    p_description TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_session_id UUID;
BEGIN
    -- If setting as current, unset other current sessions
    IF p_start_date <= CURRENT_DATE AND p_end_date >= CURRENT_DATE THEN
        UPDATE academic_sessions SET is_current = false WHERE school_id = p_school_id;
    END IF;
    
    INSERT INTO academic_sessions (
        session_name, session_code, start_date, end_date,
        is_current, description, school_id
    ) VALUES (
        p_session_name, p_session_code, p_start_date, p_end_date,
        (p_start_date <= CURRENT_DATE AND p_end_date >= CURRENT_DATE),
        p_description, p_school_id
    ) RETURNING id INTO v_session_id;
    
    RETURN v_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create academic term
CREATE OR REPLACE FUNCTION create_academic_term(
    p_session_id UUID,
    p_term_name VARCHAR(100),
    p_term_code VARCHAR(20),
    p_term_order INTEGER,
    p_start_date DATE,
    p_end_date DATE,
    p_fee_structure_id UUID,
    p_description TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_term_id UUID;
BEGIN
    -- If setting as current, unset other current terms
    IF p_start_date <= CURRENT_DATE AND p_end_date >= CURRENT_DATE THEN
        UPDATE academic_terms SET is_current = false WHERE school_id = p_school_id;
    END IF;
    
    INSERT INTO academic_terms (
        session_id, term_name, term_code, term_order, start_date, end_date,
        is_current, fee_structure_id, description, school_id
    ) VALUES (
        p_session_id, p_term_name, p_term_code, p_term_order, p_start_date, p_end_date,
        (p_start_date <= CURRENT_DATE AND p_end_date >= CURRENT_DATE),
        p_fee_structure_id, p_description, p_school_id
    ) RETURNING id INTO v_term_id;
    
    RETURN v_term_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get current academic term
CREATE OR REPLACE FUNCTION get_current_term(p_school_id UUID)
RETURNS TABLE(term_id UUID, term_name VARCHAR(100), term_code VARCHAR(20), session_id UUID, session_name VARCHAR(100)) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id, t.term_name, t.term_code, t.session_id, s.session_name
    FROM academic_terms t
    JOIN academic_sessions s ON t.session_id = s.id
    WHERE t.is_current = true
    AND t.school_id = p_school_id
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to set current term
CREATE OR REPLACE FUNCTION set_current_term(p_term_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Unset current for all terms in the same school
    UPDATE academic_terms
    SET is_current = false
    WHERE school_id = (SELECT school_id FROM academic_terms WHERE id = p_term_id);
    
    -- Set new current term
    UPDATE academic_terms
    SET is_current = true
    WHERE id = p_term_id;
END;
$$ LANGUAGE plpgsql;

-- Function to add term date
CREATE OR REPLACE FUNCTION add_term_date(
    p_term_id UUID,
    p_date_type VARCHAR(50),
    p_date_name VARCHAR(255),
    p_date_value DATE,
    p_is_school_day BOOLEAN,
    p_notes TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_date_id UUID;
BEGIN
    INSERT INTO term_dates (
        term_id, date_type, date_name, date_value, is_school_day, notes, school_id
    ) VALUES (
        p_term_id, p_date_type, p_date_name, p_date_value, p_is_school_day, p_notes, p_school_id
    ) RETURNING id INTO v_date_id;
    
    RETURN v_date_id;
END;
$$ LANGUAGE plpgsql;

-- Views for term management
CREATE OR REPLACE VIEW academic_calendar AS
SELECT 
    s.session_name,
    s.session_code,
    s.start_date as session_start,
    s.end_date as session_end,
    t.term_name,
    t.term_code,
    t.term_order,
    t.start_date as term_start,
    t.end_date as term_end,
    t.is_current,
    td.date_name,
    td.date_type,
    td.date_value,
    td.is_school_day
FROM academic_sessions s
JOIN academic_terms t ON s.id = t.session_id
LEFT JOIN term_dates td ON t.id = td.term_id
WHERE s.school_id IS NOT NULL
ORDER BY s.start_date DESC, t.term_order, td.date_value;

CREATE OR REPLACE VIEW current_academic_info AS
SELECT 
    s.id as session_id,
    s.session_name,
    s.session_code,
    t.id as term_id,
    t.term_name,
    t.term_code,
    t.start_date as current_term_start,
    t.end_date as current_term_end,
    EXTRACT(DAY FROM (t.end_date - CURRENT_DATE)) as days_remaining_in_term
FROM academic_sessions s
JOIN academic_terms t ON s.id = t.session_id
WHERE t.is_current = true;
