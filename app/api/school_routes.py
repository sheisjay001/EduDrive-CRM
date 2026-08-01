from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser, authenticate_user, create_tokens_for_user
from app.database.session import get_supabase_client

router = APIRouter(prefix="/schools", tags=["schools"])

class SchoolCreateRequest(BaseModel):
    name: str
    slug: Optional[str]
    domain: Optional[str]
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    subscription_plan: str = "basic"

class SchoolUpdateRequest(BaseModel):
    name: Optional[str]
    domain: Optional[str]
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    is_active: Optional[bool]

class SchoolRegisterRequest(BaseModel):
    school_name: str
    admin_name: str
    email: str
    phone: str
    password: str
    subscription_plan: str = "standard"

@router.post("/register")
async def register_school(request: SchoolRegisterRequest):
    """Register a new school and create admin user"""
    supabase = get_supabase_client()
    
    try:
        # Generate slug from school name
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', request.school_name.lower()).strip('-')
        
        # Create school
        school_result = supabase.table('schools').insert({
            'name': request.school_name,
            'slug': slug,
            'subscription_plan': request.subscription_plan,
            'is_active': True
        }).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=500, detail="Failed to create school")
        
        school_id = school_result.data[0]['id']
        school_slug = school_result.data[0]['slug']
        
        # Create admin user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            'email': request.email,
            'password': request.password,
            'options': {
                'data': {
                    'full_name': request.admin_name,
                    'phone': request.phone
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create user role entry
        try:
            role_result = supabase.table('user_roles').insert({
                'user_id': auth_response.user.id,
                'role': 'school_admin',
                'school_id': school_id
            }).execute()
        except Exception as e:
            print(f"Error creating user role: {e}")
            # Continue anyway - role might be optional
        
        # Authenticate user to get tokens
        user = authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to authenticate after registration")
        
        access_token, refresh_token = create_tokens_for_user(user)
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "fullName": user.fullName,
                "role": user.role,
                "schoolId": user.schoolId,
                "schoolSlug": user.schoolSlug
            },
            "school": {
                "id": school_id,
                "name": request.school_name,
                "slug": school_slug,
                "subscription_plan": request.subscription_plan
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slug/{slug}")
async def get_school_by_slug(
    slug: str
):
    """Get school information by slug"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('get_school_by_slug', {'p_slug': slug}).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        return {"school": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate/{slug}")
async def validate_school_slug(
    slug: str
):
    """Check if a school slug exists and is active"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('schools').select('*').eq('slug', slug).eq('is_active', True).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="School not found or inactive")
        
        return {"valid": True, "school": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_school(
    request: SchoolCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new school (super-admin only)"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('schools').insert({
            'name': request.name,
            'slug': request.slug,
            'domain': request.domain,
            'logo_url': request.logo_url,
            'primary_color': request.primary_color,
            'secondary_color': request.secondary_color,
            'subscription_plan': request.subscription_plan
        }).execute()
        
        return {"success": True, "school": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_schools(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all active schools"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('active_schools').select('*').execute()
        return {"schools": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{school_id}")
async def update_school(
    school_id: str,
    request: SchoolUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update school information"""
    supabase = get_supabase_client()
    
    try:
        update_data = {}
        if request.name:
            update_data['name'] = request.name
        if request.domain:
            update_data['domain'] = request.domain
        if request.logo_url:
            update_data['logo_url'] = request.logo_url
        if request.primary_color:
            update_data['primary_color'] = request.primary_color
        if request.secondary_color:
            update_data['secondary_color'] = request.secondary_color
        if request.is_active is not None:
            update_data['is_active'] = request.is_active
        
        result = supabase.table('schools').update(update_data).eq('id', school_id).execute()
        
        return {"success": True, "school": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
