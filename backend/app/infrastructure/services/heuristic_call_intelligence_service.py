from collections import Counter

from backend.app.application.interfaces.services import CallIntelligenceServiceProtocol
from backend.app.domain.entities.analysis import ActionItem, CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallOutcome, SalesSentiment


class HeuristicCallIntelligenceService(CallIntelligenceServiceProtocol):
    """Keyword-based intelligence engine that keeps the MVP runnable without LLM access."""

    _objection_keywords = {
        "price": "Pricing",
        "pricing": "Pricing",
        "budget": "Budget",
        "integration": "Integration",
        "security": "Security",
        "onboarding": "Onboarding",
        "timeline": "Timeline",
    }
    _positive_keywords = {"pilot", "proposal", "review", "good", "support"}
    _negative_keywords = {"concern", "issue", "budget", "delay", "blocked"}
    _product_keywords = {"platform", "crm", "api", "analytics", "pilot"}

    def analyze(
        self,
        customer_name: str,
        sales_rep_name: str,
        transcript_segments: list[TranscriptSegment],
        notes: str | None = None,
    ) -> CallAnalysis:
        rep_segments = [segment for segment in transcript_segments if segment.speaker == "Sales Rep"]
        customer_segments = [
            segment for segment in transcript_segments if segment.speaker != "Sales Rep"
        ]
        rep_talk_time = sum(segment.end_time - segment.start_time for segment in rep_segments)
        customer_talk_time = sum(
            segment.end_time - segment.start_time for segment in customer_segments
        )
        total_talk_time = max(rep_talk_time + customer_talk_time, 1.0)

        full_text = " ".join(segment.text.lower() for segment in transcript_segments)
        detected_objections = sorted(
            {
                label
                for keyword, label in self._objection_keywords.items()
                if keyword in full_text
            }
        )
        products_discussed = sorted(
            {
                keyword.upper() if keyword == "api" else keyword.title()
                for keyword in self._product_keywords
                if keyword in full_text
            }
        )
        keyword_counts = Counter(word.strip(".,!?") for word in full_text.split())
        key_topics = [
            topic.title()
            for topic, _ in keyword_counts.most_common(5)
            if len(topic) > 4
        ]

        positive_score = sum(1 for keyword in self._positive_keywords if keyword in full_text)
        negative_score = sum(1 for keyword in self._negative_keywords if keyword in full_text)
        if positive_score and negative_score:
            sentiment = SalesSentiment.MIXED
        elif positive_score > negative_score:
            sentiment = SalesSentiment.POSITIVE
        elif negative_score > positive_score:
            sentiment = SalesSentiment.NEGATIVE
        else:
            sentiment = SalesSentiment.NEUTRAL

        if "pilot" in full_text or "proposal" in full_text:
            outcome = CallOutcome.FOLLOW_UP
        elif "signed" in full_text or "approved" in full_text:
            outcome = CallOutcome.WON
        elif "not interested" in full_text or "blocked" in full_text:
            outcome = CallOutcome.LOST
        else:
            outcome = CallOutcome.NURTURING

        engagement_score = min(
            100.0,
            round(60 + len(transcript_segments) * 3 - len(detected_objections) * 4, 2),
        )
        close_probability = min(
            100.0,
            max(
                5.0,
                round(
                    40
                    + positive_score * 12
                    - negative_score * 8
                    + (8 if outcome == CallOutcome.FOLLOW_UP else 0),
                    2,
                ),
            ),
        )
        follow_up_required = outcome in {CallOutcome.FOLLOW_UP, CallOutcome.NURTURING}

        summary = (
            f"{sales_rep_name} introduced FitNova AI Sales Intelligence to {customer_name}, "
            f"while the customer raised {len(detected_objections)} primary concerns around "
            f"{', '.join(detected_objections).lower() if detected_objections else 'solution fit'}. "
            "The conversation ended with interest in the next commercial step."
        )
        coaching_notes = (
            "Lead with a sharper value narrative tied to onboarding speed and CRM integration, "
            "then validate budget expectations earlier to reduce objection handling later in the call."
        )
        if notes:
            coaching_notes = f"{coaching_notes} Context provided by the rep: {notes}"

        action_items = [
            ActionItem(
                description="Send tailored proposal and pilot rollout plan.",
                owner=sales_rep_name,
                due_hint="Within 2 business days",
                priority="high",
            ),
            ActionItem(
                description="Share CRM integration checklist with the customer team.",
                owner=sales_rep_name,
                due_hint="Before technical follow-up",
                priority="medium",
            ),
        ]
        next_steps = " ".join(action_item.description for action_item in action_items)

        return CallAnalysis(
            summary=summary,
            sentiment=sentiment,
            outcome=outcome,
            coaching_notes=coaching_notes,
            next_steps=next_steps,
            objection_count=len(detected_objections),
            talk_ratio_rep=round(rep_talk_time / total_talk_time, 2),
            talk_ratio_customer=round(customer_talk_time / total_talk_time, 2),
            engagement_score=engagement_score,
            close_probability=close_probability,
            follow_up_required=follow_up_required,
            detected_objections=detected_objections,
            products_discussed=products_discussed,
            key_topics=key_topics,
            action_items=action_items,
            transcript_segments=transcript_segments,
        )
