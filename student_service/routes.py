"""
Student Service Routes
Implements CRUD endpoints for student management.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from .models import (
    Student, StudentCreate, StudentUpdate, Enrollment, Grade,
    EnrollmentCreate, GradeCreate, StudentWithEnrollments, StudentStatus
)

# Mock database
STUDENTS_DB = {}
ENROLLMENTS_DB = {}
GRADES_DB = {}
STUDENT_ID_COUNTER = 1

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(student_data: StudentCreate) -> Student:
    """
    Create a new student.
    
    **Best Practice**: Validate unique student_id and email before creation
    """
    global STUDENT_ID_COUNTER
    
    # Check uniqueness
    if any(s["student_id"] == student_data.student_id for s in STUDENTS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student ID {student_data.student_id} already exists"
        )
    
    student_id = STUDENT_ID_COUNTER
    STUDENT_ID_COUNTER += 1
    
    new_student = {
        "id": student_id,
        "email": student_data.email,
        "full_name": student_data.full_name,
        "student_id": student_data.student_id,
        "phone": student_data.phone,
        "address": student_data.address,
        "status": StudentStatus.ACTIVE,
        "enrollment_date": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    STUDENTS_DB[student_id] = new_student
    return Student(**new_student)


@router.get("", response_model=List[Student])
async def list_students(skip: int = 0, limit: int = 10, status_filter: StudentStatus = None) -> List[Student]:
    """
    List all students with pagination.
    
    **Best Practice**: Always implement pagination for large datasets
    """
    students = list(STUDENTS_DB.values())
    
    if status_filter:
        students = [s for s in students if s["status"] == status_filter]
    
    students = students[skip:skip + limit]
    return [Student(**s) for s in students]


@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: int) -> Student:
    """Get a specific student by ID."""
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )
    return Student(**student)


@router.get("/{student_id}/profile", response_model=StudentWithEnrollments)
async def get_student_profile(student_id: int) -> StudentWithEnrollments:
    """
    Get student profile with enrollments and grades.
    
    **Best Practice**: Denormalize data for read-heavy operations
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    enrollments = [e for e in ENROLLMENTS_DB.values() if e["student_id"] == student_id]
    grades = [g for g in GRADES_DB.values() if g["student_id"] == student_id]
    
    return StudentWithEnrollments(
        **student,
        enrollments=enrollments,
        grades=grades
    )


@router.put("/{student_id}", response_model=Student)
async def update_student(student_id: int, student_update: StudentUpdate) -> Student:
    """Update student information."""
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields
    if student_update.full_name:
        student["full_name"] = student_update.full_name
    if student_update.email:
        student["email"] = student_update.email
    if student_update.phone:
        student["phone"] = student_update.phone
    if student_update.address:
        student["address"] = student_update.address
    
    return Student(**student)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int):
    """
    Deactivate a student (soft delete).
    
    **Best Practice**: Use soft delete to maintain data integrity and audit trail
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student["status"] = StudentStatus.INACTIVE


@router.post("/{student_id}/enroll", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
async def enroll_course(student_id: int, enrollment_data: EnrollmentCreate) -> Enrollment:
    """
    Enroll a student in a course.
    
    **Best Practice**: Validate prerequisites and check course capacity
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if already enrolled
    if any(e["student_id"] == student_id and e["course_id"] == enrollment_data.course_id 
           for e in ENROLLMENTS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled in this course"
        )
    
    enrollment_id = len(ENROLLMENTS_DB) + 1
    new_enrollment = {
        "id": enrollment_id,
        "student_id": student_id,
        "course_id": enrollment_data.course_id,
        "enrollment_date": datetime.utcnow(),
        "status": "active"
    }
    
    ENROLLMENTS_DB[enrollment_id] = new_enrollment
    return Enrollment(**new_enrollment)


@router.get("/{student_id}/enrollments", response_model=List[Enrollment])
async def get_student_enrollments(student_id: int) -> List[Enrollment]:
    """Get all enrollments for a student."""
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    enrollments = [e for e in ENROLLMENTS_DB.values() if e["student_id"] == student_id]
    return enrollments


@router.post("/{student_id}/grades", response_model=Grade, status_code=status.HTTP_201_CREATED)
async def record_grade(student_id: int, grade_data: GradeCreate) -> Grade:
    """
    Record a grade for student in a course.
    
    **Best Practice**: Validate score range and trigger notifications
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Validate score
    if not 0 <= grade_data.score <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score must be between 0 and 100"
        )
    
    grade_id = len(GRADES_DB) + 1
    letter_grade = get_letter_grade(grade_data.score)
    
    new_grade = {
        "id": grade_id,
        "student_id": student_id,
        "course_id": grade_data.course_id,
        "score": grade_data.score,
        "letter_grade": letter_grade,
        "recorded_date": datetime.utcnow()
    }
    
    GRADES_DB[grade_id] = new_grade
    return Grade(**new_grade)


@router.get("/{student_id}/grades", response_model=List[Grade])
async def get_student_grades(student_id: int) -> List[Grade]:
    """Get all grades for a student."""
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    grades = [g for g in GRADES_DB.values() if g["student_id"] == student_id]
    return grades


@router.get("/{student_id}/gpa")
async def calculate_gpa(student_id: int) -> dict:
    """
    Calculate GPA for a student.
    
    **Best Practice**: Cache GPA calculations and update periodically
    """
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    grades = [g for g in GRADES_DB.values() if g["student_id"] == student_id]
    
    if not grades:
        return {"student_id": student_id, "gpa": 0.0}
    
    # Mock GPA calculation (simplified)
    total_score = sum(g["score"] for g in grades)
    gpa = total_score / len(grades) / 20  # Convert to 4.0 scale
    
    return {
        "student_id": student_id,
        "gpa": round(gpa, 2),
        "courses_completed": len(grades)
    }


def get_letter_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
