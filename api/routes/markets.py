from fastapi import APIRouter, Request
from api.limiter import limiter
from shared.models import Market
from shared.schemas import MarketOut

router = APIRouter()


@router.get("/markets", response_model=list[MarketOut])
@limiter.limit("60/minute")
async def get_markets(request: Request) -> list[MarketOut]:
    markets = await Market.all().order_by("-updated_at").limit(100)
    return [MarketOut.model_validate(m, from_attributes=True) for m in markets]
