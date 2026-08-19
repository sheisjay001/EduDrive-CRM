-- Bulk Billing Functionality Schema
-- Generate invoices in bulk for students based on fee structures

-- Drop tables if they exists
DROP TABLE IF EXISTS bulk_billing_jobs CASCADE;
DROP TABLE IF EXISTS fee_structures CASCADE;

-- Fee structures table
CREATE TABLE IF NOT EXISTS fee_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    structure_name VARCHAR(255) NOT NULL,
    structure_type VARCHAR(50) NOT NULL, -- 'tuition', 'registration', 'extracurricular', 'transport', 'other'
    academic_year VARCHAR(20),
    term VARCHAR(20),
    class_level VARCHAR(100),
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    due_date_offset INTEGER DEFAULT 30, -- Days from invoice generation
    description TEXT,
    is_recurring BOOLEAN DEFAULT false,
    recurring_frequency VARCHAR(20), -- 'monthly', 'termly', 'yearly'
    is_active BOOLEAN DEFAULT true,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fee structures
CREATE INDEX IF NOT EXISTS idx_fee_structures_type ON fee_structures(structure_type);
CREATE INDEX IF NOT EXISTS idx_fee_structures_class_level ON fee_structures(class_level);
CREATE INDEX IF NOT EXISTS idx_fee_structures_school_id ON fee_structures(school_id);
CREATE INDEX IF NOT EXISTS idx_fee_structures_is_active ON fee_structures(is_active);

-- Bulk billing jobs table
CREATE TABLE IF NOT EXISTS bulk_billing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) NOT NULL, -- 'tuition', 'registration', 'custom'
    fee_structure_id UUID REFERENCES fee_structures(id) ON DELETE SET NULL,
    academic_year VARCHAR(20),
    term VARCHAR(20),
    class_filter VARCHAR(100), -- Filter by class
    student_filter JSONB, -- Additional filters
    invoice_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    total_students INTEGER DEFAULT 0,
    successful_invoices INTEGER DEFAULT 0,
    failed_invoices INTEGER DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'partial'
    started_by UUID REFERENCES auth.users(id),
    started_by_name VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for bulk billing jobs
CREATE INDEX IF NOT EXISTS idx_bulk_billing_jobs_status ON bulk_billing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_bulk_billing_jobs_school_id ON bulk_billing_jobs(school_id);
CREATE INDEX IF NOT EXISTS idx_bulk_billing_jobs_started_at ON bulk_billing_jobs(started_at DESC);

-- Bulk billing job details
CREATE TABLE IF NOT EXISTS bulk_billing_job_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES bulk_billing_jobs(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    invoice_id UUID REFERENCES invoices(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES parents(id) ON DELETE SET NULL,
    amount DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'created', 'failed'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for job details
CREATE INDEX IF NOT EXISTS idx_bulk_billing_job_details_job_id ON bulk_billing_job_details(job_id);
CREATE INDEX IF NOT EXISTS idx_bulk_billing_job_details_student_id ON bulk_billing_job_details(student_id);
CREATE INDEX IF NOT EXISTS idx_bulk_billing_job_details_status ON bulk_billing_job_details(status);

-- Function to create bulk billing job
CREATE OR REPLACE FUNCTION create_bulk_billing_job(
    p_job_name VARCHAR(255),
    p_job_type VARCHAR(50),
    p_fee_structure_id UUID,
    p_academic_year VARCHAR(20),
    p_term VARCHAR(20),
    p_class_filter VARCHAR(100),
    p_student_filter JSONB,
    p_invoice_date DATE,
    p_due_date DATE,
    p_started_by UUID,
    p_started_by_name VARCHAR(255),
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_job_id UUID;
    v_fee_structure RECORD;
BEGIN
    -- Get fee structure details if provided
    IF p_fee_structure_id IS NOT NULL THEN
        SELECT * INTO v_fee_structure FROM fee_structures WHERE id = p_fee_structure_id;
    END IF;
    
    -- Calculate due date if not provided
    IF p_due_date IS NULL AND v_fee_structure IS NOT NULL THEN
        p_due_date := p_invoice_date + (v_fee_structure.due_date_offset || ' days')::INTERVAL;
    END IF;
    
    -- Create bulk billing job
    INSERT INTO bulk_billing_jobs (
        job_name, job_type, fee_structure_id, academic_year, term, class_filter,
        student_filter, invoice_date, due_date, started_by, started_by_name, school_id
    ) VALUES (
        p_job_name, p_job_type, p_fee_structure_id, p_academic_year, p_term, p_class_filter,
        p_student_filter, p_invoice_date, p_due_date, p_started_by, p_started_by_name, p_school_id
    ) RETURNING id INTO v_job_id;
    
    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

-- Function to process bulk billing job
CREATE OR REPLACE FUNCTION process_bulk_billing_job(p_job_id UUID)
RETURNS VOID AS $$
DECLARE
    v_job RECORD;
    v_students CURSOR FOR 
        SELECT s.id, s.parent_id, s.class, s.first_name, s.last_name
        FROM students s
        WHERE s.school_id = (SELECT school_id FROM bulk_billing_jobs WHERE id = p_job_id)
        AND s.status = 'active';
    v_student RECORD;
    v_invoice_id UUID;
    v_fee_structure RECORD;
    v_invoice_number VARCHAR(50);
BEGIN
    -- Get job details
    SELECT * INTO v_job FROM bulk_billing_jobs WHERE id = p_job_id;
    
    -- Get fee structure
    SELECT * INTO v_fee_structure FROM fee_structures WHERE id = v_job.fee_structure_id;
    
    -- Update job status to processing
    UPDATE bulk_billing_jobs SET status = 'processing' WHERE id = p_job_id;
    
    -- Process each student
    FOR v_student IN v_students LOOP
        BEGIN
            -- Apply class filter if specified
            IF v_job.class_filter IS NOT NULL AND v_student.class != v_job.class_filter THEN
                CONTINUE;
            END IF;
            
            -- Generate invoice number
            v_invoice_number := 'INV-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('invoice_seq')::TEXT, 6, '0');
            
            -- Create invoice
            INSERT INTO invoices (
                invoice_number, student_id, parent_id, invoice_date, due_date,
                total_amount, amount_paid, status, academic_year, term,
                invoice_type, description, school_id
            ) VALUES (
                v_invoice_number, v_student.id, v_student.parent_id, v_job.invoice_date, v_job.due_date,
                v_fee_structure.amount, 0, 'pending', v_job.academic_year, v_job.term,
                v_fee_structure.structure_type, v_fee_structure.description, v_job.school_id
            ) RETURNING id INTO v_invoice_id;
            
            -- Record successful invoice creation
            INSERT INTO bulk_billing_job_details (job_id, student_id, invoice_id, parent_id, amount, status)
            VALUES (p_job_id, v_student.id, v_invoice_id, v_student.parent_id, v_fee_structure.amount, 'created');
            
            -- Update job counters
            UPDATE bulk_billing_jobs SET 
                successful_invoices = successful_invoices + 1,
                total_amount = total_amount + v_fee_structure.amount
            WHERE id = p_job_id;
            
        EXCEPTION WHEN OTHERS THEN
            -- Record failed invoice creation
            INSERT INTO bulk_billing_job_details (job_id, student_id, amount, status, error_message)
            VALUES (p_job_id, v_student.id, v_fee_structure.amount, 'failed', SQLERRM);
            
            UPDATE bulk_billing_jobs SET failed_invoices = failed_invoices + 1 WHERE id = p_job_id;
        END;
    END LOOP;
    
    -- Update total students and job status
    UPDATE bulk_billing_jobs SET 
        total_students = successful_invoices + failed_invoices,
        status = CASE WHEN failed_invoices = 0 THEN 'completed' ELSE 'partial' END,
        completed_at = NOW()
    WHERE id = p_job_id;
END;
$$ LANGUAGE plpgsql;

-- View for bulk billing history
CREATE OR REPLACE VIEW bulk_billing_history AS
SELECT 
    bbj.id,
    bbj.job_name,
    bbj.job_type,
    bbj.academic_year,
    bbj.term,
    bbj.class_filter,
    bbj.invoice_date,
    bbj.due_date,
    bbj.total_students,
    bbj.successful_invoices,
    bbj.failed_invoices,
    bbj.total_amount,
    bbj.status,
    bbj.started_by_name,
    bbj.started_at,
    bbj.completed_at,
    fs.structure_name,
    fs.structure_type
FROM bulk_billing_jobs bbj
LEFT JOIN fee_structures fs ON bbj.fee_structure_id = fs.id
ORDER BY bbj.started_at DESC;
