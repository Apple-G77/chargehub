from pyscript import document, when
import storage as st


def message(element_id, text, ok):
    st.set_html(element_id, text)
    document.getElementById(element_id).className = "msg " + ("ok" if ok else "bad")


def refresh():
    free = st.free_slot_numbers()
    if free:
        st.set_html("next-slot", "The next free slot is picked automatically: "
                    '<b class="green">Slot %d</b>' % free[0])
        st.set_html("slot", '<option value="auto">Auto (Slot %d)</option>' % free[0]
                    + "".join('<option value="%d">Slot %d</option>' % (n, n) for n in free))
    else:
        st.set_html("next-slot", '<b class="green">All %d slots are in use.</b>' % st.SLOT_COUNT)
        st.set_html("slot", '<option value="">No free slot</option>')

    rows = []
    slots = st.load_slots()
    for r in st.load_log():
        if r["claimed_at"]:
            continue
        state = st.slot_state(slots.get(str(r["slot"])))
        rows.append("<tr><td>%s</td><td>%s &middot; %s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            st.esc(r["claim"]), st.esc(r["ptype"]), st.esc(r["brand"]), r["slot"],
            "Ready for pick-up" if state == "ready" else "Charging",
            st.fmt_time(st.parse(r["ends"]))))
    st.set_html("active-body", "".join(rows) or '<tr><td colspan="5">No phones waiting to be claimed.</td></tr>')


def main():
    refresh()

    @when("click", "#checkin")
    def do_checkin(event):
        ok, result = st.check_in(st.val("name"), st.val("course"), st.val("ptype"),
                                 st.val("brand"), st.val("hours"), st.val("note"),
                                 st.val("slot") or "auto")
        if not ok:
            message("checkin-msg", st.esc(result), False)
            return
        message("checkin-msg", "Checked in. Claim number <b>%s</b> &middot; Slot %d &middot; %s &middot; ready about %s."
                % (result["claim"], result["slot"], st.peso(result["fee"]),
                   st.fmt_time(st.parse(result["ends"]))), True)
        for field in ("name", "course", "brand", "note"):
            st.set_val(field, "")
        st.set_val("hours", "1")
        refresh()

    @when("click", "#claim")
    def do_claim(event):
        ok, result = st.claim(st.val("claim-no"), st.val("claimed-by"))
        if not ok:
            message("claim-msg", st.esc(result), False)
            return
        message("claim-msg", "%s claimed by %s. Slot %d is free again." % (
            result["claim"], st.esc(result["claimed_by"]), result["slot"]), True)
        st.set_val("claim-no", "")
        st.set_val("claimed-by", "")
        refresh()

    @when("click", "#lock")
    def do_lock(event):
        st.lock()


if st.require_operator():
    main()
