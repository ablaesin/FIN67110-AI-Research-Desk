#!/usr/bin/env python3
"""Offline rule tests for the Lab 06 seeker."""
from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).parent))
import seeker
import closes_reader


class SeekerRules(unittest.TestCase):
    def setUp(self):
        self.factors = {"window_days": 180, "factors": [
            {"name": "weakness", "direction": "lower", "weight": 3, "field": "weakness"},
            {"name": "size", "direction": "higher", "weight": 2, "field": "size"},
        ]}
        self.row = {"distribution_date": "2026-10-01", "weakness": "-1", "size": "1"}

    def test_score_uses_declared_direction_and_weight(self):
        points, details, reason = seeker.score(self.row, self.factors, date(2026, 11, 10))
        self.assertEqual((points, details, reason), (5, ["weakness 3", "size 2"], ""))

    def test_zero_weight_removes_only_that_factor_points(self):
        changed = {**self.factors, "factors": [dict(item) for item in self.factors["factors"]]}
        changed["factors"][0]["weight"] = 0
        points, details, _ = seeker.score(self.row, changed, date(2026, 11, 10))
        self.assertEqual(points, 2)
        self.assertEqual(details, ["size 2"])

    def test_missing_distribution_date_is_unranked(self):
        points, _, reason = seeker.score({"size": "1"}, self.factors, date(2026, 11, 10))
        self.assertIsNone(points); self.assertEqual(reason, "missing distribution date")

    def test_fund_and_missing_information_statement_are_dropped(self):
        self.assertEqual(seeker.exclusion_reason("This is a registered investment company."), "fund registrant")
        self.assertEqual(seeker.exclusion_reason("Ordinary Form 10 text."), "Form 10 has no information statement")

    def test_no_parent_distribution_evidence_is_not_a_spinoff(self):
        facts = seeker.find_facts("Information statement about ordinary registration.", "https://example.test")
        self.assertFalse(facts["parent"] or facts["distribution_date"] or facts["distribution_ratio"])

    def test_closes_reader_uses_last_unadjusted_close_on_or_before_date(self):
        with tempfile.TemporaryDirectory() as folder:
            export = Path(folder) / "closes.csv"
            export.write_text("ticker,date,close\nABC,2026-10-02,10\nABC,2026-10-05,11\n", encoding="utf-8")
            self.assertEqual(closes_reader.last_close(export, "abc", date(2026, 10, 3)), (date(2026, 10, 2), 10.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
