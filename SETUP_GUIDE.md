# ISM Integrated System - Setup & Deployment Guide

## System Overview

The ISM (Integrated School Management) system is a microservices-based architecture with the following components:

### Microservices
1. **Auth Service** (Port 8001) - User authentication and authorization
2. **Student Service** (Port 8005) - Student management and enrollment
3. **Curriculum Service** (Port 8002) - Course and curriculum management
4. **Finance Service** (Port 8004) - Financial management and billing
5. **Notification Service** (Port 8003) - Notification delivery
6. **Staff Service** (Port 8006) - Staff and HR management
7. **API Gateway** (Port 8000) - Central routing and API aggregation

### Database
- **PostgreSQL** 15 (Port 5432)
- Single shared database for all services

---

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- PostgreSQL client tools (optional, for manual database access)
- Git
- curl (for API testing)

---

## Quick Start (Docker)

### 1. Navigate to ISM Directory
```bash
cd /workspaces/ISM
```

### 2. Build and Start Services
```bash
# Build all services and start containers
docker-compose up -d

# Optionally, watch the logs
docker-compose logs -f
```

### 3. Verify Services are Running
```bash
# Check service status
docker-compose ps

# Test gateway health
curl http://localhost:8000/health
```

### 4. Seed Database with Sample Data
```bash
# Install requirements (if not already installed)
pip install -r requirements.txt

# Run seed script
python seed_db.py
```

Expected output:
```
🌱 Starting database seeding...
✓ Database tables created
✓ Created 3 users
✓ Created 15 students
✓ Created 45 enrollments
✓ Created 45 grades
✓ Created 20 staff members
✓ Created 5 departments
✓ Created 20 salary records
✓ Created 15 student accounts
✓ Created 38 invoices
✓ Created 19 payments
✓ Created 47 transactions
✓ Created 105 audit logs
✨ Database seeding completed successfully!
```

### 5. Access APIs
- Gateway: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`
- Auth Service Docs: `http://localhost:8001/docs`
- Student Service Docs: `http://localhost:8005/docs`

---

## Local Development Setup

### 1. Prerequisites
```bash
# Ensure Python 3.11+ is installed
python --version

# Install PostgreSQL (macOS)
brew install postgresql

# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
# macOS:
brew services start postgresql

# Ubuntu:
sudo systemctl start postgresql
```

### 2. Create Local Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql shell:
CREATE USER ism_user WITH PASSWORD 'ism_password';
CREATE DATABASE ism_db OWNER ism_user;
GRANT ALL PRIVILEGES ON DATABASE ism_db TO ism_user;
\q
```

### 3. Install Dependencies
```bash
cd /workspaces/ISM
pip install -r requirements.txt
```

### 4. Seed Database
```bash
# From ISM root directory
python seed_db.py
```

### 5. Start Services (Terminal 1)
```bash
# Auth Service
cd /workspaces/ISM/auth_service
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### 6. Start More Services (Additional Terminals)
```bash
# Terminal 2 - Student Service
cd /workspaces/ISM/student_service
python -m uvicorn main:app --host 0.0.0.0 --port 8005

# Terminal 3 - Curriculum Service
cd /workspaces/ISM/curriculum_service
python -m uvicorn main:app --host 0.0.0.0 --port 8002

# Terminal 4 - Finance Service
cd /workspaces/ISM/finance_service
python -m uvicorn main:app --host 0.0.0.0 --port 8004

# Terminal 5 - Notification Service
cd /workspaces/ISM/notification_service
python -m uvicorn main:app --host 0.0.0.0 --port 8003

# Terminal 6 - Staff Service
cd /workspaces/ISM/staff_service
python -m uvicorn main:app --host 0.0.0.0 --port 8006

# Terminal 7 - Gateway Service
cd /workspaces/ISM/gateway_service
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Database Management

### Connect to Database
```bash
# Using psql
psql -U ism_user -h localhost -d ism_db

# Using docker
docker exec -it ism_postgres psql -U ism_user -d ism_db
```

### Reset Database
```bash
# Drop all tables and recreate
python -c "from db import drop_db, init_db; drop_db(); init_db(); print('Database reset')"

# Reseed with data
python seed_db.py
```

### Backup Database
```bash
# Backup to file
docker exec ism_postgres pg_dump -U ism_user ism_db > ism_db_backup.sql

# Local PostgreSQL
pg_dump -U ism_user -h localhost ism_db > ism_db_backup.sql
```

### Restore Database
```bash
# From backup
docker exec -i ism_postgres psql -U ism_user ism_db < ism_db_backup.sql
```

---

## API Testing

### Using curl

#### Test Gateway Health
```bash
curl -X GET http://localhost:8000/health
```

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ism.edu.ke",
    "full_name": "Test User",
    "password": "testpass123"
  }'
```

#### Login User
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ism.edu.ke",
    "password": "admin123"
  }'
```

#### List Students
```bash
curl -X GET "http://localhost:8000/api/students?skip=0&limit=10"
```

### Using Postman

1. Import the API collection from `API_TEST_GUIDE.md`
2. Set environment variables:
   - `base_url`: `http://localhost:8000`
   - `auth_token`: (set after login)
3. Test endpoints in order

---

## Docker Commands Reference

### Basic Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Remove volumes (DELETE data)
docker-compose down -v

# View service logs
docker-compose logs -f [service-name]

# View logs for specific service
docker-compose logs -f student_service

# Rebuild services
docker-compose build

# Build and start
docker-compose up -d --build
```

### Service-Specific Commands
```bash
# Enter service container
docker exec -it ism_student_service /bin/bash

# Run command in service
docker exec ism_postgres psql -U ism_user -d ism_db -c "SELECT COUNT(*) FROM students;"

# Check service status
docker-compose ps

# View resource usage
docker stats
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Rebuild containers
docker-compose build [service-name]
docker-compose up -d [service-name]
```

### Database Connection Issues
```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check database connectivity
docker exec ism_postgres psql -U ism_user -c "SELECT 1"

# View PostgreSQL logs
docker logs ism_postgres
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 [PID]

# Or change port in docker-compose.yml
```

### Seed Script Fails
```bash
# Ensure database tables exist
python -c "from db import init_db; init_db()"

# Check database permissions
docker exec ism_postgres psql -U ism_user -d ism_db -c "\dt"

# Run seed with verbose output
python seed_db.py
```

---

## Environment Variables

Create `.env` file in project root:
```env
# Database
DATABASE_URL=postgresql://ism_user:ism_password@localhost:5432/ism_db

# Services
AUTH_SERVICE_URL=http://auth_service:8000
STUDENT_SERVICE_URL=http://student_service:8000
CURRICULUM_SERVICE_URL=http://curriculum_service:8000
FINANCE_SERVICE_URL=http://finance_service:8000
NOTIFICATION_SERVICE_URL=http://notification_service:8000
STAFF_SERVICE_URL=http://staff_service:8000

# Logging
LOG_LEVEL=INFO

# API
API_TITLE=ISM School Management System
API_VERSION=1.0.0
```

---

## Project Structure

```
ISM/
├── db.py                          # Shared database configuration
├── seed_db.py                     # Database seeding script
├── docker-compose.yml             # Docker Compose configuration
├── requirements.txt               # Python dependencies
├── API_TEST_GUIDE.md             # API documentation
├── SETUP_GUIDE.md                # This file
│
├── auth_service/                 # Authentication service
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── Dockerfile
│   └── README.md
│
├── student_service/              # Student management service
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── Dockerfile
│   └── README.md
│
├── curriculum_service/           # Curriculum management
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── Dockerfile
│   └── README.md
│
├── finance_service/              # Financial management
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── Dockerfile
│   └── README.md
│
├── notification_service/         # Notification delivery
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── Dockerfile
│   └── README.md
│
├── staff_service/                # Staff & HR management
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── Dockerfile
│   └── README.md
│
└── gateway_service/              # API Gateway
    ├── main.py
    ├── Dockerfile
    └── README.md
```

---

## Performance Tips

1. **Connection Pooling**: Uses SQLAlchemy connection pooling by default
2. **Indexes**: Database tables have indexes on foreign keys and frequently queried fields
3. **Caching**: Consider implementing Redis for frequently accessed data
4. **Load Balancing**: Use Nginx or load balancer for multiple gateway instances

---

## Security Considerations

1. **Authentication**: Implement JWT tokens for API security
2. **HTTPS**: Use HTTPS in production (not http)
3. **Environment Variables**: Never commit credentials to git
4. **Database**: Change default credentials in production
5. **CORS**: Configure CORS properly for your domain
6. **Rate Limiting**: Implement rate limiting on gateway
7. **Input Validation**: All inputs validated by Pydantic

---

## Monitoring

### Health Checks
All services expose `/health` endpoint:
```bash
curl http://localhost:[PORT]/health
```

### Logs
```bash
# Gateway logs
docker-compose logs -f gateway_service

# All service logs
docker-compose logs -f

# Specific lines
docker-compose logs --tail=50 student_service
```

### Metrics
Consider adding Prometheus and Grafana for:
- Request latency
- Error rates
- Database connection pool
- Memory usage

---

## Next Steps

1. ✅ Run `docker-compose up -d` to start all services
2. ✅ Run `python seed_db.py` to populate database
3. ✅ Test APIs using curl or Postman (see API_TEST_GUIDE.md)
4. ✅ Access interactive docs at `http://localhost:8000/api/docs`
5. Implement authentication middleware
6. Add API rate limiting
7. Set up monitoring and logging
8. Deploy to production infrastructure

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs [service]`
2. Review API_TEST_GUIDE.md for examples
3. Check service README.md files
4. Verify database connectivity
5. Review error messages carefully

---

Last Updated: March 2026
Version: 1.0.0
