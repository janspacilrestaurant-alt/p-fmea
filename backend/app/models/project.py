import uuid
from datetime import date

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import UUIDMixin, TimestampMixin
from app.models.enums import NodeType, WorkElementCategory


class Project(UUIDMixin, TimestampMixin, Base):
    """FMEA projekt — hlavička dle AIAG-VDA Step 1 (Planning & Preparation, 5T)."""
    __tablename__ = "projects"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer: Mapped[str] = mapped_column(String(200), default="")
    fmea_number: Mapped[str] = mapped_column(String(80), default="")
    revision: Mapped[str] = mapped_column(String(40), default="A")
    fmea_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fmea_revision_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 5T
    intent: Mapped[str] = mapped_column(Text, default="")
    team: Mapped[str] = mapped_column(Text, default="")
    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)
    baseline_project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    locale: Mapped[str] = mapped_column(String(5), default="cs")

    organization: Mapped["Organization"] = relationship(back_populates="projects")
    parts: Mapped[list["Part"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    process_steps: Mapped[list["ProcessStep"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    structure_nodes: Mapped[list["StructureNode"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Part(UUIDMixin, TimestampMixin, Base):
    """Díl / sestava, ke které se PFMEA vztahuje."""
    __tablename__ = "parts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    part_number: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="")
    revision: Mapped[str] = mapped_column(String(40), default="")
    drawing_ref: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")

    project: Mapped["Project"] = relationship(back_populates="parts")


class ProcessStep(UUIDMixin, TimestampMixin, Base):
    """Operace z Process Flow Diagramu. Číslo operace musí být shodné v PFD/PFMEA/CP."""
    __tablename__ = "process_steps"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    operation_number: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    technology: Mapped[str] = mapped_column(String(80), default="")  # obrábění, svařování, montáž…

    project: Mapped["Project"] = relationship(back_populates="process_steps")
    structure_nodes: Mapped[list["StructureNode"]] = relationship(back_populates="process_step")


class StructureNode(UUIDMixin, TimestampMixin, Base):
    """Structure Analysis (Step 2) + Function Analysis (Step 3) — self-referencing strom."""
    __tablename__ = "structure_nodes"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("structure_nodes.id", ondelete="CASCADE"), nullable=True
    )
    process_step_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_steps.id", ondelete="SET NULL"), nullable=True
    )
    node_type: Mapped[NodeType] = mapped_column(SAEnum(NodeType, name="node_type"))
    work_element_category: Mapped[WorkElementCategory | None] = mapped_column(
        SAEnum(WorkElementCategory, name="work_element_category"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    # Step 3 — Function Analysis
    function: Mapped[str] = mapped_column(Text, default="")
    characteristic: Mapped[str] = mapped_column(Text, default="")
    requirement: Mapped[str] = mapped_column(Text, default="")

    project: Mapped["Project"] = relationship(back_populates="structure_nodes")
    process_step: Mapped["ProcessStep | None"] = relationship(back_populates="structure_nodes")
    parent: Mapped["StructureNode | None"] = relationship(remote_side="StructureNode.id")
