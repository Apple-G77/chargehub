"""Home page: live status, slot board and today's schedule. Refreshes every 30 s."""
import asyncio
import storage as st


def render():
    st.render_status("status-card")
    st.render_slots("slots-grid", "all", "slots-count", "slots-bar")
    st.render_schedule("schedule-body")


render()
while True:                                # keep the page up to date
    await asyncio.sleep(30)
    render()
