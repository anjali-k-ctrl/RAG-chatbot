from fastapi import APIRouter
from services.analytics_service import ( get_analytics )
from services.analytics_service import ( get_top_unanswered_questions )
from services.analytics_service import ( get_recent_unanswered_questions )
from services.analytics_service import ( get_daily_report )
from services.analytics_service import ( get_weekly_report )

router = APIRouter()

@router.get("/analytics")
def analytics():
    return get_analytics()

@router.get("/top-unanswered-questions")
def top_unanswered_questions():
    return get_top_unanswered_questions()

@router.get("/recent-unanswered-questions")
def recent_unanswered_questions():
    return get_recent_unanswered_questions()

from fastapi import Query


@router.get("/daily-report")
def daily_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
):
    return get_daily_report(
        from_date,
        to_date
    )


@router.get("/weekly-report")
def weekly_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
):
    return get_weekly_report(
        from_date,
        to_date
    )