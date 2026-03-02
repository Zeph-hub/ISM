# ISM System - Complete API Endpoint Reference

## Base URL
- **Gateway**: `http://localhost:8000`
- **Gateway Docs**: `http://localhost:8000/api/docs`

---

## 🔐 Authentication Endpoints

### POST /api/auth/register
Register a new user account
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@ism.edu.ke",
    "full_name": "New User",
    "password": "securepassword"
  }'
```

### POST /api/auth/login
Authenticate and get tokens
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ism.edu.ke",
    "password": "admin123"
  }'
```

### GET /api/auth/users
List all users
```bash
curl -X GET http://localhost:8000/api/auth/users
```

### GET /api/auth/users/{user_id}
Get specific user
```bash
curl -X GET http://localhost:8000/api/auth/users/1
```

### GET /api/auth/audit-logs
Get audit logs with optional filters
```bash
# All logs
curl -X GET http://localhost:8000/api/auth/audit-logs

# Specific user
curl -X GET "http://localhost:8000/api/auth/audit-logs?user_id=1"

# Specific action
curl -X GET "http://localhost:8000/api/auth/audit-logs?action=login"
```

---

## 👥 Student Management Endpoints

### GET /api/students
List all students with pagination
```bash
curl -X GET "http://localhost:8000/api/students?skip=0&limit=10"
```

### POST /api/students
Create new student
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstudent@ism.edu.ke",
    "full_name": "New Student",
    "student_id": "STU-9999",
    "phone": "+254700999999",
    "address": "Home Address"
  }'
```

### GET /api/students/{student_id}
Get specific student details
```bash
curl -X GET http://localhost:8000/api/students/1
```

### GET /api/students/{student_id}/profile
Get student profile with enrollments and grades
```bash
curl -X GET http://localhost:8000/api/students/1/profile
```

### PUT /api/students/{student_id}
Update student information
```bash
curl -X PUT http://localhost:8000/api/students/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+254700111111"
  }'
```

### GET /api/students/{student_id}/enrollments
List student course enrollments
```bash
curl -X GET http://localhost:8000/api/students/1/enrollments
```

### POST /api/students/{student_id}/enroll
Enroll student in a course
```bash
curl -X POST http://localhost:8000/api/students/1/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1
  }'
```

### GET /api/students/{student_id}/grades
Get student grades
```bash
curl -X GET http://localhost:8000/api/students/1/grades
```

### GET /api/students/{student_id}/gpa
Get student GPA
```bash
curl -X GET http://localhost:8000/api/students/1/gpa
```

---

## 📚 Curriculum Endpoints

### GET /api/curriculum/courses
List all courses
```bash
curl -X GET "http://localhost:8000/api/curriculum/courses?skip=0&limit=10"
```

### POST /api/curriculum/courses
Create new course
```bash
curl -X POST http://localhost:8000/api/curriculum/courses \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MATH101",
    "title": "Mathematics I",
    "description": "Introduction to Mathematics",
    "credits": 3
  }'
```

### GET /api/curriculum/courses/{course_id}
Get specific course
```bash
curl -X GET http://localhost:8000/api/curriculum/courses/1
```

### GET /api/curriculums
List all curriculums
```bash
curl -X GET http://localhost:8000/api/curriculums
```

### GET /api/curriculum/cbc
Get CBC curriculum details
```bash
curl -X GET http://localhost:8000/api/curriculum/cbc
```

---

## 💰 Finance Endpoints

### GET /api/finance/accounts/{student_id}
Get student financial account
```bash
curl -X GET http://localhost:8000/api/finance/accounts/1
```

### GET /api/finance/invoices
List invoices with optional filters
```bash
# All invoices
curl -X GET "http://localhost:8000/api/finance/invoices?skip=0&limit=10"

# Student invoices
curl -X GET "http://localhost:8000/api/finance/invoices?student_id=1"
```

### POST /api/finance/invoices
Create new invoice
```bash
curl -X POST http://localhost:8000/api/finance/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "amount": 50000,
    "description": "Tuition Fee - Term 1",
    "due_date": "2024-03-15T00:00:00"
  }'
```

### GET /api/finance/invoices/{invoice_id}
Get specific invoice
```bash
curl -X GET http://localhost:8000/api/finance/invoices/1
```

### POST /api/finance/invoices/{invoice_id}/payments
Record payment for invoice
```bash
curl -X POST http://localhost:8000/api/finance/invoices/1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "payment_method": "bank_transfer",
    "transaction_id": "TXN-123456"
  }'
```

### GET /api/finance/payments
List all payments
```bash
curl -X GET "http://localhost:8000/api/finance/payments?skip=0&limit=10"
```

### GET /api/finance/transactions
List financial transactions
```bash
# All transactions
curl -X GET "http://localhost:8000/api/finance/transactions?skip=0&limit=10"

# Student transactions
curl -X GET "http://localhost:8000/api/finance/transactions?student_id=1"
```

### POST /api/finance/transactions
Create financial transaction
```bash
curl -X POST http://localhost:8000/api/finance/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "transaction_type": "tuition",
    "amount": 50000,
    "description": "Tuition payment"
  }'
```

### GET /api/finance/reports/summary
Get financial summary report
```bash
curl -X GET http://localhost:8000/api/finance/reports/summary
```

### GET /api/finance/reports/students
Get comprehensive student financial reports
```bash
curl -X GET "http://localhost:8000/api/finance/reports/students?skip=0&limit=10"
```

---

## 🔔 Notification Endpoints

### GET /api/notifications
List notifications with filters
```bash
# All notifications
curl -X GET "http://localhost:8000/api/notifications?skip=0&limit=10"

# User notifications
curl -X GET "http://localhost:8000/api/notifications?user_id=1"

# Unread only
curl -X GET "http://localhost:8000/api/notifications?unread_only=true"
```

### POST /api/notifications
Send notification
```bash
curl -X POST http://localhost:8000/api/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": 1,
    "title": "Important Announcement",
    "content": "Please check the portal for updates",
    "notification_type": "in_app",
    "priority": "high"
  }'
```

### GET /api/notifications/{notification_id}
Get specific notification
```bash
curl -X GET http://localhost:8000/api/notifications/1
```

### PUT /api/notifications/{notification_id}/read
Mark notification as read
```bash
curl -X PUT http://localhost:8000/api/notifications/1/read
```

### POST /api/notifications/bulk
Send bulk notifications
```bash
curl -X POST http://localhost:8000/api/notifications/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_ids": [1, 2, 3],
    "title": "System Announcement",
    "content": "All users message",
    "notification_type": "email"
  }'
```

---

## 👨‍💼 Staff Management Endpoints

### GET /api/staff
List all staff members
```bash
curl -X GET "http://localhost:8000/api/staff?skip=0&limit=10"
```

### POST /api/staff
Create new staff member
```bash
curl -X POST http://localhost:8000/api/staff \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstaff@ism.edu.ke",
    "full_name": "New Staff",
    "employee_id": "EMP-9999",
    "phone": "+254700999999",
    "role": "teacher",
    "department_id": 1,
    "hire_date": "2024-01-15"
  }'
```

### GET /api/staff/{staff_id}
Get specific staff member
```bash
curl -X GET http://localhost:8000/api/staff/1
```

### PUT /api/staff/{staff_id}
Update staff member
```bash
curl -X PUT http://localhost:8000/api/staff/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+254700111111"
  }'
```

### GET /api/staff/departments
List all departments
```bash
curl -X GET http://localhost:8000/api/staff/departments
```

### POST /api/staff/departments
Create department
```bash
curl -X POST http://localhost:8000/api/staff/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Department",
    "description": "Department description"
  }'
```

### GET /api/staff/{staff_id}/salary
Get staff salary information
```bash
curl -X GET http://localhost:8000/api/staff/1/salary
```

### POST /api/staff/{staff_id}/salary
Record salary
```bash
curl -X POST http://localhost:8000/api/staff/1/salary \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "effective_date": "2024-01-01"
  }'
```

### GET /api/staff/{staff_id}/absences
Get staff absences
```bash
curl -X GET http://localhost:8000/api/staff/1/absences
```

### POST /api/staff/{staff_id}/absence
Record absence
```bash
curl -X POST http://localhost:8000/api/staff/1/absence \
  -H "Content-Type: application/json" \
  -d '{
    "absence_date": "2024-02-15",
    "reason": "Medical appointment"
  }'
```

---

## 🏥 Health & Status Endpoints

### GET /
Gateway root - Service information
```bash
curl -X GET http://localhost:8000/
```

### GET /health
Gateway and all services health status
```bash
curl -X GET http://localhost:8000/health
```

### GET /{service}/health
Individual service health (replace service with port)
```bash
# Auth service health
curl -X GET http://localhost:8001/health

# Student service health
curl -X GET http://localhost:8005/health

# All services available on their respective ports
```

---

## 📊 Bulk Operations

### List with Pagination
All list endpoints support:
- `skip`: Offset (default: 0)
- `limit`: Page size (default: 10)

```bash
curl -X GET "http://localhost:8000/api/students?skip=20&limit=20"
```

### Filter Examples
Most endpoints support filtering:

```bash
# By status
curl -X GET "http://localhost:8000/api/finance/invoices?status=issued"

# By date range
curl -X GET "http://localhost:8000/api/finance/invoices?start_date=2024-01-01&end_date=2024-03-31"

# By user/student
curl -X GET "http://localhost:8000/api/notifications?user_id=1"
```

---

## Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET request successful |
| 201 | Created | POST request successful |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

---

## Data Models Quick Reference

### Student
```json
{
  "id": 1,
  "email": "student@ism.edu.ke",
  "full_name": "Student Name",
  "student_id": "STU-1001",
  "phone": "+254700100000",
  "address": "Address",
  "status": "active",
  "enrollment_date": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00"
}
```

### Invoice
```json
{
  "id": 1,
  "invoice_number": "INV-001001",
  "student_id": 1,
  "amount": 50000,
  "description": "Tuition Fee",
  "due_date": "2024-03-15T00:00:00",
  "status": "issued",
  "created_at": "2024-01-15T10:30:00"
}
```

### Notification
```json
{
  "id": 1,
  "recipient_id": 1,
  "title": "Grade Posted",
  "content": "Your grades are available",
  "notification_type": "email",
  "priority": "normal",
  "status": "sent",
  "read": false,
  "created_at": "2024-01-15T10:30:00"
}
```

---

## Common curl Options

```bash
# POST with JSON
curl -X POST http://localhost:8000/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# GET with query parameters
curl -X GET "http://localhost:8000/api/endpoint?param1=value1&param2=value2"

# PUT request
curl -X PUT http://localhost:8000/api/endpoint/1 \
  -H "Content-Type: application/json" \
  -d '{"key": "new_value"}'

# DELETE request
curl -X DELETE http://localhost:8000/api/endpoint/1

# With custom header
curl -X GET http://localhost:8000/api/endpoint \
  -H "Authorization: Bearer token"

# Pretty print JSON response
curl -X GET http://localhost:8000/api/endpoint | jq
```

---

## Using Interactive API Docs

1. Visit: http://localhost:8000/api/docs
2. Click on endpoint to expand
3. Click "Try it out"
4. Enter parameters/body
5. Click "Execute"
6. View response

---

## Testing with Postman

1. Import from URL or manually add collections
2. Set environment variable `base_url` = `http://localhost:8000`
3. Create requests for each endpoint
4. Test in order of dependencies

---

## Performance Tips

- Use appropriate pagination limits
- Filter when possible to reduce payload
- Cache frequently accessed data
- Use batch endpoints for bulk operations

---

## Troubleshooting

### 404 Not Found
- Check endpoint path spelling
- Verify service is running on correct port
- Check resource ID exists

### 400 Bad Request
- Verify JSON syntax
- Check required fields
- Validate data types

### 500 Server Error
- Check service logs: `docker-compose logs [service]`
- Verify database connectivity
- Check error message in response

---

**Generated**: March 2, 2026  
**API Version**: v1.0.0
