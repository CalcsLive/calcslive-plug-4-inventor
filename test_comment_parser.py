"""
Test cases for new comment parser (CA0:symbol #note format)
"""
import sys
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_comment_mapping(comment: str):
    """Copy of the new parser for testing"""
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
    """Copy of the new builder for testing"""
    if not symbol:
        return ""

    # Build namespace:symbol part
    comment = f"{namespace}:{symbol}"

    # Append note if provided (preserve as-is, including any # or backticks)
    if note and note.strip():
        comment = f"{comment} #{note.strip()}"

    return comment


# Test Cases
test_cases = [
    # Valid cases
    ("CA0:L", {"mapping": "L", "note": None}),
    ("CA0:L #Length parameter", {"mapping": "L", "note": "Length parameter"}),
    ("CA0:L #`Length #1` #`Design #3`", {"mapping": "L", "note": "`Length #1` #`Design #3`"}),
    ("CA0:rho #Density", {"mapping": "rho", "note": "Density"}),
    ("CA0:η #Efficiency", {"mapping": "η", "note": "Efficiency"}),
    ("CA1:T_in #Inlet temperature", {"mapping": "T_in", "note": "Inlet temperature"}),
    ("CA0:L  #  Spaces  ", {"mapping": "L", "note": "Spaces"}),
    (" CA0:L #Note ", {"mapping": "L", "note": "Note"}),

    # Invalid cases
    ("", {"mapping": None, "note": None}),
    ("L #Note", {"mapping": None, "note": None}),  # Missing namespace
    ("XY:L #Note", {"mapping": None, "note": None}),  # Invalid namespace
    ("CA:L #Note", {"mapping": None, "note": None}),  # No digit after CA
    ("CAX:L #Note", {"mapping": None, "note": None}),  # Non-digit after CA
    ("CA0:ratio:1 #Note", {"mapping": None, "note": None}),  # Colon in symbol
    ("CA0:", {"mapping": None, "note": None}),  # Empty symbol
    ("CA0: #Note", {"mapping": None, "note": None}),  # Empty symbol with note
]

print("=" * 80)
print("PARSER TEST CASES")
print("=" * 80)

for i, (input_str, expected) in enumerate(test_cases, 1):
    result = parse_comment_mapping(input_str)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    print(f"\n{status} Test {i}: {repr(input_str)}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    if result != expected:
        print(f"  MISMATCH!")

# Builder tests
print("\n" + "=" * 80)
print("BUILDER TEST CASES")
print("=" * 80)

builder_tests = [
    (("L", None), "CA0:L"),
    (("L", "Length parameter"), "CA0:L #Length parameter"),
    (("L", "`Length #1` #`Design #3`"), "CA0:L #`Length #1` #`Design #3`"),
    (("rho", "Density"), "CA0:rho #Density"),
    (("η", "Efficiency"), "CA0:η #Efficiency"),
    ((None, "Note"), ""),  # No symbol
    (("", "Note"), ""),  # Empty symbol
]

for i, (args, expected) in enumerate(builder_tests, 1):
    result = build_comment_string(*args)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    print(f"\n{status} Test {i}: build_comment_string{args}")
    print(f"  Expected: {repr(expected)}")
    print(f"  Got:      {repr(result)}")
    if result != expected:
        print(f"  MISMATCH!")

# Round-trip tests
print("\n" + "=" * 80)
print("ROUND-TRIP TEST CASES")
print("=" * 80)

round_trip_tests = [
    ("L", None),
    ("L", "Length parameter"),
    ("L", "`Length #1` #`Design #3`"),
    ("rho", "Density of water"),
    ("η", "Pump efficiency"),
    ("T_in", "Inlet temperature"),
]

for i, (symbol, note) in enumerate(round_trip_tests, 1):
    # Build comment string
    comment = build_comment_string(symbol, note)

    # Parse it back
    parsed = parse_comment_mapping(comment)

    # Check if we got back the same symbol and note
    success = parsed["mapping"] == symbol and parsed["note"] == note
    status = "✅ PASS" if success else "❌ FAIL"

    print(f"\n{status} Round-trip {i}: symbol={repr(symbol)}, note={repr(note)}")
    print(f"  Built:  {repr(comment)}")
    print(f"  Parsed: {parsed}")
    if not success:
        print(f"  MISMATCH!")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
