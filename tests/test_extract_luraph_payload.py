import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "extract_luraph_payload.py"
SPEC = importlib.util.spec_from_file_location("extract_luraph_payload", SCRIPT)
extractor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(extractor)


class ExtractorTests(unittest.TestCase):
    def test_redirects_numeric_fields_but_not_literals_or_comments(self):
        source = (
            'local x={[124]=loadstring, [12] = loadstring, '
            's="[4]=loadstring", b=[=[ [5]=loadstring ]=] -- [6]=loadstring\n}'
        )
        patched, count = extractor.replace_loadstring_fields(source)
        self.assertEqual(count, 2)
        self.assertIn("[124]=__LPH_CAPTURE_LOADSTRING", patched)
        self.assertIn("[12] = __LPH_CAPTURE_LOADSTRING", patched)
        self.assertIn('s="[4]=loadstring"', patched)
        self.assertIn("b=[=[ [5]=loadstring ]=]", patched)
        self.assertIn("-- [6]=loadstring", patched)

    def test_long_string_delimiter_is_not_present_in_source(self):
        value = "a ]] b ]=] c ]==] d"
        literal = extractor.lua_long_string(value)
        self.assertTrue(literal.startswith("[===[") or literal.startswith("[====["))
        self.assertTrue(literal.endswith("]===]") or literal.endswith("]====]"))
        self.assertIn(value, literal)

    def test_build_runner_redirects_all_fields(self):
        runner, count = extractor.build_runner("return setmetatable({[124]=loadstring}, {}):i()(...)")
        self.assertEqual(count, 1)
        self.assertIn("__LPH_CAPTURE_LOADSTRING", runner)
        self.assertIn("loadstring(protectedSource", runner)
        self.assertIn("return source", runner)

    def test_parse_hex_capture_and_validate_length(self):
        output = (
            "noise\n__LPH_BEGIN__1__3\n"
            "__LPH_DATA__61\n__LPH_DATA__6263\n__LPH_END__1\n"
        )
        self.assertEqual(extractor.parse_captures(output), [b"abc"])
        with self.assertRaises(ValueError):
            extractor.parse_captures(
                "__LPH_BEGIN__1__4\n__LPH_DATA__616263\n__LPH_END__1\n"
            )

    def test_missing_field_is_a_clear_error(self):
        with self.assertRaisesRegex(ValueError, "no numeric table field"):
            extractor.replace_loadstring_fields('local x="[124]=loadstring" -- [8]=loadstring')


if __name__ == "__main__":
    unittest.main()
