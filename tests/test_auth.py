import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import authenticate_user, create_access_token, decode_token


client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints and functions"""
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@greenfieldcollege.ng",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@greenfieldcollege.ng",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@greenfieldcollege.ng"}
        )
        assert response.status_code == 422
    
    def test_token_refresh(self):
        """Test token refresh endpoint"""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@greenfieldcollege.ng",
                "password": "password123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_forgot_password(self):
        """Test forgot password endpoint"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "admin@greenfieldcollege.ng"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestTokenFunctions:
    """Test token creation and validation functions"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        token = create_access_token("test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        token = create_access_token("test@example.com")
        payload = decode_token(token)
        assert payload["sub"] == "test@example.com"
        assert payload["token_type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        with pytest.raises(Exception):  # HTTPException
            decode_token("invalid_token")


class TestPermissions:
    """Test permission checking system"""
    
    def test_super_admin_permissions(self):
        """Test super admin has all permissions"""
        from app.core.auth import has_permission, AuthUser
        
        user = AuthUser(
            id="test-id",
            schoolId="test-school",
            role="super_admin",
            fullName="Test Admin",
            email="admin@test.com"
        )
        
        assert has_permission(user, "dashboard:view") == True
        assert has_permission(user, "any:permission") == True
    
    def test_school_admin_permissions(self):
        """Test school admin permissions"""
        from app.core.auth import has_permission, AuthUser
        
        user = AuthUser(
            id="test-id",
            schoolId="test-school",
            role="school_admin",
            fullName="Test Admin",
            email="admin@test.com"
        )
        
        assert has_permission(user, "dashboard:view") == True
        assert has_permission(user, "students:view") == True
        assert has_permission(user, "finance:view") == True
        assert has_permission(user, "any:permission") == False
    
    def test_teacher_permissions(self):
        """Test teacher permissions"""
        from app.core.auth import has_permission, AuthUser
        
        user = AuthUser(
            id="test-id",
            schoolId="test-school",
            role="teacher",
            fullName="Test Teacher",
            email="teacher@test.com"
        )
        
        assert has_permission(user, "students:view") == True
        assert has_permission(user, "attendance:view") == True
        assert has_permission(user, "finance:view") == False
        assert has_permission(user, "settings:view") == False
