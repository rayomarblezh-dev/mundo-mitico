from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import uvicorn
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mundo Mitico Crypto API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
API_KEYS = [os.getenv("CRYPTO_API_KEY")]

# Database setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.mundo_mitico

# Models
class CreateInvoiceRequest(BaseModel):
    user_id: int
    currency: str  # "TON", "USDT_TRC20", "USDT_TON"
    amount: float
    description: Optional[str] = None

class InvoiceResponse(BaseModel):
    invoice_id: str
    payment_address: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    expires_at: datetime

# Helper functions
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return credentials.credentials

# Routes
@app.post("/api/v1/invoice", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: CreateInvoiceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new payment invoice"""
    try:
        # Generate a unique invoice ID
        invoice_id = f"inv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{invoice_data.user_id}"
        
        # In a real implementation, you would integrate with a crypto payment processor here
        # For now, we'll return a mock response
        payment_address = {
            "TON": "EQABC123...",
            "USDT_TRC20": "TXYZ789...",
            "USDT_TON": "EQXYZ456..."
        }.get(invoice_data.currency, "")
        
        if not payment_address:
            raise HTTPException(status_code=400, detail="Unsupported currency")
        
        # Save to database
        invoice = {
            "invoice_id": invoice_id,
            "user_id": invoice_data.user_id,
            "amount": invoice_data.amount,
            "currency": invoice_data.currency,
            "payment_address": payment_address,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow().timestamp() + 3600,  # 1 hour expiry
            "description": invoice_data.description
        }
        
        await db.invoices.insert_one(invoice)
        
        return {
            "invoice_id": invoice_id,
            "payment_address": payment_address,
            "amount": invoice_data.amount,
            "currency": invoice_data.currency,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow().timestamp() + 3600
        }
        
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/invoice/{invoice_id}")
async def get_invoice_status(invoice_id: str):
    """Check the status of an invoice"""
    invoice = await db.invoices.find_one({"invoice_id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

# Webhook handler for payment processors
@app.post("/api/v1/webhook/payment")
async def payment_webhook(request: Request):
    """Webhook to receive payment notifications from payment processor"""
    try:
        data = await request.json()
        # Process webhook data here
        # Update invoice status in database
        # Notify user via WebSocket or other means
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("crypto_api:app", host="0.0.0.0", port=8000, reload=True)
