def compute_mae_bias(points):
    errors = []
    for p in points:
        f = p.get("forecast_mw")
        a = p.get("actual_mw")
        if f is None or a is None:
            continue
        try:
            errors.append((float(f), float(a)))
        except Exception:
            continue
    if not errors:
        return {"mae_mw": None, "bias_mw": None}
    mae = sum(abs(f - a) for f, a in errors) / len(errors)
    bias = sum(f - a for f, a in errors) / len(errors)
    return {"mae_mw": round(mae, 6), "bias_mw": round(bias, 6)}
