# Windward Demo Video Script (Two Parts, ≤10 min total)

## Part 1: Client Pitch (≤5 min)
Target audience: UK energy utility day-ahead desk
Goal: Show "what was available at decision time" and "how accurate was it"

### Outline
1. **Opening (0:00 - 0:30)** - Problem: buy power day-ahead, wind uncertain
2. **Decision moment (0:30 - 1:30)** - Pick decision date (15 Jan), cutoff 09:00; show forecast vintage used
3. **Accuracy (1:30 - 2:30)** - KPIs, bias direction (over-forecast costly), coverage
4. **Hindsight (2:30 - 3:30)** - Toggle actuals, see error shading
5. **Horizon/value of waiting (3:30 - 4:15)** - Error by horizon, when waiting helps
6. **Close (4:15 - 5:00)** - Buffer sizing with P90, methodology/trust

### Key points to demo
- Cutoff control changes vintage
- "Latest" vs "Decision-time" view
- Vintage ledger
- Risk-adjusted concept

## Part 2: Tech-Lead Review (≤5 min)
Target audience: Engineering/reviewer
Goal: Architecture, correctness, tests, fidelity

### Outline
1. **Architecture (0:00 - 1:15)** - React+FastAPI, SQLite snapshot read-only, no runtime Elexon calls
2. **Correctness (1:15 - 2:15)** - Decision-time selection (max publish_time ≤ cutoff), inclusive boundary, tests
3. **Data/modeling (2:15 - 3:15)** - Walk-forward risk band (no look-ahead), missing data explicit
4. **Design fidelity (3:15 - 4:00)** - Pixel-faithful to design export, parity tests across viewports/themes
5. **Deploy/run/tests (4:00 - 5:00)** - Docker compose, CI, coverage, security

### Notes
- Use real numbers from the snapshot
- Show test results briefly
- Mention deliberate deltas in DESIGN_PARITY.md
