from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_call_detail(call_payload: dict[str, Any]) -> None:
    """Render detailed insights for a selected sales call."""

    st.subheader("Selected Call")

    st.write(f"**Customer:** {call_payload.get('customer_name', '-')}")
    st.write(f"**Sales Rep:** {call_payload.get('sales_rep_name', '-')}")
    st.write(f"**Status:** {call_payload.get('status', '-')}")
    st.write(
        "**Executive Summary:** "
        + (
            call_payload.get("executive_summary")
            or call_payload.get("summary")
            or "Processing not completed yet."
        )
    )
    st.write(
        f"**Coaching Notes:** {call_payload.get('coaching_notes') or 'Not available yet.'}"
    )
    st.write(
        f"**Next Steps:** {call_payload.get('next_steps') or 'Not available yet.'}"
    )

    st.divider()

    _render_top_metrics(call_payload)
    _render_scorecard(call_payload.get("scorecard"))
    _render_issues_and_recommendations(call_payload)
    _render_action_items(call_payload.get("action_items", []))
    _render_conversation(call_payload.get("transcript_segments", []))


def _render_top_metrics(call_payload: dict[str, Any]) -> None:
    metrics_columns = st.columns(4)
    metrics_columns[0].metric("Engagement", call_payload.get("engagement_score", 0))
    metrics_columns[1].metric(
        "Close Probability",
        f"{call_payload.get('close_probability', 0)}%",
    )
    metrics_columns[2].metric("Objections", call_payload.get("objection_count", 0))
    metrics_columns[3].metric(
        "Sentiment",
        str(call_payload.get("overall_sentiment", "Unknown")).title(),
    )


def _render_scorecard(scorecard: dict[str, Any] | None) -> None:
    if not scorecard:
        return

    st.divider()
    st.markdown("### AI Scorecard")

    overall_score = float(scorecard.get("overall_score", 0))
    overall_confidence = float(scorecard.get("confidence", 0))
    st.metric("Overall Score", f"{overall_score:.0f}/100")
    st.progress(int(overall_score), text=f"Confidence {overall_confidence:.0%}")
    _render_evidence_items(scorecard.get("evidence", []))

    category_scores = scorecard.get("category_scores", [])
    if category_scores:
        st.plotly_chart(
            _build_scorecard_radar_chart(category_scores),
            width="stretch",
        )

    for category_score in category_scores:
        category = (
            str(category_score.get("category", "Unknown")).replace("_", " ").title()
        )
        score = float(category_score.get("score", 0))
        confidence = float(category_score.get("confidence", 0))
        st.markdown(f"**{category}: {score:.0f}/100**")
        st.progress(int(score), text=f"Confidence {confidence:.0%}")
        _render_evidence_items(category_score.get("evidence", []))


def _build_scorecard_radar_chart(category_scores: list[dict[str, Any]]) -> go.Figure:
    categories = [
        str(category_score.get("category", "Unknown")).replace("_", " ").title()
        for category_score in category_scores
    ]
    scores = [
        float(category_score.get("score", 0)) for category_score in category_scores
    ]
    if categories:
        categories.append(categories[0])
        scores.append(scores[0])

    figure = go.Figure(
        data=[
            go.Scatterpolar(
                r=scores,
                theta=categories,
                fill="toself",
                name="Score",
            )
        ]
    )
    figure.update_layout(
        margin={"l": 30, "r": 30, "t": 20, "b": 20},
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        showlegend=False,
    )
    return figure


def _render_evidence_items(evidence_items: list[dict[str, Any]]) -> None:
    if not evidence_items:
        st.caption("No evidence captured for this score.")
        return

    for index, evidence in enumerate(evidence_items, start=1):
        timestamp = float(evidence.get("timestamp", 0))
        speaker = evidence.get("speaker", "Unknown")
        confidence = float(evidence.get("confidence", 0))
        with st.expander(f"Evidence {index} at {timestamp:.1f}s"):
            st.write(f"**Speaker:** {speaker}")
            st.write(f"**Confidence:** {confidence:.0%}")
            st.write(f"**Evidence:** {evidence.get('evidence', '')}")
            quote = evidence.get("supporting_quote")
            if quote:
                st.info(f'"{quote}"')


def _render_issues_and_recommendations(call_payload: dict[str, Any]) -> None:
    issues = call_payload.get("detected_issues", [])
    recommendations = call_payload.get("coaching_recommendations", [])
    if not issues and not recommendations:
        return

    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("### Detected Issues")
        if issues:
            for issue in issues:
                st.write(f"- {issue}")
        else:
            st.success("No issues detected.")

    with right:
        st.markdown("### Coaching Recommendations")
        if recommendations:
            for recommendation in recommendations:
                st.write(f"- {recommendation}")
        else:
            st.success("No coaching recommendations.")


def _render_action_items(action_items: list[dict[str, Any]]) -> None:
    st.divider()
    st.markdown("### Action Items")
    if action_items:
        st.dataframe(
            pd.DataFrame(action_items),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No action items extracted yet.")


def _render_conversation(transcript_segments: list[dict[str, Any]]) -> None:
    st.divider()
    st.markdown("## Conversation")
    if not transcript_segments:
        st.info("Transcript will appear after processing completes.")
        return

    for segment in transcript_segments:
        speaker = (segment.get("speaker") or "Unknown").strip()
        role = (
            "assistant"
            if speaker.lower() in {"sales rep", "sales advisor", "advisor"}
            else "user"
        )
        with st.chat_message(role):
            st.markdown(f"**{speaker}**")
            st.write(segment.get("text", ""))
            start = float(segment.get("start_time", 0))
            end = float(segment.get("end_time", 0))
            confidence = float(segment.get("confidence", 0))
            st.caption(f"{start:.1f}s to {end:.1f}s | Confidence: {confidence:.2f}")
