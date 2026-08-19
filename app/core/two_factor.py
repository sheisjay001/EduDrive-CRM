import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional, Tuple
from fastapi import HTTPException, status
from app.database.session import get_supabase_client


class TwoFactorAuth:
    """Two-factor authentication using TOTP (Time-based One-Time Password)"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, email: str, issuer: str = "EduDrive CRM") -> str:
        """Generate QR code for TOTP setup and return as base64 string"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name=issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify TOTP token against secret"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 step tolerance
    
    @staticmethod
    async def enable_2fa(user_id: str) -> Tuple[str, str]:
        """Enable 2FA for user and return secret and QR code"""
        supabase = get_supabase_client()
        
        # Generate secret
        secret = TwoFactorAuth.generate_secret()
        
        # Get user email
        user_result = supabase.table('users').select('email').eq('id', user_id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        email = user_result.data[0]['email']
        
        # Generate QR code
        qr_code = TwoFactorAuth.generate_qr_code(secret, email)
        
        # Store secret temporarily (not yet enabled)
        # In production, you'd store this in a separate table with verification status
        await supabase.table('user_2fa').upsert({
            'user_id': user_id,
            'secret': secret,
            'is_enabled': False,
            'verified_at': None
        }).execute()
        
        return secret, qr_code
    
    @staticmethod
    async def verify_and_enable_2fa(user_id: str, token: str) -> bool:
        """Verify token and enable 2FA for user"""
        supabase = get_supabase_client()
        
        # Get stored secret
        result = supabase.table('user_2fa').select('*').eq('user_id', user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="2FA not set up for user")
        
        secret = result.data[0]['secret']
        
        # Verify token
        if not TwoFactorAuth.verify_totp(secret, token):
            raise HTTPException(status_code=400, detail="Invalid token")
        
        # Enable 2FA
        await supabase.table('user_2fa').update({
            'is_enabled': True,
            'verified_at': 'now()'
        }).eq('user_id', user_id).execute()
        
        return True
    
    @staticmethod
    async def disable_2fa(user_id: str, password: str) -> bool:
        """Disable 2FA for user (requires password verification)"""
        supabase = get_supabase_client()
        
        # Verify password first (implementation depends on your auth system)
        # This is a placeholder - implement actual password verification
        
        # Delete or disable 2FA
        await supabase.table('user_2fa').delete().eq('user_id', user_id).execute()
        
        return True
    
    @staticmethod
    async def verify_2fa_login(user_id: str, token: str) -> bool:
        """Verify 2FA token during login"""
        supabase = get_supabase_client()
        
        # Get stored secret
        result = supabase.table('user_2fa').select('*').eq('user_id', user_id).execute()
        if not result.data or not result.data[0]['is_enabled']:
            # 2FA not enabled, allow login
            return True
        
        secret = result.data[0]['secret']
        
        # Verify token
        if not TwoFactorAuth.verify_totp(secret, token):
            raise HTTPException(status_code=400, detail="Invalid 2FA token")
        
        return True
    
    @staticmethod
    async def is_2fa_enabled(user_id: str) -> bool:
        """Check if 2FA is enabled for user"""
        supabase = get_supabase_client()
        
        result = supabase.table('user_2fa').select('is_enabled').eq('user_id', user_id).execute()
        return result.data and result.data[0]['is_enabled']


# Database schema for 2FA (add to your migration)
"""
CREATE TABLE user_2fa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    secret VARCHAR(255) NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX idx_user_2fa_user_id ON user_2fa(user_id);
"""
