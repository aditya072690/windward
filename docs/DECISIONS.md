# Decisions

## Series control
The design export's segmented control has three options (Demand / Wind / Solar). For wind-only data, we replace with "Decision-time" and "Latest" views while preserving component structure, styling, and behavior.

## Horizon/Error by hour sampling
Error by horizon and error by hour are computed over the full January window at the selected cutoff time-of-day (not just the selected day) to have sufficient samples for percentiles.

## UI scope
Endpoints for histogram, heatmap, evolution, CSV export exist in backend API for completeness, but UI for these is not added per design export (no such elements in index.html).
