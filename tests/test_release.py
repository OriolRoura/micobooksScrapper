import unittest

from micobooks_scraper.release import SemanticVersion, extract_version, should_build


class ReleaseVersionTests(unittest.TestCase):
    def test_extracts_canonical_version(self) -> None:
        self.assertEqual(extract_version('__version__ = "2.0.1"'), "2.0.1")

    def test_rejects_invalid_semantic_version(self) -> None:
        with self.assertRaises(ValueError):
            SemanticVersion.parse("2.0")

    def test_builds_exact_2_0_1(self) -> None:
        self.assertTrue(should_build("2.0.1", "2.0.0"))

    def test_builds_major_version_increase(self) -> None:
        self.assertTrue(should_build("3.0.0", "2.9.9"))

    def test_does_not_build_patch_or_minor_version(self) -> None:
        self.assertFalse(should_build("2.0.2", "2.0.1"))
        self.assertFalse(should_build("2.1.0", "2.0.1"))

    def test_first_release_only_builds_exact_2_0_1(self) -> None:
        self.assertTrue(should_build("2.0.1", None))
        self.assertFalse(should_build("1.0.0", None))


if __name__ == "__main__":
    unittest.main()
