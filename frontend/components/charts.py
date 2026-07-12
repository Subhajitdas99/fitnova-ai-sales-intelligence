import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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


def render_line_chart(title: str, points: list[dict], y_title: str) -> None:
    st.subheader(title)
    if not points:
        st.info("No processed data available yet.")
        return

    dataframe = pd.DataFrame(points)
    figure = px.line(
        dataframe,
        x="date",
        y="value",
        color="label" if "label" in dataframe.columns else None,
        markers=True,
    )
    figure.update_layout(
        yaxis_title=y_title,
        xaxis_title="Date",
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
    )
    st.plotly_chart(figure, width="stretch")


def render_bar_chart(title: str, points: list[dict], x_key: str = "label") -> None:
    st.subheader(title)
    if not points:
        st.info("No processed data available yet.")
        return

    dataframe = pd.DataFrame(points)
    figure = px.bar(dataframe, x=x_key, y="value")
    figure.update_layout(
        xaxis_title="",
        yaxis_title="Count",
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
    )
    st.plotly_chart(figure, width="stretch")


def render_scatter_chart(title: str, points: list[dict]) -> None:
    st.subheader(title)
    if not points:
        st.info("No category score data available yet.")
        return

    dataframe = pd.DataFrame(points)
    figure = px.box(
        dataframe,
        x="category",
        y="score",
        points="all",
        color="category",
        hover_data=["call_id", "advisor_name"],
    )
    figure.update_layout(
        yaxis_range=[0, 100],
        xaxis_title="Category",
        yaxis_title="Score",
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
        showlegend=False,
    )
    st.plotly_chart(figure, width="stretch")


def render_leaderboard_chart(title: str, advisors: list[dict]) -> None:
    st.subheader(title)
    if not advisors:
        st.info("No advisor data available yet.")
        return

    dataframe = pd.DataFrame(advisors)
    figure = px.bar(
        dataframe,
        x="average_ai_score",
        y="advisor_name",
        orientation="h",
        hover_data=["calls_handled", "average_close_probability"],
    )
    figure.update_layout(
        xaxis_range=[0, 100],
        xaxis_title="Average AI Score",
        yaxis_title="Advisor",
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
    )
    st.plotly_chart(figure, width="stretch")


def render_radar_chart(title: str, metrics: dict[str, float]) -> None:
    st.subheader(title)
    if not metrics:
        st.info("No score data available yet.")
        return

    categories = list(metrics.keys())
    values = list(metrics.values())
    categories.append(categories[0])
    values.append(values[0])
    figure = go.Figure(
        data=[go.Scatterpolar(r=values, theta=categories, fill="toself")]
    )
    figure.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    st.plotly_chart(figure, width="stretch")
