# EduDrive CRM - Project Presentation

---

## Slide 1: Title Slide

# EduDrive CRM
### Comprehensive School Management System

**A role-based, full-stack school management platform**

- Academic Management
- Financial Operations
- Admissions & Enrollment
- Communications
- Help Desk & Support
- Analytics & Reporting

---

## Slide 2: Project Overview

## What is EduDrive CRM?

EduDrive CRM is a modern, comprehensive school management system designed to streamline all aspects of school operations through a unified, role-based platform.

### Key Objectives
- **Centralize Operations**: Single platform for all school functions
- **Role-Based Access**: Tailored experiences for each user type
- **Data-Driven Decisions**: Built-in analytics and reporting
- **Streamlined Workflows**: Automated processes and reminders
- **Parent/Student Engagement**: Dedicated portals for families

### Technology Stack
- **Frontend**: Next.js 16, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, PostgreSQL (Supabase)
- **Authentication**: JWT-based with role-based access control

---

## Slide 3: User Roles & Permissions

## Five User Types

### 1. School Admin (Super Admin)
- Full system access
- User and role management
- System configuration
- All reports and analytics

### 2. Staff (Department-Specific)
- **Finance/Bursar**: Fees, billing, payments
- **Admissions**: Leads, tours, enrollment
- **Academic**: Students, classes, attendance
- **Operations/Transport**: Bus routes, vehicles
- **Help Desk**: Ticket management, SLA
- **IT/Security**: Sessions, audit logs
- **Reports/Management**: Analytics, performance

### 3. Teacher
- Class attendance
- Student records (assigned)
- Own performance metrics
- Own workload
- Create support tickets

### 4. Parent
- Child's academic records
- Child's transportation
- Make payments
- View receipts
- Create support tickets

### 5. Student
- Own academic records
- Own attendance
- Create support tickets

---

## Slide 4: Core Academic Management

## 🎓 Academic Operations

### Features
- **Student Management**: Full CRUD operations, CSV import
- **Class Structure**: Class creation, subjects, enrollments, promotions
- **Academic Calendar**: Events, assessments, availability checking
- **Attendance Tracking**: Staff/student attendance, trends, summaries

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Student Management | Admin, Staff (Academic), Teacher (read) | Dashboard → Students |
| Class Structure | Admin, Staff (Academic) | Settings → Classes |
| Academic Calendar | Admin, Staff (Academic) | Dashboard → Calendar |
| Attendance Tracking | Admin, Staff (Academic), Teacher | Dashboard → Attendance |

### API Endpoints
- `GET/POST/PATCH/DELETE /students`
- `GET/POST /classes`
- `GET/POST /calendar/events`
- `GET/POST /attendance`

---

## Slide 5: Financial Management

## 💰 Financial Operations

### Features
- **Fee Structures**: Create, update, delete fee structures
- **Bulk Billing**: Generate invoices for multiple students
- **Payment Processing**: Record and track payments
- **Receipt Generation**: Automatic receipt creation
- **Debtors Management**: Track outstanding balances
- **Fee Collection Forecasting**: Predict future revenue

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Fee Structures | Admin, Staff (Finance/Bursar) | Finance → Fee Structures |
| Bulk Billing | Admin, Staff (Finance/Bursar) | Finance → Invoices |
| Payment Processing | Admin, Staff (Finance/Bursar), Parent | Finance → Payments |
| Receipt Generation | Admin, Staff (Finance/Bursar), Parent | Finance → Receipts |
| Debtors Management | Admin, Staff (Finance/Bursar) | Finance → Debtors |
| Fee Forecasting | Admin, Staff (Finance/Bursar) | Analytics → Fee Forecasting |

### API Endpoints
- `GET/POST/PATCH/DELETE /finance/fee-structures`
- `POST /finance/bulk-billing`
- `POST /finance/payments`
- `GET /finance/receipts`
- `GET /finance/debtors`
- `GET /analytics/fee-forecasting`

---

## Slide 6: Admissions & Enrollment

## 👨‍👩‍👧‍👦 Admissions Pipeline

### Features
- **Lead Management**: Track prospective students through enrollment
- **Lost Lead Tracking**: Analyze reasons for lost opportunities
- **Tour Scheduling**: Schedule and manage school tours
- **Assessment Scheduling**: Coordinate student assessments
- **Enrollment Prediction**: Predict future enrollment numbers

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Lead Management | Admin, Staff (Admissions) | Admissions → Leads |
| Lost Lead Tracking | Admin, Staff (Admissions) | Admissions → Lost Leads |
| Tour Scheduling | Admin, Staff (Admissions) | Admissions → Lead Details |
| Assessment Scheduling | Admin, Staff (Admissions) | Admissions → Lead Details |
| Enrollment Prediction | Admin, Staff (Admissions), Staff (Reports) | Analytics → Enrollment |

### Pipeline Stages
1. **New Lead** → Initial inquiry
2. **Contacted** → Follow-up initiated
3. **Tour Scheduled** → School visit arranged
4. **Assessment** → Student evaluation
5. **Offer Made** → Enrollment offer sent
6. **Enrolled** → Student registered

### API Endpoints
- `GET/POST/PATCH/DELETE /leads`
- `GET /leads/lost-reasons-summary`
- `POST /leads/{lead_id}/tours`
- `POST /leads/{lead_id}/assessments`
- `GET /analytics/enrollment-prediction`

---

## Slide 7: Communications

## 📞 Messaging & Communications

### Features
- **Messaging Templates**: Create reusable message templates
- **Broadcast Messaging**: Send messages to multiple recipients
- **Multi-Channel Delivery**: Email, SMS, in-app notifications
- **Automated Reminders**: Fee due dates, follow-ups, events

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Messaging Templates | Admin, Staff (Admissions/Communications) | Messaging → Templates |
| Broadcast Messaging | Admin, Staff (Admissions/Communications) | Messaging → Broadcasts |
| Multi-Channel Delivery | Admin, Staff (Communications) | Messaging → Broadcasts |
| Automated Reminders | Admin, Staff (Finance/Admissions) | Reminders → Queue |

### Use Cases
- **Fee Reminders**: Automated payment due notifications
- **Admissions Follow-ups**: Lead engagement reminders
- **Event Notifications**: School events and calendar updates
- **Emergency Alerts**: Urgent communications to all stakeholders

### API Endpoints
- `GET/POST/PATCH/DELETE /messages/templates`
- `POST /messages/broadcast`
- `POST /reminders/process`

---

## Slide 8: Help Desk & Support

## 🎫 Ticket Management System

### Features
- **Ticket Management**: Create, update, resolve tickets
- **Auto-Assignment**: Intelligent ticket assignment based on workload
- **SLA Monitoring**: Track response and resolution times
- **Staff Performance**: Resolution analytics and metrics

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Ticket Management | Admin, Staff (Help Desk), Parent, Student | Help Desk → Tickets |
| Auto-Assignment | Admin, Staff (Help Desk Admin) | Help Desk → Auto Assign |
| SLA Monitoring | Admin, Staff (Help Desk Admin) | Help Desk → SLA Status |
| Staff Performance | Admin, Staff (Management) | Analytics → Resolution |

### Ticket Workflow
1. **Created** → Ticket submitted
2. **Assigned** → Staff member assigned
3. **In Progress** → Work being done
4. **Resolved** → Issue addressed
5. **Closed** → Ticket completed

### API Endpoints
- `GET/POST/PATCH/DELETE /tickets`
- `POST /helpdesk/tickets/auto-assign`
- `GET /helpdesk/tickets/sla-status`
- `GET /analytics/resolution-analytics`

---

## Slide 9: User Management & Security

## 👥 Access Control & Security

### Features
- **Role-Based Access**: Granular permissions by role
- **User Administration**: Manage users and permissions
- **Authentication**: Secure JWT-based login/signup
- **Email Verification**: Verify user email addresses
- **Session Tracking**: Monitor and manage user sessions

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Role-Based Access | Admin (Super Admin only) | Staff → Administration |
| User Administration | Admin (Super Admin only) | Staff → Administration |
| Authentication | All Users | Login/Signup Pages |
| Email Verification | All Users | Email Link |
| Session Tracking | Admin, Staff (IT/Security), All Users (own) | Settings → Sessions |

### Permission Categories
- `finance:view`, `finance:manage`
- `leads:view`, `leads:manage`, `admissions:view`, `admissions:manage`
- `staff:view`, `staff:manage`
- `tickets:view`, `tickets:manage`, `helpdesk:view`, `helpdesk:manage`
- `messaging:view`, `messaging:manage`
- `reminders:view`, `reminders:manage`
- `audit:view`
- `settings:view`, `settings:manage`

### API Endpoints
- `POST /auth/login`, `POST /auth/signup`
- `GET /admin/role-matrix`
- `POST /admin/permissions/grant`
- `GET /sessions`, `GET /sessions/all`
- `GET /audit-logs`

---

## Slide 10: Transportation

## 🚌 School Transportation

### Features
- **Bus Routes**: Create and manage bus routes
- **Vehicle Tracking**: Track school vehicles
- **Student Transportation**: Assign students to routes
- **Bus Stops**: Define pickup/drop-off locations

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Bus Routes | Admin, Staff (Operations/Transport) | Settings → Bus Routes |
| Vehicle Tracking | Admin, Staff (Operations/Transport) | Settings → Bus Routes |
| Student Transportation | Admin, Staff (Operations/Transport), Parent | Settings → Bus Routes |

### Capabilities
- Define multiple bus routes with stops
- Assign vehicles to routes
- Assign students to routes and stops
- Parents can view child's transportation details

### API Endpoints
- `GET/POST/PATCH/DELETE /transport/bus-routes`
- `GET/POST/PATCH/DELETE /transport/vehicles`
- `GET/POST /transport/students`
- `GET/POST/PATCH/DELETE /transport/bus-stops`

---

## Slide 11: Analytics & Reporting

## 📊 Data-Driven Insights

### Features
- **Predictive Analytics**: AI-powered predictions for enrollment and revenue
- **Risk Analysis**: Identify at-risk students and financial risks
- **Performance Metrics**: Track staff and student performance
- **Activity Audit Log**: Complete audit trail of all actions
- **Staff Workload Indicators**: Monitor staff capacity and utilization

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Predictive Analytics | Admin, Staff (Reports/Management) | Analytics Dashboard |
| Risk Analysis | Admin, Staff (Reports/Management), Teacher | Analytics Dashboard |
| Performance Metrics | Admin, Staff (Reports/Management), Teacher | Staff → Workload |
| Activity Audit Log | Admin, Staff (IT/Audit) | Settings → Audit Logs |
| Staff Workload | Admin, Staff (Management), Teacher | Staff → Workload |

### Analytics Available
- Enrollment predictions
- Fee collection forecasting
- Attendance trends
- Resolution analytics
- Student statistics
- Risk analysis

### API Endpoints
- `GET /analytics/predictions`
- `GET /analytics/risk-analysis`
- `GET /analytics/attendance-trends`
- `GET /analytics/resolution-analytics`
- `GET /analytics/fee-forecasting`
- `GET /audit-logs`

---

## Slide 12: Operations & Portals

## 🏢 Daily Operations & User Portals

### Operations Features
- **Front-Desk Operations**: Daily visitor and activity logging
- **Staff Workload**: Monitor and manage staff assignments
- **Reminder Queue**: Manage automated reminders

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Front-Desk Operations | Admin, Staff (Front Desk) | Front Desk |
| Staff Workload | Admin, Staff (Management), Teacher | Staff → Workload |
| Reminder Queue | Admin, Staff (Communications) | Reminders |

### Dedicated Portals

#### Parent Portal
- View child's academic records
- View child's attendance
- View child's transportation
- Make fee payments
- View payment receipts
- Create support tickets

#### Student Portal
- View own academic records
- View own attendance
- Create support tickets

### API Endpoints
- `GET/POST /frontdesk`
- `GET /staff/workload`
- `GET/POST /reminders`
- `GET /parent/*`
- `GET /student/*`

---

## Slide 13: Configuration & Reporting

## 🔧 System Configuration & Reports

### Configuration Features
- **Settings**: System-wide configuration
- **Term/Session Setup**: Academic calendar management
- **Fee Structure Configuration**: Define fee schedules

### Access & Navigation

| Feature | Who Can Access | How to Access |
|---------|---------------|--------------|
| Settings | Admin (Super Admin only) | Settings |
| Term/Session Setup | Admin, Staff (Academic Admin) | Settings → Terms |
| Fee Structure Configuration | Admin, Staff (Finance/Bursar) | Finance → Fee Structures |

### Reporting & Dashboards

| Dashboard | Who Can Access | How to Access |
|-----------|---------------|--------------|
| Analytics Dashboard | Admin, Staff (Reports/Management) | Analytics |
| Debtors Dashboard | Admin, Staff (Finance/Bursar) | Finance → Debtors |
| Staff Performance Reports | Admin, Staff (Management), Teacher | Staff → Workload |
| Attendance Reports | Admin, Staff (Academic), Teacher | Analytics → Attendance |
| Financial Reports | Admin, Staff (Finance/Bursar) | Finance |

### API Endpoints
- `GET /settings`
- `GET/POST /terms`
- `POST /finance/fee-structures`
- `GET /analytics/*`
- `GET /finance/*`

---

## Slide 14: Getting Started

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL (Supabase)
- Git

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/sheisjay001/EduDrive-CRM.git
cd EduDrive-CRM
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment**
Create `.env` file in backend:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

4. **Apply Database Schema**
- Use Supabase SQL Editor
- Apply 26 `*_schema.sql` files
- See `MIGRATION_GUIDE.md` for details

5. **Frontend Setup**
```bash
cd frontend
npm install
```

6. **Run Development Servers**
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

7. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Slide 15: Architecture

## 🏗️ System Architecture

### Technology Stack

**Frontend**
- Next.js 16 (React framework)
- TypeScript (Type safety)
- Tailwind CSS (Styling)
- Lucide Icons (UI icons)

**Backend**
- FastAPI (Python web framework)
- PostgreSQL (Supabase database)
- Pydantic (Data validation)
- JWT (Authentication)

### Project Structure

```
EduDrive-CRM/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes (20+ modules)
│   │   ├── core/          # Configuration, security
│   │   ├── models/        # Database models
│   │   └── schemas/       # Pydantic schemas
│   ├── *_schema.sql       # 26 database migration files
│   └── requirements.txt
├── frontend/
│   ├── app/               # Next.js pages (45+ routes)
│   ├── components/        # Reusable UI components
│   ├── hooks/             # Custom React hooks
│   └── package.json
└── README.md
```

### Key Design Principles
- **Role-Based Security**: All endpoints protected by permissions
- **RESTful API**: Standard HTTP methods and status codes
- **Type Safety**: TypeScript frontend, Pydantic backend
- **Responsive Design**: Mobile-friendly UI
- **Audit Logging**: Complete action tracking

---

## Slide 16: Security Features

## 🔐 Security & Compliance

### Authentication & Authorization

- **JWT-Based Authentication**: Secure token-based auth
- **Role-Based Access Control (RBAC)**: 5 user roles
- **Permission-Based Authorization**: 20+ permission categories
- **Session Management**: Track and revoke sessions
- **Email Verification**: Verify user email addresses

### Data Protection

- **Password Hashing**: Secure password storage
- **Audit Logging**: Complete audit trail
- **API Rate Limiting**: Prevent abuse
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Input sanitization

### Access Control Examples

```python
# Only school admin can delete fee structures
@router.delete("/finance/fee-structures/{fee_id}")
def delete_fee_structure(
    fee_id: str, 
    current_user: AuthUser = Depends(require_role("school_admin"))
):
    # Implementation

# Finance staff can view fee structures
@router.get("/finance/fee-structures")
def fee_structures(
    current_user: AuthUser = Depends(get_current_user)
):
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(403, "Permission denied")
```

---

## Slide 17: API Documentation

## 📚 API Overview

### Authentication

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

### Authorization Headers
```http
Authorization: Bearer <access_token>
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key API Modules
- `student_routes.py` - Student management
- `class_routes.py` - Class and subject management
- `calendar_routes.py` - Academic calendar
- `payment_routes.py` - Payment processing
- `messaging_routes.py` - Communications
- `transport_routes.py` - Transportation
- `user_admin_routes.py` - User management
- `analytics_routes.py` - Analytics and reporting

---

## Slide 18: Frontend Routes

## 🌐 Application Navigation

### Public Routes
- `/` - Landing page
- `/login` - User login
- `/signup` - User registration
- `/forgot-password` - Password reset
- `/reset-password` - Password reset confirmation

### Dashboard Routes (9 Role-Specific)
- `/dashboard` - Main dashboard
- `/dashboard/parent` - Parent dashboard
- `/dashboard/student` - Student dashboard
- `/dashboard/teacher` - Teacher dashboard
- `/dashboard/school-admin` - School admin dashboard
- `/dashboard/super-admin` - Super admin dashboard
- `/dashboard/bursar` - Finance dashboard
- `/dashboard/helpdesk` - Help desk dashboard
- `/dashboard/admissions` - Admissions dashboard

### Module Routes (35+ Pages)
- `/students` - Student management
- `/families` - Family management
- `/finance/*` - Financial operations (5 pages)
- `/admissions/*` - Admissions (5 pages)
- `/helpdesk/*` - Help desk (2 pages)
- `/messaging/*` - Communications (3 pages)
- `/settings/*` - Configuration (4 pages)
- `/staff/*` - Staff management (3 pages)
- `/analytics` - Analytics dashboard
- `/reports` - Reports center
- `/activity` - Activity audit log

---

## Slide 19: Demo Scenarios

## 🎬 Live Demo Scenarios

### Scenario 1: School Admin
1. Login as school admin
2. View analytics dashboard
3. Create new fee structure
4. Assign staff permissions
5. Review audit logs

### Scenario 2: Admissions Officer
1. Login as admissions staff
2. Create new lead
3. Schedule school tour
4. Move lead through pipeline
5. View lost lead analytics

### Scenario 3: Finance/Bursar
1. Login as finance staff
2. Generate bulk billing
3. Process payment
4. View debtors list
5. Review fee forecasting

### Scenario 4: Teacher
1. Login as teacher
2. View class attendance
3. View student records
4. Check own workload
5. Create support ticket

### Scenario 5: Parent
1. Login via parent portal
2. View child's academic records
3. View child's attendance
4. Make fee payment
5. View payment receipt

### Scenario 6: Student
1. Login via student portal
2. View own academic records
3. View own attendance
4. Create support ticket

---

## Slide 20: Benefits & Impact

## 🎯 Key Benefits

### For School Administration
- **Centralized Operations**: One platform for all functions
- **Data-Driven Decisions**: Analytics and reporting
- **Improved Efficiency**: Automated workflows
- **Better Compliance**: Audit logging and security
- **Cost Savings**: Reduced manual work

### For Staff
- **Role-Specific Tools**: Tailored interfaces
- **Workload Visibility**: Track assignments and capacity
- **Streamlined Communication**: Built-in messaging
- **Performance Tracking**: Metrics and analytics
- **Mobile Access**: Work from anywhere

### For Parents
- **Real-Time Information**: Child's progress and attendance
- **Convenient Payments**: Online fee payments
- **Direct Communication**: Support tickets
- **Transportation Visibility**: Track child's route
- **Dedicated Portal**: Easy access to all features

### For Students
- **Academic Records**: View grades and attendance
- **Support Access**: Create help desk tickets
- **Transparent Communication**: Stay informed
- **Mobile-Friendly**: Access from any device

---

## Slide 21: Future Enhancements

## 🚀 Roadmap

### Phase 1: Enhanced Analytics
- Machine learning predictions
- Advanced risk analysis
- Custom report builder
- Data export functionality

### Phase 2: Mobile Applications
- Native iOS app
- Native Android app
- Push notifications
- Offline mode

### Phase 3: Integrations
- Payment gateway integration
- SMS provider integration
- Email marketing integration
- Calendar sync (Google, Outlook)

### Phase 4: Advanced Features
- Video conferencing integration
- Learning management system
- Parent-teacher scheduling
- Automated report cards

### Phase 5: Multi-School Support
- Multi-tenant architecture
- School-specific branding
- Centralized administration
- Cross-school analytics

---

## Slide 22: Conclusion

## 🎓 Transforming School Management

### Summary

EduDrive CRM is a comprehensive, role-based school management system that:

- **Centralizes Operations**: Single platform for all school functions
- **Ensures Security**: Role-based access control and audit logging
- **Provides Insights**: Analytics and reporting for data-driven decisions
- **Enhances Engagement**: Dedicated portals for parents and students
- **Scales Easily**: Modern architecture for growth

### Key Metrics

- **45+ Frontend Pages**: Comprehensive feature coverage
- **20+ API Modules**: Full backend functionality
- **26 Database Schemas**: Complete data model
- **5 User Roles**: Tailored experiences
- **20+ Permission Categories**: Granular access control

### Get Started

- **GitHub**: https://github.com/sheisjay001/EduDrive-CRM
- **Documentation**: See README.md
- **API Docs**: http://localhost:8000/docs
- **Support**: Open an issue on GitHub

---

## Slide 23: Q&A

## Questions & Discussion

### Thank You!

**EduDrive CRM - Transforming School Management** 🎓

For questions, feedback, or contributions:
- GitHub: https://github.com/sheisjay001/EduDrive-CRM
- Issues: https://github.com/sheisjay001/EduDrive-CRM/issues

---

## Presentation Notes

### How to Use This Presentation

1. **Convert to Slides**: Use tools like:
   - Marp (Markdown Presentation Ecosystem)
   - Slidev
   - Reveal.js
   - Or export to PowerPoint/Google Slides

2. **Marp Example**:
```bash
npm install -g @marp/cli/marp-cli
marp PRESENTATION.md -o presentation.pdf
marp PRESENTATION.md -o presentation.pptx
```

3. **Customization**: 
   - Add your school's branding
   - Include screenshots of your implementation
   - Customize demo scenarios
   - Add deployment details

4. **Live Demo Tips**:
   - Prepare test accounts for each role
   - Have sample data ready
   - Test all scenarios beforehand
   - Prepare backup data

---

**End of Presentation**
