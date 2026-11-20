from worldbank_etl.validate import validate_records


def valid_record():
    return {
        "country_code": "IND",
        "country_name": "India",
        "indicator_code": "SP.POP.TOTL",
        "indicator_name": "Population, total",
        "year": 2024,
        "value": 1450935791.0,
    }


def test_valid_records():
    is_valid, errors = validate_records([valid_record()])

    assert is_valid is True
    assert errors == []


def test_missing_required_field():
    record = valid_record()
    record["country_code"] = None

    is_valid, errors = validate_records([record])

    assert is_valid is False
    assert any("country_code" in error for error in errors)


def test_invalid_year():
    record = valid_record()
    record["year"] = 1800

    is_valid, errors = validate_records([record])

    assert is_valid is False
    assert any("invalid year" in error for error in errors)


def test_negative_value():
    record = valid_record()
    record["value"] = -100

    is_valid, errors = validate_records([record])

    assert is_valid is False
    assert any("negative value" in error for error in errors)


def test_duplicate_records():
    record = valid_record()

    is_valid, errors = validate_records([record, record.copy()])

    assert is_valid is False
    assert any("duplicate" in error for error in errors)


def test_null_indicator_value_is_allowed():
    record = valid_record()
    record["value"] = None

    is_valid, errors = validate_records([record])

    assert is_valid is True
    assert errors == []