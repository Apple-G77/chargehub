"""Operator PIN page. Unlocks the operator pages for this browser tab only."""
from pyscript import document, window, when

# CHANGE THIS PIN before you submit. Anyone who reads this file can see it,
# so it is a "staff only" sign, not a real lock (see README.md).
PIN = "1234"


def show(text):
    document.getElementById("pin-msg").innerText = text


def try_unlock():
    if document.getElementById("pin").value == PIN:
        window.sessionStorage.setItem("operator", "yes")   # remembered until the tab closes
        window.location.href = "checkin.html"
    else:
        show("Wrong PIN. Try again.")
        document.getElementById("pin").value = ""


@when("click", "#unlock")
def on_click(event):
    try_unlock()


@when("keydown", "#pin")                   # event: pressing Enter also unlocks
def on_key(event):
    if event.key == "Enter":
        try_unlock()


if window.sessionStorage.getItem("operator") == "yes":
    window.location.href = "checkin.html"
