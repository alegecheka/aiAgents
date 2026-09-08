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
