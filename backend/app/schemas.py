import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import ActionPriority, NodeType, Role, WorkElementCategory


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORMBase):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: Role
    organization_id: uuid.UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""
    role: Role = Role.viewer


class OrganizationOut(ORMBase):
    id: uuid.UUID
    name: str
    slug: str


class ProjectCreate(BaseModel):
    name: str
    customer: str = ""
    fmea_number: str = ""
    revision: str = "A"
    intent: str = ""
    team: str = ""
    locale: str = "cs"
    fmea_start_date: date | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    customer: str | None = None
    fmea_number: str | None = None
    revision: str | None = None
    intent: str | None = None
    team: str | None = None
    locale: str | None = None


class ProjectOut(ORMBase):
    id: uuid.UUID
    name: str
    customer: str
    fmea_number: str
    revision: str
    intent: str
    team: str
    locale: str
    is_baseline: bool


class PartCreate(BaseModel):
    part_number: str
    name: str = ""
    revision: str = ""
    drawing_ref: str = ""
    description: str = ""


class PartOut(ORMBase):
    id: uuid.UUID
    project_id: uuid.UUID
    part_number: str
    name: str
    revision: str
    drawing_ref: str


class ProcessStepCreate(BaseModel):
    operation_number: str
    name: str
    description: str = ""
    sequence: int = 0
    technology: str = ""


class ProcessStepOut(ORMBase):
    id: uuid.UUID
    project_id: uuid.UUID
    operation_number: str
    name: str
    description: str
    sequence: int
    technology: str


class StructureNodeCreate(BaseModel):
    node_type: NodeType
    name: str
    parent_id: uuid.UUID | None = None
    process_step_id: uuid.UUID | None = None
    work_element_category: WorkElementCategory | None = None
    sequence: int = 0
    function: str = ""
    characteristic: str = ""
    requirement: str = ""


class StructureNodeOut(ORMBase):
    id: uuid.UUID
    project_id: uuid.UUID
    parent_id: uuid.UUID | None
    process_step_id: uuid.UUID | None
    node_type: NodeType
    work_element_category: WorkElementCategory | None
    name: str
    sequence: int
    function: str
    characteristic: str
    requirement: str


class APRequest(BaseModel):
    severity: int = Field(ge=1, le=10)
    occurrence: int = Field(ge=1, le=10)
    detection: int = Field(ge=1, le=10)


class APResponse(BaseModel):
    severity: int
    occurrence: int
    detection: int
    action_priority: ActionPriority
    source: Literal["AIAG-VDA FMEA 1st Ed. (2019), Step 5 — deterministic lookup"] = (
        "AIAG-VDA FMEA 1st Ed. (2019), Step 5 — deterministic lookup"
    )
