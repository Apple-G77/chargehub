import math
from pyscript import document, when
import storage as st

state = {"period": "week"}
TITLES = {"today": "Today", "week": "This week", "month": "This month"}


def render():
    e = st.earnings(state["period"])

    average = e["revenue"] / e["sessions"] if e["sessions"] else st.RATE
    needed = math.ceil(e["expenses"] / average)
    left = max(needed - e["sessions"], 0)

    cards = [(str(e["sessions"]), "charging sessions"),
             (st.peso(e["revenue"]), "total collected"),
             (st.peso(e["expenses"]), "expenses (estimate)"),
             (st.peso(e["profit"]), "profit"),
             (str(needed), "sessions to break even"),
             (str(left), "sessions still needed")]
    st.set_html("e-summary", "".join(
        '<div class="c"><div class="t big green">%s</div><div class="m">%s</div></div>' % c for c in cards))

    rows = ["<tr><td>%s</td><td>%d</td><td>%s</td></tr>" % (
        day.strftime("%a, %b %d"), count, st.peso(money)) for day, (count, money) in e["rows"]]
    rows.append("<tr><td><b>Total</b></td><td><b>%d</b></td><td><b>%s</b></td></tr>" % (
        e["sessions"], st.peso(e["revenue"])))
    st.set_html("e-body", "".join(rows) if e["rows"] else
                '<tr><td colspan="3">No sessions yet for this period.</td></tr>')

    st.set_html("share",
                "Reserve (%d%%): <b>%s</b><br>To share (%d%%): <b>%s</b><br>Per member (%d): <b>%s</b>" % (
                    round(st.RESERVE_RATE * 100), st.peso(e["reserve"]),
                    round((1 - st.RESERVE_RATE) * 100), st.peso(e["to_share"]),
                    st.MEMBER_COUNT, st.peso(e["per_member"])))
    st.set_html("e-title", TITLES[state["period"]])

    for button in document.querySelectorAll(".tab"):
        active = st.attr(button, "data-period") == state["period"]
        button.classList.toggle("pr", active)
        button.classList.toggle("ol", not active)


def main():
    st.set_val("expenses", str(st.get_expenses()))
    render()

    @when("click", ".tab")
    def change_period(event):
        state["period"] = st.attr(event.target, "data-period") or "week"
        render()

    @when("input", "#expenses")
    def change_expenses(event):
        try:
            value = float(st.val("expenses"))
        except ValueError:
            return
        if value >= 0:
            st.set_expenses(value)
            render()

    @when("click", "#lock")
    def do_lock(event):
        st.lock()


if st.require_operator():
    main()