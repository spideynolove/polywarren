from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from shared.models import Market
from shared.schemas import MarketOut

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/markets", response_model=list[MarketOut])
@limiter.limit("60/minute")
async def get_markets(request: Request) -> list[MarketOut]:
    markets = await Market.all().order_by("-updated_at").limit(100)
    return [MarketOut.model_validate(m, from_attributes=True) for m in markets]
