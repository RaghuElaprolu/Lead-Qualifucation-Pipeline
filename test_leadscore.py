import csv, tempfile, unittest
from pathlib import Path
from leadscore import Lead, score_lead, run_pipeline
from leadscore import features as f
from leadscore.llm import ClaudeQualifier, HeuristicQualifier, clamp

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_leads.csv"


class FeatureTests(unittest.TestCase):
    def test_email_validation(self):
        self.assertTrue(f.is_valid_email("a@b.co"))
        self.assertFalse(f.is_valid_email("bad-email"))

    def test_seniority_order(self):
        self.assertGreater(f.seniority_points("CEO"), f.seniority_points("VP Sales"))
        self.assertGreater(f.seniority_points("VP Sales"), f.seniority_points("Analyst"))
        self.assertEqual(f.seniority_points("Intern"), 0)

    def test_intent_is_capped(self):
        self.assertEqual(f.intent_points(10_000, 10_000, False), 15)


class ScoringTests(unittest.TestCase):
    def test_strong_lead_is_hot(self):
        lead = Lead("p@acme.com", company="Acme", title="VP Ops", employees=1200,
                    budget_usd=150000, timeline_days=30, page_views=14, email_opens=6,
                    demo_requested=True, notes="budget approved, evaluating")
        r = score_lead(lead)
        self.assertEqual(r.tier, "hot")
        self.assertLessEqual(r.score, 100)

    def test_free_email_and_no_company_penalised(self):
        base = dict(title="Director", employees=100, page_views=5)
        corp = score_lead(Lead("a@corp.com", company="Corp", **base))
        free = score_lead(Lead("a@gmail.com", **base))
        self.assertEqual(corp.score - free.score, 15)

    def test_score_never_negative(self):
        r = score_lead(Lead("a@gmail.com", notes="student just browsing no budget competitor"))
        self.assertEqual(r.score, 0)
        self.assertEqual(r.tier, "cold")

    def test_llm_adjustment_is_clamped(self):
        self.assertEqual(clamp(999), 10)
        self.assertEqual(clamp(-999), -10)

    def test_claude_qualifier_falls_back_without_sdk_or_key(self):
        adj, why = ClaudeQualifier().adjust("budget approved")
        self.assertIn(adj, range(-10, 11))
        self.assertTrue(why)  # either real rationale or 'fallback (...)'


class PipelineTests(unittest.TestCase):
    def test_sample_file_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out.csv"
            rep = run_pipeline(DATA, out)
            self.assertEqual(len(rep.rejected), 1)          # bad-email
            self.assertEqual(rep.duplicates_dropped, 1)     # priya twice
            self.assertEqual(len(rep.scored), 4)
            with open(out, newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(rows[0]["email"], "priya@acmelogistics.com")
            self.assertEqual(rows[0]["tier"], "hot")
            self.assertEqual(rows[1]["tier"], "warm")   # dana: mid-size, budget, 90d window
            self.assertEqual(rows[-1]["tier"], "cold")
            scores = [int(r["score"]) for r in rows]
            self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
