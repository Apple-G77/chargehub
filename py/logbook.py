from pyscript import document, window, when
import storage as st


def render():
    today = st.now().strftime("%Y-%m-%d")
    todays = [r for r in st.load_log() if r["in_at"][:10] == today]
    waiting = [r for r in st.load_log() if not r["claimed_at"]]
    cards = [(str(len(todays)), "phones charged today"),
             (str(len(waiting)), "not yet claimed"),
             (st.peso(sum(r["fee"] for r in todays)), "revenue today")]
    st.set_html("summary", "".join(
        '<div class="c"><div class="t big green">%s</div><div class="m">%s</div></div>' % c for c in cards))

    rows = []
    for r in st.search_log(st.val("date"), st.val("search")):
        claimed = ("%s" % st.fmt_dt(st.parse(r["claimed_at"]))) if r["claimed_at"] else "&mdash;"
        by = st.esc(r["claimed_by"]) if r["claimed_by"] else "Not yet claimed"
        rows.append("<tr><td>%s</td><td>%s</td><td>%s &middot; %s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            st.esc(r["claim"]), st.esc(r["name"]), st.esc(r["ptype"]), st.esc(r["brand"]),
            r["slot"], st.fmt_dt(st.parse(r["in_at"])), claimed, by))
    st.set_html("log-body", "".join(rows) or '<tr><td colspan="7">No records match.</td></tr>')


def main():
    st.set_val("date", st.now().strftime("%Y-%m-%d"))
    render()

    @when("input", "#search")
    def on_search(event):
        render()

    @when("change", "#date")
    def on_date(event):
        render()

    @when("click", "#all-dates")
    def show_all(event):
        st.set_val("date", "")
        render()

    @when("click", "#reset")
    def reset(event):
        if window.confirm("Delete ALL ChargeHub data saved in this browser?"):
            st.reset_all()
            render()

    @when("click", "#lock")
    def do_lock(event):
        st.lock()


if st.require_operator():
    main()
