import unittest

from striprtf.striprtf import rtf_to_text


class TestUnknownFcharset(unittest.TestCase):
    """A font whose \\fcharset is not in charset_map (e.g. 1 = DEFAULT_CHARSET) uses the
    document codepage set by \\ansicpg, not the default of the encoding argument.

    See the note in https://github.com/joshy/striprtf/issues/76
    """

    def test_default_charset_uses_ansicpg(self):
        rtf = r"{\rtf1\ansi\ansicpg1250\deff0{\fonttbl{\f0\fcharset1 Arial;}}\f0 \'e8}"
        self.assertEqual("č", rtf_to_text(rtf))  # cp1250 0xE8, not cp1252 0xE8

    def test_known_charset_is_unchanged(self):
        rtf = r"{\rtf1\ansi\ansicpg1250\deff0{\fonttbl{\f0\fcharset204 Cyr;}}\f0 \'e8}"
        self.assertEqual("и", rtf_to_text(rtf))  # cp1251

    def test_without_ansicpg_the_encoding_argument_is_used(self):
        rtf = r"{\rtf1\ansi\deff0{\fonttbl{\f0\fcharset1 Arial;}}\f0 \'e8}"
        self.assertEqual("è", rtf_to_text(rtf))
        self.assertEqual("č", rtf_to_text(rtf, encoding="cp1250"))


if __name__ == "__main__":
    unittest.main()
