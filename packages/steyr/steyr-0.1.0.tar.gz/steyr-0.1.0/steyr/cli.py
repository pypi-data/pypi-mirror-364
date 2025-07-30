"""Parse arguments and configuration at program start."""

from argparse import ArgumentParser
from pathlib import Path

from steyr.assemble import write_site
from steyr.config import FullConfig, load_config
from steyr.serve import serve_site


def _build(cfg: FullConfig) -> None:
    write_site(cfg)


def _serve(cfg: FullConfig) -> None:
    _build(cfg)
    serve_site(cfg)


def main() -> None:  # noqa: D103
    parser = ArgumentParser(prog="steyr")
    subparsers = parser.add_subparsers(dest="command")

    _ = subparsers.add_parser("build").set_defaults(callback=_build)
    _ = subparsers.add_parser("serve").set_defaults(callback=_serve)

    args = parser.parse_args()

    if hasattr(args, "callback"):
        cfg = load_config(Path.cwd())
        args.callback(cfg)  # pyright: ignore[reportAny]
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
