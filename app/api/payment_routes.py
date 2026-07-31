from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import httpx
from app.core.auth import get_current_user, AuthUser
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])

class PaystackInitRequest(BaseModel):
    email: str
    amount: int  # in kobo (lowest currency unit)
    reference: Optional[str]
    metadata: Optional[dict]

class FlutterwaveInitRequest(BaseModel):
    email: str
    amount: float
    currency: str = "NGN"
    tx_ref: Optional[str]
    customer: Optional[dict]
    meta: Optional[dict]

class BankTransferRequest(BaseModel):
    invoice_id: str
    amount: float
    bank_name: str
    account_number: str
    account_name: str
    transfer_date: datetime
    reference: str
    notes: Optional[str]

@router.post("/paystack/initialize")
async def initialize_paystack(
    request: PaystackInitRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Initialize payment via Paystack"""
    paystack_secret_key = getattr(settings, 'paystack_secret_key', None)
    
    if not paystack_secret_key:
        raise HTTPException(status_code=500, detail="Paystack not configured")
    
    import secrets
    reference = request.reference or f"EDU-{secrets.token_hex(8)}"
    
    payload = {
        "email": request.email,
        "amount": request.amount,
        "reference": reference,
        "metadata": request.metadata or {}
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

@router.post("/flutterwave/initialize")
async def initialize_flutterwave(
    request: FlutterwaveInitRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Initialize payment via Flutterwave"""
    flutterwave_secret_key = getattr(settings, 'flutterwave_secret_key', None)
    
    if not flutterwave_secret_key:
        raise HTTPException(status_code=500, detail="Flutterwave not configured")
    
    import secrets
    tx_ref = request.tx_ref or f"EDU-{secrets.token_hex(8)}"
    
    payload = {
        "tx_ref": tx_ref,
        "amount": request.amount,
        "currency": request.currency,
        "email": request.email,
        "customer": request.customer or {"email": request.email},
        "meta": request.meta or {}
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

@router.post("/bank-transfer")
async def log_bank_transfer(
    request: BankTransferRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Log manual bank transfer payment"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        # Create payment record
        result = supabase.table('payments').insert({
            'invoice_id': request.invoice_id,
            'amount': request.amount,
            'payment_method': 'bank_transfer',
            'payment_date': request.transfer_date.isoformat(),
            'reference': request.reference,
            'status': 'pending_verification',
            'bank_name': request.bank_name,
            'account_number': request.account_number,
            'account_name': request.account_name,
            'notes': request.notes,
            'recorded_by': current_user.id,
            'school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "payment_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/paystack")
async def paystack_webhook(request: Request):
    """Handle Paystack webhook"""
    paystack_secret_key = getattr(settings, 'paystack_secret_key', None)
    
    if not paystack_secret_key:
        raise HTTPException(status_code=500, detail="Paystack not configured")
    
    # Verify webhook signature
    signature = request.headers.get("x-paystack-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    body = await request.body()
    import hmac
    import hashlib
    
    calculated_signature = hmac.new(
        paystack_secret_key.encode(),
        body,
        hashlib.sha512
    ).hexdigest()
    
    if not hmac.compare_digest(calculated_signature, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process webhook
    event = await request.json()
    
    if event['event'] == 'charge.success':
        # Update payment status
        from app.database.session import get_supabase_client
        supabase = get_supabase_client()
        
        reference = event['data']['reference']
        amount = event['data']['amount'] / 100  # Convert from kobo
        
        # Find and update payment
        supabase.table('payments').update({
            'status': 'completed',
            'payment_date': datetime.now().isoformat()
        }).eq('reference', reference).execute()
        
        # Update invoice status
        supabase.table('invoices').update({
            'status': 'paid',
            'amount_paid': amount
        }).eq('reference', reference).execute()
    
    return {"status": "success"}

@router.post("/webhooks/flutterwave")
async def flutterwave_webhook(request: Request):
    """Handle Flutterwave webhook"""
    flutterwave_secret_hash = getattr(settings, 'flutterwave_secret_hash', None)
    
    if not flutterwave_secret_hash:
        raise HTTPException(status_code=500, detail="Flutterwave not configured")
    
    # Verify webhook signature
    signature = request.headers.get("verif-hash")
    if not signature or signature != flutterwave_secret_hash:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process webhook
    event = await request.json()
    
    if event['event'] == 'charge.completed':
        # Update payment status
        from app.database.session import get_supabase_client
        supabase = get_supabase_client()
        
        tx_ref = event['data']['tx_ref']
        amount = event['data']['amount']
        
        # Find and update payment
        supabase.table('payments').update({
            'status': 'completed',
            'payment_date': datetime.now().isoformat()
        }).eq('reference', tx_ref).execute()
        
        # Update invoice status
        supabase.table('invoices').update({
            'status': 'paid',
            'amount_paid': amount
        }).eq('reference', tx_ref).execute()
    
    return {"status": "success"}

@router.get("/verify/{reference}")
async def verify_payment(
    reference: str,
    provider: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Verify payment status from provider"""
    if provider == "paystack":
        paystack_secret_key = getattr(settings, 'paystack_secret_key', None)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.paystack.co/transaction/verify/{reference}",
                headers={
                    "Authorization": f"Bearer {paystack_secret_key}"
                }
            )
            return response.json()
    
    elif provider == "flutterwave":
        flutterwave_secret_key = getattr(settings, 'flutterwave_secret_key', None)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.flutterwave.com/v3/transactions/{reference}/verify",
                headers={
                    "Authorization": f"Bearer {flutterwave_secret_key}"
                }
            )
            return response.json()
    
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
