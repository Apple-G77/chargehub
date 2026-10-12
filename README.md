# ChargeHub

A portable phone charging service for Cebu Eastern College students.
Final project for Event-Driven Programming (PyScript), BSIT 3-7, instructor Mr. Vincent Cababan.

**Members:** Garabiles, Apple Mae D. · Lazarte, Alliah E. · Oacan, Jomar I. · Rollon, Jhunro Niño F. · Villaluz, MaryShien R.

Live site (after enabling GitHub Pages): `https://apple-g77.github.io/chargehub/`
Video presentation: [add link here]

## What the website does

**Customers (public, no login)**
| Page | File | What happens |
|---|---|---|
| Landing | `index.html` | Logo and the 30-second ad video. The Enter button pulses when the video ends. |
| Home | `home.html` | Live status card, slot board and today's schedule. |
| About | `about.html` | Mission, problem, USP, how it works, the team. |
| Services | `services.html` | Price calculator (button click). |
| Live Slots | `live-slots.html` | SLOT 1 to 8 with status and phone type. Filter buttons. Refreshes every 30 s. |
| Find Us | `find-us.html` | Where the team is now, schedule, recent updates. |

**Operators (PIN protected, not linked from the public menu)**
Open `operator/pin.html`, enter the PIN (default `1234`, change it in `py/pin.py`).
| Page | File | What happens |
|---|---|---|
| Check-In & Claim | `operator/checkin.html` | Assigns the lowest free slot and a claim number (CH-0001...). Claiming frees the slot. |
| Logbook | `operator/logbook.html` | Search by date, claim number, name or brand. Shows who claimed and when. |
| Schedule | `operator/schedule.html` | Add or delete schedule entries and update the current location. |
| Earnings | `operator/earnings.html` | Total collected, expenses, profit for today, this week or this month, plus the 70/30 profit share. |

## Event-driven programming in this project
Every interaction is an event handled by a Python function using `@when(event, selector)`:
click (buttons, filters, tabs), input (search box, expenses), change (date picker), keydown (Enter on the PIN field), and media events (`ended`, `error`) on the video. The Python code updates the page without reloading it.

## How the code is organised
- `py/storage.py` is shared by all pages: saved data, slot assignment, claim numbers, earnings, and the functions that draw slots, schedule and status.
- One Python file per page in `py/` (for example `py/services.py` runs `services.html`).
- `css/style.css` is the one shared look.
- Slot assignment: `check_in()` in `py/storage.py` picks the lowest free slot number, saves the claim number, and marks that slot occupied. `claim()` frees it again.

## Run it on your computer
Do not double-click the HTML files. In the project folder run:
```
python -m http.server
```
then open `http://localhost:8000`. (Or use the VS Code Live Server extension.)

## Publish
Repo **Settings → Pages → Deploy from a branch → main → / (root) → Save**.

## Important limits (say these in the video)
1. **Data is saved in the browser (localStorage).** A check-in on the operator's laptop shows on that laptop's Live Slots page, not on a student's phone. Only `_get` and `_put` in `py/storage.py` need to change to use a shared database later.
2. **The PIN is a "staff only" sign, not real security.** The repo is public, so anyone can read the PIN. Operator pages are only hidden from the menu. A real system would use proper login.
3. The `Reset all data` button in the Logbook clears everything saved in the browser.

## The video
Put your 30-second ad at `assets/chargehub-ad.mp4`. GitHub's web upload limit is 25 MB per file (100 MB with git). If it is bigger, compress it.

## Who does what (suggested)
Each member commits their own files with clear messages, so the history shows everyone's work.
| Member | Files | Ideas for meaningful commits |
|---|---|---|
| Garabiles | `index.html`, `home.html`, `about.html`, `py/landing.py`, `py/home.py` | Add the team roles, polish the landing page, add the real logo |
| Lazarte | `services.html`, `live-slots.html`, `py/services.py`, `py/live_slots.py` | Add a premium price option, add a "slots available" line to Services |
| Oacan | `operator/checkin.html`, `operator/logbook.html`, `py/checkin.py`, `py/logbook.py` | Add a condition photo note, add export of the logbook |
| Rollon | `operator/earnings.html`, `py/earnings.py` | Add a per-month chart, add a break-even line |
| Villaluz | `find-us.html`, `operator/pin.html`, `operator/schedule.html`, `py/find_us.py`, `py/pin.py`, `py/schedule.py`, `README.md` | Add an FAQ section, improve the PIN page, keep the README current |

## Quick test checklist
1. Open `operator/pin.html`, enter the PIN.
2. Schedule: click *Load sample schedule*, then update the location to Open.
3. Check-In: check in a phone. Note the claim number and slot.
4. Open `live-slots.html` in another tab: the slot shows OCCUPIED.
5. Claim the phone. The slot becomes AVAILABLE and the Logbook shows who claimed it.
6. Earnings: the total for today matches the logbook.
