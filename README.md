# EduDrive CRM - School Management System

A comprehensive, role-based school management system built with Next.js (frontend) and FastAPI (backend), featuring academic management, financial operations, admissions, communications, help desk, and analytics.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [User Roles & Permissions](#user-roles--permissions)
- [Feature Access Guide](#feature-access-guide)
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Frontend Routes](#frontend-routes)

---

## 🎯 System Overview

EduDrive CRM is designed to streamline school operations through role-based access control, ensuring each user type has appropriate permissions for their responsibilities.

### **Core Modules**
- 🎓 **Academic Management** - Students, classes, attendance, calendar
- 💰 **Financial Management** - Fees, billing, payments, debtors
- 👨‍👩‍👧‍👦 **Admissions & Enrollment** - Leads, tours, assessments, enrollment
- 📞 **Communications** - Messaging templates, broadcasts, reminders
- 🎫 **Help Desk** - Ticket management, SLA monitoring, auto-assignment
- 👥 **User Management** - Role-based access, permissions, authentication
- 🚌 **Transportation** - Bus routes, vehicles, student assignments
- 📊 **Analytics & Reporting** - Predictive analytics, performance metrics, audit logs
- 🏢 **Operations** - Front desk, staff workload, reminders
- 📱 **Portals** - Dedicated parent and student portals

---

## 👥 User Roles & Permissions

### **School Admin (Super Admin)**
- **Full system access** across all modules
- User and role management
- System configuration and settings
- View all reports and analytics
- Manage all financial operations

### **Staff (Department-Specific)**
Access varies by department:

| Department | Permissions |
|------------|-------------|
| **Finance/Bursar** | Fee structures, billing, payments, debtors, receipts |
| **Admissions** | Lead management, tours, assessments, enrollment |
| **Academic** | Student records, classes, attendance, calendar |
| **Operations/Transport** | Bus routes, vehicles, student transportation |
| **Help Desk** | Ticket management, SLA monitoring, assignments |
| **IT/Security** | Session tracking, audit logs, user activity |
| **Reports/Management** | Analytics, performance metrics, risk analysis |

### **Teacher**
- View and manage class attendance
- View assigned students' academic records
- View own performance metrics
- View own workload
- Create help desk tickets

### **Parent**
- View child's academic records and attendance
- View child's transportation details
- Make fee payments
- View payment receipts
- Create support tickets
- Access dedicated parent portal

### **Student**
- View own academic records
- View own attendance
- Create support tickets
- Access dedicated student portal

---

## 🚀 Feature Access Guide

### **🎓 CORE ACADEMIC MANAGEMENT**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Student Management** | School Admin, Staff (Academic), Teacher (read) | Dashboard → Students | `GET/POST/PATCH/DELETE /students` | `/students` |
| **Class Structure** | School Admin, Staff (Academic) | Settings → Classes | `GET/POST /classes` | `/settings/classes` |
| **Academic Calendar** | School Admin, Staff (Academic) | Dashboard → Calendar | `GET/POST /calendar/events` | `/dashboard` |
| **Attendance Tracking** | School Admin, Staff (Academic), Teacher | Dashboard → Attendance | `GET/POST /attendance` | `/dashboard` |

---

### **💰 FINANCIAL MANAGEMENT**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Fee Structures** | School Admin, Staff (Finance/Bursar) | Finance → Fee Structures | `GET/POST/PATCH/DELETE /finance/fee-structures` | `/finance/fee-structures` |
| **Bulk Billing** | School Admin, Staff (Finance/Bursar) | Finance → Invoices | `POST /finance/bulk-billing` | `/finance` |
| **Payment Processing** | School Admin, Staff (Finance/Bursar), Parent | Finance → Payments | `POST /finance/payments` | `/finance/payments` |
| **Receipt Generation** | School Admin, Staff (Finance/Bursar), Parent | Finance → Receipts | `GET /finance/receipts` | `/finance` |
| **Debtors Management** | School Admin, Staff (Finance/Bursar) | Finance → Debtors | `GET /finance/debtors` | `/finance/debtors` |
| **Fee Collection Forecasting** | School Admin, Staff (Finance/Bursar) | Analytics → Fee Forecasting | `GET /analytics/fee-forecasting` | `/analytics` |

---

### **👨‍👩‍👧‍👦 ADMISSIONS & ENROLLMENT**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Lead Management** | School Admin, Staff (Admissions) | Admissions → Leads | `GET/POST/PATCH/DELETE /leads` | `/admissions` |
| **Lost Lead Tracking** | School Admin, Staff (Admissions) | Admissions → Lost Leads | `GET /leads/lost-reasons-summary` | `/admissions/lost-leads` |
| **Tour & Assessment Scheduling** | School Admin, Staff (Admissions) | Admissions → Lead Details | `POST /leads/{lead_id}/tours` | `/admissions/[leadId]` |
| **Enrollment Prediction** | School Admin, Staff (Admissions), Staff (Reports) | Analytics → Enrollment | `GET /analytics/enrollment-prediction` | `/analytics` |

---

### **📞 COMMUNICATIONS**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Messaging Templates** | School Admin, Staff (Admissions/Communications) | Messaging → Templates | `GET/POST/PATCH/DELETE /messages/templates` | `/messaging/templates` |
| **Broadcast Messaging** | School Admin, Staff (Admissions/Communications) | Messaging → Broadcasts | `POST /messages/broadcast` | `/messaging/broadcasts` |
| **Multi-Channel Delivery** | School Admin, Staff (Communications) | Messaging → Broadcasts | `POST /messages/broadcast` | `/messaging/broadcasts` |
| **Automated Reminders** | School Admin, Staff (Finance/Admissions) | Reminders → Queue | `POST /reminders/process` | `/reminders` |

---

### **🎫 HELP DESK & SUPPORT**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Ticket Management** | School Admin, Staff (Help Desk), Parent, Student | Help Desk → Tickets | `GET/POST/PATCH/DELETE /tickets` | `/helpdesk` |
| **Auto-Assignment** | School Admin, Staff (Help Desk Admin) | Help Desk → Auto Assign | `POST /helpdesk/tickets/auto-assign` | `/helpdesk` |
| **SLA Monitoring** | School Admin, Staff (Help Desk Admin) | Help Desk → SLA Status | `GET /helpdesk/tickets/sla-status` | `/helpdesk` |
| **Staff Performance** | School Admin, Staff (Management) | Analytics → Resolution | `GET /analytics/resolution-analytics` | `/analytics` |

---

### **👥 USER MANAGEMENT & SECURITY**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Role-Based Access** | School Admin (Super Admin only) | Staff → Administration | `POST /admin/roles/apply` | `/staff/administration` |
| **User Administration** | School Admin (Super Admin only) | Staff → Administration | `GET /admin/role-matrix` | `/staff/administration` |
| **Authentication** | All Users | Login/Signup Pages | `POST /auth/login`, `POST /auth/signup` | `/login`, `/signup` |
| **Email Verification** | All Users | Email Link | Schema: `email_verification_schema.sql` | - |
| **Session Tracking** | School Admin, Staff (IT/Security), All Users (own) | Settings → Sessions | `GET /sessions`, `GET /sessions/all` | `/settings` |

---

### **🚌 TRANSPORTATION**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Bus Routes** | School Admin, Staff (Operations/Transport) | Settings → Bus Routes | `GET/POST/PATCH/DELETE /transport/bus-routes` | `/settings/bus-routes` |
| **Vehicle Tracking** | School Admin, Staff (Operations/Transport) | Settings → Bus Routes | `GET/POST/PATCH/DELETE /transport/vehicles` | `/settings/bus-routes` |
| **Student Transportation** | School Admin, Staff (Operations/Transport), Parent | Settings → Bus Routes | `GET/POST /transport/students` | `/settings/bus-routes` |

---

### **📊 ANALYTICS & REPORTING**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Predictive Analytics** | School Admin, Staff (Reports/Management) | Analytics Dashboard | `GET /analytics/predictions` | `/analytics` |
| **Risk Analysis** | School Admin, Staff (Reports/Management), Teacher | Analytics Dashboard | `GET /analytics/risk-analysis` | `/analytics` |
| **Performance Metrics** | School Admin, Staff (Reports/Management), Teacher | Staff → Workload | `GET /staff/workload/performance-trends` | `/staff/workload` |
| **Activity Audit Log** | School Admin, Staff (IT/Audit) | Settings → Audit Logs | `GET /audit-logs` | `/settings` |
| **Staff Workload Indicators** | School Admin, Staff (Management), Teacher | Staff → Workload | `GET /staff/workload` | `/staff/workload` |

---

### **🏢 OPERATIONS**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Front-Desk Operations** | School Admin, Staff (Front Desk) | Front Desk | `GET/POST /frontdesk` | `/frontdesk` |
| **Staff Workload** | School Admin, Staff (Management), Teacher | Staff → Workload | `GET /staff/workload` | `/staff/workload` |
| **Reminder Queue** | School Admin, Staff (Communications) | Reminders | `GET/POST /reminders` | `/reminders` |

---

### **📱 PORTALS**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Parent Portal** | Parent | Dashboard → Parent | `GET /parent/*` | `/dashboard/parent` |
| **Student Portal** | Student | Dashboard → Student | `GET /student/*` | `/dashboard/student` |

---

### **🔧 CONFIGURATION**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Settings** | School Admin (Super Admin only) | Settings | `GET /settings` | `/settings` |
| **Term/Session Setup** | School Admin, Staff (Academic Admin) | Settings → Terms | `GET/POST /terms` | `/settings/terms` |
| **Fee Structure Configuration** | School Admin, Staff (Finance/Bursar) | Finance → Fee Structures | `POST /finance/fee-structures` | `/finance/fee-structures` |

---

### **📈 REPORTING & DASHBOARDS**

| Feature | Who Can Access | How to Access | API Endpoint | Frontend Route |
|---------|---------------|---------------|--------------|----------------|
| **Analytics Dashboard** | School Admin, Staff (Reports/Management) | Analytics | `GET /analytics/*` | `/analytics` |
| **Debtors Dashboard** | School Admin, Staff (Finance/Bursar) | Finance → Debtors | `GET /finance/debtors` | `/finance/debtors` |
| **Staff Performance Reports** | School Admin, Staff (Management), Teacher | Staff → Workload | `GET /staff/workload` | `/staff/workload` |
| **Attendance Reports** | School Admin, Staff (Academic), Teacher | Analytics → Attendance | `GET /analytics/attendance-trends` | `/analytics` |
| **Financial Reports** | School Admin, Staff (Finance/Bursar) | Finance | `GET /finance/*` | `/finance` |

---

## 🚀 Getting Started

### **Prerequisites**
- Node.js 18+
- Python 3.9+
- PostgreSQL (Supabase)
- Git

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/sheisjay001/EduDrive-CRM.git
cd EduDrive-CRM
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create `.env` file in backend directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

4. **Apply Database Schema**
```bash
# Apply SQL schema files via Supabase SQL Editor
# See MIGRATION_GUIDE.md for detailed instructions
```

5. **Frontend Setup**
```bash
cd frontend
npm install
```

6. **Run Development Servers**
```bash
# Backend (terminal 1)
cd backend
uvicorn app.main:app --reload

# Frontend (terminal 2)
cd frontend
npm run dev
```

7. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🏗️ Architecture

### **Technology Stack**

**Frontend**
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- Lucide Icons

**Backend**
- FastAPI (Python)
- PostgreSQL (Supabase)
- Pydantic (Data validation)
- JWT Authentication

### **Project Structure**

```
EduDrive-CRM/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration, security
│   │   ├── models/        # Database models
│   │   └── schemas/       # Pydantic schemas
│   ├── *_schema.sql       # Database migration files
│   └── requirements.txt
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # Reusable components
│   ├── hooks/             # Custom React hooks
│   └── package.json
└── README.md
```

---

## 📚 API Documentation

### **Authentication**

All API endpoints (except login/signup) require authentication via JWT token.

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

**Response**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "role": "school_admin"
  }
}
```

### **Authorization Headers**
```http
Authorization: Bearer <access_token>
```

### **Permission System**

The system uses role-based access control (RBAC) with the following permission categories:
- `finance:view`, `finance:manage`
- `leads:view`, `leads:manage`, `admissions:view`, `admissions:manage`
- `staff:view`, `staff:manage`
- `tickets:view`, `tickets:manage`, `helpdesk:view`, `helpdesk:manage`
- `messaging:view`, `messaging:manage`
- `reminders:view`, `reminders:manage`
- `audit:view`
- `settings:view`, `settings:manage`

---

## 🌐 Frontend Routes

### **Public Routes**
- `/` - Landing page
- `/login` - User login
- `/signup` - User registration
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset

### **Dashboard Routes**
- `/dashboard` - Main dashboard
- `/dashboard/parent` - Parent dashboard
- `/dashboard/student` - Student dashboard
- `/dashboard/teacher` - Teacher dashboard
- `/dashboard/school-admin` - School admin dashboard
- `/dashboard/super-admin` - Super admin dashboard
- `/dashboard/bursar` - Finance dashboard
- `/dashboard/helpdesk` - Help desk dashboard
- `/dashboard/admissions` - Admissions dashboard

### **Module Routes**
- `/students` - Student management
- `/families` - Family management
- `/finance` - Financial operations
- `/finance/invoices/[invoiceId]` - Invoice details
- `/finance/debtors` - Debtors management
- `/finance/fee-structures` - Fee structures
- `/finance/payments` - Payment processing
- `/admissions` - Admissions pipeline
- `/admissions/[leadId]` - Lead details
- `/admissions/calendar` - Admissions calendar
- `/admissions/lost-leads` - Lost lead tracking
- `/helpdesk` - Help desk tickets
- `/helpdesk/[ticketId]` - Ticket details
- `/messaging` - Messaging center
- `/messaging/templates` - Message templates
- `/messaging/broadcasts` - Broadcast messages
- `/reminders` - Reminder queue
- `/frontdesk` - Front desk operations
- `/analytics` - Analytics dashboard
- `/reports` - Reports center
- `/settings` - System settings
- `/settings/classes` - Class management
- `/settings/terms` - Term/session management
- `/settings/bus-routes` - Transportation management
- `/staff` - Staff management
- `/staff/administration` - User administration
- `/staff/workload` - Staff workload
- `/activity` - Activity audit log

---

## 🔐 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Permission-based authorization
- Session tracking and management
- Audit logging for all actions
- Email verification
- Password reset functionality

---

## 📞 Support

For issues, questions, or contributions, please visit:
- GitHub Repository: https://github.com/sheisjay001/EduDrive-CRM
- Issues: https://github.com/sheisjay001/EduDrive-CRM/issues

---

## 📄 License

This project is licensed under the MIT License.

---

**EduDrive CRM - Transforming School Management** 🎓
