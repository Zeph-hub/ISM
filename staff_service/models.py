"""
Staff Service Models
Defines Pydantic and SQLAlchemy models for staff management.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Base


class StaffRole(str, Enum):
    """Staff role categories"""
    TEACHER = "teacher"
    ACCOUNTANT = "accountant"
    LIBRARIAN = "librarian"
    DRIVER = "driver"
    ADMIN = "admin"
    SUPPORT_STAFF = "support_staff"
    HR = "hr"
    IT = "it"


# SQLAlchemy ORM Models
class DepartmentORM(Base):
    """Department ORM model"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    staff_members = relationship("StaffORM", back_populates="department")


class StaffORM(Base):
    """Staff ORM model"""
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(StaffRole), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    hire_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    department = relationship("DepartmentORM", back_populates="staff_members")
    salaries = relationship("SalaryORM", back_populates="staff")
    absences = relationship("AbsenceORM", back_populates="staff")


class SalaryORM(Base):
    """Salary ORM model"""
    __tablename__ = "salaries"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    staff = relationship("StaffORM", back_populates="salaries")


class AbsenceORM(Base):
    """Absence ORM model"""
    __tablename__ = "absences"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False, index=True)
    absence_date = Column(DateTime, nullable=False)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    staff = relationship("StaffORM", back_populates="absences")


# Pydantic Models (for API validation)

    """Base department model"""
    name: str
    description: Optional[str] = None


class Department(DepartmentBase):
    """Department response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StaffBase(BaseModel):
    """Base staff model"""
    email: EmailStr
    full_name: str
    employee_id: str
    role: StaffRole


class StaffCreate(StaffBase):
    """Staff creation model"""
    phone: Optional[str] = None
    department_id: int
    hire_date: datetime


class StaffUpdate(BaseModel):
    """Staff update model"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[StaffRole] = None


class Staff(StaffBase):
    """Staff response model"""
    id: int
    phone: Optional[str] = None
    department_id: int
    hire_date: datetime
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class StaffWithDepartment(Staff):
    """Staff with department information"""
    department: Department


class SalaryBase(BaseModel):
    """Base salary model"""
    staff_id: int
    amount: float
    effective_date: datetime


class SalaryCreate(SalaryBase):
    """Salary creation model"""
    pass


class Salary(SalaryBase):
    """Salary response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AbsenceBase(BaseModel):
    """Base absence model"""
    staff_id: int
    start_date: datetime
    end_date: datetime
    reason: str


class AbsenceCreate(AbsenceBase):
    """Absence creation model"""
    pass


class Absence(AbsenceBase):
    """Absence response model"""
    id: int
    approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
