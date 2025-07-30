"""Provide functions and classes to load configurations."""

from functools import cached_property
from inspect import signature
from pathlib import Path
from tomllib import loads
from typing import Self

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pulldown_cmark import Options
from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    computed_field,
    field_validator,
    model_validator,
)
from pygments.styles import get_all_styles

from steyr.callbacks import code_callback, math_callback


class ConstModel(BaseModel):  # noqa: D101
    model_config: ConfigDict = ConfigDict(frozen=True, arbitrary_types_allowed=True)  # pyright: ignore[reportIncompatibleVariableOverride]


class _MarkdownConfig(ConstModel):
    options: Options

    @field_validator("options", mode="before")
    @classmethod
    def _to_options(cls, v: list[str]) -> Options:
        keys = set(v)
        valid = signature(Options).parameters.keys()

        if unknown := keys - valid:
            msg = f"invalid options '{unknown}'; valid options are '{valid}'"
            raise ValueError(msg)

        callbacks = {
            "math": math_callback,
            "code": code_callback,
        }

        return Options(**{key: callbacks.get(key, True) for key in keys})  # pyright: ignore[reportArgumentType]


class _PathsConfig(ConstModel):
    input: Path
    output: Path
    template: Path
    rss: Path | None = None
    styles: dict[str, Path] | None = None

    @field_validator("input", "output", "template", "rss", mode="before")
    @classmethod
    def _resolve_path(cls, v: str | None, info: ValidationInfo) -> Path | None:
        return None if v is None else info.context.get("cwd") / v  # pyright: ignore[reportOptionalMemberAccess, reportAny]

    @field_validator("styles", mode="before")
    @classmethod
    def _to_styles(
        cls,
        v: dict[str, Path] | None,
        info: ValidationInfo,
    ) -> dict[str, Path] | None:
        if v is None:
            return None

        keys = set(v.keys())
        valid = set(get_all_styles())

        if unknown := keys - valid:
            msg = f"invalid styles '{unknown}'; valid styles are '{valid}'"
            raise ValueError(msg)

        if (
            not info.context
            or not (cwd := info.context.get("cwd"))  # pyright: ignore[reportAny]
            or not isinstance(cwd, Path)
        ):
            msg = "path `cwd` required in validation context"
            raise ValueError(msg)

        return {key: cwd / path for key, path in v.items()}


class _RssConfig(ConstModel):
    url: str
    title: str
    subtitle: str
    name: str
    email: str
    language: str


class FullConfig(ConstModel):
    """Full configuration of input/output/template paths and Markdown parsing."""

    markdown: _MarkdownConfig
    paths: _PathsConfig
    rss: _RssConfig | None

    @model_validator(mode="after")
    def _validate_rss(self) -> Self:
        if (self.rss is None) ^ (self.paths.rss is None):
            msg = "`paths.rss` and `[rss]` must be specified together"
            raise ValueError(msg)

        return self

    @computed_field
    @cached_property
    def template(self) -> Template:
        """The Jinja2 page template."""
        template = self.paths.template
        return Environment(
            loader=FileSystemLoader(template.parent),
            autoescape=select_autoescape(["html"]),
        ).get_template(template.name)


def load_config(directory: Path) -> FullConfig:
    """Read the program configuration.

    We check for a file, steyr.toml, at the current directory, then traverse
    upward until it is found.

    Parameters
    ----------
    directory
        The directory at which to begin the search.

    Returns
    -------
    A FullConfig object.

    Raises
    ------
    FileNotFoundError
        If the directory traversal does not find a config file.
    ValidationError
        If the configuration file lacks a key.

    """
    filename = "steyr.toml"

    for cwd in (directory := directory.resolve(), *directory.parents):
        try:
            cfg = loads((cwd / filename).read_text())
            return FullConfig.model_validate(cfg, context={"cwd": cwd})
        except FileNotFoundError:
            continue

    msg = f"failed to find '{filename}' via upward directory traversal"
    raise FileNotFoundError(msg)
