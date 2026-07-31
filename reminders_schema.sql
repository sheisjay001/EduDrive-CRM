-- Reminders and Notifications Schema
-- Handles automated follow-up reminders for leads and payment reminders

DROP TABLE IF EXISTS reminders CASCADE;
DROP TABLE IF EXISTS lead_followup_rules CASCADE;
DROP TABLE IF EXISTS payment_reminder_rules CASCADE;

CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_type VARCHAR(50) NOT NULL, -- 'lead_followup', 'payment_reminder', 'tour_reminder', 'assessment_reminder'
    entity_type VARCHAR(50) NOT NULL, -- 'lead', 'invoice', 'student'
    entity_id VARCHAR(255) NOT NULL,
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'failed', 'cancelled'
    recipient_type VARCHAR(50) NOT NULL, -- 'parent', 'staff', 'student'
    recipient_contact VARCHAR(255) NOT NULL, -- email or phone
    channel VARCHAR(50) NOT NULL, -- 'email', 'sms', 'whatsapp'
    subject VARCHAR(255),
    message_content TEXT NOT NULL,
    template_id VARCHAR(255),
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID,
    created_by UUID
);

-- Indexes for reminder queries
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);
CREATE INDEX IF NOT EXISTS idx_reminders_scheduled_for ON reminders(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_reminders_entity ON reminders(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_reminders_school_id ON reminders(school_id);

-- Lead follow-up rules
CREATE TABLE IF NOT EXISTS lead_followup_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_stage VARCHAR(50) NOT NULL,
    hours_after_stage_change INTEGER NOT NULL,
    reminder_template_id VARCHAR(255),
    channel VARCHAR(50) DEFAULT 'whatsapp',
    is_active BOOLEAN DEFAULT true,
    school_id UUID
);

-- Payment reminder rules
CREATE TABLE IF NOT EXISTS payment_reminder_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    days_before_due INTEGER NOT NULL,
    days_after_due INTEGER,
    reminder_template_id VARCHAR(255),
    channel VARCHAR(50) DEFAULT 'whatsapp',
    is_active BOOLEAN DEFAULT true,
    school_id UUID
);

-- Function to create lead follow-up reminder
CREATE OR REPLACE FUNCTION create_lead_followup_reminder(
    p_lead_id VARCHAR(255),
    p_lead_stage VARCHAR(50),
    p_parent_contact VARCHAR(255),
    p_parent_name VARCHAR(255),
    p_child_name VARCHAR(255),
    p_school_id UUID DEFAULT NULL,
    p_created_by UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_rule_id UUID;
    v_scheduled_for TIMESTAMP WITH TIME ZONE;
    v_message_content TEXT;
BEGIN
    -- Get the follow-up rule for this stage
    SELECT id INTO v_rule_id
    FROM lead_followup_rules
    WHERE lead_stage = p_lead_stage AND is_active = true
    LIMIT 1;
    
    IF v_rule_id IS NULL THEN
        -- Default 48-hour follow-up
        v_scheduled_for := NOW() + INTERVAL '48 hours';
    ELSE
        SELECT hours_after_stage_change INTO v_scheduled_for
        FROM lead_followup_rules
        WHERE id = v_rule_id;
        v_scheduled_for := NOW() + (v_scheduled_for || ' hours')::INTERVAL;
    END IF;
    
    -- Create message content
    v_message_content := 'Dear ' || p_parent_name || ', this is a friendly follow-up regarding your inquiry for ' || p_child_name || '. We would love to discuss next steps. Please call us at your convenience.';
    
    -- Insert reminder
    INSERT INTO reminders (
        reminder_type, entity_type, entity_id, scheduled_for, status,
        recipient_type, recipient_contact, channel, subject, message_content,
        school_id, created_by
    )
    VALUES (
        'lead_followup', 'lead', p_lead_id, v_scheduled_for, 'pending',
        'parent', p_parent_contact, 'whatsapp', 
        'Follow-up on your inquiry', v_message_content,
        p_school_id, p_created_by
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;

-- Function to create payment reminder
CREATE OR REPLACE FUNCTION create_payment_reminder(
    p_invoice_id VARCHAR(255),
    p_parent_contact VARCHAR(255),
    p_parent_name VARCHAR(255),
    p_student_name VARCHAR(255),
    p_amount VARCHAR(50),
    p_due_date DATE,
    p_days_offset INTEGER,
    p_school_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_scheduled_for TIMESTAMP WITH TIME ZONE;
    v_message_content TEXT;
BEGIN
    v_scheduled_for := p_due_date::TIMESTAMP WITH TIME ZONE - (p_days_offset || ' days')::INTERVAL;
    
    v_message_content := 'Dear ' || p_parent_name || ', a quick reminder that ' || p_student_name || '''s balance of ₦' || p_amount || ' is due on ' || p_due_date || '. Click here to pay online: [Payment Link]';
    
    INSERT INTO reminders (
        reminder_type, entity_type, entity_id, scheduled_for, status,
        recipient_type, recipient_contact, channel, subject, message_content,
        school_id
    )
    VALUES (
        'payment_reminder', 'invoice', p_invoice_id, v_scheduled_for, 'pending',
        'parent', p_parent_contact, 'whatsapp',
        'Fee Payment Reminder', v_message_content,
        p_school_id
    )
    RETURNING id;
END;
$$ LANGUAGE plpgsql;

-- View for pending reminders
CREATE OR REPLACE VIEW pending_reminders AS
SELECT 
    id,
    reminder_type,
    entity_type,
    entity_id,
    scheduled_for,
    recipient_contact,
    channel,
    subject,
    message_content
FROM reminders
WHERE status = 'pending' AND scheduled_for <= NOW()
ORDER BY scheduled_for ASC;
