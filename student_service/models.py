"""
Student Service Models
Defines Pydantic models for student management.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class StudentStatus(str, Enum):
    """Student enrollment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"


class StudentBase(BaseModel):
    """Base student model"""
    email: EmailStr
    full_name: str
    student_id: str


class StudentCreate(StudentBase):
    """Student creation model"""
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentUpdate(BaseModel):
    """Student update model"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Student(StudentBase):
    """Student response model"""
    id: int
    status: StudentStatus
    phone: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnrollmentBase(BaseModel):
    """Base enrollment model"""
    student_id: int
    course_id: int


class EnrollmentCreate(EnrollmentBase):
    """Enrollment creation model"""
    pass


class Enrollment(EnrollmentBase):
    """Enrollment response model"""
    id: int
    enrollment_date: datetime
    status: str  # "active", "completed", "dropped"
    
    class Config:
        from_attributes = True


class GradeBase(BaseModel):
    """Base grade model"""
    student_id: int
    course_id: int
    score: float


class GradeCreate(GradeBase):
    """Grade creation model"""
    pass


class Grade(GradeBase):
    """Grade response model"""
    id: int
    letter_grade: str
    recorded_date: datetime
    
    class Config:
        from_attributes = True


class StudentWithEnrollments(Student):
    """Student with their enrollments and grades"""
    enrollments: List[Enrollment] = []
    grades: List[Grade] = []
