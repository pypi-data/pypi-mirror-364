import unittest
from pathlib import Path
import importlib.util


class SiteSanitizeTests(unittest.TestCase):
    @staticmethod
    def _load_site():
        spec = importlib.util.spec_from_file_location(
            "site", Path(__file__).resolve().parents[1] / "projects" / "web" / "site.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    @classmethod
    def setUpClass(cls):
        cls.site = cls._load_site()
    def test_sanitize_filename(self):
        cases = {
            "foo/bar": "foobar",
            "foo\\bar": "foobar",
            "../secret": "secret",
            ".hidden": ".hidden",
            "_private": "_private",
            "normal-name_1.txt": "normal-name_1.txt",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(self.site._sanitize_filename(raw), expected)

    def test_is_hidden_or_private(self):
        true_cases = [
            "",  # empty basename
            ".hidden",
            "_private",
            "path/.hidden",
            "path/_secret",
            "file._txt",
            "._file.txt",
        ]
        for fname in true_cases:
            with self.subTest(fname=fname):
                self.assertTrue(self.site._is_hidden_or_private(fname))

        false_cases = [
            "normal",
            "normal.txt",
            "folder/visible.md",
            "file.t_txt",
        ]
        for fname in false_cases:
            with self.subTest(fname=fname):
                self.assertFalse(self.site._is_hidden_or_private(fname))


if __name__ == "__main__":
    unittest.main()
