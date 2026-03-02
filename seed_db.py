"""
Database Seeding Script
Creates and populates the database with dummy data for testing
"""
import sys
import os
from datetime import datetime, timedelta
import random
import string
from bcrypt import hashpw, gensalt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import engine, SessionLocal, init_db, Base
from auth_service.models import UserORM, AuditLogORM, UserRole
from student_service.models import StudentORM, EnrollmentORM, GradeORM, StudentStatus
from staff_service.models import DepartmentORM, StaffORM, SalaryORM
from finance_service.models import (
    InvoiceORM, PaymentORM, TransactionORM, StudentAccountORM,
    InvoiceStatus, PaymentStatus, TransactionType
)


def generate_hash(password: str) -> str:
    """Generate bcrypt hash for password"""
    return hashpw(password.encode(), gensalt()).decode()


def seed_database():
    """Populate database with dummy data"""
    print("🌱 Starting database seeding...")
    
    # Initialize tables
    init_db()
    print("✓ Database tables created")
    
    db = SessionLocal()
    try:
        # ===== SEED USERS (Auth Service) =====
        print("\n📝 Seeding Auth Service...")
        users_data = [
            {
                "email": "admin@ism.edu.ke",
                "full_name": "Admin User",
                "password": "admin123",
                "role": UserRole.ADMIN,
            },
            {
                "email": "teacher1@ism.edu.ke",
                "full_name": "Mr. James Ochieng",
                "password": "teacher123",
                "role": UserRole.INSTRUCTOR,
            },
            {
                "email": "teacher2@ism.edu.ke",
                "full_name": "Ms. Sarah Kipchoge",
                "password": "teacher123",
                "role": UserRole.INSTRUCTOR,
            },
        ]
        
        users = []
        for user_data in users_data:
            user = UserORM(
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash=generate_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        print(f"✓ Created {len(users)} users")
        
        # ===== SEED STUDENTS (Student Service) =====
        print("\n👥 Seeding Student Service...")
        students = []
        student_base_id = 1001
        
        for i in range(15):
            student_id = f"STU-{student_base_id + i:04d}"
            student = StudentORM(
                email=f"student{i+1}@ism.edu.ke",
                full_name=f"Student {i+1} Kemboi",
                student_id=student_id,
                phone=f"+254700{100000 + i:06d}",
                address=f"P.O. Box {1000 + i}, Eldoret",
                status=StudentStatus.ACTIVE,
                enrollment_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        print(f"✓ Created {len(students)} students")
        
        # ===== SEED ENROLLMENTS =====
        print("\n📚 Seeding Enrollments...")
        enrollments = []
        course_ids = [1, 2, 3, 4, 5]  # Mock course IDs
        for student in students:
            num_courses = random.randint(3, 5)
            selected_courses = random.sample(course_ids, num_courses)
            for course_id in selected_courses:
                enrollment = EnrollmentORM(
                    student_id=student.id,
                    course_id=course_id,
                    enrollment_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                    status="active",
                )
                db.add(enrollment)
                enrollments.append(enrollment)
        
        db.commit()
        print(f"✓ Created {len(enrollments)} enrollments")
        
        # ===== SEED GRADES =====
        print("\n📊 Seeding Grades...")
        grades = []
        grade_mapping = {
            (90, 100): "A",
            (80, 89): "B",
            (70, 79): "C",
            (60, 69): "D",
            (0, 59): "E",
        }
        
        for student in students:
            for enrollment in student.enrollments:
                score = random.uniform(45, 95)
                letter_grade = next(
                    (v for (k_min, k_max), v in grade_mapping.items() if k_min <= score <= k_max),
                    "E"
                )
                grade = GradeORM(
                    student_id=student.id,
                    course_id=enrollment.course_id,
                    score=score,
                    letter_grade=letter_grade,
                    recorded_date=enrollment.enrollment_date + timedelta(days=90),
                )
                db.add(grade)
                grades.append(grade)
        
        db.commit()
        print(f"✓ Created {len(grades)} grades")
        
        # ===== SEED DEPARTMENTS (Staff Service) =====
        print("\n🏢 Seeding Staff Service...")
        departments_data = [
            {"name": "Academic Affairs", "description": "Teaching and learning management"},
            {"name": "Administration", "description": "General administration"},
            {"name": "Finance", "description": "Financial management"},
            {"name": "Student Support", "description": "Student welfare and support"},
            {"name": "ICT", "description": "Information and communications technology"},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept = DepartmentORM(
                name=dept_data["name"],
                description=dept_data["description"],
            )
            db.add(dept)
            departments.append(dept)
        
        db.commit()
        print(f"✓ Created {len(departments)} departments")
        
        # ===== SEED STAFF =====
        print("\n👨‍💼 Seeding Staff Members...")
        staff_roles = ["teacher", "accountant", "librarian", "admin", "support_staff"]
        staff_list = []
        staff_base_id = 2001
        
        for i in range(20):
            employee_id = f"EMP-{staff_base_id + i:04d}"
            dept = random.choice(departments)
            staff = StaffORM(
                email=f"staff{i+1}@ism.edu.ke",
                full_name=f"Staff Member {i+1}",
                employee_id=employee_id,
                phone=f"+254700{200000 + i:06d}",
                role=random.choice(staff_roles),
                department_id=dept.id,
                hire_date=datetime.utcnow() - timedelta(days=random.randint(365, 1825)),
                is_active=True,
            )
            db.add(staff)
            staff_list.append(staff)
        
        db.commit()
        print(f"✓ Created {len(staff_list)} staff members")
        
        # ===== SEED SALARIES =====
        print("\n💰 Seeding Salaries...")
        salaries = []
        for staff in staff_list:
            salary = SalaryORM(
                staff_id=staff.id,
                amount=random.uniform(30000, 80000),  # KES
                effective_date=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
            )
            db.add(salary)
            salaries.append(salary)
        
        db.commit()
        print(f"✓ Created {len(salaries)} salary records")
        
        # ===== SEED STUDENT ACCOUNTS (Finance Service) =====
        print("\n🏦 Seeding Finance Service...")
        accounts = []
        for student in students:
            account = StudentAccountORM(
                student_id=student.id,
                balance=random.uniform(-50000, 100000),  # Can have debt or credit
            )
            db.add(account)
            accounts.append(account)
        
        db.commit()
        print(f"✓ Created {len(accounts)} student accounts")
        
        # ===== SEED INVOICES =====
        print("\n📄 Seeding Invoices...")
        invoices = []
        invoice_counter = 1001
        
        for account in accounts:
            num_invoices = random.randint(1, 4)
            for j in range(num_invoices):
                invoice_num = f"INV-{invoice_counter:06d}"
                invoice_counter += 1
                
                amount = random.uniform(10000, 50000)  # KES
                created = datetime.utcnow() - timedelta(days=random.randint(0, 180))
                
                # Determine status based on date
                days_since_due = random.randint(-30, 120)
                if days_since_due > 0:
                    status = InvoiceStatus.OVERDUE if days_since_due > 30 else InvoiceStatus.ISSUED
                else:
                    status = random.choice([InvoiceStatus.ISSUED, InvoiceStatus.DRAFT])
                
                invoice = InvoiceORM(
                    invoice_number=invoice_num,
                    student_id=account.student_id,
                    amount=amount,
                    description=f"Tuition fee - Term {j+1}",
                    due_date=created + timedelta(days=30),
                    status=status,
                    created_at=created,
                )
                db.add(invoice)
                invoices.append(invoice)
        
        db.commit()
        print(f"✓ Created {len(invoices)} invoices")
        
        # ===== SEED PAYMENTS =====
        print("\n✅ Seeding Payments...")
        payments = []
        payment_methods = ["bank_transfer", "cash", "cheque", "mobile_money"]
        
        for invoice in invoices[:len(invoices)//2]:  # Only half of invoices are paid
            if invoice.status != InvoiceStatus.DRAFT:
                payment = PaymentORM(
                    invoice_id=invoice.id,
                    amount=invoice.amount * random.uniform(0.5, 1.0),
                    payment_method=random.choice(payment_methods),
                    transaction_id=f"TXN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}",
                    status=PaymentStatus.COMPLETED,
                    payment_date=datetime.utcnow() - timedelta(days=random.randint(0, 60)),
                )
                db.add(payment)
                payments.append(payment)
        
        db.commit()
        print(f"✓ Created {len(payments)} payments")
        
        # ===== SEED TRANSACTIONS =====
        print("\n📈 Seeding Transactions...")
        transactions = []
        
        for student in students:
            num_transactions = random.randint(1, 5)
            for i in range(num_transactions):
                txn = TransactionORM(
                    student_id=student.id,
                    transaction_type=random.choice(
                        [TransactionType.TUITION, TransactionType.FEE, 
                         TransactionType.SCHOLARSHIP, TransactionType.REFUND]
                    ),
                    amount=random.uniform(5000, 40000),
                    reference_number=f"REF-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}",
                    description=f"Transaction {i+1}",
                    transaction_date=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
                )
                db.add(txn)
                transactions.append(txn)
        
        db.commit()
        print(f"✓ Created {len(transactions)} transactions")
        
        # ===== SEED AUDIT LOGS =====
        print("\n📋 Seeding Audit Logs...")
        audit_logs = []
        actions = ["login", "register", "update_profile", "view_grades", "submit_assignment"]
        resources = ["user", "student", "course", "grade", "assignment"]
        
        for user in users:
            for _ in range(random.randint(5, 15)):
                log = AuditLogORM(
                    user_id=user.id,
                    action=random.choice(actions),
                    resource=random.choice(resources),
                    status=random.choice(["success", "failure"]),
                    ip_address=f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    details={"additional_info": "Sample audit log entry"},
                )
                db.add(log)
                audit_logs.append(log)
        
        db.commit()
        print(f"✓ Created {len(audit_logs)} audit logs")
        
        print("\n✨ Database seeding completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   • Users: {len(users)}")
        print(f"   • Students: {len(students)}")
        print(f"   • Enrollments: {len(enrollments)}")
        print(f"   • Grades: {len(grades)}")
        print(f"   • Staff: {len(staff_list)}")
        print(f"   • Departments: {len(departments)}")
        print(f"   • Invoices: {len(invoices)}")
        print(f"   • Payments: {len(payments)}")
        print(f"   • Transactions: {len(transactions)}")
        print(f"   • Audit Logs: {len(audit_logs)}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
