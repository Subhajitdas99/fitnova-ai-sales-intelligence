import pandas as pd
import plotly.express as px
import streamlit as st


def render_distribution_chart(title: str, payload: dict[str, int], color: str) -> None:
    """Render a compact donut chart for dashboard distributions."""

    st.subheader(title)
    if not payload:
        st.info("No processed data available yet.")
        return

    dataframe = pd.DataFrame(
        {"label": list(payload.keys()), "value": list(payload.values())}
    )
    figure = px.pie(
        dataframe,
        names="label",
        values="value",
        hole=0.55,
        color_discrete_sequence=[color],
    )
    figure.update_layout(margin={"l": 0, "r": 0, "t": 20, "b": 0})
    st.plotly_chart(figure, width="stretch")
