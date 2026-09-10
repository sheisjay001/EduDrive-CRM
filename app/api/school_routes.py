from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import secrets
import httpx
import uuid

from app.core.config import settings
from app.database.session import get_db
from app.core.auth import get_password_hash, authenticate_user, create_tokens_for_user

router = APIRouter(prefix="/schools", tags=["schools"])

# Pricing configuration
PRICE_PER_PERSON = 1000  # 1,000 NGN per person (student or teacher)

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
    student_count: int = 0  # Number of students to onboard
    teacher_count: int = 0  # Number of teachers to onboard
    payment_method: str = "paystack"  # paystack, flutterwave, bank_transfer
    payment_reference: Optional[str] = None  # For pre-paid registrations

class PaymentInitRequest(BaseModel):
    email: str
    student_count: int = 0
    teacher_count: int = 0
    payment_method: str = "paystack"

@router.get("/pricing-info")
async def get_pricing_info():
    """Get pricing information for school registration"""
    return {
        "price_per_person": PRICE_PER_PERSON,
        "currency": "NGN",
        "description": "Pricing is based on the total number of students and teachers",
        "formula": "Total Price = (Student Count + Teacher Count) × ₦1,000"
    }

@router.post("/payments/initialize")
async def initialize_subscription_payment(request: PaymentInitRequest):
    """Initialize payment for school subscription based on student/teacher count"""
    # Calculate total amount
    total_persons = request.student_count + request.teacher_count
    total_amount_naira = total_persons * PRICE_PER_PERSON
    total_amount_kobo = total_amount_naira * 100  # Convert to kobo for Paystack
    
    if total_amount_kobo == 0:
        raise HTTPException(status_code=400, detail="Student and teacher counts cannot both be zero")
    
    if request.payment_method == "paystack":
        paystack_secret_key = settings.paystack_secret_key
        
        if not paystack_secret_key:
            raise HTTPException(status_code=500, detail="Paystack not configured")
        
        reference = f"EDU-{secrets.token_hex(8)}"
        
        payload = {
            "email": request.email,
            "amount": total_amount_kobo,
            "reference": reference,
            "metadata": {
                "student_count": request.student_count,
                "teacher_count": request.teacher_count,
                "total_persons": total_persons,
                "price_per_person": PRICE_PER_PERSON,
                "total_amount": total_amount_naira,
                "currency": "NGN"
            },
            "callback_url": f"{settings.frontend_url}/signup?reference={reference}"
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
            "amount": total_amount_naira,
            "currency": "NGN",
            "email": request.email,
            "customer": {"email": request.email},
            "meta": {
                "student_count": request.student_count,
                "teacher_count": request.teacher_count,
                "total_persons": total_persons,
                "price_per_person": PRICE_PER_PERSON
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
    db = get_db()
    cursor = db.cursor()
    
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
            student_count = metadata.get("student_count", 0)
            teacher_count = metadata.get("teacher_count", 0)
            total_persons = metadata.get("total_persons", 0)
            total_amount = metadata.get("total_amount", 0)
            email = payment_data["data"]["customer"]["email"]
            amount_paid = payment_data["data"]["amount"]
            
            # Store payment record
            payment_id = str(uuid.uuid4())
            payment_query = """
                INSERT INTO payments (id, reference, amount, status, student_count, teacher_count, total_persons, total_amount, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(payment_query, (payment_id, reference, amount_paid / 100, 'completed', student_count, teacher_count, total_persons, total_amount))
            db.commit()
            
            return {
                "success": True,
                "payment": {"id": payment_id, "reference": reference},
                "student_count": student_count,
                "teacher_count": teacher_count,
                "total_persons": total_persons,
                "total_amount": total_amount,
                "message": "Payment verified successfully. Complete registration with /schools/register endpoint."
            }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Payment verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.post("/register")
async def register_school(request: SchoolRegisterRequest):
    """Register a new school and create admin user"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Verify payment if reference is provided
        if request.payment_reference:
            payment_verification = await verify_subscription_payment(request.payment_reference)
            if not payment_verification.get("success"):
                raise HTTPException(status_code=400, detail="Payment verification failed")
            
            # Verify the counts match
            if payment_verification.get("student_count") != request.student_count:
                raise HTTPException(status_code=400, detail="Student count mismatch")
            if payment_verification.get("teacher_count") != request.teacher_count:
                raise HTTPException(status_code=400, detail="Teacher count mismatch")
        
        # Generate slug from school name
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', request.school_name.lower()).strip('-')
        
        # Generate UUIDs
        school_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        user_role_id = str(uuid.uuid4())
        
        # Create school
        school_query = """
            INSERT INTO schools (id, name, slug, subscription_plan, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(school_query, (school_id, request.school_name, slug, 'custom', True))
        
        # Create admin user with hashed password
        password_hash = get_password_hash(request.password)
        user_query = """
            INSERT INTO users (id, school_id, full_name, email, password_hash, phone, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(user_query, (user_id, school_id, request.admin_name, request.email, password_hash, request.phone, True))
        
        # Create user role entry
        role_query = """
            INSERT INTO user_roles (id, user_id, role, school_id, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(role_query, (user_role_id, user_id, 'school_admin', school_id))
        
        # Link payment to school if reference was provided
        if request.payment_reference:
            update_payment_query = """
                UPDATE payments SET school_id = %s WHERE reference = %s
            """
            cursor.execute(update_payment_query, (school_id, request.payment_reference))
        
        db.commit()
        
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
                "slug": slug,
                "subscription_plan": "custom",
                "student_count": request.student_count,
                "teacher_count": request.teacher_count
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/slug/{slug}")
async def get_school_by_slug(
    slug: str
):
    """Get school information by slug"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "SELECT * FROM schools WHERE slug = %s"
        cursor.execute(query, (slug,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="School not found")
        
        return {"school": result}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching school by slug: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/validate/{slug}")
async def validate_school_slug(
    slug: str
):
    """Check if a school slug exists and is active"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "SELECT * FROM schools WHERE slug = %s AND is_active = TRUE"
        cursor.execute(query, (slug,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="School not found or inactive")
        
        return {"valid": True, "school": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.post("/")
async def create_school(
    request: SchoolCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new school (super-admin only)"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        school_id = str(uuid.uuid4())
        query = """
            INSERT INTO schools (id, name, slug, domain, logo_url, primary_color, secondary_color, subscription_plan, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            school_id, request.name, request.slug, request.domain,
            request.logo_url, request.primary_color, request.secondary_color, request.subscription_plan
        ))
        db.commit()
        
        return {"success": True, "school": {"id": school_id}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/")
async def get_schools(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all active schools"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "SELECT * FROM schools WHERE status = 'active'"
        cursor.execute(query)
        result = cursor.fetchall()
        return {"schools": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.patch("/{school_id}")
async def update_school(
    school_id: str,
    request: SchoolUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update school information"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        update_data = {}
        if request.name is not None:
            update_data['name'] = request.name
        if request.slug is not None:
            update_data['slug'] = request.slug
        if request.domain is not None:
            update_data['domain'] = request.domain
        if request.logo_url is not None:
            update_data['logo_url'] = request.logo_url
        if request.primary_color is not None:
            update_data['primary_color'] = request.primary_color
        if request.secondary_color is not None:
            update_data['secondary_color'] = request.secondary_color
        if request.subscription_plan is not None:
            update_data['subscription_plan'] = request.subscription_plan
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
        values = list(update_data.values()) + [school_id]
        
        query = f"UPDATE schools SET {set_clause} WHERE id = %s"
        cursor.execute(query, values)
        db.commit()
        
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
