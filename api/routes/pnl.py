from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from shared.models import PnLSnapshot
from shared.schemas import PnLSnapshotOut

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


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
