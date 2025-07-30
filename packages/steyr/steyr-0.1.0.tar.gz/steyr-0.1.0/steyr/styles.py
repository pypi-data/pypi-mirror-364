"""Provide styles for Pygments."""

from dataclasses import dataclass
from typing import ClassVar, Final

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Token,
    _TokenType,  # pyright: ignore[reportPrivateUsage]
)

# The Everforest styles follow the color and palette scheme defined
# at 'https://github.com/sainnhe/everforest/blob/master/palette.md'.

@dataclass
class _EverforestPalette:
    bg_dim: Final[str]
    bg0: Final[str]
    bg1: Final[str]
    bg2: Final[str]
    bg3: Final[str]
    bg4: Final[str]
    bg5: Final[str]
    bg_red: Final[str]
    bg_visual: Final[str]
    bg_yellow: Final[str]
    bg_green: Final[str]
    bg_blue: Final[str]
    red: Final[str]
    orange: Final[str]
    yellow: Final[str]
    green: Final[str]
    blue: Final[str]
    aqua: Final[str]
    purple: Final[str]
    fg: Final[str]
    statusline1: Final[str]
    statusline2: Final[str]
    statusline3: Final[str]
    grey0: Final[str]
    grey1: Final[str]
    grey2: Final[str]


def _everforest_palette_to_style(
    title: str,
    palette: _EverforestPalette,
) -> type[Style]:
    class DynamicEverforestStyle(Style):
        name: str = title
        background_color: str = palette.bg0
        highlight_color: str = palette.bg1
        line_number_color: str = palette.grey0
        line_number_background_color: str = palette.bg0
        line_number_special_color: str = palette.grey2
        line_number_special_background_color: str = palette.bg1

        styles: ClassVar[dict[_TokenType, str]] = {  # pyright: ignore[reportIncompatibleVariableOverride]
            Token: palette.fg,
            Error: palette.red,
            Keyword: palette.red,
            Keyword.Type: palette.yellow,
            Keyword.Constant: palette.purple,
            Keyword.Declaration: palette.orange,
            Keyword.Namespace: palette.yellow,
            Name: palette.fg,
            Name.Tag: palette.green,
            Name.Entity: palette.orange,
            Name.Constant: palette.aqua,
            Name.Class: palette.yellow,
            Name.Function: palette.green,
            Name.Builtin: palette.green,
            Name.Builtin.Pseudo: palette.blue,
            Name.Attribute: palette.purple,
            Name.Exception: palette.red,
            Literal: palette.fg,
            String: palette.green,
            String.Doc: palette.green,
            String.Interpol: palette.green,
            Number: palette.purple,
            Operator: palette.orange,
            Punctuation: palette.grey1,
            Comment: palette.grey1,
            Comment.Preproc: palette.purple,
            Comment.PreprocFile: palette.purple,
            Comment.Special: palette.grey1,
            Generic: palette.fg,
            Generic.Emph: f"italic {palette.fg}",
            Generic.Output: palette.fg,
            Generic.Heading: f"bold {palette.orange}",
            Generic.Deleted: f"bg:{palette.bg_red}",
            Generic.Inserted: f"bg:{palette.bg_green}",
            Generic.Traceback: palette.red,
            Generic.Subheading: f"bold {palette.orange}",
            Name.Variable: palette.fg,
            Name.Label: palette.orange,
            Literal.Date: palette.green,
            String.Single: palette.green,
            String.Double: palette.green,
            String.Escape: palette.green,
            Number.Float: palette.purple,
            Number.Integer: palette.purple,
            Number.Hex: palette.purple,
            Number.Oct: palette.purple,
            Operator.Word: palette.orange,
            Token.Text: palette.fg,
            Token.Text.Whitespace: palette.bg4,
        }

    return DynamicEverforestStyle

EverforestLightStyle = _everforest_palette_to_style(
    title="everforest-light",
    palette=_EverforestPalette(
        bg_dim="#f2efdf",
        bg0="#fffbef",
        bg1="#f8f5e4",
        bg2="#f2efdf",
        bg3="#edeada",
        bg4="#e8e5d5",
        bg5="#bec5b2",
        bg_red="#ffe7de",
        bg_visual="#fof2d4",
        bg_yellow="#fef2d5",
        bg_green="#f3f5d9",
        bg_blue="#ecf5ed",
        red="#f85552",
        orange="#f57d26",
        yellow="#dfa000",
        green="#8da101",
        blue="#3a94c5",
        aqua="#35a77c",
        purple="#df69ba",
        fg="#5c6a72",
        statusline1="#93b259",
        statusline2="#708089",
        statusline3="#e66868",
        grey0="#a6b0a0",
        grey1="#939f91",
        grey2="#829181",
    ),
)

EverforestDarkStyle = _everforest_palette_to_style(
    title="everforest-dark",
    palette=_EverforestPalette(
        bg_dim="#1e2326",
        bg0="#272e33",
        bg1="#2e383c",
        bg2="#374145",
        bg3="#414b50",
        bg4="#495156",
        bg5="#4f5b58",
        bg_red="#4c3743",
        bg_visual="#493b40",
        bg_yellow="#45443c",
        bg_green="#3c4841",
        bg_blue="#384b55",
        red="#e67e80",
        orange="#e69875",
        yellow="#dbbc7f",
        green="#a7c080",
        blue="#7fbbb3",
        aqua="#83c092",
        purple="#d699b6",
        fg="#d3c6aa",
        statusline1="#a7c080",
        statusline2="#d3c6aa",
        statusline3="#e67e80",
        grey0="#7a8478",
        grey1="#859289",
        grey2="#9da9a0",
    ),
)

