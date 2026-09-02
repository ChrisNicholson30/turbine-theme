#!/usr/bin/env python3
"""Turbine — token-driven generator for the Zed theme family.

Every colour in the emitted JSON is a reference to one of the tokens in
TOKENS below. No key is hand-picked; change a token and all three variants
move together (brief §2, "the four-layer token model").

Usage:
    python3 build/build_theme.py                 # write themes/turbine.json (v0.2.0 keys only)
    python3 build/build_theme.py --extended      # also emit keys verified in newer Zed builds
    python3 build/build_theme.py --report        # write docs/contrast.md and gate on WCAG AA
    python3 build/build_theme.py --check         # build to memory, diff against themes/turbine.json

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

SCHEMA_URL = "https://zed.dev/schema/themes/v0.2.0.json"
FAMILY_NAME = "Turbine"
AUTHOR = "Christopher Nicholson"

# ---------------------------------------------------------------------------
# 1. Tokens — brief §3, plus one addition (`ghost`, see docs/decisions.md)
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
        "ghost": "#6F777E",
        "disabled": "#5C646B",
        # Line layer
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
        "ghost": "#79828A",
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
        "ghost": "#686F77",
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

# ---------------------------------------------------------------------------
# 2. Key map — brief §6. Every key exists in build/schema_keys.txt (v0.2.0).
#    Values are token names, or a (token, alpha) pair, or a literal string
#    when the schema value is not a colour.
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
    ("text.placeholder", "disabled"),
    ("text.disabled", "disabled"),
    ("text.accent", "accent"),
    ("icon", "text"),
    ("icon.muted", "muted"),
    ("icon.placeholder", "disabled"),
    ("icon.disabled", "disabled"),
    ("icon.accent", "accent"),
    ("link_text.hover", "accent"),
    # Interactive elements
    ("element.background", "surface"),
    ("element.hover", "elevated"),
    ("element.active", "border"),
    ("element.selected", "sel"),
    ("element.disabled", "surface"),
    ("ghost_element.background", TRANSPARENT),
    ("ghost_element.hover", "surface"),
    ("ghost_element.active", "elevated"),
    ("ghost_element.selected", "sel"),
    ("ghost_element.disabled", TRANSPARENT),
    ("drop_target.background", "sel"),
    # Workspace chrome
    ("title_bar.background", "surface"),
    ("title_bar.inactive_background", "bg"),
    ("status_bar.background", "surface"),
    ("toolbar.background", "bg"),
    ("tab_bar.background", "surface"),
    ("tab.active_background", "bg"),
    ("tab.inactive_background", "surface"),
    ("panel.background", "surface"),
    ("panel.focused_border", "accent"),
    ("panel.indent_guide", "border"),
    ("panel.indent_guide_active", "border_hi"),
    ("panel.indent_guide_hover", "border_hi"),
    ("pane.focused_border", "accent"),
    ("pane_group.border", "border"),
    ("scrollbar.thumb.background", "border"),
    ("scrollbar.thumb.hover_background", "border_hi"),
    ("scrollbar.thumb.border", TRANSPARENT),
    ("scrollbar.track.background", TRANSPARENT),
    ("scrollbar.track.border", TRANSPARENT),
    ("search.match_background", "sel"),
    # Editor surface
    ("editor.foreground", "text"),
    ("editor.background", "bg"),
    ("editor.gutter.background", "bg"),
    ("editor.subheader.background", "surface"),
    ("editor.active_line.background", "active_ln"),
    ("editor.highlighted_line.background", "active_ln"),
    ("editor.line_number", "muted"),
    ("editor.active_line_number", "text"),
    ("editor.invisible", "disabled"),
    ("editor.wrap_guide", "border"),
    ("editor.active_wrap_guide", "border_hi"),
    ("editor.indent_guide", "border"),
    ("editor.indent_guide_active", "border_hi"),
    ("editor.document_highlight.read_background", "sel"),
    ("editor.document_highlight.write_background", "sel"),
    ("editor.document_highlight.bracket_background", "sel"),
]

# Status roles: (key, foreground token). Each expands to key, key.background,
# key.border with the surface / border tokens (brief §6, "Status Roles").
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

# Keys that exist in current Zed but not in the v0.2.0 schema. Names verified
# against zed-industries/zed assets/themes/one/one.json (main branch). Only
# emitted with --extended, because build/validate_turbine.py checks against
# the pinned v0.2.0 list and would flag these as unknown.
EXTENDED_KEYS: list[tuple[str, Value]] = [
    ("editor.hover_line_number", "text"),
    ("search.active_match_background", ("accent", 0x66)),
    ("version_control.added", "green"),
    ("version_control.deleted", "red"),
    ("version_control.modified", "yellow"),
    ("version_control.word_added", ("green", 0x33)),
    ("version_control.word_deleted", ("red", 0x33)),
    ("version_control.conflict_marker.ours", ("green", 0x40)),
    ("version_control.conflict_marker.theirs", ("blue", 0x40)),
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
REMOTE_SELECTION_ALPHA = 0x3D  # ~24 %, matches Zed's bundled themes


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


def build_style(tokens: dict[str, str], extended: bool) -> dict:
    style: dict = {}
    for key, value in STYLE_KEYS:
        style[key] = resolve(tokens, value)
    for role, fg in STATUS_ROLES:
        style[role] = resolve(tokens, fg)
        style[f"{role}.background"] = resolve(tokens, "surface")
        style[f"{role}.border"] = resolve(tokens, "border")
    for key, value in TERMINAL_KEYS:
        style[key] = resolve(tokens, value)
    if extended:
        for key, value in EXTENDED_KEYS:
            style[key] = resolve(tokens, value)

    style["players"] = []
    for i, slot in enumerate(PLAYER_SLOTS):
        hue = resolve(tokens, slot)
        selection = resolve(tokens, "sel") if i == 0 else resolve(tokens, (slot, REMOTE_SELECTION_ALPHA))
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


def build_family(extended: bool) -> dict:
    return {
        "$schema": SCHEMA_URL,
        "name": FAMILY_NAME,
        "author": AUTHOR,
        "themes": [
            {"name": name, "appearance": appearance, "style": build_style(TOKENS[name], extended)}
            for name, appearance in VARIANTS
        ],
    }


def rel(path: Path) -> str:
    """Path relative to the repo root when possible, else absolute."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def dumps(family: dict) -> str:
    return json.dumps(family, indent=2, ensure_ascii=False) + "\n"


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
    ("text on sel (selection)", "text", "sel", 4.5, False),
    ("muted on bg", "muted", "bg", 4.5, False),
    ("muted on surface", "muted", "surface", 4.5, False),
    ("muted on elevated", "muted", "elevated", 4.5, False),
    ("ghost on bg (predictive)", "ghost", "bg", 4.5, False),
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


def report() -> tuple[str, int]:
    failures = 0
    out = ["# Turbine — contrast report", "",
           "Generated by `python3 build/build_theme.py --report`. WCAG 2.1 relative-luminance maths, "
           "identical to `build/validate_turbine.py`. Text pairs require 4.5:1 (AA); non-text UI "
           "requires 3:1 (1.4.11). Rows marked *exempt* are the brief's two permitted exceptions "
           "(dividers are decoration; disabled text is exempt under 1.4.3).", ""]

    out += ["## Token pairs", "", "| Pair | " + " | ".join(n for n, _ in VARIANTS) + " |",
            "|---|" + "---|" * len(VARIANTS)]
    for label, fg, bg, floor, exempt in PAIRS:
        cells = []
        for name, _ in VARIANTS:
            t = TOKENS[name]
            r = contrast(t[fg], t[bg])
            g = grade(r, floor)
            if g == "FAIL" and not exempt:
                failures += 1
            if exempt and g == "FAIL":
                g = "below (exempt)"
            cells.append(f"{r:.2f}:1 {g}")
        out.append(f"| {label} | " + " | ".join(cells) + " |")

    out += ["", "## Syntax captures on `editor.background`", "",
            "| Capture | " + " | ".join(n for n, _ in VARIANTS) + " |", "|---|" + "---|" * len(VARIANTS)]
    for capture, (token, _, _) in SYNTAX.items():
        cells = []
        for name, _ in VARIANTS:
            t = TOKENS[name]
            r = contrast(t[token], t["bg"])
            g = grade(r, 4.5)
            if g == "FAIL":
                failures += 1
            cells.append(f"{r:.2f}:1 {g}")
        out.append(f"| `{capture}` | " + " | ".join(cells) + " |")

    out += ["", "## Terminal ANSI on `terminal.background`", "",
            "| Slot | " + " | ".join(n for n, _ in VARIANTS) + " |", "|---|" + "---|" * len(VARIANTS)]
    for key, value in TERMINAL_KEYS:
        if not key.startswith("terminal.ansi.") or key.endswith("background"):
            continue
        if key.endswith(".black"):
            # ANSI black is a background slot by convention; not a text pair.
            continue
        exempt = key.endswith("dim_black")  # the "black" family, kept at `disabled` by design
        cells = []
        for name, _ in VARIANTS:
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
    ap.add_argument("--extended", action="store_true", help="emit keys verified in newer Zed builds (not in v0.2.0)")
    ap.add_argument("--report", action="store_true", help="write docs/contrast.md and fail on any required pair below floor")
    ap.add_argument("--check", action="store_true", help="verify themes/turbine.json matches the generator output")
    ap.add_argument("--out", type=Path, default=THEME_PATH, help="output path (default themes/turbine.json)")
    args = ap.parse_args(argv)

    if args.report:
        text, failures = report()
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(text, encoding="utf-8")
        print(f"wrote {rel(REPORT_PATH)} — {failures} failure(s)")
        return 1 if failures else 0

    family = build_family(args.extended)
    text = dumps(family)

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != text:
            print(f"{rel(args.out)} is out of date — run: python3 build/build_theme.py"
                  + (" --extended" if args.extended else ""))
            return 1
        print(f"{rel(args.out)} is up to date")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    n_keys = len(family["themes"][0]["style"])
    print(f"wrote {rel(args.out)} — {len(family['themes'])} variants, {n_keys} style keys each"
          + (" (extended)" if args.extended else " (v0.2.0 strict)"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
