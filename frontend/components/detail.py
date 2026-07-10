import pandas as pd
import streamlit as st


def render_call_detail(call_payload: dict) -> None:
    """Render detailed insights for a selected sales call."""

    st.subheader("Selected Call")
    st.write(f"**Customer:** {call_payload['customer_name']}")
    st.write(f"**Sales Rep:** {call_payload['sales_rep_name']}")
    st.write(f"**Status:** {call_payload['status']}")
    st.write(f"**Summary:** {call_payload.get('summary') or 'Processing not completed yet.'}")
    st.write(f"**Coaching Notes:** {call_payload.get('coaching_notes') or 'Not available yet.'}")
    st.write(f"**Next Steps:** {call_payload.get('next_steps') or 'Not available yet.'}")

    metrics_columns = st.columns(4)
    metrics_columns[0].metric("Engagement", call_payload.get("engagement_score") or 0)
    metrics_columns[1].metric(
        "Close Probability",
        f"{call_payload.get('close_probability') or 0}%",
    )
    metrics_columns[2].metric("Objections", call_payload.get("objection_count") or 0)
    metrics_columns[3].metric(
        "Sentiment",
        (call_payload.get("overall_sentiment") or "unknown").title(),
    )

    st.markdown("**Action Items**")
    if call_payload.get("action_items"):
        action_items_df = pd.DataFrame(call_payload["action_items"])
        st.dataframe(action_items_df, use_container_width=True, hide_index=True)
    else:
        st.info("No action items extracted yet.")

    st.markdown("**Transcript**")
    transcript_segments = call_payload.get("transcript_segments", [])
    if transcript_segments:
        transcript_df = pd.DataFrame(transcript_segments)
        st.dataframe(transcript_df, use_container_width=True, hide_index=True)
    else:
        st.info("Transcript will appear after processing completes.")
