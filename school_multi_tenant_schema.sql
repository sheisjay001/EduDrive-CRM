-- Multi-Tenant School Schema
-- Adds school slug/identifier for unique school URLs and pricing tiers

-- Add school slug to schools table
ALTER TABLE schools ADD COLUMN IF NOT EXISTS slug VARCHAR(100) UNIQUE NOT NULL;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS domain VARCHAR(255) UNIQUE; -- Custom domain (optional)
ALTER TABLE schools ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);
ALTER TABLE schools ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#3B82F6';
ALTER TABLE schools ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#1E40AF';
ALTER TABLE schools ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(50) DEFAULT 'basic'; -- 'basic', 'standard', 'enterprise'
ALTER TABLE schools ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS max_students INTEGER DEFAULT 150;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS max_staff INTEGER DEFAULT 20;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS payment_gateway_enabled BOOLEAN DEFAULT false;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS whatsapp_api_enabled BOOLEAN DEFAULT false;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS automated_reminders_enabled BOOLEAN DEFAULT false;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS digital_receipts_enabled BOOLEAN DEFAULT false;

-- Create index on slug for fast lookups
CREATE INDEX IF NOT EXISTS idx_schools_slug ON schools(slug);
CREATE INDEX IF NOT EXISTS idx_schools_domain ON schools(domain);

-- Function to generate unique slug from school name
CREATE OR REPLACE FUNCTION generate_school_slug(p_school_name VARCHAR(255))
RETURNS VARCHAR(100) AS $$
DECLARE
    v_slug VARCHAR(100);
    v_counter INTEGER := 1;
BEGIN
    -- Convert to lowercase, replace spaces with hyphens, remove special chars
    v_slug := lower(regexp_replace(p_school_name, '[^a-zA-Z0-9\s-]', '', 'g'));
    v_slug := regexp_replace(v_slug, '\s+', '-', 'g');
    v_slug := regexp_replace(v_slug, '-+', '-', 'g');
    v_slug := trim(v_slug, '-');
    
    -- Ensure uniqueness
    WHILE EXISTS (SELECT 1 FROM schools WHERE slug = v_slug) LOOP
        v_slug := lower(regexp_replace(p_school_name, '[^a-zA-Z0-9\s-]', '', 'g'));
        v_slug := regexp_replace(v_slug, '\s+', '-', 'g');
        v_slug := v_slug || '-' || v_counter;
        v_counter := v_counter + 1;
    END LOOP;
    
    RETURN v_slug;
END;
$$ LANGUAGE plpgsql;

-- Function to get school by slug
CREATE OR REPLACE FUNCTION get_school_by_slug(p_slug VARCHAR(100))
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    slug VARCHAR(100),
    domain VARCHAR(255),
    logo_url VARCHAR(500),
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    is_active BOOLEAN,
    subscription_plan VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id, name, slug, domain, logo_url, primary_color, secondary_color, is_active, subscription_plan
    FROM schools
    WHERE slug = p_slug AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to validate school access
CREATE OR REPLACE FUNCTION validate_school_access(p_user_id UUID, p_school_slug VARCHAR(100))
RETURNS BOOLEAN AS $$
DECLARE
    v_user_school_id UUID;
    v_school_id UUID;
BEGIN
    -- Get user's school_id
    SELECT school_id INTO v_user_school_id
    FROM user_roles
    WHERE user_id = p_user_id;
    
    -- Get school_id from slug
    SELECT id INTO v_school_id
    FROM schools
    WHERE slug = p_school_slug;
    
    -- Check if user belongs to this school
    RETURN v_user_school_id = v_school_id;
END;
$$ LANGUAGE plpgsql;

-- View for active schools with their slugs
CREATE OR REPLACE VIEW active_schools AS
SELECT 
    id,
    name,
    slug,
    domain,
    logo_url,
    primary_color,
    secondary_color,
    subscription_plan,
    max_students,
    max_staff,
    created_at
FROM schools
WHERE is_active = true
ORDER BY name;

-- Trigger to auto-generate slug on school creation
CREATE OR REPLACE FUNCTION trigger_generate_school_slug()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.slug IS NULL OR NEW.slug = '' THEN
        NEW.slug := generate_school_slug(NEW.name);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_school_slug ON schools;
CREATE TRIGGER trigger_school_slug
    BEFORE INSERT ON schools
    FOR EACH ROW
    EXECUTE FUNCTION trigger_generate_school_slug();
