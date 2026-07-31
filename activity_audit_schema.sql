-- Activity Audit Trail Schema
-- Tracks all user actions for accountability and performance measurement

-- Drop table if it exists to ensure clean schema
DROP TABLE IF EXISTS activity_logs CASCADE;

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    action_type VARCHAR(100) NOT NULL, -- e.g., 'lead_created', 'lead_stage_changed', 'invoice_updated', 'message_sent'
    entity_type VARCHAR(100) NOT NULL, -- e.g., 'lead', 'invoice', 'student', 'ticket'
    entity_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action_type ON activity_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_activity_logs_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_school_id ON activity_logs(school_id);

-- Function to automatically log activities
CREATE OR REPLACE FUNCTION log_activity(
    p_user_id UUID,
    p_user_name VARCHAR(255),
    p_user_role VARCHAR(50),
    p_action_type VARCHAR(100),
    p_entity_type VARCHAR(100),
    p_entity_id VARCHAR(255),
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_school_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
BEGIN
    INSERT INTO activity_logs (
        user_id, user_name, user_role, action_type, entity_type, entity_id,
        old_values, new_values, description, school_id
    )
    VALUES (
        p_user_id, p_user_name, p_user_role, p_action_type, p_entity_type, p_entity_id,
        p_old_values, p_new_values, p_description, p_school_id
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;

-- View for recent activity by school
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    id,
    user_name,
    user_role,
    action_type,
    entity_type,
    entity_id,
    description,
    created_at
FROM activity_logs
ORDER BY created_at DESC
LIMIT 100;

-- View for activity by user
CREATE OR REPLACE VIEW user_activity AS
SELECT 
    user_id,
    user_name,
    user_role,
    COUNT(*) as total_actions,
    MAX(created_at) as last_activity
FROM activity_logs
GROUP BY user_id, user_name, user_role;
