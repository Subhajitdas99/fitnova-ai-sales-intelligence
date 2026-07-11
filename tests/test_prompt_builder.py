from pathlib import Path

from backend.app.application.services.prompt_builder import PromptBuilder
from backend.app.domain.entities.transcript import TranscriptSegment


def test_prompt_builder_renders_template_with_call_context(tmp_path: Path) -> None:
    template_path = tmp_path / "template.md"
    template_path.write_text(
        "Customer={{ customer_name }}\n"
        "Rep={{ sales_rep_name }}\n"
        "Notes={{ notes }}\n"
        "Transcript={{ transcript }}",
        encoding="utf-8",
    )
    builder = PromptBuilder(template_path=template_path)

    prompt = builder.build_sales_call_analysis_prompt(
        customer_name="Acme",
        sales_rep_name="Jordan",
        transcript_segments=[
            TranscriptSegment(
                speaker="Sales Rep",
                text="We can support onboarding.",
                start_time=0.0,
                end_time=2.5,
                confidence=0.95,
            )
        ],
        notes="Enterprise pilot",
    )

    assert "Customer=Acme" in prompt
    assert "Rep=Jordan" in prompt
    assert "Notes=Enterprise pilot" in prompt
    assert "[0.0-2.5] Sales Rep: We can support onboarding." in prompt
