"""Provide functions to assemble the output tree."""

from collections.abc import Iterator
from pathlib import Path
from shutil import copy2, rmtree

from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
from pulldown_cmark import render

from steyr.config import FullConfig
from steyr.page import Page
from pygments.formatters import HtmlFormatter
from typing import cast


def _to_destination(path: Path, cfg: FullConfig) -> Path:
    return cfg.paths.output / path.relative_to(cfg.paths.input)


def _write_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _render_pages(pages: list[Page], cfg: FullConfig) -> dict[Page, str]:
    content = [page.content for page in pages]
    renders = render(content, cfg.markdown.options)
    return dict(zip(pages, renders, strict=True))


def _template_pages(
    pages: list[Page],
    renders: dict[Page, str],
    cfg: FullConfig,
) -> Iterator[tuple[Path, str]]:
    index = cfg.paths.input / "index.md"
    index = next((page for page in pages if page.path == index), None)
    links = (index, *sorted(index.children, key=lambda x: x.title)) if index else ()

    for page in pages:
        destination = _to_destination(page.path, cfg)
        destination = (
            destination.parent / "index.html"
            if page.path.stem == "index"
            else destination.with_suffix(".html")
        )

        context = {
            "page": page,
            "content": renders[page],
            "posts": () if page == index else page.children,
            "links": links,
        }

        yield destination, cfg.template.render(context)


def _assemble_rss(
    pages: list[Page],
    renders: dict[Page, str],
    cfg: FullConfig,
) -> str | None:
    # These are validated as equal by Pydantic, but we check each for the type checker.
    if not cfg.rss or not cfg.paths.rss:
        return None

    link = f"{cfg.rss.url}/{cfg.paths.rss.relative_to(cfg.paths.output)}"

    fg = FeedGenerator()
    fg.title(cfg.rss.title)  # pyright: ignore[reportUnknownMemberType]
    fg.subtitle(cfg.rss.subtitle)  # pyright: ignore[reportUnknownMemberType]
    fg.author(name=cfg.rss.name, email=cfg.rss.email)  # pyright: ignore[reportUnknownMemberType]
    fg.link(href=cfg.rss.url, rel="alternate")  # pyright: ignore[reportUnknownMemberType]
    fg.link(href=link, rel="self")  # pyright: ignore[reportUnknownMemberType]
    fg.language(cfg.rss.language)  # pyright: ignore[reportUnknownMemberType]

    posts = sorted(
        [page for page in pages if not page.children],
        key=lambda x: x.date,
        reverse=True,
    )

    for post in posts:
        url = cfg.rss.url + post.href
        fe: FeedEntry = fg.add_entry()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        fe.title(post.title)  # pyright: ignore[reportUnknownMemberType]
        fe.published(post.date.isoformat() + "T00:00:00Z")  # pyright: ignore[reportUnknownMemberType]
        fe.content(content=renders[post], type="html")  # pyright: ignore[reportUnknownMemberType]
        fe.link(href=url)  # pyright: ignore[reportUnknownMemberType]

    return fg.rss_str(pretty=True).decode("utf-8")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]


def write_site(cfg: FullConfig) -> None:
    """Parse, render, template, and write the site."""
    if cfg.paths.output.is_file():
        cfg.paths.output.unlink()
    elif cfg.paths.output.is_dir():
        rmtree(cfg.paths.output)

    if not (pages := Page.from_path(cfg.paths.input)):
        return

    renders = _render_pages(pages, cfg)

    for destination, content in _template_pages(pages, renders, cfg):
        _write_parent(destination)
        _ = destination.write_text(content)

    if rss := _assemble_rss(pages, renders, cfg):
        _write_parent(cfg.paths.rss)  # pyright: ignore[reportArgumentType]
        _ = cfg.paths.rss.write_text(rss)  # pyright: ignore[reportOptionalMemberAccess]

    if cfg.paths.styles:
        for style, path in cfg.paths.styles.items():
            _write_parent(path)
            css = cast("str", HtmlFormatter(style=style).get_style_defs())  # pyright: ignore[reportUnknownMemberType]
            _ = path.write_text(css)

    for path in [
        path
        for path in cfg.paths.input.rglob("*")
        if path.is_file() and path.suffix != ".md"
    ]:
        destination = _to_destination(path, cfg)
        _write_parent(destination)
        _ = copy2(path, destination)
