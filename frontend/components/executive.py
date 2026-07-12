import pandas as pd
import streamlit as st

from frontend.components.charts import render_distribution_chart


def render_executive_dashboard(executive: dict) -> None:
    st.markdown("## Executive Dashboard")
    first_row = st.columns(4)
    first_row[0].metric(
        "Average AI Quality Score", executive["average_ai_quality_score"]
    )
    first_row[1].metric(
        "Average Close Probability", f"{executive['average_close_probability']}%"
    )
    first_row[2].metric("Total Calls", executive["total_calls"])
    first_row[3].metric("Calls Processed Today", executive["calls_processed_today"])

    second_row = st.columns(2)
    second_row[0].metric(
        "Average Call Duration", f"{executive['average_call_duration']}s"
    )
    second_row[1].metric("Average Engagement", executive["average_engagement"])

    left, right = st.columns(2)
    with left:
        render_distribution_chart(
            "Sentiment Distribution",
            executive["sentiment_distribution"],
            color="#2E8B57",
        )
    with right:
        render_distribution_chart(
            "Outcome Distribution",
            executive["outcome_distribution"],
            color="#1F77B4",
        )


def render_advisor_performance(advisors: list[dict]) -> None:
    st.markdown("## Advisor Performance")
    if not advisors:
        st.info("No completed calls available for advisor performance.")
        return

    dataframe = pd.DataFrame(advisors)
    st.dataframe(
        dataframe[
            [
                "advisor_name",
                "calls_handled",
                "average_ai_score",
                "average_close_probability",
                "average_rapport",
                "average_objection_handling",
                "average_discovery_score",
                "average_compliance_score",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
