from __future__ import annotations
from . import features as f
from .llm import HeuristicQualifier, Qualifier
from .models import Lead, ScoreResult

HOT_THRESHOLD = 70
WARM_THRESHOLD = 35


def tier_for(score: int) -> str:
    if score >= HOT_THRESHOLD:
        return "hot"
    if score >= WARM_THRESHOLD:
        return "warm"
    return "cold"


def score_lead(lead: Lead, qualifier: Qualifier | None = None) -> ScoreResult:
    qualifier = qualifier or HeuristicQualifier()
    b = {
        "seniority": f.seniority_points(lead.title),
        "company_size": f.company_size_points(lead.employees),
        "budget": f.budget_points(lead.budget_usd),
        "intent": f.intent_points(lead.page_views, lead.email_opens, lead.demo_requested),
        "urgency": f.urgency_points(lead.timeline_days),
    }
    reasons: list[str] = []
    penalty = 0
    if f.is_free_email(lead.email):
        penalty -= 10
        reasons.append("free email domain (-10)")
    if not lead.company.strip():
        penalty -= 5
        reasons.append("missing company (-5)")
    b["penalties"] = penalty

    adj, why = qualifier.adjust(lead.notes)
    b["qualifier"] = adj
    if adj:
        reasons.append(f"notes adjustment {adj:+d}: {why}")

    if lead.demo_requested:
        reasons.append("requested a demo (+20)")
    if lead.timeline_days is not None and lead.timeline_days <= 30:
        reasons.append("buying window <= 30 days")

    total = max(0, min(100, sum(b.values())))
    return ScoreResult(lead.email, total, tier_for(total), b, reasons, qualifier.name)
