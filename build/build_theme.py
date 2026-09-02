#!/usr/bin/env python3
"""Turbine — token-driven generator for the Zed theme family.

Every colour in the emitted JSON is a reference to one of the tokens in
TOKENS below. No key is hand-picked; change a token and all three variants
move together (brief §2, "the four-layer token model").

Usage:
    python3 build/build_theme.py             # write themes/turbine.json (full current key set)
    python3 build/build_theme.py --strict    # emit only the pinned v0.2.0 keys
    python3 build/build_theme.py --report    # write docs/contrast.md and gate on WCAG AA
    python3 build/build_theme.py --check     # build to memory, diff against themes/turbine.json and the site
    python3 build/build_theme.py --site      # inject the theme JSON into site/index.html

Key lists:
    build/schema_keys.txt         every key in Zed's current ThemeStyleContent,
                                  extracted from crates/settings_content/src/theme.rs
    build/schema_keys_v0.2.0.txt  the published v0.2.0 schema, as pinned by the brief

The generator has no dependencies beyond the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME_PATH = ROOT / "themes" / "turbine.json"
REPORT_PATH = ROOT / "docs" / "contrast.md"
SITE_PATH = ROOT / "site" / "index.html"
SITE_OPEN = '<script id="turbine-theme" type="application/json">'
SITE_CLOSE = "</script>"
KEYS_CURRENT = ROOT / "build" / "schema_keys.txt"
KEYS_V020 = ROOT / "build" / "schema_keys_v0.2.0.txt"

SCHEMA_URL = "https://zed.dev/schema/themes/v0.2.0.json"
FAMILY_NAME = "Turbine"
AUTHOR = "Christopher Nicholson"

# ---------------------------------------------------------------------------
# 1. Tokens — brief §3, plus `ghost` and a two-step darker Subsonic accent
#    (both explained in docs/decisions.md)
# ---------------------------------------------------------------------------

# Order matters: this is the order the variants appear in Zed's theme picker.
VARIANTS = [
    ("Turbine Hypersonic", "dark"),
    ("Turbine Supersonic", "dark"),
    ("Turbine Subsonic", "light"),
]

TOKENS: dict[str, dict[str, str]] = {
    "Turbine Hypersonic": {
        # Surface layer
        "bg": "#000000",
        "surface": "#0E1113",
        "elevated": "#16191C",
        # Content layer
        "text": "#EDEBE6",
        "muted": "#99A1A8",
        "ghost": "#7B838A",
        "disabled": "#5C646B",
        # Line layer (doubles as the neutral interaction ramp)
        "border": "#23282D",
        "border_hi": "#39424A",
        # Signal layer
        "accent": "#4FE3C1",
        "blue": "#7FB4FF",
        "green": "#7BE38B",
        "yellow": "#F2C94C",
        "orange": "#FFB067",
        "red": "#FF7B72",
        "purple": "#D9A6FF",
        # State
        "sel": "#123A38",
        "active_ln": "#0B0E10",
    },
    "Turbine Supersonic": {
        "bg": "#14171A",
        "surface": "#1B1F23",
        "elevated": "#22272C",
        "text": "#E6E4E0",
        "muted": "#9BA4AC",
        "ghost": "#868F97",
        "disabled": "#646C74",
        "border": "#2C3238",
        "border_hi": "#414A52",
        "accent": "#3FD3B4",
        "blue": "#6BA8F5",
        "green": "#6FD47F",
        "yellow": "#E6BA45",
        "orange": "#F0A05E",
        "red": "#F2736B",
        "purple": "#C79BF0",
        "sel": "#1D3B39",
        "active_ln": "#1A1E22",
    },
    "Turbine Subsonic": {
        "bg": "#F7F4EF",
        "surface": "#EFEBE4",
        "elevated": "#FFFFFF",
        "text": "#22262B",
        "muted": "#5A6169",
        "ghost": "#636A72",
        "disabled": "#8B939B",
        "border": "#D9D3CA",
        "border_hi": "#B9B1A6",
        "accent": "#0C7763",
        "blue": "#1D5FCC",
        "green": "#17714A",
        "yellow": "#8A5A00",
        "orange": "#B4470F",
        "red": "#C0342B",
        "purple": "#7A3BB5",
        "sel": "#CFE8E1",
        "active_ln": "#EFECE6",
    },
}

TRANSPARENT = "#00000000"
SIGNAL_ORDER = ["accent", "blue", "green", "yellow", "orange", "red", "purple"]

# Alpha steps (0–255). Named so the intent survives in the key map.
A_WASH = 0x0F     #  6 %  hollow diff rows
A_TINT = 0x1F     # 12 %  filled diff rows, status tints
A_SOFT = 0x26     # 15 %  highlighted line, conflict regions
A_MARK = 0x33     # 20 %  document highlights, drop target, debugger line, vim pills
A_SELECT = 0x40   # 25 %  UI text selection, remote cursors
A_WORD = 0x59     # 35 %  word-level diff marks
A_EDGE = 0x5C     # 36 %  hollow diff borders
A_LINE = 0x66     # 40 %  status borders, active search match, minimap thumb at rest
A_DRAG = 0x99     # 60 %  minimap thumb hovered
A_HELD = 0xB3     # 70 %  minimap thumb dragged

# ---------------------------------------------------------------------------
# 2. Key map — brief §6, extended to Zed's current schema.
#    Values are token names, a (token, alpha) pair, or a literal string when
#    the schema value is not a colour.
# ---------------------------------------------------------------------------

Value = str | tuple[str, int]

STYLE_KEYS: list[tuple[str, Value]] = [
    # Base, text & icons
    ("background", "bg"),
    ("background.appearance", "opaque"),
    ("surface.background", "surface"),
    ("elevated_surface.background", "elevated"),
    ("border", "border"),
    ("border.variant", "border"),
    ("border.focused", "accent"),
    ("border.selected", "accent"),
    ("border.transparent", TRANSPARENT),
    ("border.disabled", "border"),
    ("text", "text"),
    ("text.muted", "muted"),
    ("text.placeholder", "ghost"),
    ("text.disabled", "disabled"),
    ("text.accent", "accent"),
    ("icon", "text"),
    ("icon.muted", "muted"),
    ("icon.placeholder", "ghost"),
    ("icon.disabled", "disabled"),
    ("icon.accent", "accent"),
    ("link_text.hover", "accent"),
    # Interactive elements — one neutral ramp for both element families:
    # rest → hover `border` → active `border_hi` → selected `sel`.
    ("element.background", "surface"),
    ("element.hover", "border"),
    ("element.active", "border_hi"),
    ("element.selected", "sel"),
    ("element.disabled", "surface"),
    ("element.selection_background", ("accent", A_SELECT)),
    ("ghost_element.background", TRANSPARENT),
    ("ghost_element.hover", "border"),
    ("ghost_element.active", "border_hi"),
    ("ghost_element.selected", "sel"),
    ("ghost_element.disabled", TRANSPARENT),
    ("drop_target.background", ("accent", A_MARK)),
    ("drop_target.border", "accent"),
    # Workspace chrome
    ("title_bar.background", "surface"),
    ("title_bar.inactive_background", "bg"),
    ("status_bar.background", "surface"),
    ("toolbar.background", "bg"),
    ("tab_bar.background", "surface"),
    ("tab.active_background", "bg"),
    ("tab.inactive_background", "surface"),
    ("panel.background", "surface"),
    ("panel.overlay_background", "surface"),
    ("panel.overlay_hover", "border"),
    ("panel.focused_border", "accent"),
    ("panel.indent_guide", "border"),
    ("panel.indent_guide_active", "border_hi"),
    ("panel.indent_guide_hover", "border_hi"),
    ("pane.focused_border", "accent"),
    ("pane_group.border", "border"),
    ("scrollbar.thumb.background", "border"),
    ("scrollbar.thumb.hover_background", "border_hi"),
    ("scrollbar.thumb.active_background", "disabled"),
    ("scrollbar.thumb.border", TRANSPARENT),
    ("scrollbar.track.background", TRANSPARENT),
    ("scrollbar.track.border", TRANSPARENT),
    ("minimap.thumb.background", ("border_hi", A_LINE)),
    ("minimap.thumb.hover_background", ("border_hi", A_DRAG)),
    ("minimap.thumb.active_background", ("border_hi", A_HELD)),
    ("minimap.thumb.border", "border_hi"),
    ("search.match_background", "sel"),
    ("search.active_match_background", ("accent", A_LINE)),
    ("debugger.accent", "red"),
    # Editor surface
    ("editor.foreground", "text"),
    ("editor.background", "bg"),
    ("editor.gutter.background", "bg"),
    ("editor.subheader.background", "surface"),
    ("editor.active_line.background", "active_ln"),
    ("editor.highlighted_line.background", ("accent", A_SOFT)),
    ("editor.debugger_active_line.background", ("yellow", A_MARK)),
    ("editor.line_number", "muted"),
    ("editor.active_line_number", "text"),
    ("editor.hover_line_number", "text"),
    ("editor.invisible", "disabled"),
    ("editor.wrap_guide", "border"),
    ("editor.active_wrap_guide", "border_hi"),
    ("editor.indent_guide", "border"),
    ("editor.indent_guide_active", "border_hi"),
    ("editor.document_highlight.read_background", ("accent", A_MARK)),
    ("editor.document_highlight.write_background", ("yellow", A_MARK)),
    ("editor.document_highlight.bracket_background", "sel"),
    ("editor.diff_hunk.added.background", ("green", A_TINT)),
    ("editor.diff_hunk.added.hollow_background", ("green", A_WASH)),
    ("editor.diff_hunk.added.hollow_border", ("green", A_EDGE)),
    ("editor.diff_hunk.deleted.background", ("red", A_TINT)),
    ("editor.diff_hunk.deleted.hollow_background", ("red", A_WASH)),
    ("editor.diff_hunk.deleted.hollow_border", ("red", A_EDGE)),
    # Version control
    ("version_control.added", "green"),
    ("version_control.deleted", "red"),
    ("version_control.modified", "yellow"),
    ("version_control.renamed", "blue"),
    ("version_control.conflict", "orange"),
    ("version_control.ignored", "disabled"),
    ("version_control.word_added", ("green", A_WORD)),
    ("version_control.word_deleted", ("red", A_WORD)),
    ("version_control.conflict_marker.ours", ("green", A_SOFT)),
    ("version_control.conflict_marker.theirs", ("blue", A_SOFT)),
]

# Vim mode indicator: a quiet tinted pill per mode, always with `text` on it.
# Zed only paints these when both background and foreground are non-transparent.
VIM_MODES: list[tuple[str, str]] = [
    ("normal", "accent"),
    ("insert", "green"),
    ("replace", "red"),
    ("visual", "purple"),
    ("visual_line", "purple"),
    ("visual_block", "purple"),
    ("helix_normal", "accent"),
    ("helix_select", "purple"),
]
VIM_EXTRA: list[tuple[str, Value]] = [
    ("vim.yank.background", ("yellow", A_SELECT)),
    ("vim.helix_jump_label.foreground", "red"),
]

# Status roles: (key, foreground token). Each expands to key, key.background
# (hue at 12 %) and key.border (hue at 40 %) so diff rows, diagnostic blocks
# and toasts carry their hue instead of a flat grey (docs/decisions.md §3).
STATUS_ROLES: list[tuple[str, str]] = [
    ("conflict", "orange"),
    ("created", "green"),
    ("deleted", "red"),
    ("error", "red"),
    ("hidden", "disabled"),
    ("hint", "accent"),
    ("ignored", "disabled"),
    ("info", "blue"),
    ("modified", "yellow"),
    ("predictive", "ghost"),
    ("renamed", "blue"),
    ("success", "green"),
    ("unreachable", "disabled"),
    ("warning", "orange"),
]

TERMINAL_KEYS: list[tuple[str, Value]] = [
    ("terminal.background", "bg"),
    ("terminal.foreground", "text"),
    ("terminal.bright_foreground", "text"),
    ("terminal.dim_foreground", "muted"),
    ("terminal.ansi.background", "bg"),
    ("terminal.ansi.black", "surface"),
    ("terminal.ansi.red", "red"),
    ("terminal.ansi.green", "green"),
    ("terminal.ansi.yellow", "yellow"),
    ("terminal.ansi.blue", "blue"),
    ("terminal.ansi.magenta", "purple"),
    ("terminal.ansi.cyan", "accent"),
    ("terminal.ansi.white", "muted"),
    # bright_black is the de-facto "dim text" slot (zsh autosuggestions,
    # comments in TUIs). It must be legible on the canvas — see decisions.md.
    ("terminal.ansi.bright_black", "ghost"),
    ("terminal.ansi.bright_red", "red"),
    ("terminal.ansi.bright_green", "green"),
    ("terminal.ansi.bright_yellow", "yellow"),
    ("terminal.ansi.bright_blue", "blue"),
    ("terminal.ansi.bright_magenta", "purple"),
    ("terminal.ansi.bright_cyan", "accent"),
    ("terminal.ansi.bright_white", "text"),
    ("terminal.ansi.dim_black", "disabled"),
    ("terminal.ansi.dim_red", "red"),
    ("terminal.ansi.dim_green", "green"),
    ("terminal.ansi.dim_yellow", "yellow"),
    ("terminal.ansi.dim_blue", "blue"),
    ("terminal.ansi.dim_magenta", "purple"),
    ("terminal.ansi.dim_cyan", "accent"),
    ("terminal.ansi.dim_white", "ghost"),
]

# ---------------------------------------------------------------------------
# 3. Syntax captures — brief §6 (42 entries) plus captures present in Zed's
#    own themes that the brief did not list (marked "extra").
#    (token, font_style, font_weight)
# ---------------------------------------------------------------------------

Style = tuple[str, str | None, int | None]

SYNTAX: dict[str, Style] = {
    "keyword": ("purple", None, None),
    "keyword.import": ("purple", None, None),
    "function": ("blue", None, None),
    "function.method": ("blue", None, None),
    "function.definition": ("blue", None, None),
    "type": ("accent", None, None),
    "constructor": ("accent", None, None),
    "enum": ("accent", None, None),
    "variant": ("orange", None, None),
    "variable": ("text", None, None),
    "variable.special": ("orange", "italic", None),
    "property": ("text", None, None),
    "constant": ("yellow", None, None),
    "string": ("green", None, None),
    "string.escape": ("orange", None, None),
    "string.regex": ("orange", None, None),
    "string.special": ("orange", None, None),
    "string.special.symbol": ("orange", None, None),
    "number": ("yellow", None, None),
    "boolean": ("yellow", None, None),
    "comment": ("muted", "italic", None),
    "comment.doc": ("muted", "italic", None),
    "operator": ("muted", None, None),
    "punctuation": ("muted", None, None),
    "punctuation.bracket": ("muted", None, None),
    "punctuation.delimiter": ("muted", None, None),
    "punctuation.list_marker": ("accent", None, None),
    "punctuation.special": ("orange", None, None),
    "attribute": ("orange", None, None),
    "label": ("orange", None, None),
    "tag": ("purple", None, None),
    "preproc": ("purple", None, None),
    "embedded": ("text", None, None),
    "emphasis": ("accent", "italic", None),
    "emphasis.strong": ("accent", None, 700),
    "title": ("blue", None, 700),
    "link_text": ("blue", "italic", None),
    "link_uri": ("green", None, None),
    "text.literal": ("green", None, None),
    "hint": ("accent", "italic", None),
    "predictive": ("ghost", "italic", None),
    "primary": ("text", None, None),
    # extra — present in Zed's bundled themes, absent from the brief
    "variable.parameter": ("text", None, None),
    "namespace": ("text", None, None),
    "selector": ("purple", None, None),
    "selector.pseudo": ("orange", None, None),
    "punctuation.markup": ("muted", None, None),
    "diff.plus": ("green", None, None),
    "diff.minus": ("red", None, None),
}

# players: slot 0 = accent (local user); 1–7 cycle the remaining signal hues
# then muted (brief §6, "Containers").
PLAYER_SLOTS = ["accent", "blue", "green", "yellow", "orange", "red", "purple", "muted"]


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def resolve(tokens: dict[str, str], value: Value) -> str:
    """Turn a token reference into a hex string. Literals pass through."""
    if isinstance(value, tuple):
        name, alpha = value
        return f"{tokens[name]}{alpha:02X}"
    if value in tokens:
        return tokens[value]
    if value.startswith("#") or value == "opaque":
        return value
    raise KeyError(f"unknown token {value!r}")


def all_keys() -> list[tuple[str, Value]]:
    keys = list(STYLE_KEYS)
    for mode, hue in VIM_MODES:
        keys.append((f"vim.{mode}.background", (hue, A_MARK)))
        keys.append((f"vim.{mode}.foreground", "text"))
    keys += VIM_EXTRA
    for role, fg in STATUS_ROLES:
        keys.append((role, fg))
        keys.append((f"{role}.background", (fg, A_TINT)))
        keys.append((f"{role}.border", (fg, A_LINE)))
    keys += TERMINAL_KEYS
    return keys


def read_keys(path: Path) -> set[str]:
    return set(path.read_text(encoding="utf-8").split())


def build_style(tokens: dict[str, str], allowed: set[str] | None) -> dict:
    style: dict = {}
    for key, value in all_keys():
        if allowed is None or key in allowed:
            style[key] = resolve(tokens, value)

    style["players"] = []
    for i, slot in enumerate(PLAYER_SLOTS):
        hue = resolve(tokens, slot)
        selection = resolve(tokens, "sel") if i == 0 else resolve(tokens, (slot, A_SELECT))
        style["players"].append({"cursor": hue, "background": hue, "selection": selection})

    style["accents"] = [resolve(tokens, t) for t in SIGNAL_ORDER]

    style["syntax"] = {}
    for capture, (token, font_style, font_weight) in SYNTAX.items():
        entry: dict = {"color": resolve(tokens, token)}
        if font_style:
            entry["font_style"] = font_style
        if font_weight:
            entry["font_weight"] = font_weight
        style["syntax"][capture] = entry
    return style


def build_family(strict: bool) -> dict:
    allowed = read_keys(KEYS_V020) if strict else None
    return {
        "$schema": SCHEMA_URL,
        "name": FAMILY_NAME,
        "author": AUTHOR,
        "themes": [
            {"name": name, "appearance": appearance, "style": build_style(TOKENS[name], allowed)}
            for name, appearance in VARIANTS
        ],
    }


def self_check() -> None:
    """The key map must cover the current schema exactly: nothing invented,
    nothing missing. Runs before every build so drift fails loudly."""
    emitted = {k for k, _ in all_keys()} | {"players", "accents", "syntax"}
    current = read_keys(KEYS_CURRENT)
    invented = sorted(emitted - current)
    missing = sorted(current - emitted)
    if invented or missing:
        raise SystemExit(f"key map drift — invented: {invented} missing: {missing}")
    dupes = [k for k in {k for k, _ in all_keys()} if sum(1 for kk, _ in all_keys() if kk == k) > 1]
    if dupes:
        raise SystemExit(f"duplicate keys in key map: {sorted(dupes)}")


def rel(path: Path) -> str:
    """Path relative to the repo root when possible, else absolute."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def dumps(family: dict) -> str:
    return json.dumps(family, indent=2, ensure_ascii=False) + "\n"


def site_with_theme(family: dict) -> str:
    """Return site/index.html with the theme JSON injected into its data block."""
    html = SITE_PATH.read_text(encoding="utf-8")
    start = html.index(SITE_OPEN) + len(SITE_OPEN)
    end = html.index(SITE_CLOSE, start)
    blob = json.dumps(family, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return html[:start] + blob + html[end:]


# ---------------------------------------------------------------------------
# Contrast report (WCAG 2.1 relative luminance, same maths as the validator)
# ---------------------------------------------------------------------------

def _lin(c: int) -> float:
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_: str) -> float:
    h = hex_.lstrip("#")[:6]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def composite(fg_hex8: str, bg_hex6: str) -> str:
    """Flatten a #RRGGBBAA colour onto an opaque background."""
    h = fg_hex8.lstrip("#")
    r, g, b, a = (int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
    br, bg_, bb = (int(bg_hex6.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    t = a / 255
    return "#%02X%02X%02X" % (round(r * t + br * (1 - t)), round(g * t + bg_ * (1 - t)), round(b * t + bb * (1 - t)))


def grade(ratio: float, floor: float) -> str:
    if floor == 3.0:
        return "pass" if ratio >= 3.0 else "FAIL"
    if ratio >= 7.0:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    return "FAIL"


# (label, fg token, bg token, required floor, exempt)
# floor 4.5 = text; 3.0 = non-text UI (WCAG 1.4.11); exempt = brief §5 exceptions.
PAIRS: list[tuple[str, str, str, float, bool]] = [
    ("text on bg", "text", "bg", 4.5, False),
    ("text on surface", "text", "surface", 4.5, False),
    ("text on elevated", "text", "elevated", 4.5, False),
    ("text on hover (border)", "text", "border", 4.5, False),
    ("text on active (border_hi)", "text", "border_hi", 4.5, False),
    ("text on sel (selection)", "text", "sel", 4.5, False),
    ("muted on bg", "muted", "bg", 4.5, False),
    ("muted on surface", "muted", "surface", 4.5, False),
    ("muted on elevated", "muted", "elevated", 4.5, False),
    ("muted on hover (border, transient)", "muted", "border", 3.0, False),
    ("ghost on bg (predictive, placeholders)", "ghost", "bg", 4.5, False),
    ("ghost on surface (placeholders)", "ghost", "surface", 4.5, False),
    ("ghost on elevated (palette input placeholder)", "ghost", "elevated", 4.5, False),
    ("disabled on bg (exempt, 1.4.3)", "disabled", "bg", 4.5, True),
    ("accent on bg", "accent", "bg", 4.5, False),
    ("accent on surface", "accent", "surface", 4.5, False),
    ("blue on bg", "blue", "bg", 4.5, False),
    ("green on bg", "green", "bg", 4.5, False),
    ("yellow on bg", "yellow", "bg", 4.5, False),
    ("orange on bg", "orange", "bg", 4.5, False),
    ("red on bg", "red", "bg", 4.5, False),
    ("purple on bg", "purple", "bg", 4.5, False),
    ("focus ring: accent on bg (non-text)", "accent", "bg", 3.0, False),
    ("focus ring: accent on surface (non-text)", "accent", "surface", 3.0, False),
    ("divider: border on bg (exempt, decoration)", "border", "bg", 3.0, True),
    ("active rail: border_hi on bg (exempt, decoration)", "border_hi", "bg", 3.0, True),
]

# Translucent overlays that carry text: (label, overlay value, under token, text token, floor)
# Zed paints `text` on status tints (ui::TintColor) and uses the hue for icons
# and borders only, so hue-on-tint is a non-text pair with a 3:1 floor.
OVERLAYS: list[tuple[str, Value, str, str, float]] = [
    ("text on active search match", ("accent", A_LINE), "bg", "text", 4.5),
    ("text on document highlight (read)", ("accent", A_MARK), "bg", "text", 4.5),
    ("text on document highlight (write)", ("yellow", A_MARK), "bg", "text", 4.5),
    ("text on highlighted line", ("accent", A_SOFT), "bg", "text", 4.5),
    ("text on debugger line", ("yellow", A_MARK), "bg", "text", 4.5),
    ("text on added diff row", ("green", A_TINT), "bg", "text", 4.5),
    ("text on deleted diff row", ("red", A_TINT), "bg", "text", 4.5),
    ("text on conflict (ours)", ("green", A_SOFT), "bg", "text", 4.5),
    ("text on conflict (theirs)", ("blue", A_SOFT), "bg", "text", 4.5),
    ("text on error tint (diagnostic, button)", ("red", A_TINT), "surface", "text", 4.5),
    ("text on warning tint", ("orange", A_TINT), "surface", "text", 4.5),
    ("text on info tint", ("blue", A_TINT), "surface", "text", 4.5),
    ("text on success tint", ("green", A_TINT), "surface", "text", 4.5),
    ("text on inlay hint chip", ("accent", A_TINT), "bg", "text", 4.5),
    ("error icon on error tint (non-text)", ("red", A_TINT), "surface", "red", 3.0),
    ("warning icon on warning tint (non-text)", ("orange", A_TINT), "surface", "orange", 3.0),
    ("text on vim normal pill", ("accent", A_MARK), "surface", "text", 4.5),
    ("text on vim insert pill", ("green", A_MARK), "surface", "text", 4.5),
    ("text on vim visual pill", ("purple", A_MARK), "surface", "text", 4.5),
]


def report() -> tuple[str, int]:
    failures = 0
    names = [n for n, _ in VARIANTS]
    header = "| Pair | " + " | ".join(names) + " |\n|---|" + "---|" * len(names)
    out = ["# Turbine — contrast report", "",
           "Generated by `python3 build/build_theme.py --report`. WCAG 2.1 relative-luminance maths, "
           "identical to `build/validate_turbine.py`. Text pairs require 4.5:1 (AA); non-text UI "
           "requires 3:1 (1.4.11). Rows marked *exempt* are the brief's two permitted exceptions "
           "(dividers are decoration; disabled text is exempt under 1.4.3). Translucent overlays are "
           "flattened onto their host surface before measuring.", ""]

    out += ["## Token pairs", "", header]
    for label, fg, bg, floor, exempt in PAIRS:
        cells = []
        for name in names:
            t = TOKENS[name]
            r = contrast(t[fg], t[bg])
            g = grade(r, floor)
            if g == "FAIL":
                if exempt:
                    g = "below (exempt)"
                else:
                    failures += 1
            cells.append(f"{r:.2f}:1 {g}")
        out.append(f"| {label} | " + " | ".join(cells) + " |")

    out += ["", "## Text on translucent overlays", "", header]
    for label, overlay, under, fg, floor in OVERLAYS:
        cells = []
        for name in names:
            t = TOKENS[name]
            flat = composite(resolve(t, overlay), t[under])
            r = contrast(t[fg], flat)
            g = grade(r, floor)
            if g == "FAIL":
                failures += 1
            cells.append(f"{r:.2f}:1 {g}")
        out.append(f"| {label} | " + " | ".join(cells) + " |")

    out += ["", "## Syntax captures on `editor.background`", "", header.replace("| Pair |", "| Capture |")]
    for capture, (token, _, _) in SYNTAX.items():
        cells = []
        for name in names:
            t = TOKENS[name]
            r = contrast(t[token], t["bg"])
            g = grade(r, 4.5)
            if g == "FAIL":
                failures += 1
            cells.append(f"{r:.2f}:1 {g}")
        out.append(f"| `{capture}` | " + " | ".join(cells) + " |")

    out += ["", "## Terminal ANSI on `terminal.background`", "", header.replace("| Pair |", "| Slot |")]
    for key, value in TERMINAL_KEYS:
        if not key.startswith("terminal.ansi.") or key.endswith("background") or key.endswith(".black"):
            continue  # ANSI black is a background slot by convention; not a text pair.
        exempt = key.endswith("dim_black")  # the "black" family, kept at `disabled` by design
        cells = []
        for name in names:
            t = TOKENS[name]
            r = contrast(resolve(t, value), t["bg"])
            g = grade(r, 4.5)
            if g == "FAIL":
                if exempt:
                    g = "below (exempt)"
                else:
                    failures += 1
            cells.append(f"{r:.2f}:1 {g}")
        out.append(f"| `{key.removeprefix('terminal.ansi.')}` | " + " | ".join(cells) + " |")

    out += ["", f"**Result:** {'all required pairs clear their floor' if failures == 0 else f'{failures} required pair(s) FAIL'}.", ""]
    out += ["#turbine #zed-theme #accessibility", ""]
    return "\n".join(out), failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="emit only the pinned v0.2.0 keys")
    ap.add_argument("--report", action="store_true", help="write docs/contrast.md and fail on any required pair below floor")
    ap.add_argument("--check", action="store_true", help="verify themes/turbine.json and site/index.html match the generator output")
    ap.add_argument("--site", action="store_true", help="inject the theme JSON into site/index.html")
    ap.add_argument("--out", type=Path, default=THEME_PATH, help="output path (default themes/turbine.json)")
    args = ap.parse_args(argv)

    self_check()

    if args.report:
        text, failures = report()
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(text, encoding="utf-8")
        print(f"wrote {rel(REPORT_PATH)} — {failures} failure(s)")
        return 1 if failures else 0

    family = build_family(args.strict)
    text = dumps(family)

    if args.site:
        SITE_PATH.write_text(site_with_theme(family), encoding="utf-8")
        print(f"wrote theme data into {rel(SITE_PATH)}")
        return 0

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != text:
            print(f"{rel(args.out)} is out of date — run: python3 build/build_theme.py"
                  + (" --strict" if args.strict else ""))
            return 1
        print(f"{rel(args.out)} is up to date")
        if not args.strict and SITE_PATH.exists():
            if SITE_PATH.read_text(encoding="utf-8") != site_with_theme(family):
                print(f"{rel(SITE_PATH)} carries stale theme data — run: python3 build/build_theme.py --site")
                return 1
            print(f"{rel(SITE_PATH)} theme data is up to date")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    n_keys = len(family["themes"][0]["style"])
    print(f"wrote {rel(args.out)} — {len(family['themes'])} variants, {n_keys} style keys each"
          + (" (v0.2.0 strict)" if args.strict else " (current schema)"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
