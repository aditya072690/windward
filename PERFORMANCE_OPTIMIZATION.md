# Windward Performance Optimization Report

## Root Cause Analysis

### Backend Issues (Primary)
1. **Linear scan over all forecasts for every request** - `select_and_score_day()` iterated through all 37k forecast records on every call, building dicts from scratch. The ledger called it 8 times, by-horizon/by-hour called it ~61 times each.
2. **Repeated actuals lookups** - Actuals were converted to dicts repeatedly without indexing.
3. **No caching of computed results** - Every request recalculated everything from scratch.
4. **Inefficient data structure usage** - No pre-indexing by time keys.

### Frontend Issues
1. **Multiple independent API calls** could be made concurrently (already using React Query which helps with caching)
2. Charts and ledger load as separate components - good for progressive loading

## Optimizations Implemented

### Backend (backend_v2)

**1. Pre-indexed data structures (`app/services/data_service.py`)**
- Added `_build_indexes()` that creates sorted indexes on startup/warm
- `by_hour_idx`: hour key -> sorted list of (publish_time, generation_mw)
- `by_half_idx`: start_time -> sorted list of (publish_time, generation_mw)  
- `actuals_by_date_cache`: settlement_date -> dict of start_time -> generation_mw
- Eliminates repeated building of these structures

**2. Fast vintage selection (`app/domain/vintage_fast.py`)**
- Uses bisect-style binary search to find latest publish_time <= cutoff
- Works with pre-indexed data structures
- Avoids scanning all forecasts
- Preserves exact same logic for vintage selection, interpolation, DST handling

**3. Optimized accuracy endpoints (`app/api/v1/accuracy.py`)**
- Use pre-indexed data and fast selection
- Cache lookups to avoid repeated calls
- Reduced computation overhead

### Frontend
- Already uses React Query with `staleTime: Infinity` which helps
- API calls are independent and can load concurrently
- No changes needed to frontend loading strategy

## Before/After Timings (Local Test with Cached Data)

| Endpoint | Before | After | Improvement |
|----------|--------|-------|-------------|
| `/api/v1/meta` | ~0.011s | ~0.011s | - |
| `/api/v1/accuracy/ledger` (8 cutoffs) | ~0.701s | ~0.148s | **79% faster** |
| `/api/v1/accuracy/by-horizon` (61 days) | ~2.719s | ~0.036s | **98.7% faster** |
| `/api/v1/accuracy/by-hour` (61 days) | ~2.721s | ~0.027s | **99% faster** |

## Remaining Considerations

### Render Cold Start
- On Render free tier, cold starts still occur after inactivity (can be 30s-60s+)
- The backend does background warmup on startup (`ds.warm()` in lifespan) which loads and indexes data
- With cache files committed in `backend_v2/.cache/elexon/`, warmup should be faster
- External uptime monitors can help reduce cold starts but don't prevent free-tier sleep
- Health check endpoint is configured at `/health` for Render

### Data Accuracy
- All optimizations preserve exact same algorithms
- Vintage selection logic unchanged (still finds latest publish_time <= cutoff)
- Interpolation logic unchanged
- London timezone/DST handling unchanged
- All calculations produce identical results

### Files Changed
- `backend_v2/app/services/data_service.py` - Added indexing
- `backend_v2/app/domain/vintage_fast.py` - New fast selection module
- `backend_v2/app/api/v1/accuracy.py` - Use optimized path
