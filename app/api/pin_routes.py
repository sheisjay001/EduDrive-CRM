from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import random

from app.core.auth import get_current_user, require_role
from app.database.session import get_supabase_client

router = APIRouter()


# Pydantic Models
class PINGenerateRequest(BaseModel):
    quantity: int = 1


class PINResponse(BaseModel):
    id: int
    pin_code: str
    serial_number: str
    status: str
    student_id: Optional[int]
    usage_count: int
    max_usage: int
    created_at: str


class PINVerifyRequest(BaseModel):
    pin_code: str
    serial_number: str


class PINVerifyResponse(BaseModel):
    valid: bool
    message: str
    student_id: Optional[int]


# Helper function to generate random PIN
def generate_pin():
    """Generate a 12-digit PIN (4 groups of 3 digits)"""
    return ''.join([str(random.randint(1000, 9999)) for _ in range(3)])


# Helper function to generate serial number
def generate_serial_number(index: int):
    """Generate serial number in format: TISM-YYMMDDHHMM-XXX"""
    from datetime import datetime
    batch_prefix = datetime.now().strftime('%y%m%d%H%M')
    return f'TISM-{batch_prefix}-{str(index + 1).zfill(3)}'


# Admin: Generate PINs
@router.post("/pins/generate", response_model=List[PINResponse])
async def generate_pins(
    request: PINGenerateRequest,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    if request.quantity < 1 or request.quantity > 100:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 100")
    
    try:
        pins_to_create = []
        for i in range(request.quantity):
            pin_code = generate_pin()
            serial_number = generate_serial_number(i)
            
            pins_to_create.append({
                "pin_code": pin_code,
                "serial_number": serial_number,
                "status": "unused",
                "usage_count": 0,
                "max_usage": 5
            })
        
        result = supabase.table("pins").insert(pins_to_create).execute()
        
        return [
            PINResponse(
                id=pin["id"],
                pin_code=pin["pin_code"],
                serial_number=pin["serial_number"],
                status=pin["status"],
                student_id=pin.get("student_id"),
                usage_count=pin["usage_count"],
                max_usage=pin["max_usage"],
                created_at=pin["created_at"]
            )
            for pin in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PINs: {str(e)}")


# Admin: Get All PINs
@router.get("/pins", response_model=List[PINResponse])
async def get_all_pins(
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("pins").select("*, students(full_name, admission_no)").order("id", desc=True).execute()
        
        return [
            PINResponse(
                id=pin["id"],
                pin_code=pin["pin_code"],
                serial_number=pin["serial_number"],
                status=pin["status"],
                student_id=pin.get("student_id"),
                usage_count=pin["usage_count"],
                max_usage=pin["max_usage"],
                created_at=pin["created_at"]
            )
            for pin in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PINs: {str(e)}")


# Admin: Delete PIN
@router.delete("/pins/{pin_id}")
async def delete_pin(
    pin_id: int,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        supabase.table("pins").delete().eq("id", pin_id).execute()
        return {"message": "PIN deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PIN: {str(e)}")


# Admin: Block PIN
@router.post("/pins/{pin_id}/block")
async def block_pin(
    pin_id: int,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        supabase.table("pins").update({"status": "blocked"}).eq("id", pin_id).execute()
        return {"message": "PIN blocked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to block PIN: {str(e)}")


# Student: Verify PIN for Result Checking
@router.post("/pins/verify", response_model=PINVerifyResponse)
async def verify_pin(
    request: PINVerifyRequest,
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    # Clean input
    pin_code = request.pin_code.replace(' ', '').replace('-', '')
    serial_number = request.serial_number.strip()
    
    try:
        result = supabase.table("pins").select("*").eq("pin_code", pin_code).eq("serial_number", serial_number).execute()
        
        if not result.data:
            return PINVerifyResponse(
                valid=False,
                message="Invalid Scratch Card PIN or Serial Number",
                student_id=None
            )
        
        pin_data = result.data[0]
        
        # Check if PIN is blocked
        if pin_data["status"] == "blocked":
            return PINVerifyResponse(
                valid=False,
                message="This PIN has been blocked",
                student_id=None
            )
        
        # Check if PIN is unused
        if pin_data["status"] == "unused":
            # Bind PIN to student
            supabase.table("pins").update({
                "status": "used",
                "student_id": current_user["id"],
                "usage_count": 1,
                "used_at": datetime.now().isoformat()
            }).eq("id", pin_data["id"]).execute()
            
            return PINVerifyResponse(
                valid=True,
                message="PIN verified and activated",
                student_id=current_user["id"]
            )
        
        # Check if PIN is used by this student
        if pin_data["student_id"] == current_user["id"]:
            # Check usage limit
            if pin_data["usage_count"] < pin_data["max_usage"]:
                # Increment usage count
                supabase.table("pins").update({
                    "usage_count": pin_data["usage_count"] + 1
                }).eq("id", pin_data["id"]).execute()
                
                return PINVerifyResponse(
                    valid=True,
                    message=f"PIN verified (Usage: {pin_data['usage_count'] + 1}/{pin_data['max_usage']})",
                    student_id=current_user["id"]
                )
            else:
                return PINVerifyResponse(
                    valid=False,
                    message=f"PIN usage limit exceeded (Max {pin_data['max_usage']} uses)",
                    student_id=None
                )
        else:
            return PINVerifyResponse(
                valid=False,
                message="This PIN is already used by another student",
                student_id=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify PIN: {str(e)}")


# Student: Get PIN Usage History
@router.get("/pins/my-history")
async def get_my_pin_history(
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("pins").select("*").eq("student_id", current_user["id"]).order("created_at", desc=True).execute()
        
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PIN history: {str(e)}")
