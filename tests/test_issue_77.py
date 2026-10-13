import time
import unittest

from striprtf.striprtf import font_table_entries, rtf_to_text


class TestFontTable(unittest.TestCase):
    """The font table is parsed one ';'-terminated entry at a time, in linear time.

    See https://github.com/joshy/striprtf/issues/77
    """

    def test_large_font_table_is_linear(self):
        # the font table group is the whole document (unbalanced braces), and its
        # entries have no ';' (the shape from the issue: > 60s on 100 KB before)
        rtf = r"{\rtf1{\fonttbl" + r"\f1\fcharset0 " * 7000 + " text"
        start = time.time()
        rtf_to_text(rtf)
        self.assertLess(time.time() - start, 1.0)

    def test_entry_without_charset_is_linear(self):
        # many \fN and no \fcharset in one entry: quadratic for a regex with lazy
        # quantifiers
        group = r"{\fonttbl{" + r"\f1 " * 100000 + ";}}"
        start = time.time()
        self.assertEqual([], font_table_entries(group))
        self.assertLess(time.time() - start, 1.0)

    def test_line_break_inside_an_entry(self):
        # RTF writers break long lines inside the font table: \fcharset is on the
        # next line
        rtf = (
            "{\\rtf1\\ansi\\ansicpg1252"
            "{\\fonttbl{\\f0\\froman\r\n\\fcharset161 Greek;}}\\f0 \\'e1}"
        )
        self.assertEqual("α", rtf_to_text(rtf))

    def test_charset_of_the_next_entry_is_not_taken(self):
        # \f0 has no \fcharset: it must not get the charset of \f1 (204, Cyrillic)
        rtf = (
            r"{\rtf1\ansi\ansicpg1252"
            r"{\fonttbl{\f0\fswiss Arial;}{\f1\fcharset204 Cyr;}}\f0 \'e9{\f1 \'e9}}"
        )
        self.assertEqual("éй", rtf_to_text(rtf))

    def test_entries(self):
        group = (
            r"{\fonttbl{\f0\froman\fcharset238\fprq2{\*\panose 02020603}"
            r"Times New Roman;}{\f1 Sym;}}"
        )
        self.assertEqual(
            [("0", "238", r"\fprq2{\*\panose 02020603}Times New Roman")],
            font_table_entries(group),
        )
        # the name must not be empty: the last digit of the charset becomes the name
        self.assertEqual([("1", "1", "1")], font_table_entries(r"\f1\fcharset11;"))
        self.assertEqual([], font_table_entries(r"\f1\fcharset1;"))


if __name__ == "__main__":
    unittest.main()
