import streamlit as st


def render_coaching_dashboard(coaching_cards: list[dict]) -> None:
    st.markdown("## AI Coaching Dashboard")
    if not coaching_cards:
        st.info("No coaching cards are available yet.")
        return

    for card in coaching_cards:
        with st.container(border=True):
            st.markdown(f"### {card['advisor_name']} with {card['customer_name']}")
            st.caption(f"Call ID: {card['call_id']}")
            left, right = st.columns(2)
            with left:
                st.markdown("**Strengths**")
                for strength in card["strengths"]:
                    st.write(f"- {strength}")
                st.markdown("**Priority Improvement**")
                st.write(card["priority_improvement"])
                st.markdown("**Practice Goal**")
                st.write(card["practice_goal"])
            with right:
                st.markdown("**Weaknesses**")
                for weakness in card["weaknesses"]:
                    st.write(f"- {weakness}")
                st.markdown("**Manager Feedback**")
                st.write(card["manager_feedback"])
                st.markdown("**Next Coaching Exercise**")
                st.write(card["next_coaching_exercise"])
