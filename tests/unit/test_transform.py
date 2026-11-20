import pytest

from worldbank_etl.transform import transform_records


def test_transform_world_bank_record():
    records = [
        {
            "country": {"id": "IN", "value": "India"},
            "indicator": {
                "id": "SP.POP.TOTL",
                "value": "Population, total",
            },
            "countryiso3code": "IND",
            "date": "2024",
            "value": 1450935791,
        }
    ]

    result = transform_records(records)

    assert len(result) == 1
    assert result[0]["country_code"] == "IND"
    assert result[0]["country_name"] == "India"
    assert result[0]["indicator_code"] == "SP.POP.TOTL"
    assert result[0]["year"] == 2024
    assert result[0]["value"] == 1450935791.0


def test_transform_preserves_null_value():
    records = [
        {
            "country": {"id": "IN", "value": "India"},
            "indicator": {
                "id": "SP.POP.TOTL",
                "value": "Population, total",
            },
            "countryiso3code": "IND",
            "date": "2024",
            "value": None,
        }
    ]

    result = transform_records(records)

    assert result[0]["value"] is None


def test_transform_empty_records():
    assert transform_records([]) == []


def test_transform_missing_year():
    records = [
        {
            "country": {"id": "IN", "value": "India"},
            "indicator": {
                "id": "SP.POP.TOTL",
                "value": "Population, total",
            },
            "countryiso3code": "IND",
            "date": None,
            "value": 100,
        }
    ]

    with pytest.raises(ValueError, match="missing year"):
        transform_records(records)