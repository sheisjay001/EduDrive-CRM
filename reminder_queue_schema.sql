-- Reminder Queue Management Schema
-- Advanced queue management for automated reminder processing

-- Drop tables if they exist
DROP TABLE IF EXISTS reminder_queue CASCADE;
DROP TABLE IF EXISTS reminder_templates CASCADE;
DROP TABLE IF EXISTS reminder_processing_logs CASCADE;

-- Reminder templates table
CREATE TABLE IF NOT EXISTS reminder_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(255) NOT NULL,
    template_code VARCHAR(100) UNIQUE NOT NULL,
    reminder_type VARCHAR(50) NOT NULL, -- 'payment', 'followup', 'admission', 'general'
    channel VARCHAR(20) NOT NULL, -- 'email', 'sms', 'whatsapp'
    subject VARCHAR(255),
    message_body TEXT NOT NULL,
    variables JSONB, -- Available variables for template
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 5, -- 1-10, higher = more important
    send_window_start TIME DEFAULT '08:00:00',
    send_window_end TIME DEFAULT '20:00:00',
    retry_on_failure BOOLEAN DEFAULT true,
    max_retries INTEGER DEFAULT 3,
    retry_interval_hours INTEGER DEFAULT 24,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for reminder templates
CREATE INDEX IF NOT EXISTS idx_reminder_templates_type ON reminder_templates(reminder_type);
CREATE INDEX IF NOT EXISTS idx_reminder_templates_channel ON reminder_templates(channel);
CREATE INDEX IF NOT EXISTS idx_reminder_templates_is_active ON reminder_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_reminder_templates_school_id ON reminder_templates(school_id);

-- Reminder queue table (enhanced from existing reminders table)
CREATE TABLE IF NOT EXISTS reminder_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES reminder_templates(id) ON DELETE SET NULL,
    reminder_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL, -- 'invoice', 'lead', 'student', 'parent'
    entity_id UUID NOT NULL,
    recipient_type VARCHAR(20) NOT NULL, -- 'parent', 'student', 'staff'
    recipient_id UUID,
    recipient_contact VARCHAR(255) NOT NULL,
    channel VARCHAR(20) NOT NULL, -- 'email', 'sms', 'whatsapp'
    subject VARCHAR(255),
    message_content TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    send_window_start TIME,
    send_window_end TIME,
    status VARCHAR(20) DEFAULT 'queued', -- 'queued', 'pending', 'processing', 'sent', 'delivered', 'failed', 'cancelled'
    processing_started_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    external_message_id VARCHAR(255),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID REFERENCES users(id),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for reminder queue
CREATE INDEX IF NOT EXISTS idx_reminder_queue_status ON reminder_queue(status);
CREATE INDEX IF NOT EXISTS idx_reminder_queue_scheduled_for ON reminder_queue(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_reminder_queue_priority ON reminder_queue(priority DESC);
CREATE INDEX IF NOT EXISTS idx_reminder_queue_entity ON reminder_queue(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_reminder_queue_school_id ON reminder_queue(school_id);
CREATE INDEX IF NOT EXISTS idx_reminder_queue_next_retry ON reminder_queue(next_retry_at) WHERE status = 'failed';

-- Reminder processing logs
CREATE TABLE IF NOT EXISTS reminder_processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_by UUID REFERENCES users(id),
    processed_by_name VARCHAR(255),
    total_queued INTEGER DEFAULT 0,
    total_processed INTEGER DEFAULT 0,
    total_sent INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    total_skipped INTEGER DEFAULT 0,
    processing_duration_seconds INTEGER,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE
);

-- Indexes for processing logs
CREATE INDEX IF NOT EXISTS idx_reminder_processing_logs_batch_id ON reminder_processing_logs(batch_id);
CREATE INDEX IF NOT EXISTS idx_reminder_processing_logs_processed_at ON reminder_processing_logs(processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_reminder_processing_logs_school_id ON reminder_processing_logs(school_id);

-- Function to add reminder to queue
CREATE OR REPLACE FUNCTION add_reminder_to_queue(
    p_template_id UUID,
    p_reminder_type VARCHAR(50),
    p_entity_type VARCHAR(100),
    p_entity_id UUID,
    p_recipient_type VARCHAR(20),
    p_recipient_id UUID,
    p_recipient_contact VARCHAR(255),
    p_channel VARCHAR(20),
    p_subject VARCHAR(255),
    p_message_content TEXT,
    p_priority INTEGER,
    p_scheduled_for TIMESTAMP WITH TIME ZONE,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_template RECORD;
    v_queue_id UUID;
BEGIN
    -- Get template details if provided
    IF p_template_id IS NOT NULL THEN
        SELECT * INTO v_template FROM reminder_templates WHERE id = p_template_id;
    END IF;
    
    -- Use template settings if available
    IF v_template IS NOT NULL THEN
        p_priority := COALESCE(p_priority, v_template.priority);
        p_channel := COALESCE(p_channel, v_template.channel);
    END IF;
    
    -- Add to queue
    INSERT INTO reminder_queue (
        template_id, reminder_type, entity_type, entity_id,
        recipient_type, recipient_id, recipient_contact, channel,
        subject, message_content, priority, scheduled_for, school_id,
        send_window_start, send_window_end, max_retries
    ) VALUES (
        p_template_id, p_reminder_type, p_entity_type, p_entity_id,
        p_recipient_type, p_recipient_id, p_recipient_contact, p_channel,
        p_subject, p_message_content, p_priority, p_scheduled_for, p_school_id,
        COALESCE(v_template.send_window_start, '08:00:00'::TIME),
        COALESCE(v_template.send_window_end, '20:00:00'::TIME),
        COALESCE(v_template.max_retries, 3)
    ) RETURNING id INTO v_queue_id;
    
    RETURN v_queue_id;
END;
$$ LANGUAGE plpgsql;

-- Function to process reminder queue
CREATE OR REPLACE FUNCTION process_reminder_queue(p_school_id UUID, p_batch_size INTEGER DEFAULT 100)
RETURNS UUID AS $$
DECLARE
    v_batch_id UUID;
    v_processing_start TIMESTAMP WITH TIME ZONE;
    v_total_queued INTEGER;
    v_total_processed INTEGER := 0;
    v_total_sent INTEGER := 0;
    v_total_failed INTEGER := 0;
    v_total_skipped INTEGER := 0;
    v_reminder RECORD;
BEGIN
    v_batch_id := gen_random_uuid();
    v_processing_start := NOW();
    
    -- Get reminders ready for processing
    FOR v_reminder IN 
        SELECT * FROM reminder_queue
        WHERE status IN ('queued', 'pending')
        AND scheduled_for <= NOW()
        AND school_id = p_school_id
        ORDER BY priority DESC, scheduled_for ASC
        LIMIT p_batch_size
    LOOP
        BEGIN
            -- Check if within send window
            IF EXTRACT(HOUR FROM NOW()) < EXTRACT(HOUR FROM v_reminder.send_window_start) 
               OR EXTRACT(HOUR FROM NOW()) > EXTRACT(HOUR FROM v_reminder.send_window_end) THEN
                -- Skip for now, will be processed later
                UPDATE reminder_queue SET status = 'queued' WHERE id = v_reminder.id;
                v_total_skipped := v_total_skipped + 1;
                CONTINUE;
            END IF;
            
            -- Mark as processing
            UPDATE reminder_queue
            SET 
                status = 'processing',
                processing_started_at = NOW()
            WHERE id = v_reminder.id;
            
            -- Here you would integrate with actual messaging service
            -- For now, simulating send
            UPDATE reminder_queue
            SET 
                status = 'sent',
                sent_at = NOW(),
                external_message_id := 'MSG-' || gen_random_uuid()
            WHERE id = v_reminder.id;
            
            v_total_sent := v_total_sent + 1;
            v_total_processed := v_total_processed + 1;
            
        EXCEPTION WHEN OTHERS THEN
            -- Mark as failed
            UPDATE reminder_queue
            SET 
                status = 'failed',
                error_message = SQLERRM,
                retry_count = retry_count + 1,
                next_retry_at = NOW() + INTERVAL '24 hours'
            WHERE id = v_reminder.id;
            
            v_total_failed := v_total_failed + 1;
            v_total_processed := v_total_processed + 1;
        END;
    END LOOP;
    
    -- Get total queued count
    SELECT COUNT(*) INTO v_total_queued
    FROM reminder_queue
    WHERE status IN ('queued', 'pending')
    AND school_id = p_school_id;
    
    -- Log processing batch
    INSERT INTO reminder_processing_logs (
        batch_id, processed_by, processed_by_name,
        total_queued, total_processed, total_sent, total_failed, total_skipped,
        processing_duration_seconds, school_id
    ) VALUES (
        v_batch_id, NULL, 'System',
        v_total_queued, v_total_processed, v_total_sent, v_total_failed, v_total_skipped,
        EXTRACT(EPOCH FROM (NOW() - v_processing_start))::INTEGER, p_school_id
    );
    
    RETURN v_batch_id;
END;
$$ LANGUAGE plpgsql;

-- Function to retry failed reminders
CREATE OR REPLACE FUNCTION retry_failed_reminders(p_school_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_retry_count INTEGER := 0;
BEGIN
    UPDATE reminder_queue
    SET 
        status = 'queued',
        retry_count = 0,
        next_retry_at = NULL
    WHERE status = 'failed'
    AND retry_count < max_retries
    AND (next_retry_at IS NULL OR next_retry_at <= NOW())
    AND school_id = p_school_id;
    
    GET DIAGNOSTICS v_retry_count = ROW_COUNT;
    
    RETURN v_retry_count;
END;
$$ LANGUAGE plpgsql;

-- Views for queue management
CREATE OR REPLACE VIEW reminder_queue_summary AS
SELECT 
    status,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE channel = 'email') as email_count,
    COUNT(*) FILTER (WHERE channel = 'sms') as sms_count,
    COUNT(*) FILTER (WHERE channel = 'whatsapp') as whatsapp_count,
    COUNT(*) FILTER (WHERE priority >= 8) as high_priority_count,
    MIN(scheduled_for) as earliest_scheduled,
    MAX(scheduled_for) as latest_scheduled
FROM reminder_queue
GROUP BY status;

CREATE OR REPLACE VIEW reminder_queue_backlog AS
SELECT 
    reminder_type,
    entity_type,
    COUNT(*) as pending_count,
    COUNT(*) FILTER (WHERE scheduled_for < NOW()) as overdue_count,
    AVG(EXTRACT(EPOCH FROM (NOW() - scheduled_for)) / 3600) as avg_hours_overdue
FROM reminder_queue
WHERE status IN ('queued', 'pending')
GROUP BY reminder_type, entity_type
ORDER BY overdue_count DESC;
