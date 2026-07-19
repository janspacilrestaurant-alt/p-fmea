import enum


class Role(str, enum.Enum):
    admin = "admin"
    engineer = "engineer"
    viewer = "viewer"


class NodeType(str, enum.Enum):
    """AIAG-VDA Structure Analysis (Step 2), 3 úrovně."""
    process_item = "process_item"          # úroveň 1 — systém / proces
    process_step = "process_step"          # úroveň 2 — operace
    process_work_element = "process_work_element"  # úroveň 3 — 4M


class WorkElementCategory(str, enum.Enum):
    """4M kategorie pro process work element."""
    machine = "machine"
    man = "man"
    material = "material"
    environment = "environment"


class ActionStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    discarded = "discarded"
    not_applicable = "not_applicable"


class ActionType(str, enum.Enum):
    prevention = "prevention"
    detection = "detection"


class CatalogKind(str, enum.Enum):
    severity = "severity"
    occurrence = "occurrence"
    detection = "detection"


class ActionPriority(str, enum.Enum):
    H = "H"
    M = "M"
    L = "L"
