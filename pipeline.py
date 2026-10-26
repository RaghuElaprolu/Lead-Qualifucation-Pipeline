from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
from .features import is_valid_email
from .llm import Qualifier
from .models import Lead, ScoreResult
from .scoring import score_lead


@dataclass
class PipelineReport:
    scored: list[ScoreResult] = field(default_factory=list)
    rejected: list[tuple[int, str]] = field(default_factory=list)  # (row_number, reason)
    duplicates_dropped: int = 0

    def tier_counts(self) -> dict[str, int]:
        out = {"hot": 0, "warm": 0, "cold": 0}
        for r in self.scored:
            out[r.tier] += 1
        return out


def _int(v: str) -> int | None:
    v = (v or "").strip()
    return int(float(v)) if v else None


def _float(v: str) -> float | None:
    v = (v or "").strip()
    return float(v) if v else None


def _bool(v: str) -> bool:
    return (v or "").strip().lower() in {"1", "true", "yes", "y"}


def parse_row(row: dict[str, str]) -> Lead:
    return Lead(
        email=(row.get("email") or "").strip().lower(),
        name=row.get("name", "").strip(),
        company=row.get("company", "").strip(),
        title=row.get("title", "").strip(),
        employees=_int(row.get("employees", "")),
        industry=row.get("industry", "").strip(),
        budget_usd=_float(row.get("budget_usd", "")),
        timeline_days=_int(row.get("timeline_days", "")),
        page_views=_int(row.get("page_views", "")) or 0,
        email_opens=_int(row.get("email_opens", "")) or 0,
        demo_requested=_bool(row.get("demo_requested", "")),
        notes=row.get("notes", ""),
    )


def run_pipeline(in_csv: str | Path, out_csv: str | Path, qualifier: Qualifier | None = None) -> PipelineReport:
    report = PipelineReport()
    latest: dict[str, tuple[int, Lead]] = {}
    with open(in_csv, newline="", encoding="utf-8") as fh:
        for i, row in enumerate(csv.DictReader(fh), start=2):  # row 1 is the header
            try:
                lead = parse_row(row)
            except ValueError as exc:
                report.rejected.append((i, f"unparseable number: {exc}"))
                continue
            if not is_valid_email(lead.email):
                report.rejected.append((i, "invalid email"))
                continue
            if lead.email in latest:
                report.duplicates_dropped += 1
            latest[lead.email] = (i, lead)  # last row wins

    report.scored = sorted(
        (score_lead(lead, qualifier) for _, lead in latest.values()),
        key=lambda r: (-r.score, r.email),
    )
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["email", "score", "tier", "reasons"])
        for r in report.scored:
            w.writerow([r.email, r.score, r.tier, " | ".join(r.reasons)])
    return report
