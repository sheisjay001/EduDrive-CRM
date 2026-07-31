# Role-Based Login Guide for EduDrive CRM

## How Different Roles Login

All roles use the same login process but have different permissions and access levels based on their assigned role in the system.

## Login Process

### 1. Access the Login Page
Navigate to: `https://your-domain.com/login` or `http://localhost:3000/login`

### 2. Enter Credentials
All users login with:
- **Email**: Their registered school email address
- **Password**: Their assigned password

### 3. Authentication Flow
1. Frontend sends credentials to backend API
2. Backend validates credentials against the database
3. Backend returns JWT access token and refresh token
4. Frontend stores tokens and user information
5. User is redirected to dashboard based on their role

## Role-Specific Access After Login

### Super Admin (Proprietor/Board)
**Email Example:** `admin@greenfieldcollege.ng`

**After Login:**
- Full access to all modules
- Can view financial reports across all branches
- Can manage staff accounts and permissions
- Can access system settings
- Can view all student and family records
- Full dashboard visibility

**Accessible Pages:**
- Dashboard (full metrics)
- Admissions (full pipeline)
- Families (all records)
- Students (all records)
- Finance (full access)
- Messaging (all features)
- Helpdesk (all tickets)
- Staff (management)
- Reports (all reports)
- Settings (full configuration)

---

### Admissions Officer
**Email Example:** `admissions@greenfieldcollege.ng`

**After Login:**
- Can manage leads and inquiries
- Can schedule school tours
- Can log prospective parent inquiries
- Can view parent information
- Limited dashboard access

**Accessible Pages:**
- Dashboard (admissions metrics only)
- Admissions (full pipeline management)
- Parents (view only)
- Messaging (send admissions communications)

**Restricted Access:**
- Cannot access financial data
- Cannot access staff management
- Cannot access system settings
- Cannot view full reports

---

### Bursar/Accounts Manager
**Email Example:** `bursar@greenfieldcollege.ng`

**After Login:**
- Can view fee statuses
- Can log payment records
- Can issue receipts
- Can trigger automated fee reminders
- Can view student records (for billing purposes)

**Accessible Pages:**
- Dashboard (financial metrics only)
- Finance (full access)
- Students (view for billing)
- Messaging (send payment reminders)

**Restricted Access:**
- Cannot access admissions pipeline
- Cannot access staff management
- Cannot access system settings
- Cannot view helpdesk tickets

---

### Teacher/Class Supervisor
**Email Example:** `teacher@greenfieldcollege.ng`

**After Login:**
- Can log student attendance
- Can input daily behavioral notes
- Can input academic notes
- Can trigger parent notifications
- Can view assigned students
- Can view parent information

**Accessible Pages:**
- Dashboard (class-specific metrics)
- Students (assigned students only)
- Parents (view student parents)
- Messaging (send parent communications)

**Restricted Access:**
- Cannot access financial data
- Cannot access admissions pipeline
- Cannot access staff management
- Cannot access system settings
- Cannot view full reports

---

## Permission Enforcement

### Backend Protection
All API endpoints have permission checks:
```python
if not has_permission(current_user, "finance:view"):
    raise HTTPException(status_code=403, detail="Permission denied")
```

### Frontend Protection
Frontend should also hide/show navigation items based on user role:
```typescript
if (user.role === 'teacher') {
  // Show only teacher-relevant menu items
}
```

## Creating Users with Different Roles

### Via Backend (Seed Script)
Run the seed script to create users with different roles:
```bash
cd backend
python seed_db.py
```

### Via Database
Insert users directly into the database with appropriate role_id:
```sql
INSERT INTO users (id, school_id, role_id, full_name, email, password_hash)
VALUES (
    uuid_generate_v4(),
    (SELECT id FROM schools LIMIT 1),
    (SELECT id FROM roles WHERE name = 'teacher'),
    'John Teacher',
    'teacher@greenfieldcollege.ng',
    'hashed_password_here'
);
```

## Demo Credentials

For testing purposes, the following demo credentials are pre-filled on the login page:

**Super Admin:**
- Email: `admin@greenfieldcollege.ng`
- Password: `password123`

**Note:** In production, each user will have their own unique credentials assigned by the school administrator.

## Security Notes

1. **Tokens:** JWT tokens are stored in localStorage and sent with each API request
2. **Session Expiry:** Access tokens expire after 1 hour, refresh tokens after 7 days
3. **Automatic Refresh:** The frontend automatically refreshes tokens when they expire
4. **Role Validation:** The backend validates permissions on every request
5. **School Isolation:** Users can only access data from their own school

## Troubleshooting

### Login Issues
- Verify email and password are correct
- Check that user account status is 'active'
- Ensure user has a valid role assigned

### Access Denied Errors
- Verify user has the required permissions
- Check that role permissions are correctly configured
- Ensure the user belongs to the correct school

### Permission Changes
- Contact Super Admin to modify user roles
- Role changes require re-login to take effect
