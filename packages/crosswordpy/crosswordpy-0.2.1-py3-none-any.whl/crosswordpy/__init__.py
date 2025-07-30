"""No Hint Crossword Puzzle"""

from importlib.metadata import metadata

from .game import Crossword

_package_metadata = metadata(str(__package__))
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")


def main() -> None:
    """ゲーム実行"""
    Crossword().run()
