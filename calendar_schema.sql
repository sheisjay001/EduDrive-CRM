-- Tour and Assessment Calendar Booking Schema
-- Handles scheduling of parent visits and student assessments

DROP TABLE IF EXISTS calendar_events CASCADE;
DROP TABLE IF EXISTS tour_time_slots CASCADE;
DROP TABLE IF EXISTS assessment_schedules CASCADE;

CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL, -- 'tour', 'assessment', 'meeting'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'no_show'
    
    -- Lead/Student information
    related_entity_type VARCHAR(50), -- 'lead', 'student'
    related_entity_id VARCHAR(255),
    
    -- Parent/Contact information
    parent_name VARCHAR(255),
    parent_contact VARCHAR(255),
    parent_email VARCHAR(255),
    
    -- Staff assignment
    assigned_staff_id UUID,
    assigned_staff_name VARCHAR(255),
    
    -- Assessment specific
    assessment_type VARCHAR(100), -- 'entrance', 'placement', 'progress'
    assessment_subjects TEXT[], -- array of subjects
    
    -- Tour specific
    tour_type VARCHAR(100), -- 'general', 'academic', 'facilities'
    
    -- Notes and follow-up
    notes TEXT,
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_date DATE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    school_id UUID
);

-- Indexes for calendar queries
CREATE INDEX IF NOT EXISTS idx_calendar_events_date ON calendar_events(event_date);
CREATE INDEX IF NOT EXISTS idx_calendar_events_status ON calendar_events(status);
CREATE INDEX IF NOT EXISTS idx_calendar_events_entity ON calendar_events(related_entity_type, related_entity_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_staff ON calendar_events(assigned_staff_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_school_id ON calendar_events(school_id);

-- Available time slots for tours
CREATE TABLE IF NOT EXISTS tour_time_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    day_of_week INTEGER NOT NULL, -- 0-6 (Sunday-Saturday)
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_bookings INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT true,
    school_id UUID
);

-- Assessment schedules
CREATE TABLE IF NOT EXISTS assessment_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_name VARCHAR(255) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    assessment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255),
    max_participants INTEGER DEFAULT 20,
    current_participants INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'full', 'closed', 'completed'
    description TEXT,
    required_documents TEXT[], -- array of required documents
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Function to check slot availability
CREATE OR REPLACE FUNCTION check_slot_availability(
    p_event_date DATE,
    p_start_time TIME,
    p_end_time TIME,
    p_school_id UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM calendar_events
    WHERE event_date = p_event_date
    AND (
        (start_time <= p_start_time AND end_time > p_start_time) OR
        (start_time < p_end_time AND end_time >= p_end_time) OR
        (start_time >= p_start_time AND end_time <= p_end_time)
    )
    AND status IN ('scheduled', 'confirmed')
    AND (p_school_id IS NULL OR school_id = p_school_id);
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Function to create calendar event
CREATE OR REPLACE FUNCTION create_calendar_event(
    p_event_type VARCHAR(50),
    p_title VARCHAR(255),
    p_description TEXT,
    p_event_date DATE,
    p_start_time TIME,
    p_end_time TIME,
    p_location VARCHAR(255),
    p_related_entity_type VARCHAR(50),
    p_related_entity_id VARCHAR(255),
    p_parent_name VARCHAR(255),
    p_parent_contact VARCHAR(255),
    p_parent_email VARCHAR(255),
    p_assigned_staff_id UUID,
    p_assigned_staff_name VARCHAR(255),
    p_assessment_type VARCHAR(100),
    p_assessment_subjects TEXT[],
    p_tour_type VARCHAR(100),
    p_notes TEXT,
    p_school_id UUID,
    p_created_by UUID
)
RETURNS UUID AS $$
DECLARE
    v_conflict_count INTEGER;
    v_event_id UUID;
BEGIN
    -- Check for scheduling conflicts
    SELECT check_slot_availability(p_event_date, p_start_time, p_end_time, p_school_id) INTO v_conflict_count;
    
    IF v_conflict_count > 0 THEN
        RAISE EXCEPTION 'Scheduling conflict: % events already scheduled for this time slot', v_conflict_count;
    END IF;
    
    -- Create the event
    INSERT INTO calendar_events (
        event_type, title, description, event_date, start_time, end_time, location,
        related_entity_type, related_entity_id,
        parent_name, parent_contact, parent_email,
        assigned_staff_id, assigned_staff_name,
        assessment_type, assessment_subjects, tour_type,
        notes, school_id, created_by
    )
    VALUES (
        p_event_type, p_title, p_description, p_event_date, p_start_time, p_end_time, p_location,
        p_related_entity_type, p_related_entity_id,
        p_parent_name, p_parent_contact, p_parent_email,
        p_assigned_staff_id, p_assigned_staff_name,
        p_assessment_type, p_assessment_subjects, p_tour_type,
        p_notes, p_school_id, p_created_by
    )
    RETURNING id INTO v_event_id;
    
    -- If it's an assessment, increment participant count
    IF p_event_type = 'assessment' THEN
        UPDATE assessment_schedules
        SET current_participants = current_participants + 1
        WHERE assessment_date = p_event_date
        AND start_time = p_start_time
        AND status = 'open';
    END IF;
    
    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;

-- View for upcoming events
CREATE OR REPLACE VIEW upcoming_events AS
SELECT 
    id,
    event_type,
    title,
    event_date,
    start_time,
    end_time,
    location,
    status,
    parent_name,
    parent_contact,
    assigned_staff_name
FROM calendar_events
WHERE event_date >= CURRENT_DATE
AND status IN ('scheduled', 'confirmed')
ORDER BY event_date ASC, start_time ASC;

-- View for today's events
CREATE OR REPLACE VIEW todays_events AS
SELECT 
    id,
    event_type,
    title,
    event_date,
    start_time,
    end_time,
    location,
    status,
    parent_name,
    parent_contact,
    assigned_staff_name
FROM calendar_events
WHERE event_date = CURRENT_DATE
AND status IN ('scheduled', 'confirmed')
ORDER BY start_time ASC;
