"""
Test cases for comment parser (CA0:symbol #note format)
Run with: pytest test_comment_parser.py -v
"""
import pytest


def parse_comment_mapping(comment: str):
    """Copy of the parser from inventor_api.py for testing"""
    result = {"mapping": None, "note": None}

    if not comment or not comment.strip():
        return result

    comment = comment.strip()

    # Split on first # to separate namespace:symbol from note
    if '#' in comment:
        mapping_part, note_part = comment.split('#', 1)  # maxsplit=1 preserves # in notes
        result["note"] = note_part.strip() if note_part.strip() else None
    else:
        mapping_part = comment
        result["note"] = None

    # Parse namespace:symbol
    mapping_part = mapping_part.strip()
    if ':' not in mapping_part:
        return {"mapping": None, "note": None}  # Invalid: no namespace

    namespace, symbol = mapping_part.split(':', 1)
    namespace = namespace.strip()
    symbol = symbol.strip()

    # Validate namespace (must be CA followed by digit(s))
    if not namespace.startswith('CA') or len(namespace) < 3:
        return {"mapping": None, "note": None}

    # Validate namespace has digit after CA
    try:
        int(namespace[2:])  # Check CA0, CA1, etc.
    except ValueError:
        return {"mapping": None, "note": None}

    # Validate symbol (non-empty, no colons - MathJS compatibility)
    if not symbol or ':' in symbol:
        return {"mapping": None, "note": None}

    result["mapping"] = symbol

    return result


def build_comment_string(symbol, note=None, namespace="CA0"):
    """Copy of the builder from inventor_api.py for testing"""
    if not symbol:
        return ""

    # Build namespace:symbol part
    comment = f"{namespace}:{symbol}"

    # Append note if provided (preserve as-is, including any # or backticks)
    if note and note.strip():
        comment = f"{comment} #{note.strip()}"

    return comment


# ============================================================================
# PARSER TESTS
# ============================================================================

class TestParseCommentMapping:
    """Tests for parse_comment_mapping function"""

    # Valid cases
    def test_simple_mapping(self):
        assert parse_comment_mapping("CA0:L") == {"mapping": "L", "note": None}

    def test_mapping_with_note(self):
        assert parse_comment_mapping("CA0:L #Length parameter") == {"mapping": "L", "note": "Length parameter"}

    def test_mapping_with_hash_in_note(self):
        result = parse_comment_mapping("CA0:L #`Length #1` #`Design #3`")
        assert result == {"mapping": "L", "note": "`Length #1` #`Design #3`"}

    def test_greek_symbol(self):
        assert parse_comment_mapping("CA0:rho #Density") == {"mapping": "rho", "note": "Density"}

    def test_unicode_greek_symbol(self):
        assert parse_comment_mapping("CA0:η #Efficiency") == {"mapping": "η", "note": "Efficiency"}

    def test_different_namespace(self):
        result = parse_comment_mapping("CA1:T_in #Inlet temperature")
        assert result == {"mapping": "T_in", "note": "Inlet temperature"}

    def test_extra_spaces(self):
        assert parse_comment_mapping("CA0:L  #  Spaces  ") == {"mapping": "L", "note": "Spaces"}

    def test_leading_trailing_spaces(self):
        assert parse_comment_mapping(" CA0:L #Note ") == {"mapping": "L", "note": "Note"}

    # Invalid cases
    def test_empty_string(self):
        assert parse_comment_mapping("") == {"mapping": None, "note": None}

    def test_missing_namespace(self):
        assert parse_comment_mapping("L #Note") == {"mapping": None, "note": None}

    def test_invalid_namespace_prefix(self):
        assert parse_comment_mapping("XY:L #Note") == {"mapping": None, "note": None}

    def test_namespace_no_digit(self):
        assert parse_comment_mapping("CA:L #Note") == {"mapping": None, "note": None}

    def test_namespace_non_digit(self):
        assert parse_comment_mapping("CAX:L #Note") == {"mapping": None, "note": None}

    def test_colon_in_symbol(self):
        assert parse_comment_mapping("CA0:ratio:1 #Note") == {"mapping": None, "note": None}

    def test_empty_symbol(self):
        assert parse_comment_mapping("CA0:") == {"mapping": None, "note": None}

    def test_empty_symbol_with_note(self):
        assert parse_comment_mapping("CA0: #Note") == {"mapping": None, "note": None}

    def test_none_input(self):
        assert parse_comment_mapping(None) == {"mapping": None, "note": None}

    def test_whitespace_only(self):
        assert parse_comment_mapping("   ") == {"mapping": None, "note": None}


# ============================================================================
# BUILDER TESTS
# ============================================================================

class TestBuildCommentString:
    """Tests for build_comment_string function"""

    def test_symbol_only(self):
        assert build_comment_string("L", None) == "CA0:L"

    def test_symbol_with_note(self):
        assert build_comment_string("L", "Length parameter") == "CA0:L #Length parameter"

    def test_note_with_hash(self):
        result = build_comment_string("L", "`Length #1` #`Design #3`")
        assert result == "CA0:L #`Length #1` #`Design #3`"

    def test_greek_symbol(self):
        assert build_comment_string("rho", "Density") == "CA0:rho #Density"

    def test_unicode_greek_symbol(self):
        assert build_comment_string("η", "Efficiency") == "CA0:η #Efficiency"

    def test_none_symbol(self):
        assert build_comment_string(None, "Note") == ""

    def test_empty_symbol(self):
        assert build_comment_string("", "Note") == ""

    def test_custom_namespace(self):
        assert build_comment_string("L", "Note", "CA1") == "CA1:L #Note"


# ============================================================================
# ROUND-TRIP TESTS
# ============================================================================

class TestRoundTrip:
    """Tests that build -> parse -> original values match"""

    @pytest.mark.parametrize("symbol,note", [
        ("L", None),
        ("L", "Length parameter"),
        ("L", "`Length #1` #`Design #3`"),
        ("rho", "Density of water"),
        ("η", "Pump efficiency"),
        ("T_in", "Inlet temperature"),
    ])
    def test_round_trip(self, symbol, note):
        # Build comment string
        comment = build_comment_string(symbol, note)

        # Parse it back
        parsed = parse_comment_mapping(comment)

        # Check if we got back the same symbol and note
        assert parsed["mapping"] == symbol
        assert parsed["note"] == note
