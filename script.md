# Windward Video Walkthrough Script (3m 38s)

*Target audience: Hiring team reviewing the full-stack take-home* 

*Presenter notes: Speak naturally, don't rush. Focus more on *why* than *what*.*


## SCENE 1: INTRODUCTION (00:00 - 00:19) | Duration: 19s

| Element | Details |
| :-- | :-- |
| **Timestamp** | 00:00 – 00:19 |
| **On-Screen** | Load the app at the Hero section (`#top`). Show the "Windward" brand, "The forecast, held to account." tagline and the "Open the pilot" button. |
| **Action to Perform** | Open `http://localhost:5173/` (or deployed URL). Hover over the nav bar briefly, then focus on the hero. |
| **Key Point** | Set the context of the project immediately. |

### Exact Spoken Script

*"Hi, I'm [Your Name]. This is Windward, a GB electricity forecast accountability dashboard. The goal here is simple: take publicly available wind forecasts from the Elexon BMRS API, compare them against what actually happened, and make it clear just how much of a difference the timing of those forecasts makes."*


## SCENE 2: THE PROBLEM (00:19 - 00:48) | Duration: 29s

| Element | Details |
| :-- | :-- |
| **Timestamp** | 00:19 – 00:48 |
| **On-Screen** | Stay on the Hero. Scroll down slightly to transition into the Overview. |
| **Action to Perform** | Click "Open the pilot" to smoothly scroll to the "Today at a glance" section. |
| **Key Point** | Establish the real-world energy problem. |

### Exact Spoken Script

*"In Great Britain's electricity market, wind forecasts matter a lot. Electricity buyers need to commit to positions ahead of time, and the forecast they rely on at their decision cutoff can be very different from a forecast published hours later. 

Windward is built to hold those forecasts accountable. Not by looking at the 'latest' forecast alone, but by looking at the exact forecast that *would have been available* at the time a decision was made."*


## SCENE 3: LIVE APPLICATION WALKTHROUGH (00:48 - 01:57) | Duration: 1m 09s

| Element | Details |
| :-- | :-- |
| **Timestamp** | 00:48 – 01:57 |
| **On-Screen** | Cycle through Overview -> Charts -> Vintages. Use the "View" toggle, cutoff slider and day selector as you speak. |
| **Action to Perform** | Methodically demonstrate each section with deliberate clicks. |
| **Key Point** | Show the core user value and the distinction between "Decision-time" and "Latest". |

### Exact Spoken Script

*"Let's start with the Overview. Here I can see the headline numbers for the selected delivery day at the chosen cutoff. Peak forecast, Mean Absolute Error, Bias and Accuracy are all calculated from the scored half-hour slots. Notice the bias sign too, since in this dashboard a positive bias means the forecast ran high."* 

*(Pause briefly and look at the KPI cards)*

*"Moving onto the Charts section. This is the main comparison view. I can see forecast against actual generation in half-hourly resolution, plotted for the delivery day. I can switch between 'Decision-time' and 'Latest'. 

'Decision-time' is the important one here. For this view, I'm only allowed to use forecasts that were published *on or before* the cutoff time on the decision day. If I slide the cutoff, I'm changing that exact vintage selection. If I switch to 'Latest', the cutoff is ignored and I see the newest vintages for each slot instead."* 

*(Toggle between Decision-time and Latest, then move the cutoff slider)*

*"Further down, we have 'Error by horizon' and 'Error by hour'. Error by horizon buckets forecast age in hours and looks at absolute error percentiles across the period. Error by hour groups by London local hour and shows mean signed error, taking into account that on the DST change day, the 01:00 hour can occur twice. That's something I had to be careful with."*

*(Scroll to the Vintages/Ledger section)*

*"Finally, the Vintages ledger. Here we see all eight cutoffs for that decision day, 00:00 right through to 21:00 in London local time. For each one, I can see MAE, bias, peak forecast and 'Vintages used'. Clicking 'Open' on any of these will jump me straight back to the charts with that exact cutoff applied. This makes it incredibly easy to see how much accuracy improves, or deteriorates, as more up-to-date forecasts become available."*


## SCENE 4: TECHNICAL IMPLEMENTATION (01:57 - 02:51) | Duration: 54s

| Element | Details |
| :-- | :-- |
| **Timestamp** | 01:57 – 02:51 |
| **On-Screen** | Briefly show `backend_v2/` file tree in VSCode, `app/sources/elexon.py`, `app/domain/vintage.py`, `app/domain/timeutil.py` and the running `uvicorn` logs. Do *not* dump the entire codebase. |
| **Action to Perform** | Switch to IDE for ~10-15 seconds showing structure, then back to the browser showing live network calls to `localhost:8001/api/v1/...` if desired. |
| **Key Point** | Prove this is a real implementation against the Elexon API with correct domain logic. |

### Exact Spoken Script

*"Under the hood, I built `backend_v2` from scratch with FastAPI. The backend has no runtime dependency on SQLite. On startup, it pulls data directly from the Elexon BMRS API using `httpx` with retries via `tenacity`, validates responses and caches them to disk under `.cache/elexon`. 

There are two datasets I'm working with. `WINDFOR` gives hourly wind forecasts with multiple publish times per start time. `FUELHH` filtered to fuelType WIND gives half-hourly actual generation, returned newest first with `publishTime = startTime + 30 minutes`. Getting the windows right for those was critical, and I had to pad the windows to avoid missing the very first half-hour slot."*

*(Show `app/sources/elexon.py` briefly)*

*"All of the time-critical logic lives in the domain layer. `timeutil` handles everything in Europe/London using `zoneinfo`. `vintage.py` is the single source of truth for slot generation, cutoff conversion, vintage selection with bisect-style logic, hourly to half-hour interpolation, and scoring. `metrics.py` handles MAE and bias with the exact definitions the frontend expects. 

The frontend is React with Vite and TanStack Query. It reads its bounds, default day and period straight from `/api/v1/meta`, so there are no hardcoded January values left. Everything is driven by the live data."*


## SCENE 5: KEY ENGINEERING DECISIONS & CHALLENGES (02:51 - 03:19) | Duration: 28s

| Element | Details |
| :-- | :-- |
| **Timestamp** | 02:51 – 03:19 |
| **On-Screen** | Go back to the Charts view on the DST-adjacent period. Optionally show the day selector landing on a later day, or look at the ledger for context. |
| **Action to Perform** | Show the app handling the period correctly, especially around the end of October. |
| **Key Point** | Focus on the hardest, verified problems solved. |

### Exact Spoken Script

*"The trickiest part by far was time. Great Britain's electricity market crosses between BST and GMT and the London delivery day doesn't align with UTC midnight. I had to generate slots from London day bounds, produce 48 half-hours normally and exactly 50 on 2026-10-25. FUELHH's `publishTime = startTime + 30 min` combined with newest-first ordering meant I couldn't just filter by publish time for actuals at all. 

Also, for WINDFOR, the same start time can appear under many publish times, so vintage selection has to pick the latest publish time <= cutoff. For half-hours derived by interpolation between hourly values, I take the later of the two publish times to be conservative and correct.

Getting those details right was the difference between correct alignment and shifted slots. Once the slot keys matched exactly between forecasts and actuals, the rest fell into place."*


## SCENE 6: CONCLUSION (03:19 - 03:38) | Duration: 19s

| Element | Details |
| :-- | :-- |
| **Timestamp** | 03:19 – 03:38 |
| **On-Screen** | Return to the full dashboard view, showing Overview + a glimpse of the Charts. End on the nav bar. |
| **Action to Perform** | Scroll to a clean overview, pause for a second, then stop screen recording. |
| **Key Point** | Concise wrap-up with impact. |

### Exact Spoken Script

*"Windward turns raw Elexon data into something actually useful for forecast accountability. It shows not just how accurate forecasts were, but *which* forecasts were used, at *what* time, against *what* actually occurred. 

The implementation keeps the frontend contract intact, sources data live from Elexon with caching, and treats time, vintages and interpolation as first-class concerns. 

Thanks for taking the time to look through it."*


## PRODUCTION NOTES FOR RECORDING

- **Pace:** Speak slightly slower than your natural conversational pace. The time boundaries are tight enough that rushing will hurt clarity.
- **Cursor discipline:** Move deliberately between sections. Don't flick between tabs.
- **Code glimpse:** Only show `elexon.py`, `vintage.py` and `timeutil.py` for a few seconds. Resist the urge to scroll through entire files.
- **Focus on the "why":** The strongest moments are explaining *Decision-time vs Latest* and *London time/DST*. Lean into those.
- **Be honest:** Stick exactly to what's implemented. Avoid saying "Redis", "Postgres", or "real-time websockets" as none of those exist here.
- **Transitions:** Use smooth scrolls between sections rather than jumping instantly. They read better on camera.
