#!/bin/bash

# ISM System Setup Script
# This script automates the setup of the ISM system

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Main setup
print_header "ISM System Setup"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker found"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose found"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi
print_success "Python 3 found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_warning "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# Install Python dependencies
print_header "Installing Python Dependencies"
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt > /dev/null 2>&1
print_success "Python dependencies installed"

# Build Docker images
print_header "Building Docker Images"
docker-compose build --no-cache
print_success "Docker images built"

# Start containers
print_header "Starting Docker Containers"
docker-compose up -d
print_success "Docker containers started"

# Wait for database to be ready
print_header "Waiting for Database to be Ready"
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker exec ism_postgres pg_isready -U ism_user -d ism_db > /dev/null 2>&1; then
        print_success "Database is ready"
        break
    fi
    
    echo -ne "Attempt $attempt/$max_attempts... \r"
    sleep 1
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Database failed to start after $max_attempts attempts"
    exit 1
fi

# Seed database
print_header "Seeding Database with Sample Data"
python3 seed_db.py
print_success "Database seeded successfully"

# Verify services are running
print_header "Verifying Services"
services=("ism_postgres" "ism_auth_service" "ism_student_service" "ism_curriculum_service" "ism_finance_service" "ism_notification_service" "ism_staff_service" "ism_gateway")

for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        print_success "$service is running"
    else
        print_error "$service is not running"
    fi
done

# Test gateway health
print_header "Testing Gateway Health"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Gateway is responding to health checks"
else
    print_warning "Gateway health check failed - services may still be starting"
fi

# Print summary
print_header "Setup Complete!"

echo -e "${GREEN}ISM System is now running!${NC}\n"
echo "Access Points:"
echo "  • API Gateway: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/api/docs"
echo "  • Auth Service: http://localhost:8001"
echo "  • Curriculum Service: http://localhost:8002"
echo "  • Notification Service: http://localhost:8003"
echo "  • Finance Service: http://localhost:8004"
echo "  • Student Service: http://localhost:8005"
echo "  • Staff Service: http://localhost:8006"
echo ""
echo "Database:"
echo "  • Host: localhost:5432"
echo "  • Username: ism_user"
echo "  • Password: ism_password"
echo "  • Database: ism_db"
echo ""
echo "Next Steps:"
echo "  1. Test APIs using curl or Postman (see API_TEST_GUIDE.md)"
echo "  2. Access the interactive API docs at http://localhost:8000/api/docs"
echo "  3. Review SETUP_GUIDE.md for detailed information"
echo "  4. Check service-specific docs in each service directory"
echo ""
echo "Useful Commands:"
echo "  • View logs: docker-compose logs -f [service-name]"
echo "  • Stop services: docker-compose down"
echo "  • Reset database: python3 seed_db.py (after dropping tables)"
echo "  • Enter database: docker exec -it ism_postgres psql -U ism_user -d ism_db"
echo ""

print_success "Setup completed successfully!"
