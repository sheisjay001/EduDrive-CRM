import os
from typing import Optional
import httpx

class BrevoService:
    """Service for sending emails via Brevo (formerly Sendinblue)"""
    
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY", "")
        self.sender_email = os.getenv("BREVO_SENDER_EMAIL", "autajoy2003@gmail.com")
        self.sender_name = os.getenv("BREVO_SENDER_NAME", "EduDrive CRM")
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
    
    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> dict:
        """
        Send a transactional email via Brevo
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            html_content: HTML content of the email
            sender_email: Sender email (defaults to school email)
            sender_name: Sender name (defaults to school name)
        
        Returns:
            Response from Brevo API
        """
        if not self.api_key:
            raise ValueError("Brevo API key not configured")
        
        payload = {
            "sender": {
                "email": sender_email or self.sender_email,
                "name": sender_name or self.sender_name
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/smtp/email",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def send_template_email(
        self,
        to_email: str,
        to_name: str,
        template_id: int,
        params: dict
    ) -> dict:
        """
        Send an email using a Brevo template
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            template_id: Brevo template ID
            params: Parameters to substitute in template
        
        Returns:
            Response from Brevo API
        """
        if not self.api_key:
            raise ValueError("Brevo API key not configured")
        
        payload = {
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "templateId": template_id,
            "params": params
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/smtp/email",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def send_bulk_email(
        self,
        recipients: list[dict],  # List of {"email": str, "name": str}
        subject: str,
        html_content: str,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> dict:
        """
        Send bulk email to multiple recipients
        
        Args:
            recipients: List of recipient dictionaries with email and name
            subject: Email subject
            html_content: HTML content of the email
            sender_email: Sender email
            sender_name: Sender name
        
        Returns:
            Response from Brevo API
        """
        if not self.api_key:
            raise ValueError("Brevo API key not configured")
        
        payload = {
            "sender": {
                "email": sender_email or self.sender_email,
                "name": sender_name or self.sender_name
            },
            "to": recipients,
            "subject": subject,
            "htmlContent": html_content
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/smtp/email",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()


# Singleton instance
brevo_service = BrevoService()
