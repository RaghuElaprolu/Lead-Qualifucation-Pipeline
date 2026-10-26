"""Deterministic feature extraction. Every function is pure and unit-tested."""
from __future__ import annotations
import re

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "proton.me", "protonmail.com", "aol.com", "mail.com",
}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Ordered: first match wins.
SENIORITY = [
    (re.compile(r"\b(ceo|cto|cfo|coo|cio|chief|founder|co-founder|owner|president)\b", re.I), 15),
    (re.compile(r"\b(vp|vice president|head of)\b", re.I), 13),
    (re.compile(r"\bdirector\b", re.I), 11),
    (re.compile(r"\b(senior manager|manager|lead)\b", re.I), 7),
    (re.compile(r"\b(engineer|analyst|specialist|consultant|developer)\b", re.I), 3),
    (re.compile(r"\b(intern|student|trainee)\b", re.I), 0),
]


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))


def email_domain(email: str) -> str:
    return email.strip().lower().rsplit("@", 1)[-1]


def is_free_email(email: str) -> bool:
    return email_domain(email) in FREE_EMAIL_DOMAINS


def seniority_points(title: str) -> int:
    for pattern, pts in SENIORITY:
        if pattern.search(title or ""):
            return pts
    return 2 if title else 0


def company_size_points(employees: int | None) -> int:
    if employees is None:
        return 0
    if employees >= 1000:
        return 10
    if employees >= 200:
        return 8
    if employees >= 50:
        return 6
    if employees >= 10:
        return 3
    return 1


def budget_points(budget_usd: float | None) -> int:
    if budget_usd is None:
        return 0
    if budget_usd >= 100_000:
        return 10
    if budget_usd >= 25_000:
        return 7
    if budget_usd >= 5_000:
        return 4
    return 1


def urgency_points(timeline_days: int | None) -> int:
    if timeline_days is None:
        return 0
    if timeline_days <= 30:
        return 15
    if timeline_days <= 90:
        return 10
    if timeline_days <= 180:
        return 5
    return 1


def intent_points(page_views: int, email_opens: int, demo_requested: bool) -> int:
    pts = 20 if demo_requested else 0
    pts += min(page_views, 10)       # capped: bots/refresh loops shouldn't dominate
    pts += min(email_opens, 5)
    return pts
