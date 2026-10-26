from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Lead:
    email: str
    name: str = ""
    company: str = ""
    title: str = ""
    employees: int | None = None
    industry: str = ""
    budget_usd: float | None = None
    timeline_days: int | None = None
    page_views: int = 0
    email_opens: int = 0
    demo_requested: bool = False
    notes: str = ""


@dataclass
class ScoreResult:
    email: str
    score: int
    tier: str  # hot | warm | cold
    breakdown: dict[str, int] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    qualifier: str = "heuristic"
