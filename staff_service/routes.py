"""
Staff Service Routes
Implements CRUD endpoints for staff management.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from .models import (
    Staff, StaffCreate, StaffUpdate, StaffWithDepartment,
    Department, DepartmentBase, Salary, SalaryCreate, Absence, AbsenceCreate
)

# Mock database
STAFF_DB = {}
DEPARTMENTS_DB = {1: {"id": 1, "name": "Academic", "description": "Teaching staff", "created_at": datetime.utcnow()}}
SALARIES_DB = {}
ABSENCES_DB = {}
STAFF_ID_COUNTER = 1

router = APIRouter(prefix="/api/staff", tags=["Staff"])


# ===== DEPARTMENTS =====
@router.post("/departments", response_model=Department, status_code=status.HTTP_201_CREATED)
async def create_department(dept_data: DepartmentBase) -> Department:
    """Create a new department."""
    dept_id = len(DEPARTMENTS_DB) + 1
    new_dept = {
        "id": dept_id,
        "name": dept_data.name,
        "description": dept_data.description,
        "created_at": datetime.utcnow()
    }
    DEPARTMENTS_DB[dept_id] = new_dept
    return Department(**new_dept)


@router.get("/departments", response_model=List[Department])
async def list_departments() -> List[Department]:
    """List all departments."""
    return [Department(**d) for d in DEPARTMENTS_DB.values()]


@router.get("/departments/{dept_id}", response_model=Department)
async def get_department(dept_id: int) -> Department:
    """Get a specific department."""
    dept = DEPARTMENTS_DB.get(dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return Department(**dept)


# ===== STAFF CRUD =====
@router.post("", response_model=Staff, status_code=status.HTTP_201_CREATED)
async def create_staff(staff_data: StaffCreate) -> Staff:
    """
    Create a new staff member.
    
    **Best Practice**: Validate employee_id uniqueness and background checks
    """
    global STAFF_ID_COUNTER
    
    # Check uniqueness
    if any(s["employee_id"] == staff_data.employee_id for s in STAFF_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )
    
    # Verify department exists
    if staff_data.department_id not in DEPARTMENTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    staff_id = STAFF_ID_COUNTER
    STAFF_ID_COUNTER += 1
    
    new_staff = {
        "id": staff_id,
        "email": staff_data.email,
        "full_name": staff_data.full_name,
        "employee_id": staff_data.employee_id,
        "role": staff_data.role,
        "phone": staff_data.phone,
        "department_id": staff_data.department_id,
        "hire_date": staff_data.hire_date,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    STAFF_DB[staff_id] = new_staff
    return Staff(**new_staff)


@router.get("", response_model=List[Staff])
async def list_staff(skip: int = 0, limit: int = 10, department_id: int = None) -> List[Staff]:
    """
    List all staff members with pagination.
    
    **Best Practice**: Filter by department for better performance
    """
    staff = list(STAFF_DB.values())
    
    if department_id:
        staff = [s for s in staff if s["department_id"] == department_id]
    
    staff = staff[skip:skip + limit]
    return [Staff(**s) for s in staff]


@router.get("/{staff_id}", response_model=StaffWithDepartment)
async def get_staff(staff_id: int) -> StaffWithDepartment:
    """Get staff member with department details."""
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    dept = DEPARTMENTS_DB.get(staff["department_id"])
    return StaffWithDepartment(**staff, department=dept)


@router.put("/{staff_id}", response_model=Staff)
async def update_staff(staff_id: int, staff_update: StaffUpdate) -> Staff:
    """Update staff information."""
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    if staff_update.full_name:
        staff["full_name"] = staff_update.full_name
    if staff_update.email:
        staff["email"] = staff_update.email
    if staff_update.phone:
        staff["phone"] = staff_update.phone
    if staff_update.role:
        staff["role"] = staff_update.role
    
    return Staff(**staff)


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_staff(staff_id: int):
    """Deactivate a staff member (soft delete)."""
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    staff["is_active"] = False


# ===== SALARY MANAGEMENT =====
@router.post("/{staff_id}/salary", response_model=Salary, status_code=status.HTTP_201_CREATED)
async def set_salary(staff_id: int, salary_data: SalaryCreate) -> Salary:
    """
    Set or update staff salary.
    
    **Best Practice**: Maintain salary history and require authorization
    """
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    salary_id = len(SALARIES_DB) + 1
    new_salary = {
        "id": salary_id,
        "staff_id": staff_id,
        "amount": salary_data.amount,
        "effective_date": salary_data.effective_date,
        "created_at": datetime.utcnow()
    }
    
    SALARIES_DB[salary_id] = new_salary
    return Salary(**new_salary)


@router.get("/{staff_id}/salary", response_model=Salary)
async def get_current_salary(staff_id: int) -> Salary:
    """Get current salary for staff member."""
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    # Get latest salary
    salaries = sorted(
        [s for s in SALARIES_DB.values() if s["staff_id"] == staff_id],
        key=lambda x: x["effective_date"],
        reverse=True
    )
    
    if not salaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No salary record found"
        )
    
    return Salary(**salaries[0])


# ===== ABSENCE MANAGEMENT =====
@router.post("/{staff_id}/absence", response_model=Absence, status_code=status.HTTP_201_CREATED)
async def request_absence(staff_id: int, absence_data: AbsenceCreate) -> Absence:
    """
    Request absence/leave.
    
    **Best Practice**: Validate leave balance and approval workflow
    """
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    # Validate dates
    if absence_data.end_date <= absence_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    absence_id = len(ABSENCES_DB) + 1
    new_absence = {
        "id": absence_id,
        "staff_id": staff_id,
        "start_date": absence_data.start_date,
        "end_date": absence_data.end_date,
        "reason": absence_data.reason,
        "approved": False,
        "created_at": datetime.utcnow()
    }
    
    ABSENCES_DB[absence_id] = new_absence
    return Absence(**new_absence)


@router.get("/{staff_id}/absences", response_model=List[Absence])
async def get_staff_absences(staff_id: int) -> List[Absence]:
    """Get absence records for a staff member."""
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    absences = [a for a in ABSENCES_DB.values() if a["staff_id"] == staff_id]
    return absences


@router.post("/{staff_id}/absences/{absence_id}/approve", status_code=status.HTTP_200_OK)
async def approve_absence(staff_id: int, absence_id: int):
    """Approve an absence request (admin only)."""
    staff = STAFF_DB.get(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    absence = ABSENCES_DB.get(absence_id)
    if not absence or absence["staff_id"] != staff_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence record not found"
        )
    
    absence["approved"] = True
    return {"message": "Absence approved"}
