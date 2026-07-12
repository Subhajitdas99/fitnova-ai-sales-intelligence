# Sprint 7 Analytics Architecture

## Design Decisions

### Analytics Lives In The Application Layer

Dashboard and analytics calculations are use-case logic. They combine persisted call records into executive metrics, advisor performance, coaching cards, and chart-ready datasets. Keeping this logic in `application/services` lets FastAPI, Streamlit, tests, or a future worker reuse the same behavior without duplicating formulas.

### Repository Only Retrieves Data

The repository now exposes `list_calls_for_analytics()`, which loads calls and related transcript, action item, and scorecard evidence rows. It does not calculate averages, trends, rankings, or coaching guidance. This keeps persistence focused on database access and prevents SQLAlchemy models from becoming business services.

### Dashboard Remains Presentation-Only

The Streamlit app calls API endpoints that already return analytics DTOs. Streamlit renders cards, tables, progress bars, and Plotly charts, but it does not decide how to calculate quality score, advisor ranking, coaching priorities, issue frequency, or trends. This keeps the UI easy to replace and keeps business behavior testable without a browser.

### DTOs Define The Reporting Contract

Sprint 7 responses are Pydantic DTOs in the application layer. They give the backend and frontend a typed contract for executive KPIs, advisor leaderboard rows, coaching cards, time-series points, frequency points, and category score distributions.

### Plotly Is Used At The Presentation Boundary

The backend returns simple chart-ready arrays. Plotly is only used in Streamlit because chart rendering is a presentation concern, while the reusable analytics data remains framework-neutral.
