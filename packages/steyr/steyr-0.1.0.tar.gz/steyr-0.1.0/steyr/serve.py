"""Provide `serve_site()`."""

from functools import partial

from livereload import Server

from steyr.assemble import write_site
from steyr.config import FullConfig


def serve_site(cfg: FullConfig) -> None:
    """Serve the HTTP server."""
    server = Server()
    server.watch(cfg.paths.input, partial(write_site, cfg))  # pyright: ignore[reportUnknownMemberType]
    server.serve(root=cfg.paths.output)  # pyright: ignore[reportUnknownMemberType]
