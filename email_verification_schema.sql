-- Email Verification Schema
-- Handle email verification for new user registrations

-- Drop table if it exists
DROP TABLE IF EXISTS email_verifications CASCADE;

-- Email verifications table
CREATE TABLE IF NOT EXISTS email_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    verification_token VARCHAR(255) UNIQUE NOT NULL,
    verification_code VARCHAR(10), -- 6-digit code for alternative verification
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    is_verified BOOLEAN DEFAULT false,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 5,
    ip_address VARCHAR(45),
    user_agent TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for email verifications
CREATE INDEX IF NOT EXISTS idx_email_verifications_user_id ON email_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verifications_email ON email_verifications(email);
CREATE INDEX IF NOT EXISTS idx_email_verifications_token ON email_verifications(verification_token);
CREATE INDEX IF NOT EXISTS idx_email_verifications_code ON email_verifications(verification_code);
CREATE INDEX IF NOT EXISTS idx_email_verifications_expires_at ON email_verifications(expires_at);

-- Add email verification tracking to auth.users metadata
-- Note: This will be handled via Supabase auth metadata

-- Function to generate verification token
CREATE OR REPLACE FUNCTION generate_email_verification_token(p_user_id UUID, p_email VARCHAR(255), p_school_id UUID)
RETURNS UUID AS $$
DECLARE
    v_verification_id UUID;
    v_token VARCHAR(255);
    v_code VARCHAR(10);
BEGIN
    -- Generate random token
    v_token := encode(gen_random_bytes(32), 'hex');
    
    -- Generate 6-digit code
    v_code := LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');
    
    -- Create verification record
    INSERT INTO email_verifications (
        user_id, email, verification_token, verification_code,
        expires_at, school_id
    ) VALUES (
        p_user_id, p_email, v_token, v_code,
        NOW() + INTERVAL '24 hours', p_school_id
    ) RETURNING id INTO v_verification_id;
    
    RETURN v_verification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to verify email with token
CREATE OR REPLACE FUNCTION verify_email_token(p_token VARCHAR(255))
RETURNS BOOLEAN AS $$
DECLARE
    v_verification RECORD;
BEGIN
    -- Get verification record
    SELECT * INTO v_verification
    FROM email_verifications
    WHERE verification_token = p_token
    AND is_verified = false
    AND expires_at > NOW();
    
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    
    -- Check max attempts
    IF v_verification.attempts >= v_verification.max_attempts THEN
        RETURN false;
    END IF;
    
    -- Mark as verified
    UPDATE email_verifications
    SET 
        is_verified = true,
        verified_at = NOW(),
        attempts = attempts + 1
    WHERE id = v_verification.id;
    
    -- Update user metadata in auth.users
    -- This would typically be done via Supabase auth admin API
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Function to verify email with code
CREATE OR REPLACE FUNCTION verify_email_code(p_email VARCHAR(255), p_code VARCHAR(10))
RETURNS BOOLEAN AS $$
DECLARE
    v_verification RECORD;
BEGIN
    -- Get verification record
    SELECT * INTO v_verification
    FROM email_verifications
    WHERE email = p_email
    AND verification_code = p_code
    AND is_verified = false
    AND expires_at > NOW();
    
    IF NOT FOUND THEN
        -- Increment attempts
        UPDATE email_verifications
        SET attempts = attempts + 1
        WHERE email = p_email
        AND is_verified = false
        AND expires_at > NOW();
        
        RETURN false;
    END IF;
    
    -- Check max attempts
    IF v_verification.attempts >= v_verification.max_attempts THEN
        RETURN false;
    END IF;
    
    -- Mark as verified
    UPDATE email_verifications
    SET 
        is_verified = true,
        verified_at = NOW(),
        attempts = attempts + 1
    WHERE id = v_verification.id;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Function to resend verification email
CREATE OR REPLACE FUNCTION resend_verification_email(p_user_id UUID, p_email VARCHAR(255), p_school_id UUID)
RETURNS UUID AS $$
DECLARE
    v_verification_id UUID;
BEGIN
    -- Invalidate existing tokens
    UPDATE email_verifications
    SET is_verified = true, verified_at = NOW()
    WHERE user_id = p_user_id
    AND is_verified = false
    
    -- Generate new token
    v_verification_id := generate_email_verification_token(p_user_id, p_email, p_school_id);
    
    RETURN v_verification_id;
END;
$$ LANGUAGE plpgsql;

-- View for verification statistics
CREATE OR REPLACE VIEW email_verification_stats AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as total_verifications,
    COUNT(*) FILTER (WHERE is_verified = true) as verified,
    COUNT(*) FILTER (WHERE is_verified = false AND expires_at < NOW()) as expired,
    COUNT(*) FILTER (WHERE is_verified = false AND expires_at > NOW()) as pending,
    ROUND(COUNT(*) FILTER (WHERE is_verified = true)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as verification_rate
FROM email_verifications
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;
