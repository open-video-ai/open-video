"""``python -m open_video`` entry point and the ``open-video`` console script.

Delegates to open_video.cli.open_video.main() (the real CLI). A leading ``gen`` token is
stripped as a convenience so both forms work identically:

    open-video gen "waves at sunset" --duration 10
    open-video "waves at sunset" --duration 10
    python -m open_video "waves at sunset" --duration 10

The genuine subcommands (list-models / list-presets / serve) are passed through
untouched. See cli/open_video.py for the full CLI contract.
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    """Forward to open_video.cli.open_video.main, optionally stripping a leading ``gen``.

    Returns the process exit code so this works both as a console_scripts entry
    point (``open-video``) and as ``python -m open_video``.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    # `open-video gen "prompt" [...]` == `open-video "prompt" [...]`
    # Only strip when something follows `gen`, so genuine subcommands and a
    # bare `open-video gen` (treated as a literal prompt) are not perturbed.
    if len(argv) >= 2 and argv[0] == "gen":
        argv = argv[1:]
    from open_video.cli.open_video import main as _cli_main
    return _cli_main(argv)


if __name__ == "__main__":
    sys.exit(main())
