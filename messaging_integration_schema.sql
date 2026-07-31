-- Messaging Integration Schema
-- Handles WhatsApp/SMS API integration and message sending

DROP TABLE IF EXISTS message_templates CASCADE;
DROP TABLE IF EXISTS sent_messages CASCADE;
DROP TABLE IF EXISTS message_queue CASCADE;

CREATE TABLE message_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(255) NOT NULL,
    template_code VARCHAR(100) UNIQUE NOT NULL,
    channel VARCHAR(50) NOT NULL, -- 'whatsapp', 'sms', 'email'
    use_case VARCHAR(100) NOT NULL, -- 'fee_reminder', 'welcome', 'assessment_notice', etc.
    subject VARCHAR(255),
    body TEXT NOT NULL,
    variables TEXT[], -- array of variable names like ['parent_name', 'student_name', 'amount']
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    school_id UUID
);

CREATE TABLE IF NOT EXISTS sent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_type VARCHAR(50) NOT NULL, -- 'parent', 'staff', 'student'
    recipient_id VARCHAR(255),
    recipient_contact VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL, -- 'whatsapp', 'sms', 'email'
    message_type VARCHAR(100) NOT NULL, -- 'fee_reminder', 'welcome', 'broadcast', etc.
    subject VARCHAR(255),
    message_content TEXT NOT NULL,
    template_id UUID,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
    external_message_id VARCHAR(255), -- ID from WhatsApp/SMS provider
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    cost DECIMAL(10,2),
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Message queue for batch processing
CREATE TABLE IF NOT EXISTS message_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_type VARCHAR(50) NOT NULL,
    recipient_id VARCHAR(255),
    recipient_contact VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    message_type VARCHAR(100) NOT NULL,
    subject VARCHAR(255),
    message_content TEXT NOT NULL,
    template_id UUID,
    priority INTEGER DEFAULT 5, -- 1-10, lower is higher priority
    scheduled_for TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'processing', 'sent', 'failed'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    school_id UUID
);

-- Indexes for messaging
CREATE INDEX IF NOT EXISTS idx_sent_messages_status ON sent_messages(status);
CREATE INDEX IF NOT EXISTS idx_sent_messages_recipient ON sent_messages(recipient_contact);
CREATE INDEX IF NOT EXISTS idx_sent_messages_created_at ON sent_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_message_queue_status ON message_queue(status);
CREATE INDEX IF NOT EXISTS idx_message_queue_scheduled ON message_queue(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_message_queue_priority ON message_queue(priority, scheduled_for);

-- Function to send message (will be called by backend service)
CREATE OR REPLACE FUNCTION queue_message(
    p_recipient_type VARCHAR(50),
    p_recipient_id VARCHAR(255),
    p_recipient_contact VARCHAR(255),
    p_channel VARCHAR(50),
    p_message_type VARCHAR(100),
    p_subject VARCHAR(255),
    p_message_content TEXT,
    p_template_id UUID,
    p_priority INTEGER DEFAULT 5,
    p_scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    p_school_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
BEGIN
    INSERT INTO message_queue (
        recipient_type, recipient_id, recipient_contact, channel,
        message_type, subject, message_content, template_id,
        priority, scheduled_for, school_id
    )
    VALUES (
        p_recipient_type, p_recipient_id, p_recipient_contact, p_channel,
        p_message_type, p_subject, p_message_content, p_template_id,
        p_priority, p_scheduled_for, p_school_id
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;

-- Function to record sent message
CREATE OR REPLACE FUNCTION record_sent_message(
    p_queue_id UUID,
    p_external_message_id VARCHAR(255),
    p_status VARCHAR(50),
    p_error_message TEXT DEFAULT NULL,
    p_cost DECIMAL DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_message_id UUID;
    v_queue_record RECORD;
BEGIN
    -- Get queue record
    SELECT * INTO v_queue_record
    FROM message_queue
    WHERE id = p_queue_id;
    
    -- Insert into sent_messages
    INSERT INTO sent_messages (
        recipient_type, recipient_id, recipient_contact, channel,
        message_type, subject, message_content, template_id,
        status, external_message_id, error_message, cost,
        sent_at, school_id
    )
    VALUES (
        v_queue_record.recipient_type, v_queue_record.recipient_id, 
        v_queue_record.recipient_contact, v_queue_record.channel,
        v_queue_record.message_type, v_queue_record.subject, 
        v_queue_record.message_content, v_queue_record.template_id,
        p_status, p_external_message_id, p_error_message, p_cost,
        NOW(), v_queue_record.school_id
    )
    RETURNING id INTO v_message_id;
    
    -- Update queue status
    UPDATE message_queue
    SET status = p_status,
        processed_at = NOW(),
        attempts = attempts + 1,
        error_message = p_error_message
    WHERE id = p_queue_id;
    
    RETURN v_message_id;
END;
$$ LANGUAGE plpgsql;

-- View for pending messages
CREATE OR REPLACE VIEW pending_messages AS
SELECT 
    id,
    recipient_type,
    recipient_contact,
    channel,
    message_type,
    subject,
    message_content,
    priority,
    scheduled_for
FROM message_queue
WHERE status = 'queued'
AND (scheduled_for IS NULL OR scheduled_for <= NOW())
ORDER BY priority ASC, scheduled_for ASC;

-- View for message statistics
CREATE OR REPLACE VIEW message_statistics AS
SELECT 
    channel,
    message_type,
    COUNT(*) as total_sent,
    COUNT(*) FILTER (WHERE status = 'delivered') as delivered,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    ROUND(COUNT(*) FILTER (WHERE status = 'delivered')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as delivery_rate,
    SUM(cost) as total_cost
FROM sent_messages
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY channel, message_type;
