import json
from datetime import datetime, date, timedelta
from html import escape as esc
from pyscript import document, window

# ---------------------------------------------------------------- settings
RATE = 5                      # pesos per hour per gadget
SLOT_COUNT = 8                # slots on the portable charging unit
MONTHLY_EXPENSES = 400        # default, can be changed on the Earnings page
SCHOOL_DAYS = 20              # school days per month
MEMBER_COUNT = 5
RESERVE_RATE = 0.30           # 30% kept as business reserve, 70% shared

MEMBERS = ["Apple Mae", "Alliah", "Jomar", "Jhunro Niño", "MaryShien"]
LOCATIONS = ["IT Building hallway", "Canteen", "Covered court", "Other"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
STATUS = {                    # key: (label, pill color class)
    "open": ("OPEN NOW", "av"),
    "break": ("ON BREAK", "rd"),
    "moving": ("MOVING", "rd"),
    "closed": ("CLOSED", "oc"),
}


# ------------------------------------------------------------ small helpers
def now():
    """Current local time of the visitor's browser, as a Python datetime."""
    d = window.Date.new()
    return datetime(d.getFullYear(), d.getMonth() + 1, d.getDate(),
                    d.getHours(), d.getMinutes(), d.getSeconds())


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def parse(text):
    return datetime.fromisoformat(text)


def fmt_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0")


def fmt_dt(dt):
    return dt.strftime("%b %d, %Y ") + fmt_time(dt)


def peso(amount):
    if abs(amount - round(amount)) < 0.005:
        text = "{:,.0f}".format(abs(amount))
    else:
        text = "{:,.2f}".format(abs(amount))
    return ("-" if amount < -0.004 else "") + "\u20b1" + text


def set_html(element_id, html):
    """Put HTML inside the element with this id (does nothing if missing)."""
    try:
        document.getElementById(element_id).innerHTML = html
    except Exception:
        pass


def val(element_id):
    """Text typed into an input / selected in a dropdown, trimmed."""
    return str(document.getElementById(element_id).value).strip()


def set_val(element_id, value):
    document.getElementById(element_id).value = value


def attr(element, name):
    try:
        value = element.getAttribute(name)
    except Exception:
        return ""
    return value if isinstance(value, str) else ""


def options(items, selected=None):
    return "".join('<option%s>%s</option>' % (" selected" if i == selected else "", esc(i))
                   for i in items)


# --------------------------------------------------------- browser storage
def _get(key, default):
    try:
        raw = window.localStorage.getItem(key)
        if not isinstance(raw, str):
            return default
        return json.loads(raw)
    except Exception:
        return default


def _put(key, value):
    window.localStorage.setItem(key, json.dumps(value))


# ------------------------------------------------------ operator protection
def is_operator():
    return window.sessionStorage.getItem("operator") == "yes"


def require_operator():
    """Call at the top of every operator page. Sends visitors to the PIN page."""
    if is_operator():
        document.body.classList.remove("locked")
        return True
    window.location.href = "pin.html"
    return False


def lock():
    window.sessionStorage.removeItem("operator")


# ------------------------------------------------------------------- slots
def load_slots():
    saved = _get("ch_slots", {})
    if not isinstance(saved, dict):
        saved = {}
    return {str(i): saved.get(str(i)) for i in range(1, SLOT_COUNT + 1)}


def slot_state(slot):
    """'available', 'occupied' (still charging) or 'ready' (time is up)."""
    if not slot:
        return "available"
    return "ready" if now() >= parse(slot["ends"]) else "occupied"


def free_slot_numbers(slots=None):
    slots = slots or load_slots()
    return [i for i in range(1, SLOT_COUNT + 1) if not slots[str(i)]]


# -------------------------------------------------------------------- log
def load_log():
    log = _get("ch_log", [])
    return log if isinstance(log, list) else []


def _save_log(log):
    _put("ch_log", log)


def normalize_claim(text):
    text = text.strip().upper()
    digits = text[3:] if text.startswith("CH-") else text
    if digits.isdigit():
        return "CH-%04d" % int(digits)
    return text


def check_in(name, course, ptype, brand, hours_text, note, slot_choice="auto"):
    """Register a phone. Returns (True, record) or (False, error message)."""
    name, course, brand, note = name.strip(), course.strip(), brand.strip(), note.strip()
    if not name:
        return False, "Enter the student's name."
    if not brand:
        return False, "Enter the phone brand."
    try:
        hours = int(hours_text)
    except ValueError:
        return False, "Hours must be a whole number."
    if hours < 1 or hours > 12:
        return False, "Hours must be between 1 and 12."

    slots = load_slots()
    free = free_slot_numbers(slots)
    if not free:
        return False, "All %d slots are in use. Wait for a phone to be claimed." % SLOT_COUNT
    if slot_choice == "auto":
        slot_no = free[0]                      # lowest free slot number
    else:
        try:
            slot_no = int(slot_choice)
        except ValueError:
            return False, "Choose a slot."
        if slot_no not in free:
            return False, "Slot %s is not free." % slot_choice

    counter = _get("ch_counter", 0) + 1
    _put("ch_counter", counter)
    claim_no = "CH-%04d" % counter
    start = now()
    ends = start + timedelta(hours=hours)

    record = {
        "claim": claim_no, "name": name, "course": course, "ptype": ptype,
        "brand": brand, "slot": slot_no, "hours": hours, "fee": hours * RATE,
        "note": note, "in_at": iso(start), "ends": iso(ends),
        "claimed_at": None, "claimed_by": None,
    }
    log = load_log()
    log.append(record)
    _save_log(log)

    slots[str(slot_no)] = {"claim": claim_no, "ptype": ptype, "brand": brand,
                           "started": iso(start), "ends": iso(ends)}
    _put("ch_slots", slots)
    return True, record


def claim(claim_text, claimed_by):
    """Hand a phone back. Returns (True, record) or (False, error message)."""
    claim_no = normalize_claim(claim_text)
    claimed_by = claimed_by.strip()
    if not claim_no:
        return False, "Enter the claim number."
    if not claimed_by:
        return False, "Enter who is claiming the phone."
    log = load_log()
    for record in log:
        if record["claim"] == claim_no:
            if record["claimed_at"]:
                return False, "%s was already claimed by %s." % (claim_no, record["claimed_by"])
            record["claimed_at"] = iso(now())
            record["claimed_by"] = claimed_by
            slots = load_slots()
            key = str(record["slot"])
            if slots.get(key) and slots[key]["claim"] == claim_no:
                slots[key] = None              # the slot is free again
            _put("ch_slots", slots)
            _save_log(log)
            return True, record
    return False, "Claim number %s was not found." % claim_no


def search_log(date_text, query):
    """Log entries for one date ('' = all dates) that match the search text."""
    query = query.strip().lower()
    found = []
    for r in load_log():
        if date_text and r["in_at"][:10] != date_text:
            continue
        text = " ".join([r["claim"], r["name"], r["brand"], r["ptype"],
                         r["claimed_by"] or ""]).lower()
        if query in text:
            found.append(r)
    return list(reversed(found))               # newest first


def reset_all():
    for key in ("ch_slots", "ch_log", "ch_counter", "ch_schedule", "ch_sched_id",
                "ch_location", "ch_history", "ch_expenses"):
        window.localStorage.removeItem(key)


# --------------------------------------------------------------- location
def get_location():
    loc = _get("ch_location", None)
    if not isinstance(loc, dict):
        loc = {"location": "", "status": "closed", "note": "", "onduty": "", "updated": None}
    return loc


def set_location(location, status, note, onduty):
    loc = {"location": location, "status": status, "note": note.strip(),
           "onduty": onduty, "updated": iso(now())}
    _put("ch_location", loc)
    label = STATUS.get(status, STATUS["closed"])[0].title()
    history = _get("ch_history", [])
    history.append({"at": loc["updated"], "text": "%s at %s" % (label, location)
                    + (" - " + loc["note"] if loc["note"] else "")})
    _put("ch_history", history[-30:])


# --------------------------------------------------------------- schedule
def load_schedule():
    items = _get("ch_schedule", [])
    if not isinstance(items, list):
        items = []
    return sorted(items, key=lambda s: (DAYS.index(s["day"]) if s["day"] in DAYS else 9, s["time"]))


def add_schedule(day, time_text, location, onduty):
    time_text = time_text.strip()
    if not time_text:
        return False, "Enter the time, for example 8:00 AM - 12:00 PM."
    items = _get("ch_schedule", [])
    new_id = _get("ch_sched_id", 0) + 1
    _put("ch_sched_id", new_id)
    items.append({"id": new_id, "day": day, "time": time_text,
                  "location": location, "onduty": onduty})
    _put("ch_schedule", items)
    return True, "Added %s, %s at %s." % (day, time_text, location)


def delete_schedule(item_id):
    items = [s for s in _get("ch_schedule", []) if str(s["id"]) != str(item_id)]
    _put("ch_schedule", items)


def load_sample_schedule():
    _put("ch_schedule", [])
    for day, time_text, loc, who in [
        ("Monday", "8:00 AM - 12:00 PM", "IT Building hallway", "Apple Mae"),
        ("Monday", "1:00 PM - 5:00 PM", "Canteen", "Alliah"),
        ("Tuesday", "8:00 AM - 12:00 PM", "Covered court", "Jomar"),
        ("Wednesday", "8:00 AM - 5:00 PM", "IT Building hallway", "Jhunro Niño"),
        ("Thursday", "8:00 AM - 5:00 PM", "Canteen", "MaryShien"),
    ]:
        add_schedule(day, time_text, loc, who)


# --------------------------------------------------------------- earnings
def get_expenses():
    value = _get("ch_expenses", MONTHLY_EXPENSES)
    return value if isinstance(value, (int, float)) else MONTHLY_EXPENSES


def set_expenses(value):
    _put("ch_expenses", value)


def period_range(period):
    today = now().date()
    if period == "today":
        return today, today
    if period == "week":
        monday = today - timedelta(days=today.weekday())
        return monday, monday + timedelta(days=6)
    return today.replace(day=1), today


def earnings(period):
    start, end = period_range(period)
    rows = {}
    for r in load_log():
        day = date.fromisoformat(r["in_at"][:10])
        if start <= day <= end:
            row = rows.setdefault(day, [0, 0])
            row[0] += 1
            row[1] += r["fee"]
    sessions = sum(v[0] for v in rows.values())
    revenue = sum(v[1] for v in rows.values())
    share_of_month = {"today": 1 / SCHOOL_DAYS, "week": 0.25, "month": 1}[period]
    expenses = get_expenses() * share_of_month
    profit = revenue - expenses
    positive = max(profit, 0)
    return {
        "rows": sorted(rows.items()), "sessions": sessions, "revenue": revenue,
        "expenses": expenses, "profit": profit,
        "reserve": positive * RESERVE_RATE,
        "to_share": positive * (1 - RESERVE_RATE),
        "per_member": positive * (1 - RESERVE_RATE) / MEMBER_COUNT,
    }


# ------------------------------------------------------ shared page pieces
def render_status(element_id):
    loc = get_location()
    if not loc["updated"]:
        set_html(element_id, '<span class="p oc">NO UPDATE YET</span>'
                 '<div class="m">The team has not posted a location today.</div>')
        return
    label, css = STATUS.get(loc["status"], STATUS["closed"])
    updated = fmt_time(parse(loc["updated"]))
    set_html(element_id,
             '<span class="p %s">%s</span><div class="m">Currently at</div>'
             '<div class="t big">%s</div><div class="m">Updated %s &middot; On duty: %s</div>%s'
             % (css, label, esc(loc["location"]), updated, esc(loc["onduty"]),
                "<div>%s</div>" % esc(loc["note"]) if loc["note"] else ""))


def render_slots(grid_id, flt="all", count_id=None, bar_id=None):
    slots = load_slots()
    cards, free_count = [], 0
    for i in range(1, SLOT_COUNT + 1):
        slot = slots[str(i)]
        state = slot_state(slot)
        if state == "available":
            free_count += 1
        if flt != "all" and flt != state:
            continue
        if state == "available":
            pill, line1, line2 = '<span class="p av">AVAILABLE</span>', "Free to use", ""
        else:
            css, label = ("oc", "OCCUPIED") if state == "occupied" else ("rd", "READY FOR PICK-UP")
            pill = '<span class="p %s">%s</span>' % (css, label)
            line1 = "%s &middot; %s" % (esc(slot["ptype"].upper()), esc(slot["brand"]))
            ends = fmt_time(parse(slot["ends"]))
            line2 = ("Started %s &middot; ready ~%s" % (fmt_time(parse(slot["started"])), ends)
                     if state == "occupied" else "Finished %s" % ends)
        cards.append('<div class="sl"><div class="t">SLOT %d</div>%s<div>%s</div>'
                     '<div class="m">%s</div></div>' % (i, pill, line1, line2))
    set_html(grid_id, "".join(cards) or '<div class="c">No slots match this filter.</div>')
    if count_id:
        set_html(count_id, "%d of %d slots available" % (free_count, SLOT_COUNT))
    if bar_id:
        document.getElementById(bar_id).style.width = "%d%%" % round(100 * free_count / SLOT_COUNT)
    return free_count


def render_schedule(element_id, with_delete=False):
    today_name = now().strftime("%A")
    rows = []
    for s in load_schedule():
        is_today = s["day"] == today_name
        rows.append('<tr%s><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td>%s</tr>' % (
            ' class="today"' if is_today else "", esc(s["day"]), " (today)" if is_today else "",
            esc(s["time"]), esc(s["location"]), esc(s["onduty"]),
            '<td><button class="btn ol sm" data-id="%s">Delete</button></td>' % s["id"]
            if with_delete else ""))
    cols = 5 if with_delete else 4
    set_html(element_id, "".join(rows) or
             '<tr><td colspan="%d">No schedule posted yet.</td></tr>' % cols)


def render_history(element_id, limit=6):
    items = list(reversed(_get("ch_history", [])))[:limit]
    set_html(element_id, "<br>".join(
        "%s &middot; %s" % (fmt_time(parse(h["at"])), esc(h["text"])) for h in items)
        or "No updates yet.")
