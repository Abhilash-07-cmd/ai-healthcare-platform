from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.all_models import Department, Doctor
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.services.audit_service import create_audit_log
from app.core.logging import logger

# Standard hospital departments seed dataset
DEFAULT_DEPARTMENTS = [
    {
        "name": "General Medicine",
        "code": "GEN_MED",
        "description": "Comprehensive primary healthcare, wellness exams, and general medical consultations.",
        "icon": "stethoscope"
    },
    {
        "name": "Dermatology",
        "code": "DERM",
        "description": "Diagnosis and treatment of skin, hair, and nail disorders, cosmetic skin care.",
        "icon": "user-check"
    },
    {
        "name": "Cardiology",
        "code": "CARD",
        "description": "Heart health, cardiovascular risk assessment, hypertension, and cardiac consultations.",
        "icon": "heart"
    },
    {
        "name": "Pediatrics",
        "code": "PED",
        "description": "Medical care, immunizations, and developmental monitoring for infants, children, and teens.",
        "icon": "baby"
    },
    {
        "name": "Orthopedics",
        "code": "ORTHO",
        "description": "Bone, joint, ligament, and musculoskeletal care, fracture management, and joint pain.",
        "icon": "activity"
    },
    {
        "name": "Neurology",
        "code": "NEURO",
        "description": "Brain and nervous system evaluation, migraine, stroke care, and nerve disorders.",
        "icon": "brain"
    }
]


def seed_default_departments(db: Session):
    """
    Seeds initial standard hospital departments if the departments table is empty.
    """
    try:
        count = db.query(Department).count()
        if count == 0:
            logger.info("Seeding initial hospital departments...")
            for dept_data in DEFAULT_DEPARTMENTS:
                dept = Department(
                    name=dept_data["name"],
                    code=dept_data["code"],
                    description=dept_data["description"],
                    icon=dept_data["icon"],
                    is_active=True
                )
                db.add(dept)
            db.commit()
            logger.info("Successfully seeded standard hospital departments.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding default departments: {str(e)}")


def list_departments(db: Session, include_inactive: bool = False) -> List[dict]:
    """
    Returns list of departments with computed doctor counts.
    """
    query = db.query(
        Department,
        func.count(Doctor.id).label("doctor_count")
    ).outerjoin(Doctor, Department.id == Doctor.department_id)

    if not include_inactive:
        query = query.filter(Department.is_active == True)

    results = query.group_by(Department.id).order_by(Department.name.asc()).all()

    departments_list = []
    for dept, doc_count in results:
        dept_dict = {
            "id": dept.id,
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "icon": dept.icon,
            "is_active": dept.is_active,
            "created_at": dept.created_at,
            "doctor_count": doc_count
        }
        departments_list.append(dept_dict)

    return departments_list


def get_department_by_id(db: Session, department_id: int) -> dict:
    dept_with_count = (
        db.query(Department, func.count(Doctor.id).label("doctor_count"))
        .outerjoin(Doctor, Department.id == Doctor.department_id)
        .filter(Department.id == department_id)
        .group_by(Department.id)
        .first()
    )

    if not dept_with_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found."
        )

    dept, doc_count = dept_with_count
    return {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "icon": dept.icon,
        "is_active": dept.is_active,
        "created_at": dept.created_at,
        "doctor_count": doc_count
    }


def create_department(db: Session, dept_in: DepartmentCreate, admin_user_id: int, ip_address: Optional[str] = None) -> Department:
    # Check duplicate code or name
    existing = db.query(Department).filter(
        (Department.code == dept_in.code.upper()) | (Department.name == dept_in.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A department with this name or code already exists."
        )

    dept = Department(
        name=dept_in.name,
        code=dept_in.code.upper(),
        description=dept_in.description,
        icon=dept_in.icon,
        is_active=True
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)

    create_audit_log(
        db=db,
        action="CREATE_DEPARTMENT",
        resource="departments",
        user_id=admin_user_id,
        resource_id=str(dept.id),
        details={"name": dept.name, "code": dept.code},
        ip_address=ip_address
    )

    return dept


def update_department(db: Session, department_id: int, dept_in: DepartmentUpdate, admin_user_id: int, ip_address: Optional[str] = None) -> Department:
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found."
        )

    if dept_in.name is not None:
        dept.name = dept_in.name
    if dept_in.code is not None:
        dept.code = dept_in.code.upper()
    if dept_in.description is not None:
        dept.description = dept_in.description
    if dept_in.icon is not None:
        dept.icon = dept_in.icon
    if dept_in.is_active is not None:
        dept.is_active = dept_in.is_active

    db.commit()
    db.refresh(dept)

    create_audit_log(
        db=db,
        action="UPDATE_DEPARTMENT",
        resource="departments",
        user_id=admin_user_id,
        resource_id=str(dept.id),
        details={"updated_fields": dept_in.model_dump(exclude_unset=True)},
        ip_address=ip_address
    )

    return dept


def delete_department(db: Session, department_id: int, admin_user_id: int, ip_address: Optional[str] = None) -> dict:
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found."
        )

    dept.is_active = False
    db.commit()

    create_audit_log(
        db=db,
        action="DEACTIVATE_DEPARTMENT",
        resource="departments",
        user_id=admin_user_id,
        resource_id=str(dept.id),
        details={"name": dept.name},
        ip_address=ip_address
    )

    return {"message": f"Department '{dept.name}' deactivated successfully."}
