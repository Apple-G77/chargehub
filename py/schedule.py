"""Operator: Schedule & Location. What students see on the Find Us page."""
from pyscript import document, when
import storage as st


def message(element_id, text, ok):
    st.set_html(element_id, text)
    document.getElementById(element_id).className = "msg " + ("ok" if ok else "bad")


def render():
    st.render_schedule("schedule-body", with_delete=True)
    st.render_status("status-card")


def main():
    st.set_html("s-day", st.options(st.DAYS))
    st.set_html("s-loc", st.options(st.LOCATIONS))
    st.set_html("s-duty", st.options(st.MEMBERS))
    st.set_html("l-loc", st.options(st.LOCATIONS))
    st.set_html("l-duty", st.options(st.MEMBERS))
    st.set_html("l-status", "".join('<option value="%s">%s</option>' % (k, v[0].title())
                                    for k, v in st.STATUS.items()))
    render()

    @when("click", "#s-add")
    def add(event):
        ok, text = st.add_schedule(st.val("s-day"), st.val("s-time"), st.val("s-loc"), st.val("s-duty"))
        message("s-msg", st.esc(text), ok)
        if ok:
            st.set_val("s-time", "")
            render()

    @when("click", "#l-update")
    def update_location(event):
        st.set_location(st.val("l-loc"), st.val("l-status"), st.val("l-note"), st.val("l-duty"))
        message("l-msg", "Location updated. Students can see it on the Find Us page.", True)
        st.set_val("l-note", "")
        render()

    @when("click", "#schedule-body")         # one listener handles every Delete button
    def delete(event):
        item_id = st.attr(event.target, "data-id")
        if item_id:
            st.delete_schedule(item_id)
            render()

    @when("click", "#s-sample")
    def sample(event):
        st.load_sample_schedule()
        message("s-msg", "Sample schedule loaded.", True)
        render()

    @when("click", "#lock")
    def do_lock(event):
        st.lock()


if st.require_operator():
    main()
