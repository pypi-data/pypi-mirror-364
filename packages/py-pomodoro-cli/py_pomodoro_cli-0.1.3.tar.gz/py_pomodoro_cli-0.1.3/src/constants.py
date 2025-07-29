from typing import Dict, TypedDict


class Theme(TypedDict):
    START: str
    END: str
    TEXT_COLOUR: str
    ALT: str


THEMES: Dict[str, Theme] = {
    "nord-frost": {
        "START": "#5E81AC",
        "END": "#8FBCBB",
        "TEXT_COLOUR": "#ECEFF4",
        "ALT": "#88C0D0",
    },
    "nord-polar-night": {
        "START": "#3B4252",
        "END": "#ECEFF4",
        "TEXT_COLOUR": "#4C566A",
        "ALT": "#ECEFF4",
    },
    "nord-aurora": {
        "START": "#B48EAD",
        "END": "#A3BE8C",
        "TEXT_COLOUR": "#88C0D0",
        "ALT": "#D08770",
    },
    "tokyo-night": {
        "START": "#00ffd2",
        "END": "#004687",
        "TEXT_COLOUR": "#ff4499",
        "ALT": "#00ffd2",
    },
    "tokyo-city-night-drive": {
        "START": "#fffcb0",
        "END": "#a4aed6",
        "TEXT_COLOUR": "#dadef4",
        "ALT": "#fffcb0",
    },
    "matrix": {
        "START": "#008F11",
        "END": "#00FF41",
        "TEXT_COLOUR": "#008F11",
        "ALT": "#00FF41",
    },
    "alien": {
        "START": "#194820",
        "END": "#a0ac32",
        "TEXT_COLOUR": "#a7a6a3",
        "ALT": "#194820",
    },
    "akira": {
        "START": "#115363",
        "END": "#9c3111",
        "TEXT_COLOUR": "#7ea228",
        "ALT": "#115363",
    },
    "ghost-in-the-shell": {
        "START": "#324b77",
        "END": "#74e6f7",
        "TEXT_COLOUR": "#a2d0d8",
        "ALT": "#324b77",
    },
    "sailor-moon": {
        "START": "#5158ff",
        "END": "#d260ff",
        "TEXT_COLOUR": "#fff666",
        "ALT": "#ffb3df",
    },
    "evangelion": {
        "START": "#765898",
        "END": "#52d053",
        "TEXT_COLOUR": "#e6770b",
        "ALT": "#d3290f",
    },
    "dbz": {
        "START": "#1c4595",
        "END": "#e76a24",
        "TEXT_COLOUR": "#fbbc42",
        "ALT": "#e7e5e8",
    },
}

DEFAULT_THEME: Theme = {
    "START": "#4C566A",
    "END": "#FFFFFF",
    "TEXT_COLOUR": "#FFFFFF",
    "ALT": "#FFFFFF",
}
