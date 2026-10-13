"""Live Slots page: filter buttons (click events) and automatic refresh."""
import asyncio
from pyscript import document, when
import storage as st

current = {"filter": "all"}


def render():
    st.render_slots("slots-grid", current["filter"], "slots-count", "slots-bar")
    st.set_html("updated", "Last updated " + st.fmt_time(st.now()))


@when("click", ".filter")
def set_filter(event):
    current["filter"] = st.attr(event.target, "data-filter") or "all"
    for button in document.querySelectorAll(".filter"):
        active = st.attr(button, "data-filter") == current["filter"]
        button.classList.toggle("pr", active)
        button.classList.toggle("ol", not active)
    render()


render()
while True:
    await asyncio.sleep(30)
    render()