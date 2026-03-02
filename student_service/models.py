"""
Student Service Models
Defines Pydantic and SQLAlchemy models for student management.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Base


class StudentStatus(str, Enum):
    """Student enrollment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"


# SQLAlchemy ORM Models
class StudentORM(Base):
    """Student ORM model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    status = Column(SQLEnum(StudentStatus), default=StudentStatus.ACTIVE)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    enrollments = relationship("EnrollmentORM", back_populates="student")
    grades = relationship("GradeORM", back_populates="student")


class EnrollmentORM(Base):
    """Enrollment ORM model"""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="active")  # active, completed, dropped
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("StudentORM", back_populates="enrollments")


class GradeORM(Base):
    """Grade ORM model"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    score = Column(Float, nullable=False)
    letter_grade = Column(String(2), nullable=True)
    recorded_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("StudentORM", back_populates="grades")


# Pydantic Models (for API validation)
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
    letter_grade: Optional[str]
        from_attributes = True


class StudentWithEnrollments(Student):
    """Student with their enrollments and grades"""
    enrollments: List[Enrollment] = []
    grades: List[Grade] = []
