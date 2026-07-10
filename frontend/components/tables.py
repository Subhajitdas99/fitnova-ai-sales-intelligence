import pandas as pd
import streamlit as st


def render_calls_table(calls: list[dict]) -> None:
    """Render the recent-calls table."""

    st.subheader("Recent Calls")
    if not calls:
        st.info("Upload a call to populate the dashboard.")
        return

    dataframe = pd.DataFrame(calls)
    display_columns = [
        "id",
        "customer_name",
        "sales_rep_name",
        "status",
        "overall_sentiment",
        "outcome",
        "close_probability",
        "created_at",
    ]
    available_columns = [column for column in display_columns if column in dataframe.columns]
    st.dataframe(
        dataframe[available_columns],
        use_container_width=True,
        hide_index=True,
    )
