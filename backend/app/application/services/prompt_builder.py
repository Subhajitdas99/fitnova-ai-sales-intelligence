from pathlib import Path

from backend.app.domain.entities.transcript import TranscriptSegment


class PromptBuilder:
    """Builds prompts from stored templates and call context."""

    def __init__(self, template_path: Path | None = None) -> None:
        self._template_path = template_path or (
            Path(__file__).resolve().parents[1]
            / "prompt_templates"
            / "sales_call_analysis.md"
        )

    def build_sales_call_analysis_prompt(
        self,
        customer_name: str,
        sales_rep_name: str,
        transcript_segments: list[TranscriptSegment],
        notes: str | None = None,
    ) -> str:
        template = self._template_path.read_text(encoding="utf-8")
        transcript = "\n".join(
            (
                f"[{segment.start_time:.1f}-{segment.end_time:.1f}] "
                f"{segment.speaker}: {segment.text}"
            )
            for segment in transcript_segments
        )
        replacements = {
            "{{ customer_name }}": customer_name,
            "{{ sales_rep_name }}": sales_rep_name,
            "{{ notes }}": notes or "None",
            "{{ transcript }}": transcript,
        }
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        return template
