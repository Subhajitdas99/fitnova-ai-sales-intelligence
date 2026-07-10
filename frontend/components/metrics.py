import streamlit as st


def render_overview_metrics(overview: dict) -> None:
    """Render headline KPI cards."""

    total, completed, processing, close_probability = st.columns(4)
    total.metric("Total Calls", overview["total_calls"])
    completed.metric("Completed", overview["completed_calls"])
    processing.metric("In Flight", overview["processing_calls"])
    close_probability.metric(
        "Avg Close Probability",
        f"{overview['average_close_probability']}%",
    )
