-- Analytics and Performance Tracking Schema
-- Handles lead conversion rates and response speed measurements

DROP TABLE IF EXISTS lead_conversion_metrics CASCADE;

-- Add conversion tracking to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS conversion_date DATE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS time_to_convert_days INTEGER; -- Days from creation to conversion
ALTER TABLE leads ADD COLUMN IF NOT EXISTS assigned_to UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS assigned_to_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS first_response_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS first_response_hours DECIMAL(5,2); -- Hours from creation to first response
ALTER TABLE leads ADD COLUMN IF NOT EXISTS follow_up_count INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_follow_up_date TIMESTAMP WITH TIME ZONE;

-- Create lead conversion tracking table
CREATE TABLE IF NOT EXISTS lead_conversion_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL,
    stage VARCHAR(50) NOT NULL,
    stage_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    previous_stage VARCHAR(50),
    time_in_previous_stage_hours DECIMAL(5,2),
    changed_by UUID,
    changed_by_name VARCHAR(255),
    school_id UUID
);

-- Indexes for conversion metrics
CREATE INDEX IF NOT EXISTS idx_conversion_metrics_lead_id ON lead_conversion_metrics(lead_id);
CREATE INDEX IF NOT EXISTS idx_conversion_metrics_stage ON lead_conversion_metrics(stage);
CREATE INDEX IF NOT EXISTS idx_conversion_metrics_changed_at ON lead_conversion_metrics(stage_changed_at DESC);

-- Function to track stage changes and calculate conversion metrics
CREATE OR REPLACE FUNCTION track_lead_stage_change(
    p_lead_id UUID,
    p_new_stage VARCHAR(50),
    p_changed_by UUID,
    p_changed_by_name VARCHAR(255),
    p_school_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_previous_stage VARCHAR(50);
    v_stage_changed_at TIMESTAMP WITH TIME ZONE;
    v_time_in_stage DECIMAL(5,2);
    v_conversion_date DATE;
    v_time_to_convert_days INTEGER;
BEGIN
    -- Get current stage and last change date
    SELECT stage, stage_changed_at INTO v_previous_stage, v_stage_changed_at
    FROM leads
    WHERE id = p_lead_id;
    
    -- Calculate time in previous stage
    IF v_stage_changed_at IS NOT NULL THEN
        v_time_in_stage := EXTRACT(EPOCH FROM (NOW() - v_stage_changed_at)) / 3600;
    END IF;
    
    -- Update lead stage
    UPDATE leads
    SET 
        stage = p_new_stage,
        stage_changed_at = NOW(),
        follow_up_count = follow_up_count + 1,
        last_follow_up_date = NOW()
    WHERE id = p_lead_id;
    
    -- Track conversion if moving to enrolled
    IF p_new_stage = 'enrolled' AND v_previous_stage != 'enrolled' THEN
        v_conversion_date := CURRENT_DATE;
        v_time_to_convert_days := (CURRENT_DATE - (SELECT created_at::DATE FROM leads WHERE id = p_lead_id));
        
        UPDATE leads
        SET 
            conversion_date = v_conversion_date,
            time_to_convert_days = v_time_to_convert_days
        WHERE id = p_lead_id;
    END IF;
    
    -- Record stage change
    INSERT INTO lead_conversion_metrics (
        lead_id, stage, previous_stage, stage_changed_at,
        time_in_previous_stage_hours, changed_by, changed_by_name, school_id
    )
    VALUES (
        p_lead_id, p_new_stage, v_previous_stage, NOW(),
        v_time_in_stage, p_changed_by, p_changed_by_name, p_school_id
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;

-- Function to record first response time
CREATE OR REPLACE FUNCTION record_first_response(
    p_lead_id UUID,
    p_responded_by UUID,
    p_responded_by_name VARCHAR(255)
)
RETURNS VOID AS $$
DECLARE
    v_created_at TIMESTAMP WITH TIME ZONE;
    v_response_hours DECIMAL(5,2);
BEGIN
    -- Get lead creation time
    SELECT created_at INTO v_created_at
    FROM leads
    WHERE id = p_lead_id AND first_response_time IS NULL;
    
    IF v_created_at IS NOT NULL THEN
        v_response_hours := EXTRACT(EPOCH FROM (NOW() - v_created_at)) / 3600;
        
        UPDATE leads
        SET 
            first_response_time = NOW(),
            first_response_hours = v_response_hours,
            assigned_to = p_responded_by,
            assigned_to_name = p_responded_by_name
        WHERE id = p_lead_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- View for conversion rate by stage
CREATE OR REPLACE VIEW conversion_rate_by_stage AS
SELECT 
    stage,
    COUNT(*) as total_leads,
    COUNT(*) FILTER (WHERE stage = 'enrolled') as converted_leads,
    ROUND(COUNT(*) FILTER (WHERE stage = 'enrolled')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as conversion_rate,
    AVG(time_to_convert_days) as avg_days_to_convert
FROM leads
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY stage;

-- View for response time metrics
CREATE OR REPLACE VIEW response_time_metrics AS
SELECT 
    assigned_to_name,
    COUNT(*) as leads_handled,
    AVG(first_response_hours) as avg_response_hours,
    COUNT(*) FILTER (WHERE first_response_hours <= 2) as responded_within_2hrs,
    COUNT(*) FILTER (WHERE first_response_hours <= 24) as responded_within_24hrs,
    ROUND(COUNT(*) FILTER (WHERE first_response_hours <= 24)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as within_24hr_rate
FROM leads
WHERE first_response_time IS NOT NULL
AND created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY assigned_to_name
ORDER BY avg_response_hours ASC;

-- View for lead funnel analysis
CREATE OR REPLACE VIEW lead_funnel_analysis AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_leads,
    COUNT(*) FILTER (WHERE stage = 'tour_scheduled') as tours_scheduled,
    COUNT(*) FILTER (WHERE stage = 'form_purchased') as forms_purchased,
    COUNT(*) FILTER (WHERE stage = 'assessment_completed') as assessments_completed,
    COUNT(*) FILTER (WHERE stage = 'admission_offered') as offers_made,
    COUNT(*) FILTER (WHERE stage = 'enrolled') as enrolled
FROM leads
WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- View for staff performance on leads
CREATE OR REPLACE VIEW staff_lead_performance AS
SELECT 
    assigned_to_name,
    COUNT(*) as total_assigned,
    COUNT(*) FILTER (WHERE stage = 'enrolled') as converted,
    ROUND(COUNT(*) FILTER (WHERE stage = 'enrolled')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as conversion_rate,
    AVG(first_response_hours) as avg_response_time,
    AVG(follow_up_count) as avg_follow_ups,
    AVG(time_to_convert_days) as avg_days_to_convert
FROM leads
WHERE assigned_to_name IS NOT NULL
AND created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY assigned_to_name
ORDER BY conversion_rate DESC;
