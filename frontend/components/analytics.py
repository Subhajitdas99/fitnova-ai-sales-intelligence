import pandas as pd
import streamlit as st

from frontend.components.charts import (
    render_bar_chart,
    render_leaderboard_chart,
    render_line_chart,
    render_scatter_chart,
)


def render_analytics_dashboard(analytics: dict) -> None:
    st.markdown("## Analytics")
    top_left, top_right = st.columns(2)
    with top_left:
        render_line_chart("Call Volume", analytics["call_volume"], y_title="Calls")
    with top_right:
        render_line_chart(
            "Close Probability Trend",
            analytics["close_probability_trend"],
            y_title="Close Probability",
        )

    middle_left, middle_right = st.columns(2)
    with middle_left:
        render_bar_chart("Issue Frequency", analytics["issue_frequency"])
    with middle_right:
        render_bar_chart("Top Customer Concerns", analytics["top_customer_concerns"])

    lower_left, lower_right = st.columns(2)
    with lower_left:
        render_scatter_chart(
            "Category Score Distribution",
            analytics["category_score_distribution"],
        )
    with lower_right:
        render_leaderboard_chart(
            "Advisor Leaderboard", analytics["advisor_leaderboard"]
        )

    sentiment_trend = analytics.get("sentiment_trend", [])
    if sentiment_trend:
        st.markdown("### Sentiment Trend")
        dataframe = pd.DataFrame(sentiment_trend)
        st.dataframe(dataframe, width="stretch", hide_index=True)
