import json

from src.tools import calculate_storage_capacity


def test_storage_calculation() -> None:
    raw = calculate_storage_capacity.invoke(
        {
            "data_size_gb": 500,
            "compression_ratio": 0.6,
            "replication_factor": 3,
            "number_of_copies": 2,
        }
    )
    result = json.loads(raw)

    assert result["after_compression_gb"] == 300
    assert result["after_replication_gb"] == 900
    assert result["required_physical_storage_gb"] == 1800
