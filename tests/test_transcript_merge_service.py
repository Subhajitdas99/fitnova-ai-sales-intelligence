from backend.app.application.dto.diarization_result import (
    DiarizationResult,
    DiarizationSpeakerSegment,
)
from backend.app.application.services.transcript_merge_service import (
    TranscriptDiarizationMergeService,
)
from backend.app.domain.entities.transcript import TranscriptSegment


def test_merge_assigns_speaker_with_largest_time_overlap() -> None:
    transcript_segments = [
        TranscriptSegment(
            speaker="Unknown",
            text="First segment",
            start_time=0.0,
            end_time=5.0,
            confidence=0.9,
        ),
        TranscriptSegment(
            speaker="Unknown",
            text="Second segment",
            start_time=5.0,
            end_time=8.0,
            confidence=0.8,
        ),
    ]
    diarization_result = DiarizationResult(
        provider="test",
        segments=[
            DiarizationSpeakerSegment(
                speaker="Customer",
                start_time=0.0,
                end_time=1.0,
            ),
            DiarizationSpeakerSegment(
                speaker="Sales Rep",
                start_time=1.0,
                end_time=5.2,
            ),
            DiarizationSpeakerSegment(
                speaker="Customer",
                start_time=5.2,
                end_time=8.0,
            ),
        ],
    )

    merged_segments = TranscriptDiarizationMergeService().merge(
        transcript_segments=transcript_segments,
        diarization_result=diarization_result,
    )

    assert [segment.speaker for segment in merged_segments] == ["Sales Rep", "Customer"]
    assert [segment.text for segment in merged_segments] == ["First segment", "Second segment"]


def test_merge_preserves_transcript_speaker_when_diarization_is_empty() -> None:
    transcript_segments = [
        TranscriptSegment(
            speaker="Unknown",
            text="Unassigned",
            start_time=0.0,
            end_time=2.0,
            confidence=0.7,
        )
    ]

    merged_segments = TranscriptDiarizationMergeService().merge(
        transcript_segments=transcript_segments,
        diarization_result=DiarizationResult(provider="test"),
    )

    assert merged_segments[0].speaker == "Unknown"
    assert merged_segments[0].text == "Unassigned"
