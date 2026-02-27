from fastapi import APIRouter, Request
from api.limiter import limiter
from shared.models import PnLSnapshot
from shared.schemas import PnLSnapshotOut

router = APIRouter()


@router.get("/pnl", response_model=list[PnLSnapshotOut])
@limiter.limit("60/minute")
async def get_pnl(request: Request) -> list[PnLSnapshotOut]:
    snapshots = await PnLSnapshot.all().order_by("-timestamp").limit(200)
    return [
        PnLSnapshotOut(
            id=str(s.id),
            timestamp=s.timestamp,
            value=s.value,
            venue=s.venue,
        )
        for s in snapshots
    ]
