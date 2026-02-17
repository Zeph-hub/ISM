"""
Staff Service Models
Defines Pydantic models for staff management.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


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


class DepartmentBase(BaseModel):
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
