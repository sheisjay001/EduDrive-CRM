-- Device and Session Tracking Schema
-- Track user sessions and devices for security

-- Drop tables if they exist
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS user_devices CASCADE;

-- User devices table
CREATE TABLE IF NOT EXISTS user_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- 'desktop', 'mobile', 'tablet'
    device_brand VARCHAR(100),
    device_model VARCHAR(100),
    os_name VARCHAR(100),
    os_version VARCHAR(50),
    browser_name VARCHAR(100),
    browser_version VARCHAR(50),
    user_agent TEXT,
    is_trusted BOOLEAN DEFAULT false,
    last_seen_at TIMESTAMP WITH TIME ZONE,
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user devices
CREATE INDEX IF NOT EXISTS idx_user_devices_user_id ON user_devices(user_id);
CREATE INDEX IF NOT EXISTS idx_user_devices_is_trusted ON user_devices(is_trusted);
CREATE INDEX IF NOT EXISTS idx_user_devices_school_id ON user_devices(school_id);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id UUID REFERENCES user_devices(id) ON DELETE SET NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    location_country VARCHAR(100),
    location_city VARCHAR(100),
    login_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    logout_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    session_duration_seconds INTEGER,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_device_id ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_school_id ON user_sessions(school_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_login_at ON user_sessions(login_at DESC);

-- Function to log user session
CREATE OR REPLACE FUNCTION log_user_session(
    p_user_id UUID,
    p_session_token VARCHAR(255),
    p_refresh_token VARCHAR(255),
    p_ip_address VARCHAR(45),
    p_user_agent TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_device_id UUID;
    v_device_name VARCHAR(255);
    v_device_type VARCHAR(50);
    v_session_id UUID;
BEGIN
    -- Parse user agent to determine device type
    p_user_agent := COALESCE(p_user_agent, '');
    
    IF p_user_agent ~* 'Mobile|Android|iPhone' THEN
        v_device_type := 'mobile';
    ELSIF p_user_agent ~* 'Tablet|iPad' THEN
        v_device_type := 'tablet';
    ELSE
        v_device_type := 'desktop';
    END IF;
    
    -- Generate device name
    v_device_name := v_device_type || ' - ' || SUBSTRING(p_user_agent FROM 1 FOR 50);
    
    -- Check if device already exists
    SELECT id INTO v_device_id
    FROM user_devices
    WHERE user_id = p_user_id
    AND user_agent = p_user_agent
    LIMIT 1;
    
    -- Create device if not exists
    IF v_device_id IS NULL THEN
        INSERT INTO user_devices (
            user_id, device_name, device_type, user_agent, 
            last_seen_at, school_id
        ) VALUES (
            p_user_id, v_device_name, v_device_type, p_user_agent,
            NOW(), p_school_id
        ) RETURNING id INTO v_device_id;
    ELSE
        -- Update last seen
        UPDATE user_devices
        SET last_seen_at = NOW()
        WHERE id = v_device_id;
    END IF;
    
    -- Create session
    INSERT INTO user_sessions (
        user_id, device_id, session_token, refresh_token,
        ip_address, user_agent, school_id
    ) VALUES (
        p_user_id, v_device_id, p_session_token, p_refresh_token,
        p_ip_address, p_user_agent, p_school_id
    ) RETURNING id INTO v_session_id;
    
    RETURN v_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update session activity
CREATE OR REPLACE FUNCTION update_session_activity(p_session_token VARCHAR(255))
RETURNS VOID AS $$
BEGIN
    UPDATE user_sessions
    SET last_activity_at = NOW()
    WHERE session_token = p_session_token
    AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to logout session
CREATE OR REPLACE FUNCTION logout_session(p_session_token VARCHAR(255))
RETURNS VOID AS $$
DECLARE
    v_login_at TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get login time
    SELECT login_at INTO v_login_at
    FROM user_sessions
    WHERE session_token = p_session_token;
    
    -- Update session
    UPDATE user_sessions
    SET 
        is_active = false,
        logout_at = NOW(),
        session_duration_seconds = EXTRACT(EPOCH FROM (NOW() - v_login_at))::INTEGER
    WHERE session_token = p_session_token;
END;
$$ LANGUAGE plpgsql;

-- Function to revoke all user sessions except current
CREATE OR REPLACE FUNCTION revoke_other_sessions(p_user_id UUID, p_current_session_token VARCHAR(255))
RETURNS INTEGER AS $$
DECLARE
    v_revoked_count INTEGER;
BEGIN
    UPDATE user_sessions
    SET is_active = false, logout_at = NOW()
    WHERE user_id = p_user_id
    AND session_token != p_current_session_token
    AND is_active = true;
    
    GET DIAGNOSTICS v_revoked_count = ROW_COUNT;
    
    RETURN v_revoked_count;
END;
$$ LANGUAGE plpgsql;

-- Function to trust device
CREATE OR REPLACE FUNCTION trust_device(p_user_id UUID, p_device_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE user_devices
    SET is_trusted = true
    WHERE id = p_device_id
    AND user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- View for active sessions
CREATE OR REPLACE VIEW active_user_sessions AS
SELECT 
    us.id,
    us.user_id,
    u.email,
    ud.device_name,
    ud.device_type,
    us.ip_address,
    us.location_country,
    us.location_city,
    us.login_at,
    us.last_activity_at,
    EXTRACT(EPOCH FROM (NOW() - us.login_at)) / 3600 as session_hours,
    ud.is_trusted
FROM user_sessions us
JOIN auth.users u ON us.user_id = u.id
JOIN user_devices ud ON us.device_id = ud.id
WHERE us.is_active = true
ORDER BY us.last_activity_at DESC;

-- View for session analytics
CREATE OR REPLACE VIEW session_analytics AS
SELECT 
    DATE_TRUNC('day', login_at) as date,
    COUNT(*) as total_sessions,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(session_duration_seconds) / 3600 as avg_session_hours,
    COUNT(*) FILTER (WHERE device_type = 'mobile') as mobile_sessions,
    COUNT(*) FILTER (WHERE device_type = 'desktop') as desktop_sessions,
    COUNT(*) FILTER (WHERE device_type = 'tablet') as tablet_sessions
FROM user_sessions
WHERE logout_at IS NOT NULL
GROUP BY DATE_TRUNC('day', login_at)
ORDER BY date DESC;
