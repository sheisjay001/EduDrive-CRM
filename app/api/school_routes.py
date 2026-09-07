from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser, authenticate_user, create_tokens_for_user
from app.database.session import get_supabase_client
from app.core.config import settings
import httpx
import secrets

router = APIRouter(prefix="/schools", tags=["schools"])

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price": 50000,  # 50,000 NGN in kobo
        "currency": "NGN",
        "features": ["Up to 100 students", "Basic reporting", "Email support"],
        "duration": "monthly"
    },
    "standard": {
        "name": "Standard",
        "price": 150000,  # 150,000 NGN in kobo
        "currency": "NGN",
        "features": ["Up to 500 students", "Advanced reporting", "Priority support", "SMS notifications"],
        "duration": "monthly"
    },
    "premium": {
        "name": "Premium",
        "price": 300000,  # 300,000 NGN in kobo
        "currency": "NGN",
        "features": ["Unlimited students", "Custom integrations", "24/7 support", "Advanced analytics", "White-label option"],
        "duration": "monthly"
    }
}

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
    payment_method: str = "paystack"  # paystack, flutterwave, bank_transfer
    payment_reference: Optional[str] = None  # For pre-paid registrations

class PaymentInitRequest(BaseModel):
    email: str
    subscription_plan: str
    payment_method: str = "paystack"

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {"plans": SUBSCRIPTION_PLANS}

@router.post("/payments/initialize")
async def initialize_subscription_payment(request: PaymentInitRequest):
    """Initialize payment for school subscription"""
    if request.subscription_plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    plan = SUBSCRIPTION_PLANS[request.subscription_plan]
    
    if request.payment_method == "paystack":
        paystack_secret_key = settings.paystack_secret_key
        
        if not paystack_secret_key:
            raise HTTPException(status_code=500, detail="Paystack not configured")
        
        reference = f"EDU-{secrets.token_hex(8)}"
        
        payload = {
            "email": request.email,
            "amount": plan["price"],  # Amount in kobo
            "reference": reference,
            "metadata": {
                "subscription_plan": request.subscription_plan,
                "plan_name": plan["name"],
                "currency": plan["currency"],
                "duration": plan["duration"]
            },
            "callback_url": f"{settings.api_prefix}/schools/payments/verify/{reference}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.paystack.co/transaction/initialize",
                json=payload,
                headers={
                    "Authorization": f"Bearer {paystack_secret_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to initialize payment")
            
            return response.json()
    
    elif request.payment_method == "flutterwave":
        flutterwave_secret_key = settings.flutterwave_secret_key
        
        if not flutterwave_secret_key:
            raise HTTPException(status_code=500, detail="Flutterwave not configured")
        
        tx_ref = f"EDU-{secrets.token_hex(8)}"
        
        payload = {
            "tx_ref": tx_ref,
            "amount": plan["price"] / 100,  # Convert from kobo to naira
            "currency": plan["currency"],
            "email": request.email,
            "customer": {"email": request.email},
            "meta": {
                "subscription_plan": request.subscription_plan,
                "plan_name": plan["name"]
            },
            "redirect_url": f"{settings.api_prefix}/schools/payments/verify/{tx_ref}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.flutterwave.com/v3/payments",
                json=payload,
                headers={
                    "Authorization": f"Bearer {flutterwave_secret_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to initialize payment")
            
            return response.json()
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")

@router.get("/payments/verify/{reference}")
async def verify_subscription_payment(reference: str):
    """Verify subscription payment and complete school registration"""
    supabase = get_supabase_client()
    
    try:
        # Verify payment with Paystack
        paystack_secret_key = settings.paystack_secret_key
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.paystack.co/transaction/verify/{reference}",
                headers={
                    "Authorization": f"Bearer {paystack_secret_key}"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to verify payment")
            
            payment_data = response.json()
            
            if not payment_data.get("data", {}).get("status") == "success":
                raise HTTPException(status_code=400, detail="Payment not successful")
            
            # Extract metadata
            metadata = payment_data["data"]["metadata"]
            subscription_plan = metadata.get("subscription_plan", "standard")
            email = payment_data["data"]["customer"]["email"]
            amount_paid = payment_data["data"]["amount"]
            
            # Store payment record
            payment_result = supabase.table('payments').insert({
                'reference': reference,
                'amount': amount_paid / 100,  # Convert to naira
                'payment_method': 'paystack',
                'status': 'completed',
                'payment_date': payment_data["data"]["paid_at"],
                'metadata': metadata
            }).execute()
            
            return {
                "success": True,
                "payment": payment_result.data[0],
                "subscription_plan": subscription_plan,
                "message": "Payment verified successfully. Complete registration with /schools/register endpoint."
            }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Payment verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register_school(request: SchoolRegisterRequest):
    """Register a new school and create admin user"""
    supabase = get_supabase_client()
    
    try:
        # Verify payment if reference is provided
        if request.payment_reference:
            payment_verification = await verify_subscription_payment(request.payment_reference)
            if not payment_verification.get("success"):
                raise HTTPException(status_code=400, detail="Payment verification failed")
            
            # Verify the subscription plan matches
            if payment_verification.get("subscription_plan") != request.subscription_plan:
                raise HTTPException(status_code=400, detail="Subscription plan mismatch")
        
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
        
        # Link payment to school if reference was provided
        if request.payment_reference:
            try:
                supabase.table('payments').update({
                    'school_id': school_id
                }).eq('reference', request.payment_reference).execute()
            except Exception as e:
                print(f"Error linking payment to school: {e}")
        
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
        result = supabase.table('schools').select('*').eq('slug', slug).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        return {"school": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching school by slug: {e}")
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
