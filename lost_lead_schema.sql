-- Lost Lead Reason Tracking Schema
-- Track reasons for lost leads to improve conversion strategies

-- Drop table if it exists
DROP TABLE IF EXISTS lost_lead_reasons CASCADE;

-- Lost lead reasons table
CREATE TABLE IF NOT EXISTS lost_lead_reasons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    reason_category VARCHAR(100) NOT NULL, -- 'price', 'location', 'competition', 'timing', 'communication', 'other'
    reason_description VARCHAR(255),
    detailed_reason TEXT,
    lost_to_competitor VARCHAR(255),
    competitor_offer_details TEXT,
    price_sensitivity VARCHAR(50), -- 'high', 'medium', 'low'
    budget_range VARCHAR(100),
    decision_timeline VARCHAR(100),
    feedback_rating INTEGER, -- 1-5 scale for feedback quality
    follow_up_potential BOOLEAN DEFAULT false,
    follow_up_date DATE,
    recorded_by UUID REFERENCES auth.users(id),
    recorded_by_name VARCHAR(255),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for lost lead reasons
CREATE INDEX IF NOT EXISTS idx_lost_lead_reasons_lead_id ON lost_lead_reasons(lead_id);
CREATE INDEX IF NOT EXISTS idx_lost_lead_reasons_category ON lost_lead_reasons(reason_category);
CREATE INDEX IF NOT EXISTS idx_lost_lead_reasons_school_id ON lost_lead_reasons(school_id);
CREATE INDEX IF NOT EXISTS idx_lost_lead_reasons_recorded_at ON lost_lead_reasons(recorded_at DESC);

-- Add lost lead tracking to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS is_lost BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lost_date DATE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lost_reason_id UUID REFERENCES lost_lead_reasons(id);

-- Predefined lost reason categories
CREATE OR REPLACE FUNCTION get_lost_reason_categories()
RETURNS TABLE(category VARCHAR(100), description VARCHAR(255)) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        unnest(ARRAY['price', 'location', 'competition', 'timing', 'communication', 'curriculum', 'facilities', 'reputation', 'other']) as category,
        unnest(ARRAY[
            'Price too high / budget constraints',
            'Location too far / transportation issues',
            'Chose competitor school',
            'Timing not right / deferred enrollment',
            'Poor communication / slow response',
            'Curriculum not suitable',
            'Facilities not adequate',
            'School reputation concerns',
            'Other reasons'
        ]) as description;
END;
$$ LANGUAGE plpgsql;

-- Function to mark lead as lost
CREATE OR REPLACE FUNCTION mark_lead_as_lost(
    p_lead_id UUID,
    p_reason_category VARCHAR(100),
    p_reason_description VARCHAR(255),
    p_detailed_reason TEXT,
    p_lost_to_competitor VARCHAR(255),
    p_competitor_offer_details TEXT,
    p_price_sensitivity VARCHAR(50),
    p_budget_range VARCHAR(100),
    p_decision_timeline VARCHAR(100),
    p_follow_up_potential BOOLEAN,
    p_follow_up_date DATE,
    p_recorded_by UUID,
    p_recorded_by_name VARCHAR(255),
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_reason_id UUID;
BEGIN
    -- Create lost lead reason record
    INSERT INTO lost_lead_reasons (
        lead_id, reason_category, reason_description, detailed_reason,
        lost_to_competitor, competitor_offer_details, price_sensitivity,
        budget_range, decision_timeline, follow_up_potential, follow_up_date,
        recorded_by, recorded_by_name, school_id
    ) VALUES (
        p_lead_id, p_reason_category, p_reason_description, p_detailed_reason,
        p_lost_to_competitor, p_competitor_offer_details, p_price_sensitivity,
        p_budget_range, p_decision_timeline, p_follow_up_potential, p_follow_up_date,
        p_recorded_by, p_recorded_by_name, p_school_id
    ) RETURNING id INTO v_reason_id;
    
    -- Update lead status
    UPDATE leads
    SET 
        is_lost = true,
        lost_date = CURRENT_DATE,
        lost_reason_id = v_reason_id,
        stage = 'lost'
    WHERE id = p_lead_id;
    
    RETURN v_reason_id;
END;
$$ LANGUAGE plpgsql;

-- View for lost lead analytics
CREATE OR REPLACE VIEW lost_lead_analytics AS
SELECT 
    llr.reason_category,
    COUNT(*) as total_lost,
    ROUND(COUNT(*)::DECIMAL / NULLIF((SELECT COUNT(*) FROM leads WHERE is_lost = true), 0) * 100, 2) as percentage,
    COUNT(*) FILTER (WHERE llr.price_sensitivity = 'high') as high_price_sensitivity,
    COUNT(*) FILTER (WHERE llr.follow_up_potential = true) as follow_up_potential,
    AVG(llr.feedback_rating) as avg_feedback_rating
FROM lost_lead_reasons llr
JOIN leads l ON llr.lead_id = l.id
WHERE l.is_lost = true
GROUP BY llr.reason_category
ORDER BY total_lost DESC;

-- View for competitor analysis
CREATE OR REPLACE VIEW competitor_analysis AS
SELECT 
    lost_to_competitor as competitor,
    COUNT(*) as lost_leads,
    AVG(price_sensitivity) as avg_price_sensitivity,
    COUNT(*) FILTER (WHERE reason_category = 'price') as price_related,
    COUNT(*) FILTER (WHERE reason_category = 'competition') as competition_related
FROM lost_lead_reasons
WHERE lost_to_competitor IS NOT NULL
GROUP BY lost_to_competitor
ORDER BY lost_leads DESC;

-- View for lost lead trends
CREATE OR REPLACE VIEW lost_lead_trends AS
SELECT 
    DATE_TRUNC('month', lost_date) as month,
    COUNT(*) as total_lost,
    COUNT(*) FILTER (WHERE reason_category = 'price') as price_related,
    COUNT(*) FILTER (WHERE reason_category = 'competition') as competition_related,
    COUNT(*) FILTER (WHERE reason_category = 'location') as location_related,
    COUNT(*) FILTER (WHERE follow_up_potential = true) as follow_up_potential
FROM leads
WHERE is_lost = true
AND lost_date IS NOT NULL
GROUP BY DATE_TRUNC('month', lost_date)
ORDER BY month DESC;
