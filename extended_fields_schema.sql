-- Extended Fields Schema
-- Adds missing fields to parent and student records

-- Create bus routes tables
DROP TABLE IF EXISTS bus_stops CASCADE;
DROP TABLE IF EXISTS bus_routes CASCADE;

ALTER TABLE parents ADD COLUMN IF NOT EXISTS workplace VARCHAR(255);
ALTER TABLE parents ADD COLUMN IF NOT EXISTS work_address TEXT;
ALTER TABLE parents ADD COLUMN IF NOT EXISTS occupation VARCHAR(100);
ALTER TABLE parents ADD COLUMN IF NOT EXISTS income_level VARCHAR(50);
ALTER TABLE parents ADD COLUMN IF NOT EXISTS discount_category VARCHAR(50); -- 'staff_child', 'sibling_discount', 'early_payment', 'none'
ALTER TABLE parents ADD COLUMN IF NOT EXISTS discount_percentage INTEGER DEFAULT 0;
ALTER TABLE parents ADD COLUMN IF NOT EXISTS preferred_contact_method VARCHAR(50); -- 'whatsapp', 'sms', 'email'

-- Add bus route fields to students table
ALTER TABLE students ADD COLUMN IF NOT EXISTS bus_route_id UUID;
ALTER TABLE students ADD COLUMN IF NOT EXISTS bus_stop VARCHAR(255);
ALTER TABLE parents ADD COLUMN IF NOT EXISTS transport_fee_included BOOLEAN DEFAULT false;

-- Create bus routes table
CREATE TABLE IF NOT EXISTS bus_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_name VARCHAR(255) NOT NULL,
    route_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    driver_name VARCHAR(255),
    driver_phone VARCHAR(20),
    vehicle_number VARCHAR(50),
    capacity INTEGER DEFAULT 40,
    current_students INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Create bus stops table
CREATE TABLE IF NOT EXISTS bus_stops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES bus_routes(id) ON DELETE CASCADE,
    stop_name VARCHAR(255) NOT NULL,
    stop_order INTEGER NOT NULL,
    location_address TEXT,
    estimated_arrival TIME,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID
);

-- Indexes for bus routes
CREATE INDEX IF NOT EXISTS idx_bus_routes_school_id ON bus_routes(school_id);
CREATE INDEX IF NOT EXISTS idx_bus_stops_route_id ON bus_stops(route_id);
CREATE INDEX IF NOT EXISTS idx_bus_routes_route_code ON bus_routes(route_code);

-- Add satisfaction score to helpdesk tickets
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS satisfaction_score INTEGER; -- 1-5 rating
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS satisfaction_feedback TEXT;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS resolution_hours DECIMAL(5,2); -- Time to resolution in hours

-- Add SLA tracking to tickets
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS sla_deadline TIMESTAMP WITH TIME ZONE;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS sla_breached BOOLEAN DEFAULT false;

-- Function to calculate SLA deadline (24 hours)
CREATE OR REPLACE FUNCTION set_ticket_sla_deadline()
RETURNS TRIGGER AS $$
BEGIN
    NEW.sla_deadline := NEW.created_at + INTERVAL '24 hours';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically set SLA deadline on ticket creation
DROP TRIGGER IF EXISTS trigger_set_sla_deadline ON tickets;
CREATE TRIGGER trigger_set_sla_deadline
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_ticket_sla_deadline();

-- Function to check SLA breaches
CREATE OR REPLACE FUNCTION check_sla_breaches()
RETURNS INTEGER AS $$
DECLARE
    v_breach_count INTEGER;
BEGIN
    UPDATE tickets
    SET sla_breached = true
    WHERE status != 'resolved'
    AND sla_deadline < NOW()
    AND sla_breached = false;
    
    GET DIAGNOSTICS v_breach_count = ROW_COUNT;
    RETURN v_breach_count;
END;
$$ LANGUAGE plpgsql;

-- View for SLA monitoring
CREATE OR REPLACE VIEW sla_monitoring AS
SELECT 
    id,
    subject,
    parent_id,
    priority,
    status,
    created_at,
    sla_deadline,
    sla_breached,
    CASE 
        WHEN sla_deadline < NOW() AND status != 'resolved' THEN 'BREACHED'
        WHEN sla_deadline < NOW() + INTERVAL '6 hours' AND status != 'resolved' THEN 'CRITICAL'
        WHEN sla_deadline < NOW() + INTERVAL '12 hours' AND status != 'resolved' THEN 'WARNING'
        ELSE 'OK'
    END as sla_status
FROM tickets
WHERE status != 'resolved'
ORDER BY sla_deadline ASC;
