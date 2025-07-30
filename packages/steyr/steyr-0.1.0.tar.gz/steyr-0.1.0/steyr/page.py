"""Provide `Page`."""

from __future__ import annotations

import re
from datetime import date as date_t
from functools import cached_property
from pathlib import Path
from tomllib import loads
from typing import Final

from steyr.config import ConstModel

_frontmatter_regex: Final = re.compile(
    r"^\s*\+{3}\s+(.*?)\s+\+{3}\s*(.*)$",
    re.DOTALL | re.MULTILINE,
)


class Page(ConstModel):
    """A Markdown representation which caches file contents and hierarchical information."""  # noqa: E501

    path: Path
    title: str
    date: date_t
    content: str
    children: tuple[Page, ...]

    private_input: Path  # Used to find href.

    @classmethod
    def _load_frontmatter(cls, path: Path) -> tuple[dict[str, str], str]:
        """Parse a Markdown file for a frontmatter dictionary and the text remainder."""
        if not (parsed := _frontmatter_regex.search(path.read_text())):
            return {}, ""

        frontmatter, content = parsed.group(1), parsed.group(2)
        return loads(frontmatter), content

    @classmethod
    def _from_path_init(
        cls,
        path: Path,
        input: Path,  # noqa: A002
        children: tuple[Page, ...],
    ) -> Page:
        frontmatter, content = cls._load_frontmatter(path)
        return cls(
            path=path,
            **frontmatter,  # pyright: ignore[reportArgumentType]
            content=content,
            children=children,
            private_input=input,
        )

    @classmethod
    def from_path(cls, input: Path) -> list[Page]:  # noqa: A002
        """Build a nested list of Markdown pages within a path."""
        markdown = [
            path
            for path in input.rglob("*.md")
            if not any(part.startswith(".") for part in path.relative_to(input).parts)
        ]

        # Group files by parent directory. We sort leaf-first to avoid the following.
        #    1. We process a parent directory, e.g., /, and create a Page object for,
        #       e.g., /posts/index.md, which has no children. This gets added to the
        #       parent's children.
        #    2. Later, when we loop over /posts/, we create a new Page object which
        #       correctly includes its children, e.g., /posts/post.md, and overwrite the
        #       prior, simple Page in the cache. But, the parent still holds a reference
        #       to the original, simple page.
        trees = sorted(
            {path.parent for path in markdown},
            key=lambda x: len(x.parts),
            reverse=True,
        )

        # Cache pages as we traverse the input tree.
        pages: dict[Path, Page] = {}

        for tree in trees:
            local = {path for path in markdown if path.parent == tree}
            index = next((path for path in local if path.stem == "index"), None)

            children: list[Page] = []
            for post in local - {index}:
                page = cls._from_path_init(post, input, ())
                children.append(page)
                pages[post] = page

            if index:
                # Add indexes of child directories.
                children += [
                    pages[page]  # Valid, as we traverse leaf-first.
                    for page in pages
                    if page.name == "index.md" and page.parent.parent == tree
                ]
                children = sorted(children, key=lambda x: x.date, reverse=True)
                page = cls._from_path_init(index, input, tuple(children))
                pages[index] = page

        return list(pages.values())

    @cached_property
    def href(self) -> str:
        """Get the root-relative URL for this page."""
        relative = self.path.relative_to(self.private_input)
        if self.path.stem == "index":
            return f"/{relative.parent.as_posix()}/".replace("/./", "/")
        return f"/{relative.with_suffix('.html').as_posix()}"
