from src.graph import route_after_classification


def test_compare_route() -> None:
    assert route_after_classification({"route": "compare"}) == "compare_technologies"


def test_calculation_route() -> None:
    assert route_after_classification({"route": "calculate"}) == "calculate_storage"
