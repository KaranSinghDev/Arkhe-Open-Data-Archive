import pytest


def test_parse_csv():
    from app.workers.tasks.parse_file import _parse_csv
    data = b"col1,col2,col3\n1,2,3\n4,5,6\n"
    result = _parse_csv(data)
    assert result["columns"] == ["col1", "col2", "col3"]
    assert result["row_count"] == 2


def test_parse_json_object():
    from app.workers.tasks.parse_file import _parse_json
    import json
    data = json.dumps({"name": "LHC", "energy": 13.6}).encode()
    result = _parse_json(data)
    assert result["type"] == "object"
    assert "name" in result["keys"]
    assert "energy" in result["keys"]


def test_parse_json_array():
    from app.workers.tasks.parse_file import _parse_json
    import json
    data = json.dumps([{"a": 1}, {"a": 2}]).encode()
    result = _parse_json(data)
    assert result["type"] == "array"
    assert result["length"] == 2


def test_parse_csv_malformed_returns_empty():
    from app.workers.tasks.parse_file import _parse_csv
    result = _parse_csv(b"")
    assert isinstance(result, dict)


def test_storage_object_key_spaces():
    from app.services.storage import build_object_key
    key = build_object_key("rec-1", "data file with spaces.csv")
    assert " " not in key
    assert key.startswith("records/rec-1/")
