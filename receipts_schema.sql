-- Receipt Generation and Delivery Schema
-- Handles digital receipt generation, storage, and delivery

-- Drop tables if they exist
DROP TABLE IF EXISTS receipt_delivery CASCADE;
DROP TABLE IF EXISTS receipts CASCADE;

-- Receipts table
CREATE TABLE IF NOT EXISTS receipts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    payment_id UUID REFERENCES payments(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES parents(id) ON DELETE SET NULL,
    receipt_type VARCHAR(20) NOT NULL DEFAULT 'payment', -- 'payment', 'refund', 'adjustment'
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    payment_method VARCHAR(50),
    payment_date TIMESTAMP WITH TIME ZONE,
    receipt_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    issued_by UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'generated', -- 'generated', 'sent', 'delivered', 'failed'
    delivery_method VARCHAR(20), -- 'email', 'whatsapp', 'sms', 'download'
    delivery_attempts INTEGER DEFAULT 0,
    delivery_status VARCHAR(20), -- 'pending', 'sent', 'delivered', 'failed', 'bounced'
    delivery_error TEXT,
    receipt_url TEXT, -- URL to download receipt PDF
    receipt_data JSONB, -- Receipt details for PDF generation
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for receipts
CREATE INDEX IF NOT EXISTS idx_receipts_payment_id ON receipts(payment_id);
CREATE INDEX IF NOT EXISTS idx_receipts_invoice_id ON receipts(invoice_id);
CREATE INDEX IF NOT EXISTS idx_receipts_student_id ON receipts(student_id);
CREATE INDEX IF NOT EXISTS idx_receipts_parent_id ON receipts(parent_id);
CREATE INDEX IF NOT EXISTS idx_receipts_receipt_number ON receipts(receipt_number);
CREATE INDEX IF NOT EXISTS idx_receipts_school_id ON receipts(school_id);
CREATE INDEX IF NOT EXISTS idx_receipts_created_at ON receipts(created_at DESC);

-- Receipt delivery tracking table
CREATE TABLE IF NOT EXISTS receipt_delivery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id UUID REFERENCES receipts(id) ON DELETE CASCADE,
    recipient_type VARCHAR(20) NOT NULL, -- 'parent', 'student', 'staff'
    recipient_id UUID,
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(20),
    delivery_method VARCHAR(20) NOT NULL, -- 'email', 'whatsapp', 'sms'
    delivery_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'queued', 'sent', 'delivered', 'failed', 'bounced'
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    external_message_id VARCHAR(255),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for receipt delivery
CREATE INDEX IF NOT EXISTS idx_receipt_delivery_receipt_id ON receipt_delivery(receipt_id);
CREATE INDEX IF NOT EXISTS idx_receipt_delivery_status ON receipt_delivery(delivery_status);
CREATE INDEX IF NOT EXISTS idx_receipt_delivery_school_id ON receipt_delivery(school_id);

-- Function to generate receipt number
CREATE OR REPLACE FUNCTION generate_receipt_number(p_school_id UUID)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_prefix VARCHAR(10);
    v_sequence INTEGER;
    v_receipt_number VARCHAR(50);
BEGIN
    -- Get school prefix or use default
    SELECT COALESCE(SUBSTRING(name FROM 1 FOR 3), 'EDU') INTO v_prefix
    FROM schools WHERE id = p_school_id LIMIT 1;
    
    -- Get next sequence number
    SELECT COALESCE(MAX(CAST(SUBSTRING(receipt_number FROM 5) AS INTEGER)), 0) + 1
    INTO v_sequence
    FROM receipts
    WHERE school_id = p_school_id
    AND receipt_number LIKE v_prefix || '%';
    
    -- Generate receipt number: PREFIX-YYYYMMDD-SEQUENCE
    v_receipt_number := v_prefix || '-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(v_sequence::TEXT, 6, '0');
    
    RETURN v_receipt_number;
END;
$$ LANGUAGE plpgsql;

-- Function to create receipt for payment
CREATE OR REPLACE FUNCTION create_payment_receipt(
    p_payment_id UUID,
    p_invoice_id UUID,
    p_student_id UUID,
    p_parent_id UUID,
    p_issued_by UUID,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_receipt_id UUID;
    v_receipt_number VARCHAR(50);
    v_payment RECORD;
BEGIN
    -- Get payment details
    SELECT * INTO v_payment
    FROM payments
    WHERE id = p_payment_id;
    
    -- Generate receipt number
    v_receipt_number := generate_receipt_number(p_school_id);
    
    -- Create receipt
    INSERT INTO receipts (
        receipt_number, payment_id, invoice_id, student_id, parent_id,
        amount, currency, payment_method, payment_date, issued_by, school_id,
        receipt_data
    ) VALUES (
        v_receipt_number, p_payment_id, p_invoice_id, p_student_id, p_parent_id,
        v_payment.amount, v_payment.currency, v_payment.payment_method, v_payment.payment_date,
        p_issued_by, p_school_id,
        jsonb_build_object(
            'payment_id', p_payment_id,
            'invoice_id', p_invoice_id,
            'amount', v_payment.amount,
            'payment_method', v_payment.payment_method,
            'payment_date', v_payment.payment_date,
            'reference', v_payment.reference
        )
    ) RETURNING id INTO v_receipt_id;
    
    RETURN v_receipt_id;
END;
$$ LANGUAGE plpgsql;

-- Function to queue receipt delivery
CREATE OR REPLACE FUNCTION queue_receipt_delivery(
    p_receipt_id UUID,
    p_delivery_method VARCHAR(20),
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_delivery_id UUID;
    v_receipt RECORD;
    v_recipient_email VARCHAR(255);
    v_recipient_phone VARCHAR(20);
BEGIN
    -- Get receipt details
    SELECT r.*, p.email as parent_email, p.phone as parent_phone,
           s.email as student_email, s.phone_number as student_phone
    INTO v_receipt
    FROM receipts r
    LEFT JOIN parents p ON r.parent_id = p.id
    LEFT JOIN students s ON r.student_id = s.id
    WHERE r.id = p_receipt_id;
    
    -- Determine recipient contact based on delivery method
    IF p_delivery_method = 'email' THEN
        v_recipient_email := COALESCE(v_receipt.parent_email, v_receipt.student_email);
    ELSIF p_delivery_method IN ('whatsapp', 'sms') THEN
        v_recipient_phone := COALESCE(v_receipt.parent_phone, v_receipt.student_phone);
    END IF;
    
    -- Create delivery record
    INSERT INTO receipt_delivery (
        receipt_id, recipient_type, recipient_id, recipient_email, recipient_phone,
        delivery_method, delivery_status, school_id
    ) VALUES (
        p_receipt_id, 
        CASE WHEN v_receipt.parent_id IS NOT NULL THEN 'parent' ELSE 'student' END,
        COALESCE(v_receipt.parent_id, v_receipt.student_id),
        v_recipient_email,
        v_recipient_phone,
        p_delivery_method,
        'pending',
        p_school_id
    ) RETURNING id INTO v_delivery_id;
    
    RETURN v_delivery_id;
END;
$$ LANGUAGE plpgsql;

-- View for recent receipts
CREATE OR REPLACE VIEW recent_receipts AS
SELECT 
    r.id,
    r.receipt_number,
    r.amount,
    r.currency,
    r.payment_method,
    r.receipt_date,
    r.status,
    r.delivery_status,
    CONCAT(p.first_name, ' ', p.last_name) as parent_name,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    i.invoice_number
FROM receipts r
LEFT JOIN parents p ON r.parent_id = p.id
LEFT JOIN students s ON r.student_id = s.id
LEFT JOIN invoices i ON r.invoice_id = i.id
ORDER BY r.receipt_date DESC
LIMIT 100;
