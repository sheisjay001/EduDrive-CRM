from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi


def custom_openapi():
    """
    Custom OpenAPI schema for EduDrive CRM API documentation
    """
    from app.main import app
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="EduDrive CRM API",
        version="1.0.0",
        description="""
        ## EduDrive CRM API Documentation
        
        A comprehensive CRM system for educational institutions, managing:
        - Admissions and lead tracking
        - Student lifecycle management
        - Financial operations and billing
        - Help desk and support tickets
        - Messaging and communication
        - Staff and user administration
        - Analytics and reporting
        
        ### Authentication
        
        Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your_access_token>
        ```
        
        ### Roles
        
        The system supports the following roles:
        - **super_admin**: Full system access
        - **school_admin**: School-level administration
        - **admissions_officer**: Admissions and lead management
        - **bursar**: Financial operations
        - **teacher**: Academic and student management
        - **helpdesk_officer**: Support ticket management
        
        ### Error Responses
        
        Standard error responses follow this format:
        ```json
        {
          "detail": "Error message description"
        }
        ```
        """,
        routes=app.routes,
    )
    
    # Add custom tags and descriptions
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "User authentication, token management, and password reset"
        },
        {
            "name": "Dashboard",
            "description": "Dashboard summaries and KPIs for different user roles"
        },
        {
            "name": "Admissions",
            "description": "Lead management, conversion tracking, and lost lead analytics"
        },
        {
            "name": "Families",
            "description": "Family management and parent information"
        },
        {
            "name": "Students",
            "description": "Student records, lifecycle logs, and academic management"
        },
        {
            "name": "Finance",
            "description": "Invoices, payments, fee structures, and debtors management"
        },
        {
            "name": "Messaging",
            "description": "Message templates, broadcasts, and communication channels"
        },
        {
            "name": "Help Desk",
            "description": "Support tickets, SLA tracking, and parent satisfaction"
        },
        {
            "name": "Staff",
            "description": "Staff management, workload tracking, and user administration"
        },
        {
            "name": "Settings",
            "description": "School settings, academic calendar, and class structure"
        },
        {
            "name": "Activity",
            "description": "Activity audit log and system event tracking"
        },
        {
            "name": "Reminders",
            "description": "Automated reminders and follow-up management"
        },
        {
            "name": "Calendar",
            "description": "Tour and assessment calendar management"
        },
        {
            "name": "Lifecycle",
            "description": "Student lifecycle tracking and history"
        },
        {
            "name": "Payments",
            "description": "Payment gateway integration and webhooks"
        },
        {
            "name": "Reports",
            "description": "Analytics, forecasting, and report generation"
        },
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /auth/login endpoint"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Example endpoint documentation templates
"""
## Authentication Endpoints

### POST /auth/login
Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "role": "school_admin",
    "fullName": "John Doe",
    "schoolId": "school-id"
  }
}
```

## Admissions Endpoints

### GET /leads
Retrieve all leads with filtering options.

**Query Parameters:**
- `stage`: Filter by lead stage (new, contacted, tour_scheduled, assessment_scheduled, enrolled, lost)
- `source`: Filter by lead source
- `date_from`: Filter leads from this date
- `date_to`: Filter leads until this date

**Response:**
```json
{
  "leads": [
    {
      "id": "lead-id",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+2348000000000",
      "stage": "new",
      "source": "website",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "conversion_rate": 45.5
}
```

## Finance Endpoints

### GET /finance/debtors
Retrieve debtors dashboard with aging buckets.

**Response:**
```json
{
  "aging_buckets": {
    "1-30_days": {
      "count": 10,
      "amount": 500000
    },
    "31-60_days": {
      "count": 5,
      "amount": 250000
    },
    "61-90_days": {
      "count": 3,
      "amount": 150000
    },
    "90+_days": {
      "count": 2,
      "amount": 100000
    }
  },
  "total_outstanding": 1000000,
  "total_debtors": 20,
  "debtors_list": [...]
}
```
"""
