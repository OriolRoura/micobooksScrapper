import unittest

from micobooks_scraper.server import build_parser


class ServerOptionsTests(unittest.TestCase):
    def test_lan_only_is_the_default_policy(self) -> None:
        options = build_parser().parse_args([])

        self.assertFalse(options.allow_public_access)

    def test_public_access_requires_explicit_flag(self) -> None:
        options = build_parser().parse_args(["--allow-public-access"])

        self.assertTrue(options.allow_public_access)


if __name__ == "__main__":
    unittest.main()
