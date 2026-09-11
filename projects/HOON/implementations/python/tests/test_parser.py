import pytest
from hoon import parse, ParseError

def test_basic_parse():
    ast = parse("{{{ name: \"test\"; val: 42 }}}")
    assert isinstance(ast, dict)
    assert ast["name"] == "test"
    assert ast["val"] == 42

def test_hex_numbers():
    ast = parse("{{{ num: 0x2A; neg: -0xFF }}}")
    assert ast["num"] == 42
    assert ast["neg"] == -255

def test_rejects_duplicate_keys():
    with pytest.raises(ParseError, match="duplicate key"):
        parse("{{{ a: 1; a: 2 }}}")

def test_hoon_to_json():
    from hoon.serializer import hoon_to_json
    import json
    hoon = '{{{ name: "test"; val: 42; flag: true }}}'
    j = hoon_to_json(hoon)
    obj = json.loads(j)
    assert obj == {"name": "test", "val": 42, "flag": True}

def test_json_to_hoon():
    from hoon.serializer import json_to_hoon, hoon_to_json
    import json
    j = '{"a": 1, "b": [2, 3], "c": {"x": "y"}}'
    hoon = json_to_hoon(j)
    obj = json.loads(hoon_to_json(hoon))
    assert obj == json.loads(j)

def test_roundtrip_torture():
    from hoon.serializer import hoon_to_json, json_to_hoon
    import json, pathlib
    p = pathlib.Path("../../spec-tests/valid/integration/torture.hoon")
    if not p.exists():
        p = pathlib.Path("projects/HOON/spec-tests/valid/integration/torture.hoon")
    hoon = p.read_text()
    j = hoon_to_json(hoon)
    hoon2 = json_to_hoon(j)
    j2 = hoon_to_json(hoon2)
    assert json.loads(j) == json.loads(j2)

def test_json_text_block():
    from hoon.serializer import hoon_to_json, json_to_hoon
    hoon = '{{{ note: """\nhello\nworld\n""" }}}'
    j = hoon_to_json(hoon)
    assert "hello\\nworld" in j
    hoon2 = json_to_hoon(j)
    assert "hello" in hoon2
    assert hoon_to_json(hoon2) == j

def test_hex_becomes_decimal():
    from hoon.serializer import hoon_to_json
    import json
    j = hoon_to_json("{{{ n: 0x2A }}}")
    assert json.loads(j)["n"] == 42
