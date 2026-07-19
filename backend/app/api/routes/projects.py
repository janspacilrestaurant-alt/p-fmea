import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_role
from app.db import get_db
from app.models import Part, ProcessStep, Project, Role, StructureNode, User
from app.schemas import (PartCreate, PartOut, ProcessStepCreate, ProcessStepOut,
                         ProjectCreate, ProjectOut, ProjectUpdate,
                         StructureNodeCreate, StructureNodeOut)

router = APIRouter(prefix="/api/projects", tags=["projects"])
Engineer = Annotated[User, Depends(require_role(Role.engineer))]
AnyUser = Annotated[User, Depends(get_current_user)]
Db = Annotated[Session, Depends(get_db)]


def _get_project(db: Session, project_id: uuid.UUID, user: User) -> Project:
    project = db.get(Project, project_id)
    if not project or project.organization_id != user.organization_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projekt nenalezen")
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(user: AnyUser, db: Db):
    return db.scalars(
        select(Project).where(Project.organization_id == user.organization_id)
        .order_by(Project.created_at.desc())
    ).all()


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, user: Engineer, db: Db):
    project = Project(organization_id=user.organization_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: uuid.UUID, user: AnyUser, db: Db):
    return _get_project(db, project_id, user)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: uuid.UUID, payload: ProjectUpdate, user: Engineer, db: Db):
    project = _get_project(db, project_id, user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: uuid.UUID,
                   user: Annotated[User, Depends(require_role(Role.admin))], db: Db):
    db.delete(_get_project(db, project_id, user))
    db.commit()


# --- Parts ---------------------------------------------------------------
@router.get("/{project_id}/parts", response_model=list[PartOut])
def list_parts(project_id: uuid.UUID, user: AnyUser, db: Db):
    return _get_project(db, project_id, user).parts


@router.post("/{project_id}/parts", response_model=PartOut, status_code=201)
def create_part(project_id: uuid.UUID, payload: PartCreate, user: Engineer, db: Db):
    _get_project(db, project_id, user)
    part = Part(project_id=project_id, **payload.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


# --- Process steps (sdílená entita PFD <-> PFMEA <-> CP) -----------------
@router.get("/{project_id}/process-steps", response_model=list[ProcessStepOut])
def list_steps(project_id: uuid.UUID, user: AnyUser, db: Db):
    _get_project(db, project_id, user)
    return db.scalars(
        select(ProcessStep).where(ProcessStep.project_id == project_id)
        .order_by(ProcessStep.sequence)
    ).all()


@router.post("/{project_id}/process-steps", response_model=ProcessStepOut, status_code=201)
def create_step(project_id: uuid.UUID, payload: ProcessStepCreate, user: Engineer, db: Db):
    _get_project(db, project_id, user)
    step = ProcessStep(project_id=project_id, **payload.model_dump())
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


# --- Structure nodes -----------------------------------------------------
@router.get("/{project_id}/structure", response_model=list[StructureNodeOut])
def list_structure(project_id: uuid.UUID, user: AnyUser, db: Db):
    _get_project(db, project_id, user)
    return db.scalars(
        select(StructureNode).where(StructureNode.project_id == project_id)
        .order_by(StructureNode.sequence)
    ).all()


@router.post("/{project_id}/structure", response_model=StructureNodeOut, status_code=201)
def create_node(project_id: uuid.UUID, payload: StructureNodeCreate, user: Engineer, db: Db):
    _get_project(db, project_id, user)
    node = StructureNode(project_id=project_id, **payload.model_dump())
    db.add(node)
    db.commit()
    db.refresh(node)
    return node
