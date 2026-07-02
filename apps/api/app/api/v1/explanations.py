from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter(prefix="/explanations", tags=["explanations"])


@router.get("/status", response_model=ModuleStatusResponse)
def explanations_module_status() -> ModuleStatusResponse:
    return ModuleStatusResponse(
        module="explanations",
        status="available",
        detail="Explanations API module is registered. Explanation endpoints will be added in Phase 4H.",
    )
