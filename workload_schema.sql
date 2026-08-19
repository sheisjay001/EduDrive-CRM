-- Staff Workload Indicators Schema
-- Track and analyze staff workload across different tasks

-- Drop tables if they exist
DROP TABLE IF EXISTS staff_workload CASCADE;
DROP TABLE IF EXISTS workload_metrics CASCADE;

-- Staff workload table
CREATE TABLE IF NOT EXISTS staff_workload (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    staff_name VARCHAR(255),
    staff_role VARCHAR(50),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL, -- 'lead_followup', 'ticket_resolution', 'parent_communication', 'grading', 'admin'
    task_count INTEGER DEFAULT 0,
    task_capacity INTEGER DEFAULT 100, -- Maximum tasks staff can handle
    workload_percentage DECIMAL(5,2) GENERATED ALWAYS AS (ROUND((task_count::DECIMAL / NULLIF(task_capacity, 0)) * 100, 2)) STORED,
    priority_level VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high', 'overloaded'
    assigned_date DATE DEFAULT CURRENT_DATE,
    week_number INTEGER,
    month_number INTEGER,
    year_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for staff workload
CREATE INDEX IF NOT EXISTS idx_staff_workload_staff_id ON staff_workload(staff_id);
CREATE INDEX IF NOT EXISTS idx_staff_workload_task_type ON staff_workload(task_type);
CREATE INDEX IF NOT EXISTS idx_staff_workload_school_id ON staff_workload(school_id);
CREATE INDEX IF NOT EXISTS idx_staff_workload_assigned_date ON staff_workload(assigned_date DESC);
CREATE INDEX IF NOT EXISTS idx_staff_workload_priority ON staff_workload(priority_level);

-- Workload metrics table (aggregated data)
CREATE TABLE IF NOT EXISTS workload_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    staff_name VARCHAR(255),
    staff_role VARCHAR(50),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    metric_period VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_assigned INTEGER DEFAULT 0,
    avg_task_completion_hours DECIMAL(10,2),
    avg_response_time_hours DECIMAL(10,2),
    task_completion_rate DECIMAL(5,2),
    overtime_hours DECIMAL(10,2) DEFAULT 0,
    productivity_score DECIMAL(5,2), -- 0-100 score
    efficiency_rating VARCHAR(20), -- 'excellent', 'good', 'average', 'needs_improvement'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for workload metrics
CREATE INDEX IF NOT EXISTS idx_workload_metrics_staff_id ON workload_metrics(staff_id);
CREATE INDEX IF NOT EXISTS idx_workload_metrics_period ON workload_metrics(metric_period, period_start);
CREATE INDEX IF NOT EXISTS idx_workload_metrics_school_id ON workload_metrics(school_id);

-- Function to update staff workload
CREATE OR REPLACE FUNCTION update_staff_workload(
    p_staff_id UUID,
    p_staff_name VARCHAR(255),
    p_staff_role VARCHAR(50),
    p_task_type VARCHAR(100),
    p_task_change INTEGER, -- +1 to add task, -1 to remove task
    p_school_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_workload RECORD;
    v_new_count INTEGER;
    v_new_percentage DECIMAL(5,2);
    v_new_priority VARCHAR(20);
BEGIN
    -- Get current workload
    SELECT * INTO v_workload
    FROM staff_workload
    WHERE staff_id = p_staff_id
    AND task_type = p_task_type
    AND assigned_date = CURRENT_DATE;
    
    IF v_workload IS NULL THEN
        -- Create new workload record
        v_new_count := GREATEST(0, p_task_change);
        v_new_percentage := ROUND((v_new_count::DECIMAL / 100) * 100, 2);
        
        IF v_new_percentage >= 100 THEN
            v_new_priority := 'overloaded';
        ELSIF v_new_percentage >= 80 THEN
            v_new_priority := 'high';
        ELSIF v_new_percentage >= 50 THEN
            v_new_priority := 'normal';
        ELSE
            v_new_priority := 'low';
        END IF;
        
        INSERT INTO staff_workload (
            staff_id, staff_name, staff_role, task_type, task_count,
            task_capacity, priority_level, school_id,
            week_number, month_number, year_number
        ) VALUES (
            p_staff_id, p_staff_name, p_staff_role, p_task_type, v_new_count,
            100, v_new_priority, p_school_id,
            EXTRACT(WEEK FROM CURRENT_DATE)::INTEGER,
            EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER,
            EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER
        );
    ELSE
        -- Update existing workload
        v_new_count := GREATEST(0, v_workload.task_count + p_task_change);
        v_new_percentage := ROUND((v_new_count::DECIMAL / v_workload.task_capacity) * 100, 2);
        
        IF v_new_percentage >= 100 THEN
            v_new_priority := 'overloaded';
        ELSIF v_new_percentage >= 80 THEN
            v_new_priority := 'high';
        ELSIF v_new_percentage >= 50 THEN
            v_new_priority := 'normal';
        ELSE
            v_new_priority := 'low';
        END IF;
        
        UPDATE staff_workload
        SET 
            task_count = v_new_count,
            priority_level = v_new_priority,
            updated_at = NOW()
        WHERE id = v_workload.id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate workload metrics
CREATE OR REPLACE FUNCTION calculate_workload_metrics(
    p_staff_id UUID,
    p_staff_name VARCHAR(255),
    p_staff_role VARCHAR(50),
    p_metric_period VARCHAR(20),
    p_period_start DATE,
    p_period_end DATE,
    p_school_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_tasks_completed INTEGER;
    v_tasks_assigned INTEGER;
    v_avg_completion_hours DECIMAL(10,2);
    v_avg_response_hours DECIMAL(10,2);
    v_completion_rate DECIMAL(5,2);
    v_productivity_score DECIMAL(5,2);
    v_efficiency_rating VARCHAR(20);
BEGIN
    -- Calculate metrics based on task type
    -- This would aggregate data from various tables (leads, tickets, etc.)
    -- For now, using placeholder logic
    
    v_tasks_completed := 0; -- Would be calculated from actual task completions
    v_tasks_assigned := 0; -- Would be calculated from task assignments
    v_avg_completion_hours := 0;
    v_avg_response_hours := 0;
    v_completion_rate := 0;
    
    IF v_tasks_assigned > 0 THEN
        v_completion_rate := (v_tasks_completed::DECIMAL / v_tasks_assigned) * 100;
    END IF;
    
    -- Calculate productivity score (0-100)
    v_productivity_score := LEAST(100, GREATEST(0, 
        (v_completion_rate * 0.6) + 
        (CASE WHEN v_avg_completion_hours > 0 THEN LEAST(100, 24 / v_avg_completion_hours * 20) ELSE 0 END) +
        (CASE WHEN v_avg_response_hours > 0 THEN LEAST(100, 2 / v_avg_response_hours * 20) ELSE 0 END)
    ));
    
    -- Determine efficiency rating
    IF v_productivity_score >= 80 THEN
        v_efficiency_rating := 'excellent';
    ELSIF v_productivity_score >= 60 THEN
        v_efficiency_rating := 'good';
    ELSIF v_productivity_score >= 40 THEN
        v_efficiency_rating := 'average';
    ELSE
        v_efficiency_rating := 'needs_improvement';
    END IF;
    
    -- Insert or update metrics
    INSERT INTO workload_metrics (
        staff_id, staff_name, staff_role, metric_period, period_start, period_end,
        total_tasks_completed, total_tasks_assigned, avg_task_completion_hours,
        avg_response_time_hours, task_completion_rate, productivity_score,
        efficiency_rating, school_id
    ) VALUES (
        p_staff_id, p_staff_name, p_staff_role, p_metric_period, p_period_start, p_period_end,
        v_tasks_completed, v_tasks_assigned, v_avg_completion_hours,
        v_avg_response_hours, v_completion_rate, v_productivity_score,
        v_efficiency_rating, p_school_id
    )
    ON CONFLICT (staff_id, metric_period, period_start) DO UPDATE SET
        total_tasks_completed = EXCLUDED.total_tasks_completed,
        total_tasks_assigned = EXCLUDED.total_tasks_assigned,
        avg_task_completion_hours = EXCLUDED.avg_task_completion_hours,
        avg_response_time_hours = EXCLUDED.avg_response_time_hours,
        task_completion_rate = EXCLUDED.task_completion_rate,
        productivity_score = EXCLUDED.productivity_score,
        efficiency_rating = EXCLUDED.efficiency_rating;
END;
$$ LANGUAGE plpgsql;

-- Views for workload analysis
CREATE OR REPLACE VIEW current_workload_status AS
SELECT 
    staff_id,
    staff_name,
    staff_role,
    task_type,
    task_count,
    task_capacity,
    workload_percentage,
    priority_level,
    assigned_date
FROM staff_workload
WHERE assigned_date = CURRENT_DATE
ORDER BY workload_percentage DESC;

CREATE OR REPLACE VIEW workload_summary_by_role AS
SELECT 
    staff_role,
    COUNT(DISTINCT staff_id) as total_staff,
    AVG(workload_percentage) as avg_workload_percentage,
    COUNT(*) FILTER (WHERE priority_level = 'overloaded') as overloaded_count,
    COUNT(*) FILTER (WHERE priority_level = 'high') as high_workload_count,
    SUM(task_count) as total_tasks,
    SUM(task_capacity) as total_capacity
FROM staff_workload
WHERE assigned_date = CURRENT_DATE
GROUP BY staff_role
ORDER BY avg_workload_percentage DESC;

CREATE OR REPLACE VIEW staff_performance_trends AS
SELECT 
    staff_id,
    staff_name,
    staff_role,
    metric_period,
    period_start,
    productivity_score,
    efficiency_rating,
    task_completion_rate,
    avg_task_completion_hours
FROM workload_metrics
WHERE period_end >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY period_start DESC, productivity_score DESC;
