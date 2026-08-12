"""CLI entrypoint for ptop system monitor."""

import argparse

from ptop import __version__
from ptop.app import PtopApp
from ptop.config import Config


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ptop",
        description="A modern, beautiful, and feature-packed system monitor written in Python and Textual.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-t",
        "--theme",
        type=str,
        help="Initial theme (catppuccin, tokyonight, nord, dracula, cyberpunk)",
    )
    parser.add_argument(
        "-l",
        "--layout",
        type=str,
        choices=["full", "compact", "gpu", "proc"],
        help="Initial layout preset",
    )
    parser.add_argument(
        "-r",
        "--refresh",
        type=int,
        help="Refresh interval in milliseconds (default: 1000)",
    )

    args = parser.parse_args()

    config = Config.load()
    if args.theme:
        config.theme = args.theme
    if args.layout:
        config.layout = args.layout
    if args.refresh and args.refresh >= 100:
        config.refresh_rate_ms = args.refresh

    config.save()

    app = PtopApp()
    app.run()


if __name__ == "__main__":
    main()
