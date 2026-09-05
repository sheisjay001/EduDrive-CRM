# EduDrive CRM - Frontend Pages Reference

**Production URL:** https://edudrive-crm.onrender.com/

---

## 📋 Table of Contents

- [Public Pages](#-public-pages)
- [Dashboard Pages](#-dashboard-pages-9-role-specific)
- [Academic Management](#-academic-management)
- [Financial Management](#-financial-management)
- [Admissions & Enrollment](#-admissions--enrollment)
- [Communications](#-communications)
- [Help Desk & Support](#-help-desk--support)
- [Transportation](#-transportation)
- [Operations](#-operations)
- [Staff Management](#-staff-management)
- [Analytics & Reporting](#-analytics--reporting)
- [Settings](#-settings)
- [Dynamic Routes](#-dynamic-routes)

---

## 🏠 Public Pages

| Route | URL | Description |
|-------|-----|-------------|
| `/` | https://edudrive-crm.onrender.com/ | Landing page - Main homepage |
| `/login` | https://edudrive-crm.onrender.com/login | User login page |
| `/signup` | https://edudrive-crm.onrender.com/signup | User registration page |
| `/forgot-password` | https://edudrive-crm.onrender.com/forgot-password | Password reset request |
| `/reset-password` | https://edudrive-crm.onrender.com/reset-password | Password reset confirmation |
| `/parent-login` | https://edudrive-crm.onrender.com/parent-login | Dedicated parent login |
| `/student-login` | https://edudrive-crm.onrender.com/student-login | Dedicated student login |

---

## 📊 Dashboard Pages (9 Role-Specific)

| Route | URL | Description |
|-------|-----|-------------|
| `/dashboard` | https://edudrive-crm.onrender.com/dashboard | Main dashboard (role-based) |
| `/dashboard/parent` | https://edudrive-crm.onrender.com/dashboard/parent | Parent portal dashboard |
| `/dashboard/student` | https://edudrive-crm.onrender.com/dashboard/student | Student portal dashboard |
| `/dashboard/teacher` | https://edudrive-crm.onrender.com/dashboard/teacher | Teacher dashboard |
| `/dashboard/school-admin` | https://edudrive-crm.onrender.com/dashboard/school-admin | School admin dashboard |
| `/dashboard/super-admin` | https://edudrive-crm.onrender.com/dashboard/super-admin | Super admin dashboard |
| `/dashboard/bursar` | https://edudrive-crm.onrender.com/dashboard/bursar | Finance/bursar dashboard |
| `/dashboard/helpdesk` | https://edudrive-crm.onrender.com/dashboard/helpdesk | Help desk dashboard |
| `/dashboard/admissions` | https://edudrive-crm.onrender.com/dashboard/admissions | Admissions dashboard |

---

## 🎓 Academic Management

| Route | URL | Description |
|-------|-----|-------------|
| `/students` | https://edudrive-crm.onrender.com/students | Student management (CRUD, import) |
| `/families` | https://edudrive-crm.onrender.com/families | Family management |
| `/families/[familyId]` | https://edudrive-crm.onrender.com/families/{id} | Family details page |
| `/settings/classes` | https://edudrive-crm.onrender.com/settings/classes | Class structure management (includes timetable upload) |
| `/settings/terms` | https://edudrive-crm.onrender.com/settings/terms | Academic term/session setup |

---

## 💰 Financial Management

| Route | URL | Description |
|-------|-----|-------------|
| `/finance` | https://edudrive-crm.onrender.com/finance | Financial operations overview |
| `/finance/fee-structures` | https://edudrive-crm.onrender.com/finance/fee-structures | Fee structure configuration |
| `/finance/invoices/[invoiceId]` | https://edudrive-crm.onrender.com/finance/invoices/{id} | Invoice details and payments |
| `/finance/debtors` | https://edudrive-crm.onrender.com/finance/debtors | Debtors management |
| `/finance/payments` | https://edudrive-crm.onrender.com/finance/payments | Payment processing |

---

## 👨‍👩‍👧‍👦 Admissions & Enrollment

| Route | URL | Description |
|-------|-----|-------------|
| `/admissions` | https://edudrive-crm.onrender.com/admissions | Admissions pipeline/leads |
| `/admissions/[leadId]` | https://edudrive-crm.onrender.com/admissions/{id} | Lead details and management |
| `/admissions/calendar` | https://edudrive-crm.onrender.com/admissions/calendar | Admissions calendar |
| `/admissions/leads/[leadId]` | https://edudrive-crm.onrender.com/admissions/leads/{id} | Lead detail view |
| `/admissions/lost-leads` | https://edudrive-crm.onrender.com/admissions/lost-leads | Lost lead tracking |

---

## 📞 Communications

| Route | URL | Description |
|-------|-----|-------------|
| `/messaging` | https://edudrive-crm.onrender.com/messaging | Messaging center overview (includes school notifications) |
| `/messaging/templates` | https://edudrive-crm.onrender.com/messaging/templates | Message templates management |
| `/messaging/broadcasts` | https://edudrive-crm.onrender.com/messaging/broadcasts | Broadcast messaging |
| `/reminders` | https://edudrive-crm.onrender.com/reminders | Reminder queue management |

---

## 🎫 Help Desk & Support

| Route | URL | Description |
|-------|-----|-------------|
| `/helpdesk` | https://edudrive-crm.onrender.com/helpdesk | Help desk tickets list |
| `/helpdesk/[ticketId]` | https://edudrive-crm.onrender.com/helpdesk/{id} | Ticket details and management |

---

## 🚌 Transportation

| Route | URL | Description |
|-------|-----|-------------|
| `/settings/bus-routes` | https://edudrive-crm.onrender.com/settings/bus-routes | Bus routes and vehicle management |

---

## 🏢 Operations

| Route | URL | Description |
|-------|-----|-------------|
| `/frontdesk` | https://edudrive-crm.onrender.com/frontdesk | Front desk operations |
| `/activity` | https://edudrive-crm.onrender.com/activity | Activity audit log |

---

## 👥 Staff Management

| Route | URL | Description |
|-------|-----|-------------|
| `/staff` | https://edudrive-crm.onrender.com/staff | Staff overview |
| `/staff/administration` | https://edudrive-crm.onrender.com/staff/administration | User administration & permissions |
| `/staff/workload` | https://edudrive-crm.onrender.com/staff/workload | Staff workload indicators |

---

## 📊 Analytics & Reporting

| Route | URL | Description |
|-------|-----|-------------|
| `/analytics` | https://edudrive-crm.onrender.com/analytics | Analytics dashboard |
| `/reports` | https://edudrive-crm.onrender.com/reports | Reports center |

---

## 🔧 Settings

| Route | URL | Description |
|-------|-----|-------------|
| `/settings` | https://edudrive-crm.onrender.com/settings | System settings overview (includes PIN management) |

---

## 📱 Dynamic Routes

| Route | URL | Description |
|-------|-----|-------------|
| `/[schoolSlug]` | https://edudrive-crm.onrender.com/{school} | School-specific landing page |
| `/students/[studentId]` | https://edudrive-crm.onrender.com/students/{id} | Student details |
| `/students/[studentId]/lifecycle` | https://edudrive-crm.onrender.com/students/{id}/lifecycle | Student lifecycle management |

---

## 📊 Summary

**Total Pages:** 45

**Categories:**
- Public Pages: 7
- Dashboard Pages: 9
- Academic Management: 5
- Financial Management: 5
- Admissions & Enrollment: 5
- Communications: 4
- Help Desk & Support: 2
- Transportation: 1
- Operations: 2
- Staff Management: 3
- Analytics & Reporting: 2
- Settings: 1
- Dynamic Routes: 3

---

## 🔗 Quick Access by Role

### **School Admin**
- `/dashboard/super-admin`
- `/dashboard/school-admin`
- `/settings`
- `/staff/administration`
- `/analytics`
- `/reports`

### **Staff (Finance/Bursar)**
- `/dashboard/bursar`
- `/finance`
- `/finance/fee-structures`
- `/finance/debtors`
- `/finance/payments`

### **Staff (Admissions)**
- `/dashboard/admissions`
- `/admissions`
- `/admissions/calendar`
- `/admissions/lost-leads`
- `/messaging/templates`
- `/messaging/broadcasts`

### **Staff (Academic)**
- `/students`
- `/settings/classes`
- `/settings/terms`
- `/families`

### **Staff (Help Desk)**
- `/dashboard/helpdesk`
- `/helpdesk`
- `/activity`

### **Staff (Operations/Transport)**
- `/settings/bus-routes`
- `/frontdesk`

### **Teacher**
- `/dashboard/teacher` (includes My Students, Attendance, CSV Results Upload)
- `/students`
- `/staff/workload`

### **Parent**
- `/dashboard/parent`
- `/families/[familyId]`
- `/finance/payments`
- `/helpdesk`

### **Student**
- `/dashboard/student` (includes CBT Exams, Results Check with PIN)
- `/students/[studentId]`
- `/helpdesk`

---

**EduDrive CRM - Production URL: https://edudrive-crm.onrender.com/**
