from fastapi import APIRouter, Request
from api.limiter import limiter
from shared.models import Position
from shared.schemas import PositionOut

router = APIRouter()


@router.get("/positions", response_model=list[PositionOut])
@limiter.limit("60/minute")
async def get_positions(request: Request) -> list[PositionOut]:
    positions = await Position.all().prefetch_related("market").order_by("-opened_at").limit(50)
    return [
        PositionOut(
            id=str(p.id),
            market_id=str(p.market_id),
            venue=p.venue,
            side=p.side,
            size=p.size,
            entry_price=p.entry_price,
            opened_at=p.opened_at,
        )
        for p in positions
    ]
