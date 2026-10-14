"""Find Us page: where the ChargeHub team is today (read-only for students)."""
import asyncio
import storage as st


def render():
    st.render_status("status-card")
    st.render_schedule("schedule-body")
    st.render_history("history-list")


render()
while True:
    await asyncio.sleep(30)
    render()
