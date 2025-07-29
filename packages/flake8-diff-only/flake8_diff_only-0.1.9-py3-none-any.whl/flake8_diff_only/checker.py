import ast
from importlib.metadata import version as _version
from typing import Any, ClassVar

__version__ = _version("flake8-diff-only")


class Flake8DiffOnlyChecker:
    name = "flake8-diff-only"
    version = __version__

    enabled: ClassVar[bool] = False

    def __init__(self, tree: ast.AST, filename: str):
        pass

    @classmethod
    def add_options(cls, parser: Any) -> None:
        parser.add_option(
            "--diff-only",
            action="store_true",
            default=False,
            help=(
                "Enable flake8-diff-only filtering"
                " (only show errors in changed lines)."
            ),
        )

    @classmethod
    def parse_options(cls, options: Any) -> None:
        cls.enabled = options.diff_only

    def run(self):  # type: ignore[no-untyped-def]
        return []
