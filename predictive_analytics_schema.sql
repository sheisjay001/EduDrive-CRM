-- Predictive Analytics Schema
-- Enrollment prediction, fee collection forecasting, and student retention analysis

-- Drop tables if they exist
DROP TABLE IF EXISTS retention_predictions CASCADE;
DROP TABLE IF EXISTS enrollment_predictions CASCADE;
DROP TABLE IF EXISTS fee_forecasting CASCADE;

-- Enrollment predictions table
CREATE TABLE IF NOT EXISTS enrollment_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_date DATE NOT NULL,
    prediction_period VARCHAR(20) NOT NULL, -- 'monthly', 'termly', 'yearly'
    predicted_enrollments INTEGER NOT NULL,
    confidence_level DECIMAL(5,2), -- 0-100
    prediction_method VARCHAR(50), -- 'linear_regression', 'moving_average', 'seasonal'
    historical_data_points INTEGER,
    factors_considered JSONB, -- 'lead_volume', 'conversion_rate', 'seasonality', etc.
    class_level VARCHAR(50),
    session_id UUID REFERENCES academic_sessions(id) ON DELETE SET NULL,
    actual_enrollments INTEGER,
    prediction_accuracy DECIMAL(5,2), -- Calculated after actual data available
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for enrollment predictions
CREATE INDEX IF NOT EXISTS idx_enrollment_predictions_date ON enrollment_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_enrollment_predictions_period ON enrollment_predictions(prediction_period);
CREATE INDEX IF NOT EXISTS idx_enrollment_predictions_class_level ON enrollment_predictions(class_level);
CREATE INDEX IF NOT EXISTS idx_enrollment_predictions_school_id ON enrollment_predictions(school_id);

-- Fee forecasting table
CREATE TABLE IF NOT EXISTS fee_forecasting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_date DATE NOT NULL,
    forecast_period VARCHAR(20) NOT NULL, -- 'monthly', 'termly', 'yearly'
    predicted_revenue DECIMAL(15,2) NOT NULL,
    predicted_collections DECIMAL(15,2) NOT NULL,
    predicted_outstanding DECIMAL(15,2) NOT NULL,
    confidence_level DECIMAL(5,2),
    forecast_method VARCHAR(50),
    historical_data_points INTEGER,
    factors_considered JSONB, -- 'enrollment', 'payment_history', 'economic_factors', etc.
    term_id UUID REFERENCES academic_terms(id) ON DELETE SET NULL,
    actual_revenue DECIMAL(15,2),
    actual_collections DECIMAL(15,2),
    forecast_accuracy DECIMAL(5,2),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fee forecasting
CREATE INDEX IF NOT EXISTS idx_fee_forecasting_date ON fee_forecasting(forecast_date);
CREATE INDEX IF NOT EXISTS idx_fee_forecasting_period ON fee_forecasting(forecast_period);
CREATE INDEX IF NOT EXISTS idx_fee_forecasting_term_id ON fee_forecasting(term_id);
CREATE INDEX IF NOT EXISTS idx_fee_forecasting_school_id ON fee_forecasting(school_id);

-- Retention predictions table
CREATE TABLE IF NOT EXISTS retention_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    prediction_date DATE NOT NULL,
    prediction_period VARCHAR(20) NOT NULL, -- 'term', 'year'
    retention_probability DECIMAL(5,2) NOT NULL, -- 0-100
    retention_risk VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    risk_factors JSONB, -- 'academic_performance', 'attendance', 'payment_issues', 'behavior'
    recommended_actions JSONB,
    intervention_priority INTEGER, -- 1-10, higher = more urgent
    actual_retention BOOLEAN, -- Updated after period ends
    prediction_accuracy BOOLEAN, -- Was prediction correct?
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for retention predictions
CREATE INDEX IF NOT EXISTS idx_retention_predictions_student_id ON retention_predictions(student_id);
CREATE INDEX IF NOT EXISTS idx_retention_predictions_date ON retention_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_retention_predictions_risk ON retention_predictions(retention_risk);
CREATE INDEX IF NOT EXISTS idx_retention_predictions_school_id ON retention_predictions(school_id);

-- Function to generate enrollment prediction
CREATE OR REPLACE FUNCTION generate_enrollment_prediction(
    p_prediction_date DATE,
    p_prediction_period VARCHAR(20),
    p_class_level VARCHAR(50),
    p_session_id UUID,
    p_prediction_method VARCHAR(50),
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_prediction_id UUID;
    v_predicted_enrollments INTEGER;
    v_confidence_level DECIMAL(5,2);
    v_historical_data_points INTEGER;
    v_factors JSONB;
BEGIN
    -- Calculate historical data points
    SELECT COUNT(DISTINCT DATE_TRUNC('month', created_at)) INTO v_historical_data_points
    FROM leads
    WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
    AND school_id = p_school_id;
    
    -- Simple prediction logic (would be enhanced with ML in production)
    CASE p_prediction_method
        WHEN 'moving_average' THEN
            -- Calculate 3-month moving average of enrollments
            SELECT ROUND(AVG(enrollment_count)) INTO v_predicted_enrollments
            FROM (
                SELECT COUNT(*) as enrollment_count
                FROM class_enrollments
                WHERE enrollment_date >= CURRENT_DATE - INTERVAL '3 months'
                AND school_id = p_school_id
                GROUP BY DATE_TRUNC('month', enrollment_date)
            ) sub;
            
        WHEN 'linear_regression' THEN
            -- Simple linear projection based on trend
            SELECT ROUND(COUNT(*) * 1.1) INTO v_predicted_enrollments
            FROM class_enrollments
            WHERE enrollment_date >= CURRENT_DATE - INTERVAL '3 months'
            AND school_id = p_school_id;
            
        ELSE
            -- Default to current enrollment + 10%
            SELECT ROUND(COUNT(*) * 1.1) INTO v_predicted_enrollments
            FROM class_enrollments
            WHERE enrollment_status = 'active'
            AND school_id = p_school_id;
    END CASE;
    
    -- Calculate confidence based on data availability
    v_confidence_level := LEAST(95, v_historical_data_points * 8);
    
    -- Build factors JSON
    v_factors := jsonb_build_object(
        'lead_volume', (SELECT COUNT(*) FROM leads WHERE school_id = p_school_id),
        'conversion_rate', (SELECT ROUND(COUNT(*) FILTER (WHERE stage = 'enrolled')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) FROM leads WHERE school_id = p_school_id),
        'seasonality', EXTRACT(MONTH FROM p_prediction_date),
        'historical_data_points', v_historical_data_points
    );
    
    -- Insert prediction
    INSERT INTO enrollment_predictions (
        prediction_date, prediction_period, predicted_enrollments,
        confidence_level, prediction_method, historical_data_points,
        factors_considered, class_level, session_id, school_id
    ) VALUES (
        p_prediction_date, p_prediction_period, v_predicted_enrollments,
        v_confidence_level, p_prediction_method, v_historical_data_points,
        v_factors, p_class_level, p_session_id, p_school_id
    ) RETURNING id INTO v_prediction_id;
    
    RETURN v_prediction_id;
END;
$$ LANGUAGE plpgsql;

-- Function to generate fee forecast
CREATE OR REPLACE FUNCTION generate_fee_forecast(
    p_forecast_date DATE,
    p_forecast_period VARCHAR(20),
    p_term_id UUID,
    p_prediction_method VARCHAR(50),
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_forecast_id UUID;
    v_predicted_revenue DECIMAL(15,2);
    v_predicted_collections DECIMAL(15,2);
    v_predicted_outstanding DECIMAL(15,2);
    v_confidence_level DECIMAL(5,2);
    v_factors JSONB;
BEGIN
    -- Calculate predicted revenue based on active enrollments
    -- Note: fee_structures table needs to be created separately
    SELECT 0 INTO v_predicted_revenue;
    -- Simplified version - would use fee_structures when available
    
    -- Predict collections based on historical payment rate (assume 85%)
    v_predicted_collections := v_predicted_revenue * 0.85;
    v_predicted_outstanding := v_predicted_revenue - v_predicted_collections;
    
    -- Calculate confidence
    v_confidence_level := 75; -- Default confidence
    
    -- Build factors JSON
    v_factors := jsonb_build_object(
        'active_enrollments', (SELECT COUNT(*) FROM class_enrollments WHERE enrollment_status = 'active' AND school_id = p_school_id),
        'historical_collection_rate', 0.85,
        'economic_factors', 'stable',
        'seasonality', EXTRACT(MONTH FROM p_forecast_date)
    );
    
    -- Insert forecast
    INSERT INTO fee_forecasting (
        forecast_date, forecast_period, predicted_revenue,
        predicted_collections, predicted_outstanding, confidence_level,
        forecast_method, factors_considered, term_id, school_id
    ) VALUES (
        p_forecast_date, p_forecast_period, v_predicted_revenue,
        v_predicted_collections, v_predicted_outstanding, v_confidence_level,
        p_prediction_method, v_factors, p_term_id, p_school_id
    ) RETURNING id INTO v_forecast_id;
    
    RETURN v_forecast_id;
END;
$$ LANGUAGE plpgsql;

-- Function to generate retention prediction
CREATE OR REPLACE FUNCTION generate_retention_prediction(
    p_student_id UUID,
    p_prediction_date DATE,
    p_prediction_period VARCHAR(20),
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_prediction_id UUID;
    v_retention_probability DECIMAL(5,2);
    v_retention_risk VARCHAR(20);
    v_risk_factors JSONB;
    v_intervention_priority INTEGER;
    v_academic_score DECIMAL(5,2);
    v_attendance_rate DECIMAL(5,2);
    v_payment_issues INTEGER;
BEGIN
    -- Get academic performance
    SELECT COALESCE(AVG((academic_performance->>'average_score')::DECIMAL), 70) INTO v_academic_score
    FROM student_lifecycle_logs
    WHERE student_id = p_student_id
    AND log_type = 'academic';
    
    -- Get attendance rate
    SELECT COALESCE(
        ROUND(COUNT(*) FILTER (WHERE status = 'present')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2),
        85
    ) INTO v_attendance_rate
    FROM student_attendance
    WHERE student_id = p_student_id;
    
    -- Check for payment issues
    SELECT COUNT(*) INTO v_payment_issues
    FROM debtor_aging
    WHERE student_id = p_student_id
    AND aging_bucket IN ('61-90', '90+');
    
    -- Calculate retention probability
    v_retention_probability := 100
        - (100 - v_academic_score) * 0.3
        - (100 - v_attendance_rate) * 0.4
        - (v_payment_issues * 10);
    
    v_retention_probability := GREATEST(0, LEAST(100, v_retention_probability));
    
    -- Determine risk level
    IF v_retention_probability >= 80 THEN
        v_retention_risk := 'low';
        v_intervention_priority := 1;
    ELSIF v_retention_probability >= 60 THEN
        v_retention_risk := 'medium';
        v_intervention_priority := 5;
    ELSIF v_retention_probability >= 40 THEN
        v_retention_risk := 'high';
        v_intervention_priority := 8;
    ELSE
        v_retention_risk := 'critical';
        v_intervention_priority := 10;
    END IF;
    
    -- Build risk factors
    v_risk_factors := jsonb_build_object(
        'academic_performance', v_academic_score,
        'attendance_rate', v_attendance_rate,
        'payment_issues', v_payment_issues,
        'disciplinary_records', (SELECT COUNT(*) FROM student_lifecycle_logs WHERE student_id = p_student_id AND log_type = 'disciplinary')
    );
    
    -- Insert prediction
    INSERT INTO retention_predictions (
        student_id, prediction_date, prediction_period,
        retention_probability, retention_risk, risk_factors,
        intervention_priority, school_id
    ) VALUES (
        p_student_id, p_prediction_date, p_prediction_period,
        v_retention_probability, v_retention_risk, v_risk_factors,
        v_intervention_priority, p_school_id
    ) RETURNING id INTO v_prediction_id;
    
    RETURN v_prediction_id;
END;
$$ LANGUAGE plpgsql;

-- Views for predictive analytics
CREATE OR REPLACE VIEW enrollment_forecast_summary AS
SELECT 
    prediction_date,
    prediction_period,
    class_level,
    predicted_enrollments,
    confidence_level,
    actual_enrollments,
    CASE 
        WHEN actual_enrollments IS NOT NULL 
        THEN ROUND(ABS(predicted_enrollments - actual_enrollments)::DECIMAL / NULLIF(actual_enrollments, 0) * 100, 2)
        ELSE NULL 
    END as prediction_error_percentage,
    prediction_method
FROM enrollment_predictions
ORDER BY prediction_date DESC;

CREATE OR REPLACE VIEW fee_forecast_summary AS
SELECT 
    forecast_date,
    forecast_period,
    predicted_revenue,
    predicted_collections,
    predicted_outstanding,
    confidence_level,
    actual_revenue,
    actual_collections,
    CASE 
        WHEN actual_collections IS NOT NULL 
        THEN ROUND(ABS(predicted_collections - actual_collections)::DECIMAL / NULLIF(actual_collections, 0) * 100, 2)
        ELSE NULL 
    END as forecast_error_percentage
FROM fee_forecasting
ORDER BY forecast_date DESC;

CREATE OR REPLACE VIEW retention_risk_report AS
SELECT 
    rp.student_id,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    s.class,
    rp.retention_probability,
    rp.retention_risk,
    rp.intervention_priority,
    rp.risk_factors->>'academic_performance' as academic_score,
    rp.risk_factors->>'attendance_rate' as attendance_rate,
    rp.risk_factors->>'payment_issues' as payment_issues,
    rp.recommended_actions
FROM retention_predictions rp
JOIN students s ON rp.student_id = s.id
WHERE rp.prediction_date = (
    SELECT MAX(prediction_date) FROM retention_predictions
)
ORDER BY rp.intervention_priority DESC;

CREATE OR REPLACE VIEW analytics_dashboard AS
SELECT 
    -- Enrollment metrics
    (SELECT predicted_enrollments FROM enrollment_predictions 
     WHERE prediction_date >= CURRENT_DATE ORDER BY prediction_date DESC LIMIT 1) as predicted_enrollments,
    (SELECT COUNT(*) FROM class_enrollments WHERE enrollment_status = 'active') as current_enrollments,
    
    -- Fee metrics
    (SELECT predicted_collections FROM fee_forecasting 
     WHERE forecast_date >= CURRENT_DATE ORDER BY forecast_date DESC LIMIT 1) as predicted_collections,
    (SELECT COALESCE(SUM(amount_paid), 0) FROM invoices WHERE status = 'paid') as actual_collections,
    
    -- Retention metrics
    (SELECT COUNT(*) FROM retention_predictions WHERE retention_risk = 'critical') as critical_risk_students,
    (SELECT COUNT(*) FROM retention_predictions WHERE retention_risk = 'high') as high_risk_students,
    (SELECT ROUND(AVG(retention_probability), 2) FROM retention_predictions) as avg_retention_probability,
    
    -- Lead metrics
    (SELECT COUNT(*) FROM leads WHERE stage = 'enrolled') as enrolled_leads,
    (SELECT COUNT(*) FROM leads WHERE stage NOT IN ('enrolled', 'lost')) as active_leads,
    
    -- Payment metrics
    (SELECT COUNT(*) FROM debtor_aging WHERE balance_due > 0) as total_debtors,
    (SELECT SUM(balance_due) FROM debtor_aging WHERE balance_due > 0) as total_outstanding;
