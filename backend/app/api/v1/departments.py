from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.services.department_service import (
    list_departments,
    get_department_by_id,
    create_department,
    update_department,
    delete_department
)
from app.api.deps import RequireRole
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/departments", tags=["Hospital Departments"])


@router.get(
    "",
    response_model=List[DepartmentResponse],
    summary="List Hospital Departments",
    description="Public endpoint returning active hospital departments along with doctor counts."
)
def get_departments(
    include_inactive: bool = Query(False, description="Admin flag to include inactive departments"),
    db: Session = Depends(get_db)
):
    return list_departments(db=db, include_inactive=include_inactive)


@router.get(
    "/{id}",
    response_model=DepartmentResponse,
    summary="Get Department Details by ID",
    description="Public endpoint to retrieve department metadata and active doctor count."
)
def get_department(
    id: int,
    db: Session = Depends(get_db)
):
    return get_department_by_id(db=db, department_id=id)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Hospital Department (Admin Only)",
    description="Creates a new clinical department or medical specialty unit."
)
def create_new_department(
    dept_in: DepartmentCreate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    dept = create_department(
        db=db,
        dept_in=dept_in,
        admin_user_id=current_user.id,
        ip_address=ip_address
    )
    return get_department_by_id(db=db, department_id=dept.id)


@router.put(
    "/{id}",
    response_model=DepartmentResponse,
    summary="Update Department (Admin Only)",
    description="Modifies existing department parameters (name, code, description, icon, active status)."
)
def update_existing_department(
    id: int,
    dept_in: DepartmentUpdate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    dept = update_department(
        db=db,
        department_id=id,
        dept_in=dept_in,
        admin_user_id=current_user.id,
        ip_address=ip_address
    )
    return get_department_by_id(db=db, department_id=dept.id)


@router.delete(
    "/{id}",
    summary="Deactivate Department (Admin Only)",
    description="Soft-deletes a department by marking it inactive."
)
def deactivate_department(
    id: int,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return delete_department(
        db=db,
        department_id=id,
        admin_user_id=current_user.id,
        ip_address=ip_address
    )
