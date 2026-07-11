from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.application.dto.call_context import CallCreationData
from backend.app.application.dto.scorecard import CategoryScore, Evidence, Scorecard
from backend.app.domain.entities.analysis import CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallOutcome, SalesSentiment
from backend.app.infrastructure.database.base import Base
from backend.app.infrastructure.repositories.call_repository import CallRepository


def test_repository_persists_llm_analysis_fields() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    with session_factory() as session:
        repository = CallRepository(session)
        repository.create_call(
            CallCreationData(
                call_id="call-1",
                original_file_name="call.wav",
                stored_file_name="call-1.wav",
                audio_path="/tmp/call.wav",
                customer_name="Acme",
                sales_rep_name="Jordan",
                language="en",
            )
        )
        repository.save_analysis(
            call_id="call-1",
            analysis=CallAnalysis(
                summary="Legacy summary",
                executive_summary="Executive summary",
                overall_score=88,
                overall_confidence=0.92,
                category_scores={"discovery": 90},
                category_score_details=[
                    {
                        "category": "discovery",
                        "score": 90,
                        "confidence": 0.87,
                    }
                ],
                scorecard=Scorecard(
                    overall_score=88,
                    confidence=0.92,
                    evidence=[
                        Evidence(
                            evidence="Strong next step clarity.",
                            timestamp=4.2,
                            supporting_quote="I will send the proposal tomorrow.",
                        )
                    ],
                    category_scores=[
                        CategoryScore(
                            category="discovery",
                            score=90,
                            confidence=0.87,
                            evidence=[
                                Evidence(
                                    evidence="Rep asked about business need.",
                                    timestamp=1.0,
                                    supporting_quote="What are your goals?",
                                )
                            ],
                        )
                    ],
                ),
                detected_issues=["Discovery could be deeper."],
                coaching_recommendations=["Ask one more implication question."],
                sentiment=SalesSentiment.POSITIVE,
                outcome=CallOutcome.FOLLOW_UP,
                coaching_notes="Ask one more implication question.",
                next_steps="Send proposal.",
                objection_count=1,
                talk_ratio_rep=0.6,
                talk_ratio_customer=0.4,
                engagement_score=88,
                close_probability=78,
                follow_up_required=True,
                transcript_segments=[
                    TranscriptSegment(
                        speaker="Sales Rep",
                        text="Hello",
                        start_time=0,
                        end_time=1,
                        confidence=0.9,
                    )
                ],
            ),
            duration_seconds=1,
        )

        record = repository.get_call("call-1")

    assert record is not None
    assert record.executive_summary == "Executive summary"
    assert record.overall_score == 88
    assert record.overall_confidence == 0.92
    assert record.category_scores == {"discovery": 90}
    assert record.category_score_details[0]["confidence"] == 0.87
    assert record.detected_issues == ["Discovery could be deeper."]
    assert record.coaching_recommendations == ["Ask one more implication question."]
    assert len(record.scorecard_evidence) == 2
    assert record.scorecard["evidence"][0]["supporting_quote"] == (
        "I will send the proposal tomorrow."
    )
