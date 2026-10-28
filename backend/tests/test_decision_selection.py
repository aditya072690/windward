from app.services.decision import get_decision_forecast


def test_decision_selection_basic():
    res = get_decision_forecast("2026-01-15", "09:00", "decision")
    assert res["delivery_date"] == "2026-01-16"
    assert len(res["points"]) == 48
    assert res["view"] == "decision"


def test_latest_view():
    res = get_decision_forecast("2026-01-15", "09:00", "latest")
    assert res["view"] == "latest"
    assert res["cutoff_utc"] is None
