import pytest
from pydantic import ValidationError

from backend.app.application.dto.scorecard import CategoryScore, Scorecard


def test_scorecard_requires_evidence_for_every_score() -> None:
    with pytest.raises(ValidationError):
        Scorecard(
            overall_score=80,
            confidence=0.9,
            evidence=[],
            category_scores=[
                CategoryScore(
                    category="discovery",
                    score=80,
                    confidence=0.9,
                    evidence=[],
                )
            ],
        )
