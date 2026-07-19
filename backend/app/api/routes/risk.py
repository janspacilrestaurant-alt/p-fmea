from fastapi import APIRouter, Depends

from app.core.ap import ap_lookup
from app.core.security import get_current_user
from app.schemas import APRequest, APResponse

router = APIRouter(prefix="/api/risk", tags=["risk"],
                   dependencies=[Depends(get_current_user)])


@router.post("/action-priority", response_model=APResponse)
def action_priority(payload: APRequest) -> APResponse:
    """Deterministický AP lookup. Nikdy neprochází přes LLM."""
    return APResponse(
        severity=payload.severity,
        occurrence=payload.occurrence,
        detection=payload.detection,
        action_priority=ap_lookup(payload.severity, payload.occurrence, payload.detection),
    )
