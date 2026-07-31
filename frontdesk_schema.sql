-- Front-Desk Daily Log Schema
-- Tracks front-desk activities: calls logged, visitors checked in, follow-up calls completed

DROP TABLE IF EXISTS frontdesk_daily_logs CASCADE;
DROP TABLE IF EXISTS frontdesk_activities CASCADE;

CREATE TABLE frontdesk_daily_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_date DATE NOT NULL,
    staff_id UUID NOT NULL,
    staff_name VARCHAR(255) NOT NULL,
    staff_role VARCHAR(50) NOT NULL,
    
    -- Call metrics
    calls_logged INTEGER DEFAULT 0,
    calls_answered INTEGER DEFAULT 0,
    calls_missed INTEGER DEFAULT 0,
    calls_followed_up INTEGER DEFAULT 0,
    
    -- Visitor metrics
    visitors_checked_in INTEGER DEFAULT 0,
    visitors_checked_out INTEGER DEFAULT 0,
    walk_in_inquiries INTEGER DEFAULT 0,
    
    -- Lead metrics
    new_leads_created INTEGER DEFAULT 0,
    lead_follow_ups_completed INTEGER DEFAULT 0,
    tours_scheduled INTEGER DEFAULT 0,
    
    -- General activities
    messages_sent INTEGER DEFAULT 0,
    complaints_logged INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    
    -- Performance notes
    notes TEXT,
    performance_rating VARCHAR(20), -- 'excellent', 'good', 'satisfactory', 'needs_improvement'
    
    -- Timestamps
    shift_start TIME,
    shift_end TIME,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Indexes for front-desk logs
CREATE INDEX IF NOT EXISTS idx_frontdesk_logs_date ON frontdesk_daily_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_frontdesk_logs_staff ON frontdesk_daily_logs(staff_id);
CREATE INDEX IF NOT EXISTS idx_frontdesk_logs_school_id ON frontdesk_daily_logs(school_id);

-- Front-desk activity details (for audit trail)
CREATE TABLE IF NOT EXISTS frontdesk_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_log_id UUID REFERENCES frontdesk_daily_logs(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL, -- 'call_logged', 'visitor_checkin', 'lead_created', etc.
    activity_description TEXT,
    related_entity_type VARCHAR(50), -- 'lead', 'visitor', 'parent', 'student'
    related_entity_id VARCHAR(255),
    activity_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    school_id UUID
);

-- Indexes for activity details
CREATE INDEX IF NOT EXISTS idx_frontdesk_activities_log_id ON frontdesk_activities(daily_log_id);
CREATE INDEX IF NOT EXISTS idx_frontdesk_activities_type ON frontdesk_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_frontdesk_activities_time ON frontdesk_activities(activity_time DESC);

-- Function to create or update daily log
CREATE OR REPLACE FUNCTION upsert_frontdesk_log(
    p_log_date DATE,
    p_staff_id UUID,
    p_staff_name VARCHAR(255),
    p_staff_role VARCHAR(50),
    p_calls_logged INTEGER DEFAULT 0,
    p_calls_answered INTEGER DEFAULT 0,
    p_calls_missed INTEGER DEFAULT 0,
    p_calls_followed_up INTEGER DEFAULT 0,
    p_visitors_checked_in INTEGER DEFAULT 0,
    p_visitors_checked_out INTEGER DEFAULT 0,
    p_walk_in_inquiries INTEGER DEFAULT 0,
    p_new_leads_created INTEGER DEFAULT 0,
    p_lead_follow_ups_completed INTEGER DEFAULT 0,
    p_tours_scheduled INTEGER DEFAULT 0,
    p_messages_sent INTEGER DEFAULT 0,
    p_complaints_logged INTEGER DEFAULT 0,
    p_tasks_completed INTEGER DEFAULT 0,
    p_notes TEXT DEFAULT NULL,
    p_performance_rating VARCHAR(20) DEFAULT NULL,
    p_shift_start TIME DEFAULT NULL,
    p_shift_end TIME DEFAULT NULL,
    p_school_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    -- Try to update existing log
    UPDATE frontdesk_daily_logs
    SET 
        calls_logged = calls_logged + p_calls_logged,
        calls_answered = calls_answered + p_calls_answered,
        calls_missed = calls_missed + p_calls_missed,
        calls_followed_up = calls_followed_up + p_calls_followed_up,
        visitors_checked_in = visitors_checked_in + p_visitors_checked_in,
        visitors_checked_out = visitors_checked_out + p_visitors_checked_out,
        walk_in_inquiries = walk_in_inquiries + p_walk_in_inquiries,
        new_leads_created = new_leads_created + p_new_leads_created,
        lead_follow_ups_completed = lead_follow_ups_completed + p_lead_follow_ups_completed,
        tours_scheduled = tours_scheduled + p_tours_scheduled,
        messages_sent = messages_sent + p_messages_sent,
        complaints_logged = complaints_logged + p_complaints_logged,
        tasks_completed = tasks_completed + p_tasks_completed,
        notes = COALESCE(p_notes, notes),
        performance_rating = COALESCE(p_performance_rating, performance_rating),
        shift_start = COALESCE(p_shift_start, shift_start),
        shift_end = COALESCE(p_shift_end, shift_end),
        updated_at = NOW()
    WHERE log_date = p_log_date AND staff_id = p_staff_id
    RETURNING id INTO v_log_id;
    
    -- If no update, insert new log
    IF v_log_id IS NULL THEN
        INSERT INTO frontdesk_daily_logs (
            log_date, staff_id, staff_name, staff_role,
            calls_logged, calls_answered, calls_missed, calls_followed_up,
            visitors_checked_in, visitors_checked_out, walk_in_inquiries,
            new_leads_created, lead_follow_ups_completed, tours_scheduled,
            messages_sent, complaints_logged, tasks_completed,
            notes, performance_rating, shift_start, shift_end, school_id
        )
        VALUES (
            p_log_date, p_staff_id, p_staff_name, p_staff_role,
            p_calls_logged, p_calls_answered, p_calls_missed, p_calls_followed_up,
            p_visitors_checked_in, p_visitors_checked_out, p_walk_in_inquiries,
            p_new_leads_created, p_lead_follow_ups_completed, p_tours_scheduled,
            p_messages_sent, p_complaints_logged, p_tasks_completed,
            p_notes, p_performance_rating, p_shift_start, p_shift_end, p_school_id
        )
        RETURNING id INTO v_log_id;
    END IF;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Function to log specific activity
CREATE OR REPLACE FUNCTION log_frontdesk_activity(
    p_daily_log_id UUID,
    p_activity_type VARCHAR(100),
    p_activity_description TEXT,
    p_related_entity_type VARCHAR(50) DEFAULT NULL,
    p_related_entity_id VARCHAR(255) DEFAULT NULL,
    p_notes TEXT DEFAULT NULL,
    p_school_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
BEGIN
    INSERT INTO frontdesk_activities (
        daily_log_id, activity_type, activity_description,
        related_entity_type, related_entity_id, notes, school_id
    )
    VALUES (
        p_daily_log_id, p_activity_type, p_activity_description,
        p_related_entity_type, p_related_entity_id, p_notes, p_school_id
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;

-- View for daily performance summary
CREATE OR REPLACE VIEW frontdesk_daily_summary AS
SELECT 
    log_date,
    staff_name,
    staff_role,
    calls_logged,
    calls_answered,
    calls_followed_up,
    visitors_checked_in,
    new_leads_created,
    lead_follow_ups_completed,
    tours_scheduled,
    messages_sent,
    tasks_completed,
    performance_rating
FROM frontdesk_daily_logs
ORDER BY log_date DESC, staff_name;

-- View for staff performance over time
CREATE OR REPLACE VIEW frontdesk_staff_performance AS
SELECT 
    staff_id,
    staff_name,
    staff_role,
    AVG(calls_followed_up::FLOAT / NULLIF(calls_logged, 0)) as follow_up_rate,
    AVG(new_leads_created) as avg_leads_per_day,
    AVG(tours_scheduled) as avg_tours_per_day,
    AVG(tasks_completed) as avg_tasks_per_day,
    COUNT(*) as days_logged
FROM frontdesk_daily_logs
WHERE log_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY staff_id, staff_name, staff_role
ORDER BY avg_leads_per_day DESC;
