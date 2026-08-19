-- Help Desk Enhancements Schema
-- Ticket routing, resolution analytics, and workflow management

-- Drop tables if they exist
DROP TABLE IF EXISTS ticket_workflow CASCADE;
DROP TABLE IF EXISTS ticket_resolution_analytics CASCADE;
DROP TABLE IF EXISTS ticket_routing CASCADE;

-- Ticket routing configuration
CREATE TABLE IF NOT EXISTS ticket_routing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    priority VARCHAR(20), -- 'low', 'medium', 'high', 'urgent'
    assigned_role VARCHAR(50), -- 'admin', 'staff', 'teacher', etc.
    assigned_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    auto_assign BOOLEAN DEFAULT false,
    assignment_criteria JSONB, -- Rules for auto-assignment
    is_active BOOLEAN DEFAULT true,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ticket routing
CREATE INDEX IF NOT EXISTS idx_ticket_routing_category ON ticket_routing(category);
CREATE INDEX IF NOT EXISTS idx_ticket_routing_priority ON ticket_routing(priority);
CREATE INDEX IF NOT EXISTS idx_ticket_routing_school_id ON ticket_routing(school_id);

-- Ticket workflow states
CREATE TABLE IF NOT EXISTS ticket_workflow (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    transitioned_by UUID REFERENCES auth.users(id),
    transitioned_by_name VARCHAR(255),
    transitioned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    duration_hours DECIMAL(10,2),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE
);

-- Indexes for ticket workflow
CREATE INDEX IF NOT EXISTS idx_ticket_workflow_ticket_id ON ticket_workflow(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_workflow_to_status ON ticket_workflow(to_status);
CREATE INDEX IF NOT EXISTS idx_ticket_workflow_school_id ON ticket_workflow(school_id);

-- Ticket resolution analytics
CREATE TABLE IF NOT EXISTS ticket_resolution_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    category VARCHAR(100),
    priority VARCHAR(20),
    assigned_to UUID REFERENCES auth.users(id),
    assigned_to_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE,
    first_response_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    time_to_first_response_hours DECIMAL(10,2),
    time_to_resolution_hours DECIMAL(10,2),
    time_to_closure_hours DECIMAL(10,2),
    sla_breached BOOLEAN DEFAULT false,
    sla_breach_reason TEXT,
    satisfaction_score INTEGER, -- 1-5 rating
    resolution_quality VARCHAR(20), -- 'excellent', 'good', 'fair', 'poor'
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_completed BOOLEAN DEFAULT false,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE
);

-- Indexes for resolution analytics
CREATE INDEX IF NOT EXISTS idx_resolution_analytics_ticket_id ON ticket_resolution_analytics(ticket_id);
CREATE INDEX IF NOT EXISTS idx_resolution_analytics_category ON ticket_resolution_analytics(category);
CREATE INDEX IF NOT EXISTS idx_resolution_analytics_assigned_to ON ticket_resolution_analytics(assigned_to);
CREATE INDEX IF NOT EXISTS idx_resolution_analytics_sla_breached ON ticket_resolution_analytics(sla_breached);
CREATE INDEX IF NOT EXISTS idx_resolution_analytics_school_id ON ticket_resolution_analytics(school_id);

-- Add workflow tracking to tickets table
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS workflow_stage VARCHAR(50) DEFAULT 'new';
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS auto_assigned BOOLEAN DEFAULT false;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS routing_rule_id UUID;

-- Function to auto-assign ticket based on routing rules
CREATE OR REPLACE FUNCTION auto_assign_ticket(p_ticket_id UUID, p_school_id UUID)
RETURNS UUID AS $$
DECLARE
    v_assigned_user_id UUID;
    v_assigned_role VARCHAR(50);
    v_ticket RECORD;
BEGIN
    -- Get ticket details
    SELECT * INTO v_ticket FROM tickets WHERE id = p_ticket_id;
    
    -- Find matching routing rule
    SELECT assigned_user_id, assigned_role
    INTO v_assigned_user_id, v_assigned_role
    FROM ticket_routing
    WHERE is_active = true
    AND school_id = p_school_id
    AND (category IS NULL OR category = v_ticket.category)
    AND (priority IS NULL OR priority = v_ticket.priority)
    ORDER BY priority DESC, created_at ASC
    LIMIT 1;
    
    -- If rule found and auto_assign is true, assign ticket
    IF v_assigned_user_id IS NOT NULL OR v_assigned_role IS NOT NULL THEN
        UPDATE tickets
        SET 
            assigned_to = v_assigned_user_id,
            assigned_role = v_assigned_role,
            auto_assigned = true,
            routing_rule_id = (
                SELECT id FROM ticket_routing
                WHERE is_active = true
                AND school_id = p_school_id
                AND (category IS NULL OR category = v_ticket.category)
                AND (priority IS NULL OR priority = v_ticket.priority)
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            )
        WHERE id = p_ticket_id;
        
        RETURN COALESCE(v_assigned_user_id, v_assigned_role::UUID);
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to record ticket workflow transition
CREATE OR REPLACE FUNCTION record_ticket_transition(
    p_ticket_id UUID,
    p_to_status VARCHAR(50),
    p_transitioned_by UUID,
    p_transitioned_by_name VARCHAR(255),
    p_notes TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_workflow_id UUID;
    v_current_status VARCHAR(50);
    v_created_at TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get current status and creation time
    SELECT status, created_at INTO v_current_status, v_created_at
    FROM tickets WHERE id = p_ticket_id;
    
    -- Calculate duration in current status
    INSERT INTO ticket_workflow (
        ticket_id, from_status, to_status, transitioned_by, transitioned_by_name,
        notes, school_id, duration_hours
    ) VALUES (
        p_ticket_id, v_current_status, p_to_status, p_transitioned_by, p_transitioned_by_name,
        p_notes, p_school_id,
        EXTRACT(EPOCH FROM (NOW() - v_created_at)) / 3600
    ) RETURNING id INTO v_workflow_id;
    
    -- Update ticket status
    UPDATE tickets
    SET status = p_to_status, workflow_stage = p_to_status
    WHERE id = p_ticket_id;
    
    RETURN v_workflow_id;
END;
$$ LANGUAGE plpgsql;

-- Function to track resolution analytics
CREATE OR REPLACE FUNCTION track_ticket_resolution(p_ticket_id UUID)
RETURNS VOID AS $$
DECLARE
    v_ticket RECORD;
    v_first_response TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get ticket details
    SELECT * INTO v_ticket FROM tickets WHERE id = p_ticket_id;
    
    -- Get first response time
    SELECT MIN(created_at) INTO v_first_response
    FROM ticket_comments
    WHERE ticket_id = p_ticket_id;
    
    -- Insert or update resolution analytics
    INSERT INTO ticket_resolution_analytics (
        ticket_id, category, priority, assigned_to, assigned_to_name,
        created_at, first_response_at, resolved_at, closed_at,
        time_to_first_response_hours, time_to_resolution_hours, time_to_closure_hours,
        sla_breached, satisfaction_score, school_id
    ) VALUES (
        p_ticket_id, v_ticket.category, v_ticket.priority, v_ticket.assigned_to, v_ticket.assigned_to_name,
        v_ticket.created_at, v_first_response,
        CASE WHEN v_ticket.status = 'resolved' THEN NOW() END,
        CASE WHEN v_ticket.status = 'closed' THEN NOW() END,
        CASE WHEN v_first_response IS NOT NULL 
             THEN EXTRACT(EPOCH FROM (v_first_response - v_ticket.created_at)) / 3600 END,
        CASE WHEN v_ticket.status = 'resolved' 
             THEN EXTRACT(EPOCH FROM (NOW() - v_ticket.created_at)) / 3600 END,
        CASE WHEN v_ticket.status = 'closed' 
             THEN EXTRACT(EPOCH FROM (NOW() - v_ticket.created_at)) / 3600 END,
        v_ticket.sla_breached, v_ticket.satisfaction_score, v_ticket.school_id
    )
    ON CONFLICT (ticket_id) DO UPDATE SET
        resolved_at = EXCLUDED.resolved_at,
        closed_at = EXCLUDED.closed_at,
        time_to_resolution_hours = EXCLUDED.time_to_resolution_hours,
        time_to_closure_hours = EXCLUDED.time_to_closure_hours,
        sla_breached = EXCLUDED.sla_breached,
        satisfaction_score = EXCLUDED.satisfaction_score;
END;
$$ LANGUAGE plpgsql;

-- Views for analytics
CREATE OR REPLACE VIEW ticket_resolution_summary AS
SELECT 
    assigned_to_name,
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
    COUNT(*) FILTER (WHERE status = 'closed') as closed,
    AVG(time_to_first_response_hours) as avg_first_response,
    AVG(time_to_resolution_hours) as avg_resolution_time,
    AVG(time_to_closure_hours) as avg_closure_time,
    COUNT(*) FILTER (WHERE sla_breached = true) as sla_breaches,
    ROUND(AVG(satisfaction_score), 2) as avg_satisfaction,
    ROUND(COUNT(*) FILTER (WHERE sla_breached = true)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as sla_breach_rate
FROM ticket_resolution_analytics
GROUP BY assigned_to_name;

CREATE OR REPLACE VIEW ticket_category_performance AS
SELECT 
    category,
    COUNT(*) as total_tickets,
    AVG(time_to_resolution_hours) as avg_resolution_time,
    COUNT(*) FILTER (WHERE sla_breached = true) as sla_breaches,
    ROUND(AVG(satisfaction_score), 2) as avg_satisfaction
FROM ticket_resolution_analytics
GROUP BY category
ORDER BY avg_resolution_time ASC;
