import os

import requests
import streamlit as st
from dotenv import load_dotenv

from frontend.components.charts import render_distribution_chart
from frontend.components.detail import render_call_detail
from frontend.components.metrics import render_overview_metrics
from frontend.components.tables import render_calls_table
from frontend.services.api_client import FitNovaApiClient

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()


def get_backend_url() -> str:
    """
    Resolve backend URL using the following priority:

    1. Environment Variable (.env)
    2. Streamlit Secrets (Deployment)
    3. Local Default
    """

    # 1. Environment Variable
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url

    # 2. Streamlit Secrets
    try:
        if "BACKEND_URL" in st.secrets:
            return st.secrets["BACKEND_URL"]
    except Exception:
        pass

    # 3. Local Default
    return "http://127.0.0.1:8000"


BACKEND_URL = get_backend_url()

client = FitNovaApiClient(BACKEND_URL)

# ---------------------------------------------------------
# Streamlit Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="FitNova AI Sales Intelligence",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 FitNova AI Sales Intelligence")
st.caption(
    "Operational cockpit for AI-powered sales call transcription, "
    "analysis, coaching, and quality monitoring."
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("📤 Upload Sales Call")

    uploaded_file = st.file_uploader(
        "Audio File",
        type=["mp3", "wav", "m4a", "mp4", "mpeg", "ogg"],
    )

    customer_name = st.text_input(
        "Customer Name",
        placeholder="Rahul Sharma",
    )

    sales_rep_name = st.text_input(
        "Sales Advisor",
        placeholder="Jordan Lee",
    )

    language = st.selectbox(
        "Language Hint",
        ["auto", "en", "hi", "es"],
        index=0,
    )

    notes = st.text_area(
        "Notes",
        placeholder="Optional notes...",
    )

    if st.button("🚀 Upload & Process", width="stretch"):

        if uploaded_file is None:
            st.warning("Please upload an audio file.")
            st.stop()

        if not customer_name.strip():
            st.warning("Customer name is required.")
            st.stop()

        if not sales_rep_name.strip():
            st.warning("Sales advisor name is required.")
            st.stop()

        try:

            result = client.upload_call(
                file_name=uploaded_file.name,
                file_bytes=uploaded_file.getvalue(),
                customer_name=customer_name,
                sales_rep_name=sales_rep_name,
                language=language,
                notes=notes,
            )

            st.success(result.get("message", "Call uploaded successfully."))

        except requests.RequestException as exc:
            st.error(f"Upload failed:\n\n{exc}")

# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

try:

    overview = client.get_dashboard_overview()

    calls = client.list_calls(limit=20)

except requests.RequestException as exc:

    st.error(
        "Unable to connect to the backend.\n\n"
        "Please make sure FastAPI is running at:\n\n"
        f"{BACKEND_URL}\n\n"
        f"Error:\n{exc}"
    )

    st.stop()

# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

render_overview_metrics(overview)

# ---------------------------------------------------------
# Charts
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    render_distribution_chart(
        "Sentiment Distribution",
        overview["sentiment_breakdown"],
        color="#2E8B57",
    )

with right:

    render_distribution_chart(
        "Outcome Distribution",
        overview["outcome_breakdown"],
        color="#1F77B4",
    )

# ---------------------------------------------------------
# Calls Table
# ---------------------------------------------------------

render_calls_table(calls)

# ---------------------------------------------------------
# Call Detail
# ---------------------------------------------------------

if calls:

    selected_call_id = st.selectbox(
        "Inspect Call",
        options=[call["id"] for call in calls],
        format_func=lambda cid: next(
            (
                f"{call['customer_name']} | "
                f"{call['sales_rep_name']} | "
                f"{call['status']}"
                for call in calls
                if call["id"] == cid
            ),
            cid,
        ),
    )

    call = client.get_call(selected_call_id)

    render_call_detail(call)
