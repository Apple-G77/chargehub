"""Services page: price calculator (click event)."""
from pyscript import when
import storage as st

MESSAGES = {
    "Wait & Charge": "Stay beside the station. We will tell you when your phone is done.",
    "Leave & Claim": "You will get a claim number. Bring it when you pick up your phone.",
}


def show(html, ok):
    st.set_html("result", html)
    st.document.getElementById("result").className = "msg " + ("ok" if ok else "bad")


@when("click", "#compute")
def compute(event=None):
    try:
        gadgets = int(st.val("gadgets"))
        hours = int(st.val("hours"))
    except ValueError:
        show("Enter whole numbers for gadgets and hours.", False)
        return
    if not 1 <= gadgets <= st.SLOT_COUNT:
        show("Gadgets must be between 1 and %d." % st.SLOT_COUNT, False)
        return
    if not 1 <= hours <= 12:
        show("Hours must be between 1 and 12.", False)
        return
    total = gadgets * hours * st.RATE
    show('<div class="t big green">%s</div><div class="m">%d gadget(s) &times; %d hr &times; %s per hour</div>'
         '<p>%s</p>' % (st.peso(total), gadgets, hours, st.peso(st.RATE),
                        MESSAGES.get(st.val("mode"), "")), True)


compute()
