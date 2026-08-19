-- Debtors Dashboard with Aging Buckets Schema
-- Track outstanding payments and aging analysis

-- Drop tables if they exist
DROP TABLE IF EXISTS debtor_aging CASCADE;
DROP TABLE IF EXISTS payment_reconciliation CASCADE;

-- Debtor aging table
CREATE TABLE IF NOT EXISTS debtor_aging (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES parents(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50),
    invoice_date DATE,
    due_date DATE,
    amount_due DECIMAL(12,2),
    amount_paid DECIMAL(12,2) DEFAULT 0,
    balance_due DECIMAL(12,2),
    days_overdue INTEGER,
    aging_bucket VARCHAR(20), -- 'current', '1-30', '31-60', '61-90', '90+'
    last_payment_date DATE,
    payment_count INTEGER DEFAULT 0,
    contact_attempts INTEGER DEFAULT 0,
    last_contact_date DATE,
    promise_to_pay_date DATE,
    promise_amount DECIMAL(12,2),
    promise_kept BOOLEAN,
    collection_status VARCHAR(20) DEFAULT 'active', -- 'active', 'in_progress', 'escalated', 'written_off', 'resolved'
    assigned_to UUID REFERENCES auth.users(id),
    assigned_to_name VARCHAR(255),
    notes TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for debtor aging
CREATE INDEX IF NOT EXISTS idx_debtor_aging_invoice_id ON debtor_aging(invoice_id);
CREATE INDEX IF NOT EXISTS idx_debtor_aging_student_id ON debtor_aging(student_id);
CREATE INDEX IF NOT EXISTS idx_debtor_aging_parent_id ON debtor_aging(parent_id);
CREATE INDEX IF NOT EXISTS idx_debtor_aging_aging_bucket ON debtor_aging(aging_bucket);
CREATE INDEX IF NOT EXISTS idx_debtor_aging_collection_status ON debtor_aging(collection_status);
CREATE INDEX IF NOT EXISTS idx_debtor_aging_school_id ON debtor_aging(school_id);
CREATE INDEX IF NOT EXISTS idx_debtor_aging_days_overdue ON debtor_aging(days_overdue);

-- Payment reconciliation table
CREATE TABLE IF NOT EXISTS payment_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID REFERENCES payments(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    reconciliation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reconciled_by UUID REFERENCES auth.users(id),
    reconciled_by_name VARCHAR(255),
    payment_amount DECIMAL(12,2),
    invoice_amount DECIMAL(12,2),
    difference DECIMAL(12,2),
    reconciliation_status VARCHAR(20), -- 'matched', 'partial', 'overpayment', 'underpayment', 'dispute'
    notes TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for payment reconciliation
CREATE INDEX IF NOT EXISTS idx_payment_reconciliation_payment_id ON payment_reconciliation(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_reconciliation_invoice_id ON payment_reconciliation(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payment_reconciliation_status ON payment_reconciliation(reconciliation_status);
CREATE INDEX IF NOT EXISTS idx_payment_reconciliation_school_id ON payment_reconciliation(school_id);

-- Function to calculate aging bucket
CREATE OR REPLACE FUNCTION calculate_aging_bucket(p_days_overdue INTEGER)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF p_days_overdue <= 0 THEN
        RETURN 'current';
    ELSIF p_days_overdue <= 30 THEN
        RETURN '1-30';
    ELSIF p_days_overdue <= 60 THEN
        RETURN '31-60';
    ELSIF p_days_overdue <= 90 THEN
        RETURN '61-90';
    ELSE
        RETURN '90+';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to update debtor aging
CREATE OR REPLACE FUNCTION update_debtor_aging(p_invoice_id UUID)
RETURNS VOID AS $$
DECLARE
    v_invoice RECORD;
    v_balance_due DECIMAL(12,2);
    v_days_overdue INTEGER;
    v_aging_bucket VARCHAR(20);
BEGIN
    -- Get invoice details
    SELECT * INTO v_invoice FROM invoices WHERE id = p_invoice_id;
    
    -- Calculate balance due
    v_balance_due := v_invoice.total_amount - COALESCE(v_invoice.amount_paid, 0);
    
    -- Calculate days overdue
    v_days_overdue := EXTRACT(DAY FROM (CURRENT_DATE - v_invoice.due_date));
    
    -- Calculate aging bucket
    v_aging_bucket := calculate_aging_bucket(v_days_overdue);
    
    -- Insert or update debtor aging record
    INSERT INTO debtor_aging (
        invoice_id, student_id, parent_id, invoice_number, invoice_date, due_date,
        amount_due, amount_paid, balance_due, days_overdue, aging_bucket,
        school_id
    ) VALUES (
        p_invoice_id, v_invoice.student_id, v_invoice.parent_id, v_invoice.invoice_number,
        v_invoice.invoice_date, v_invoice.due_date, v_invoice.total_amount,
        COALESCE(v_invoice.amount_paid, 0), v_balance_due, v_days_overdue, v_aging_bucket,
        v_invoice.school_id
    )
    ON CONFLICT (invoice_id) DO UPDATE SET
        amount_paid = EXCLUDED.amount_paid,
        balance_due = EXCLUDED.balance_due,
        days_overdue = EXCLUDED.days_overdue,
        aging_bucket = EXCLUDED.aging_bucket,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to reconcile payment
CREATE OR REPLACE FUNCTION reconcile_payment(
    p_payment_id UUID,
    p_invoice_id UUID,
    p_reconciled_by UUID,
    p_reconciled_by_name VARCHAR(255),
    p_notes TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_payment RECORD;
    v_invoice RECORD;
    v_difference DECIMAL(12,2);
    v_reconciliation_status VARCHAR(20);
    v_reconciliation_id UUID;
BEGIN
    -- Get payment and invoice details
    SELECT * INTO v_payment FROM payments WHERE id = p_payment_id;
    SELECT * INTO v_invoice FROM invoices WHERE id = p_invoice_id;
    
    -- Calculate difference
    v_difference := v_payment.amount - v_invoice.total_amount;
    
    -- Determine reconciliation status
    IF ABS(v_difference) < 0.01 THEN
        v_reconciliation_status := 'matched';
    ELSIF v_difference > 0 THEN
        v_reconciliation_status := 'overpayment';
    ELSE
        v_reconciliation_status := 'underpayment';
    END IF;
    
    -- Create reconciliation record
    INSERT INTO payment_reconciliation (
        payment_id, invoice_id, payment_amount, invoice_amount, difference,
        reconciliation_status, reconciled_by, reconciled_by_name, notes, school_id
    ) VALUES (
        p_payment_id, p_invoice_id, v_payment.amount, v_invoice.total_amount,
        v_difference, v_reconciliation_status, p_reconciled_by, p_reconciled_by_name,
        p_notes, p_school_id
    ) RETURNING id INTO v_reconciliation_id;
    
    -- Update debtor aging
    PERFORM update_debtor_aging(p_invoice_id);
    
    RETURN v_reconciliation_id;
END;
$$ LANGUAGE plpgsql;

-- Views for debtors dashboard
CREATE OR REPLACE VIEW debtors_summary AS
SELECT 
    aging_bucket,
    COUNT(*) as number_of_debtors,
    SUM(balance_due) as total_balance_due,
    AVG(balance_due) as avg_balance_due,
    MAX(days_overdue) as max_days_overdue
FROM debtor_aging
WHERE balance_due > 0
GROUP BY aging_bucket
ORDER BY 
    CASE aging_bucket
        WHEN 'current' THEN 1
        WHEN '1-30' THEN 2
        WHEN '31-60' THEN 3
        WHEN '61-90' THEN 4
        WHEN '90+' THEN 5
    END;

CREATE OR REPLACE VIEW debtor_details AS
SELECT 
    da.id,
    da.invoice_number,
    da.invoice_date,
    da.due_date,
    da.amount_due,
    da.amount_paid,
    da.balance_due,
    da.days_overdue,
    da.aging_bucket,
    da.collection_status,
    CONCAT(p.first_name, ' ', p.last_name) as parent_name,
    p.phone as parent_phone,
    p.email as parent_email,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    s.class as student_class,
    da.assigned_to_name,
    da.promise_to_pay_date,
    da.promise_amount,
    da.promise_kept,
    da.contact_attempts,
    da.last_contact_date
FROM debtor_aging da
LEFT JOIN parents p ON da.parent_id = p.id
LEFT JOIN students s ON da.student_id = s.id
WHERE da.balance_due > 0
ORDER BY da.days_overdue DESC;

CREATE OR REPLACE VIEW collection_performance AS
SELECT 
    assigned_to_name,
    COUNT(*) as total_assigned,
    COUNT(*) FILTER (WHERE collection_status = 'resolved') as resolved,
    COUNT(*) FILTER (WHERE collection_status = 'in_progress') as in_progress,
    COUNT(*) FILTER (WHERE promise_kept = true) as promises_kept,
    SUM(balance_due) FILTER (WHERE collection_status = 'resolved') as amount_collected,
    AVG(days_overdue) as avg_days_overdue,
    ROUND(COUNT(*) FILTER (WHERE collection_status = 'resolved')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as resolution_rate
FROM debtor_aging
WHERE assigned_to_name IS NOT NULL
GROUP BY assigned_to_name
ORDER BY amount_collected DESC;
