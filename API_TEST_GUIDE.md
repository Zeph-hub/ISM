# ISM System - API Test Collection

This document contains all the API endpoints for testing the ISM system with sample requests and responses.

## Base URL
- Gateway: `http://localhost:8000`
- Auth Service: `http://localhost:8001`
- Curriculum Service: `http://localhost:8002`
- Notification Service: `http://localhost:8003`
- Finance Service: `http://localhost:8004`
- Student Service: `http://localhost:8005`
- Staff Service: `http://localhost:8006`

## Gateway Health Check

### Check Gateway Health
```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "gateway": "healthy",
  "services": {
    "auth": {...},
    "student": {...},
    "curriculum": {...},
    "finance": {...},
    "notification": {...},
    "staff": {...}
  }
}
```

## Authentication Endpoints

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@ism.edu.ke",
    "full_name": "New User",
    "password": "securepassword123"
  }'
```

### Login User
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ism.edu.ke",
    "password": "admin123"
  }'
```

### Get All Users
```bash
curl -X GET http://localhost:8000/api/auth/users
```

### Get Specific User
```bash
curl -X GET http://localhost:8000/api/auth/users/1
```

### Get Audit Logs
```bash
curl -X GET "http://localhost:8000/api/auth/audit-logs?user_id=1&action=login"
```

## Student Endpoints

### List Students
```bash
curl -X GET "http://localhost:8000/api/students?skip=0&limit=10"
```

Response:
```json
{
  "total": 15,
  "students": [
    {
      "id": 1,
      "email": "student1@ism.edu.ke",
      "full_name": "Student 1 Kemboi",
      "student_id": "STU-1001",
      "phone": "+254700100000",
      "address": "P.O. Box 1000, Eldoret",
      "status": "active",
      "enrollment_date": "2024-01-15T10:30:00",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Create Student
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newendstudent@ism.edu.ke",
    "full_name": "New End Student",
    "student_id": "STU-9999",
    "phone": "+254700999999",
    "address": "New Address"
  }'
```

### Get Student by ID
```bash
curl -X GET http://localhost:8000/api/students/1
```

### Get Student Profile (with enrollments and grades)
```bash
curl -X GET http://localhost:8000/api/students/1/profile
```

### Update Student
```bash
curl -X PUT http://localhost:8000/api/students/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+254700111111"
  }'
```

## Curriculum Endpoints

### List Courses
```bash
curl -X GET "http://localhost:8000/api/curriculum/courses?skip=0&limit=10"
```

### Create Course
```bash
curl -X POST http://localhost:8000/api/curriculum/courses \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ENG101",
    "title": "English Literature",
    "description": "Introduction to English Literature",
    "credits": 3
  }'
```

### Get Course
```bash
curl -X GET http://localhost:8000/api/curriculum/courses/1
```

### List Curriculums
```bash
curl -X GET http://localhost:8000/api/curriculums
```

## Finance Endpoints

### Get Student Account
```bash
curl -X GET http://localhost:8000/api/finance/accounts/1
```

Response:
```json
{
  "id": 1,
  "student_id": 1,
  "balance": 15000.50,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### List Invoices
```bash
curl -X GET "http://localhost:8000/api/finance/invoices?student_id=1&skip=0&limit=10"
```

Response:
```json
{
  "total": 3,
  "invoices": [
    {
      "id": 1,
      "invoice_number": "INV-001001",
      "student_id": 1,
      "amount": 35000.00,
      "description": "Tuition fee - Term 1",
      "due_date": "2024-02-15T10:30:00",
      "status": "issued",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Create Invoice
```bash
curl -X POST http://localhost:8000/api/finance/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "amount": 50000,
    "description": "Tuition Fee - Term 2",
    "due_date": "2024-03-15T00:00:00"
  }'
```

### Get Financial Summary
```bash
curl -X GET http://localhost:8000/api/finance/reports/summary
```

## Notification Endpoints

### List Notifications
```bash
curl -X GET "http://localhost:8000/api/notifications?user_id=1&unread_only=false&skip=0&limit=10"
```

Response:
```json
{
  "total": 25,
  "notifications": [
    {
      "id": 1,
      "recipient_id": 1,
      "title": "Grade Posted",
      "content": "Your grades have been posted",
      "notification_type": "email",
      "priority": "normal",
      "status": "sent",
      "read": false,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Send Notification
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

## Staff Endpoints

### List Staff
```bash
curl -X GET "http://localhost:8000/api/staff?skip=0&limit=10"
```

Response:
```json
{
  "total": 20,
  "staff": [
    {
      "id": 1,
      "email": "staff1@ism.edu.ke",
      "full_name": "Staff Member 1",
      "employee_id": "EMP-2001",
      "phone": "+254700200000",
      "role": "teacher",
      "department_id": 1,
      "hire_date": "2022-01-15T00:00:00",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### Create Staff
```bash
curl -X POST http://localhost:8000/api/staff \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstaff@ism.edu.ke",
    "full_name": "New Staff Member",
    "employee_id": "EMP-9999",
    "phone": "+254700999999",
    "role": "teacher",
    "department_id": 1,
    "hire_date": "2024-01-15"
  }'
```

### Get Staff
```bash
curl -X GET http://localhost:8000/api/staff/1
```

## Database Credentials

### PostgreSQL Connection
- Host: `localhost` (or `postgres` in Docker)
- Port: `5432`
- Username: `ism_user`
- Password: `ism_password`
- Database: `ism_db`

### Connection String
```
postgresql://ism_user:ism_password@localhost:5432/ism_db
```

## Testing with Docker

### Start all services
```bash
docker-compose up -d
```

### Stop all services
```bash
docker-compose down
```

### View service logs
```bash
docker-compose logs -f [service-name]
```

### Seed database with dummy data
```bash
python seed_db.py
```

## Common Response Codes

| Code | Meaning |
|------|---------|
| 200  | OK - Request successful |
| 201  | Created - Resource created successfully |
| 400  | Bad Request - Invalid input |
| 401  | Unauthorized - Missing or invalid authentication |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource not found |
| 500  | Server Error - Internal server error |

## Data Models

### Student
- `id`: Unique identifier
- `email`: Student email
- `full_name`: Full name
- `student_id`: Unique student ID (STU-XXXX)
- `phone`: Phone number
- `address`: Physical address
- `status`: ACTIVE, INACTIVE, GRADUATED, SUSPENDED
- `enrollment_date`: Date of first enrollment
- `created_at`: Record creation timestamp

### Invoice
- `id`: Unique identifier
- `invoice_number`: Unique invoice number (INV-XXXXXX)
- `student_id`: Associated student
- `amount`: Amount in KES
- `description`: Invoice description
- `due_date`: Payment due date
- `status`: DRAFT, ISSUED, PAID, OVERDUE, CANCELLED
- `created_at`: Record creation timestamp

### Notification
- `id`: Unique identifier
- `recipient_id`: User receiving notification
- `title`: Notification title
- `content`: Notification content
- `notification_type`: EMAIL, SMS, IN_APP, PUSH
- `priority`: LOW, NORMAL, HIGH, URGENT
- `status`: PENDING, SENT, FAILED, DELIVERED, READ
- `created_at`: Record creation timestamp

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Currency amounts are in Kenyan Shillings (KES)
- Phone numbers should include country code (+254)
- Database seeding creates 15 students, 20 staff members, and sample transactions
- All services use PostgreSQL for persistent data storage
