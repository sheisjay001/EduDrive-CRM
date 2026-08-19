-- User Administration Interface Schema
-- Comprehensive user management for school administrators

-- Drop tables if they exist
DROP TABLE IF EXISTS user_permissions CASCADE;
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS user_audit_logs CASCADE;

-- User permissions table
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    permission_name VARCHAR(100) NOT NULL,
    permission_category VARCHAR(50), -- 'finance', 'admissions', 'academic', 'admin', 'reports'
    can_create BOOLEAN DEFAULT false,
    can_read BOOLEAN DEFAULT false,
    can_update BOOLEAN DEFAULT false,
    can_delete BOOLEAN DEFAULT false,
    granted_by UUID REFERENCES auth.users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user permissions
CREATE INDEX IF NOT EXISTS idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_permission_name ON user_permissions(permission_name);
CREATE INDEX IF NOT EXISTS idx_user_permissions_category ON user_permissions(permission_category);
CREATE INDEX IF NOT EXISTS idx_user_permissions_school_id ON user_permissions(school_id);

-- Role permissions table (template permissions for roles)
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role VARCHAR(50) NOT NULL, -- 'school_admin', 'staff', 'teacher', 'parent', 'student'
    permission_name VARCHAR(100) NOT NULL,
    permission_category VARCHAR(50),
    can_create BOOLEAN DEFAULT false,
    can_read BOOLEAN DEFAULT false,
    can_update BOOLEAN DEFAULT false,
    can_delete BOOLEAN DEFAULT false,
    is_default BOOLEAN DEFAULT true,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for role permissions
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_name ON role_permissions(permission_name);
CREATE INDEX IF NOT EXISTS idx_role_permissions_school_id ON role_permissions(school_id);

-- User audit logs (enhanced from activity_logs)
CREATE TABLE IF NOT EXISTS user_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    user_name VARCHAR(255),
    user_role VARCHAR(50),
    action_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    action_details JSONB,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    action_result VARCHAR(20), -- 'success', 'failure', 'partial'
    error_message TEXT,
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user audit logs
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_user_id ON user_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_action_type ON user_audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_entity ON user_audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_school_id ON user_audit_logs(school_id);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_created_at ON user_audit_logs(created_at DESC);

-- Function to grant user permission
CREATE OR REPLACE FUNCTION grant_user_permission(
    p_user_id UUID,
    p_permission_name VARCHAR(100),
    p_permission_category VARCHAR(50),
    p_can_create BOOLEAN,
    p_can_read BOOLEAN,
    p_can_update BOOLEAN,
    p_can_delete BOOLEAN,
    p_granted_by UUID,
    p_expires_at TIMESTAMP WITH TIME ZONE,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_permission_id UUID;
BEGIN
    INSERT INTO user_permissions (
        user_id, permission_name, permission_category,
        can_create, can_read, can_update, can_delete,
        granted_by, expires_at, school_id
    ) VALUES (
        p_user_id, p_permission_name, p_permission_category,
        p_can_create, p_can_read, p_can_update, p_can_delete,
        p_granted_by, p_expires_at, p_school_id
    ) RETURNING id INTO v_permission_id;
    
    RETURN v_permission_id;
END;
$$ LANGUAGE plpgsql;

-- Function to revoke user permission
CREATE OR REPLACE FUNCTION revoke_user_permission(p_user_id UUID, p_permission_name VARCHAR(100))
RETURNS VOID AS $$
BEGIN
    UPDATE user_permissions
    SET is_active = false
    WHERE user_id = p_user_id
    AND permission_name = p_permission_name;
END;
$$ LANGUAGE plpgsql;

-- Function to check user permission
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id UUID,
    p_permission_name VARCHAR(100),
    p_required_action VARCHAR(10) -- 'create', 'read', 'update', 'delete'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN;
BEGIN
    SELECT CASE p_required_action
        WHEN 'create' THEN can_create
        WHEN 'read' THEN can_read
        WHEN 'update' THEN can_update
        WHEN 'delete' THEN can_delete
        ELSE false
    END INTO v_has_permission
    FROM user_permissions
    WHERE user_id = p_user_id
    AND permission_name = p_permission_name
    AND is_active = true
    AND (expires_at IS NULL OR expires_at > NOW())
    LIMIT 1;
    
    RETURN COALESCE(v_has_permission, false);
END;
$$ LANGUAGE plpgsql;

-- Function to log user action
CREATE OR REPLACE FUNCTION log_user_action(
    p_user_id UUID,
    p_user_name VARCHAR(255),
    p_user_role VARCHAR(50),
    p_action_type VARCHAR(100),
    p_entity_type VARCHAR(100),
    p_entity_id UUID,
    p_action_details JSONB,
    p_old_values JSONB,
    p_new_values JSONB,
    p_ip_address VARCHAR(45),
    p_user_agent TEXT,
    p_action_result VARCHAR(20),
    p_error_message TEXT,
    p_school_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO user_audit_logs (
        user_id, user_name, user_role, action_type, entity_type, entity_id,
        action_details, old_values, new_values, ip_address, user_agent,
        action_result, error_message, school_id
    ) VALUES (
        p_user_id, p_user_name, p_user_role, p_action_type, p_entity_type, p_entity_id,
        p_action_details, p_old_values, p_new_values, p_ip_address, p_user_agent,
        p_action_result, p_error_message, p_school_id
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Function to apply role permissions to user
CREATE OR REPLACE FUNCTION apply_role_permissions(p_user_id UUID, p_role VARCHAR(50), p_school_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_applied_count INTEGER;
BEGIN
    -- Remove existing custom permissions
    DELETE FROM user_permissions WHERE user_id = p_user_id;
    
    -- Copy role permissions to user
    INSERT INTO user_permissions (
        user_id, permission_name, permission_category,
        can_create, can_read, can_update, can_delete, school_id
    )
    SELECT 
        p_user_id, permission_name, permission_category,
        can_create, can_read, can_update, can_delete, p_school_id
    FROM role_permissions
    WHERE role = p_role
    AND school_id = p_school_id;
    
    GET DIAGNOSTICS v_applied_count = ROW_COUNT;
    
    RETURN v_applied_count;
END;
$$ LANGUAGE plpgsql;

-- Views for user administration
CREATE OR REPLACE VIEW user_permissions_summary AS
SELECT 
    u.id as user_id,
    u.email,
    ur.role,
    up.permission_category,
    COUNT(*) FILTER (WHERE up.can_create = true) as create_permissions,
    COUNT(*) FILTER (WHERE up.can_read = true) as read_permissions,
    COUNT(*) FILTER (WHERE up.can_update = true) as update_permissions,
    COUNT(*) FILTER (WHERE up.can_delete = true) as delete_permissions,
    COUNT(*) as total_permissions
FROM auth.users u
JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN user_permissions up ON u.id = up.user_id AND up.is_active = true
GROUP BY u.id, u.email, ur.role, up.permission_category
ORDER BY u.email;

CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    user_id,
    user_name,
    user_role,
    COUNT(*) as total_actions,
    COUNT(*) FILTER (WHERE action_result = 'success') as successful_actions,
    COUNT(*) FILTER (WHERE action_result = 'failure') as failed_actions,
    MAX(created_at) as last_action,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as actions_last_24h,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as actions_last_7d
FROM user_audit_logs
GROUP BY user_id, user_name, user_role
ORDER BY total_actions DESC;

CREATE OR REPLACE VIEW role_permission_matrix AS
SELECT 
    role,
    permission_category,
    STRING_AGG(
        CASE 
            WHEN can_create THEN 'C' 
            WHEN can_read THEN 'R' 
            WHEN can_update THEN 'U' 
            WHEN can_delete THEN 'D' 
            ELSE '-' 
        END, ''
    ) as permissions
FROM role_permissions
GROUP BY role, permission_category
ORDER BY role, permission_category;
