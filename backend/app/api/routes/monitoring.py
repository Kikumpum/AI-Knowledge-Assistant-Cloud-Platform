from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from app.api.dependencies import CurrentUser, DbSession
from app.api.schemas import MonitoringStats
from app.application.chat_service import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

REQUEST_COUNT = Counter("chatbot_http_requests_total", "Total HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("chatbot_request_latency_seconds", "Request latency")


@router.get("/stats", response_model=MonitoringStats)
async def get_stats(current_user: CurrentUser, db: DbSession):
    service = MonitoringService(db)
    return await service.get_stats()


@router.get("/metrics")
async def prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
