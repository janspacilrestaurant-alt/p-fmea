import uuid
from datetime import date

from sqlalchemy import (Boolean, Date, Enum as SAEnum, ForeignKey, Integer,
                        String, Text, CheckConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import UUIDMixin, TimestampMixin
from app.models.enums import ActionPriority, ActionStatus, ActionType, CatalogKind


class FailureMode(UUIDMixin, TimestampMixin, Base):
    """Failure Analysis (Step 4) — FM na úrovni Process Step."""
    __tablename__ = "failure_modes"

    structure_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("structure_nodes.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, default=0)

    effects: Mapped[list["FailureEffect"]] = relationship(
        back_populates="failure_mode", cascade="all, delete-orphan"
    )
    causes: Mapped[list["FailureCause"]] = relationship(
        back_populates="failure_mode", cascade="all, delete-orphan"
    )


class FailureEffect(UUIDMixin, TimestampMixin, Base):
    """Failure Effect (FE) + Severity. Severity je fixní — nesnižuje se kvůli AP."""
    __tablename__ = "failure_effects"
    __table_args__ = (
        CheckConstraint("severity BETWEEN 1 AND 10", name="ck_severity_range"),
    )

    failure_mode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_modes.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    affects_own_plant: Mapped[bool] = mapped_column(Boolean, default=False)
    affects_ship_to_plant: Mapped[bool] = mapped_column(Boolean, default=False)
    affects_end_user: Mapped[bool] = mapped_column(Boolean, default=False)
    is_safety_or_regulatory: Mapped[bool] = mapped_column(Boolean, default=False)
    special_characteristic: Mapped[str] = mapped_column(String(20), default="")  # SC / CC

    failure_mode: Mapped["FailureMode"] = relationship(back_populates="effects")


class FailureCause(UUIDMixin, TimestampMixin, Base):
    """Failure Cause (FC) + Risk Analysis (Step 5) + Optimization (Step 6)."""
    __tablename__ = "failure_causes"
    __table_args__ = (
        CheckConstraint("occurrence BETWEEN 1 AND 10", name="ck_occurrence_range"),
        CheckConstraint("detection BETWEEN 1 AND 10", name="ck_detection_range"),
    )

    failure_mode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_modes.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    work_element_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("structure_nodes.id", ondelete="SET NULL"), nullable=True
    )
    prevention_control: Mapped[str] = mapped_column(Text, default="")
    detection_control: Mapped[str] = mapped_column(Text, default="")
    occurrence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    detection: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # AP je počítáno deterministicky backendem a persistováno pro audit trail
    action_priority: Mapped[ActionPriority | None] = mapped_column(
        SAEnum(ActionPriority, name="action_priority"), nullable=True
    )
    # High AP bez akce vyžaduje písemné zdůvodnění (auditní požadavek)
    no_action_justification: Mapped[str] = mapped_column(Text, default="")
    cpk: Mapped[str] = mapped_column(String(20), default="")

    failure_mode: Mapped["FailureMode"] = relationship(back_populates="causes")
    actions: Mapped[list["OptimizationAction"]] = relationship(
        back_populates="failure_cause", cascade="all, delete-orphan"
    )


class OptimizationAction(UUIDMixin, TimestampMixin, Base):
    """Step 6 — Optimization: akce, odpovědnost, termín, status, re-rating."""
    __tablename__ = "optimization_actions"

    failure_cause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_causes.id", ondelete="CASCADE"), index=True
    )
    action_type: Mapped[ActionType] = mapped_column(SAEnum(ActionType, name="action_type"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsible: Mapped[str] = mapped_column(String(200), default="")
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ActionStatus] = mapped_column(
        SAEnum(ActionStatus, name="action_status"), default=ActionStatus.open
    )
    evidence: Mapped[str] = mapped_column(Text, default="")
    # re-rating po realizaci akce
    new_severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_occurrence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_detection: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_action_priority: Mapped[ActionPriority | None] = mapped_column(
        SAEnum(ActionPriority, name="action_priority", create_type=False), nullable=True
    )

    failure_cause: Mapped["FailureCause"] = relationship(back_populates="actions")


class RatingCatalog(UUIDMixin, TimestampMixin, Base):
    """Hodnoticí katalog S/O/D. Customer-supplied — nekopírujeme AIAG-VDA texty 1:1.

    org_id = NULL → globální default katalog dodaný s produktem.
    """
    __tablename__ = "rating_catalogs"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    kind: Mapped[CatalogKind] = mapped_column(SAEnum(CatalogKind, name="catalog_kind"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    locale: Mapped[str] = mapped_column(String(5), default="cs")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    entries: Mapped[list["RatingCatalogEntry"]] = relationship(
        back_populates="catalog", cascade="all, delete-orphan", order_by="RatingCatalogEntry.value"
    )


class RatingCatalogEntry(UUIDMixin, Base):
    __tablename__ = "rating_catalog_entries"
    __table_args__ = (CheckConstraint("value BETWEEN 1 AND 10", name="ck_rating_value_range"),)

    catalog_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rating_catalogs.id", ondelete="CASCADE"), index=True
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(120), default="")
    criteria: Mapped[str] = mapped_column(Text, default="")

    catalog: Mapped["RatingCatalog"] = relationship(back_populates="entries")
