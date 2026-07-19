"""initial schema

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    role = sa.Enum("admin", "engineer", "viewer", name="role")
    node_type = sa.Enum("process_item", "process_step", "process_work_element", name="node_type")
    work_cat = sa.Enum("machine", "man", "material", "environment", name="work_element_category")
    action_status = sa.Enum("open", "in_progress", "completed", "discarded",
                            "not_applicable", name="action_status")
    action_type = sa.Enum("prevention", "detection", name="action_type")
    catalog_kind = sa.Enum("severity", "occurrence", "detection", name="catalog_kind")
    ap = sa.Enum("H", "M", "L", name="action_priority")

    op.create_table(
        "organizations",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("default_locale", sa.String(5), server_default="cs"),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("organization_id", UUID,
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), index=True),
        sa.Column("email", sa.String(255), nullable=False, index=True),
        sa.Column("full_name", sa.String(200), server_default=""),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", role, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
        sa.UniqueConstraint("organization_id", "email", name="uq_user_org_email"),
    )

    op.create_table(
        "projects",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("organization_id", UUID,
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("customer", sa.String(200), server_default=""),
        sa.Column("fmea_number", sa.String(80), server_default=""),
        sa.Column("revision", sa.String(40), server_default="A"),
        sa.Column("fmea_start_date", sa.Date),
        sa.Column("fmea_revision_date", sa.Date),
        sa.Column("intent", sa.Text, server_default=""),
        sa.Column("team", sa.Text, server_default=""),
        sa.Column("is_baseline", sa.Boolean, server_default=sa.false()),
        sa.Column("baseline_project_id", UUID, sa.ForeignKey("projects.id", ondelete="SET NULL")),
        sa.Column("locale", sa.String(5), server_default="cs"),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "parts",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("projects.id", ondelete="CASCADE"), index=True),
        sa.Column("part_number", sa.String(120), nullable=False),
        sa.Column("name", sa.String(200), server_default=""),
        sa.Column("revision", sa.String(40), server_default=""),
        sa.Column("drawing_ref", sa.String(255), server_default=""),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "process_steps",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("projects.id", ondelete="CASCADE"), index=True),
        sa.Column("operation_number", sa.String(40), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("sequence", sa.Integer, server_default="0"),
        sa.Column("technology", sa.String(80), server_default=""),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "structure_nodes",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("projects.id", ondelete="CASCADE"), index=True),
        sa.Column("parent_id", UUID, sa.ForeignKey("structure_nodes.id", ondelete="CASCADE")),
        sa.Column("process_step_id", UUID,
                  sa.ForeignKey("process_steps.id", ondelete="SET NULL")),
        sa.Column("node_type", node_type, nullable=False),
        sa.Column("work_element_category", work_cat),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sequence", sa.Integer, server_default="0"),
        sa.Column("function", sa.Text, server_default=""),
        sa.Column("characteristic", sa.Text, server_default=""),
        sa.Column("requirement", sa.Text, server_default=""),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "failure_modes",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("structure_node_id", UUID,
                  sa.ForeignKey("structure_nodes.id", ondelete="CASCADE"), index=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("sequence", sa.Integer, server_default="0"),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "failure_effects",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("failure_mode_id", UUID,
                  sa.ForeignKey("failure_modes.id", ondelete="CASCADE"), index=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("severity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("affects_own_plant", sa.Boolean, server_default=sa.false()),
        sa.Column("affects_ship_to_plant", sa.Boolean, server_default=sa.false()),
        sa.Column("affects_end_user", sa.Boolean, server_default=sa.false()),
        sa.Column("is_safety_or_regulatory", sa.Boolean, server_default=sa.false()),
        sa.Column("special_characteristic", sa.String(20), server_default=""),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
        sa.CheckConstraint("severity BETWEEN 1 AND 10", name="ck_severity_range"),
    )

    op.create_table(
        "failure_causes",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("failure_mode_id", UUID,
                  sa.ForeignKey("failure_modes.id", ondelete="CASCADE"), index=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("work_element_node_id", UUID,
                  sa.ForeignKey("structure_nodes.id", ondelete="SET NULL")),
        sa.Column("prevention_control", sa.Text, server_default=""),
        sa.Column("detection_control", sa.Text, server_default=""),
        sa.Column("occurrence", sa.Integer, nullable=False, server_default="1"),
        sa.Column("detection", sa.Integer, nullable=False, server_default="1"),
        sa.Column("action_priority", ap),
        sa.Column("no_action_justification", sa.Text, server_default=""),
        sa.Column("cpk", sa.String(20), server_default=""),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
        sa.CheckConstraint("occurrence BETWEEN 1 AND 10", name="ck_occurrence_range"),
        sa.CheckConstraint("detection BETWEEN 1 AND 10", name="ck_detection_range"),
    )

    op.create_table(
        "optimization_actions",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("failure_cause_id", UUID,
                  sa.ForeignKey("failure_causes.id", ondelete="CASCADE"), index=True),
        sa.Column("action_type", action_type, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("responsible", sa.String(200), server_default=""),
        sa.Column("target_date", sa.Date),
        sa.Column("completed_date", sa.Date),
        sa.Column("status", action_status, server_default="open"),
        sa.Column("evidence", sa.Text, server_default=""),
        sa.Column("new_severity", sa.Integer),
        sa.Column("new_occurrence", sa.Integer),
        sa.Column("new_detection", sa.Integer),
        sa.Column("new_action_priority", ap),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "rating_catalogs",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("organization_id", UUID,
                  sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("kind", catalog_kind, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("locale", sa.String(5), server_default="cs"),
        sa.Column("is_default", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", TS, server_default=sa.func.now()),
        sa.Column("updated_at", TS, server_default=sa.func.now()),
    )

    op.create_table(
        "rating_catalog_entries",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("catalog_id", UUID,
                  sa.ForeignKey("rating_catalogs.id", ondelete="CASCADE"), index=True),
        sa.Column("value", sa.Integer, nullable=False),
        sa.Column("label", sa.String(120), server_default=""),
        sa.Column("criteria", sa.Text, server_default=""),
        sa.CheckConstraint("value BETWEEN 1 AND 10", name="ck_rating_value_range"),
    )


def downgrade() -> None:
    for table in ["rating_catalog_entries", "rating_catalogs", "optimization_actions",
                  "failure_causes", "failure_effects", "failure_modes", "structure_nodes",
                  "process_steps", "parts", "projects", "users", "organizations"]:
        op.drop_table(table)
    for enum_name in ["action_priority", "catalog_kind", "action_type", "action_status",
                      "work_element_category", "node_type", "role"]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
