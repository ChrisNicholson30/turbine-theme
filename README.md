# Turbine

A community-led theme family for [Zed](https://zed.dev). Three variants, one token model, one JSON file.

**Site:** https://chrisnicholson30.github.io/turbine-theme/

| Variant | Appearance | Canvas | Use it for |
|---|---|---|---|
| **Turbine Hypersonic** | dark | `#000000` (OLED black) | Battery-critical work, OLED laptops, low light |
| **Turbine Supersonic** | dark | `#14171A` | Desk default, long sessions, mixed lighting |
| **Turbine Subsonic** | light | `#F7F4EF` (warm cream) | Daylight, glare, light-mode preference |

Every text-bearing pair in every variant clears WCAG AA (4.5:1), including text on selections, diff rows, diagnostic tints and vim mode pills. Most dark-variant pairs clear AAA. The computed table is in [`docs/contrast.md`](docs/contrast.md).

## Showcase site

`site/index.html` is a single-page showcase that re-themes itself live from the theme file: an engine-mode selector for the three regimes, a Zed window mockup painted from `turbine.json`, token gauges with live contrast ratios, the install steps, and a battery-aware nudge toward Hypersonic. It follows the OS colour scheme by default, remembers your choice, and answers to the keys 1, 2 and 3. Christopher's turbine emblem is the site logo and favicon (`site/assets/`).

The `pages` workflow deploys it to https://chrisnicholson30.github.io/turbine-theme/ on every push to `main` that touches the site or theme. It publishes both ways: an Actions deployment (the repository's Pages source) and a `gh-pages` branch, so either Pages setting serves it. To preview locally, open `site/index.html` in a browser; no build step is needed. When the theme changes, `python3 build/build_theme.py --site` re-injects the JSON, and `--check` fails if the site is stale.

## Install

**One command, kept up to date (macOS and Linux):**

```sh
curl -fsSL https://raw.githubusercontent.com/chrisnicholson30/turbine-theme/main/install.sh | bash
```

`install.sh` downloads `themes/turbine.json` into `~/.config/zed/themes/`, which Zed watches, so the theme appears in `theme selector` without a restart. It then keeps a local copy of itself in `~/.local/share/turbine-theme/` and registers a daily `update` with launchd on macOS, a systemd user timer on Linux, or cron as a fallback. The updater downloads only the theme file, validates it, and replaces the installed copy only when it changed.

| Command | Does |
|---|---|
| `turbine.sh update` | Fetch the latest theme now |
| `turbine.sh status` | Show what is installed, the schedule, and the last log lines |
| `turbine.sh uninstall` | Remove the theme, the updater and its schedule |
| `install.sh --no-auto` | Install without the daily updater |
| `install.sh --ref <branch or tag>` | Track something other than `main` (also `TURBINE_REF=…`) |
| `install.sh --variant hypersonic` | Print the `settings.json` snippet for that dark variant |

The script never edits `settings.json`, because Zed's settings allow comments and a blind rewrite could damage them. It prints the snippet to paste instead.

**As a dev extension (for working on the theme):**

1. Clone this repository.
2. In Zed run `zed: install dev extension` and pick the cloned folder.
3. Open `theme selector` and choose a Turbine variant.

**From the extension store:** not yet published. `extension.toml` is ready for submission to [zed-industries/extensions](https://github.com/zed-industries/extensions).

## How the theme is built

Turbine is generated, not hand-written. `themes/turbine.json` is the output of `build/build_theme.py`, which resolves every key in Zed's current theme schema through a four-layer token model. Change a token and all three variants move together.

### The four-layer token model

| Layer | Tokens | Rule |
|---|---|---|
| **Surface** | `bg` → `surface` → `elevated` | Three depths, never more |
| **Content** | `text` → `muted` → `ghost` → `disabled` | Four weights (`ghost` is the legible floor for predictive text and placeholders) |
| **Line** | `border` → `border_hi` → `accent` | Dividers → active rails → focus. The same two neutrals form the hover → active interaction ramp |
| **Signal** | `accent`, `blue`, `green`, `yellow`, `orange`, `red`, `purple` | Seven hues, one semantic job each |

Plus two state tokens: `sel` (selection, search hits, bracket match) and `active_ln` (cursor line). Translucent uses of a hue (diff rows, document highlights, status tints, vim pills) are the same token at a named alpha step, so they stay in sync too.

### Token values

| Token | Hypersonic | Supersonic | Subsonic | Job |
|---|---|---|---|---|
| `bg` | `#000000` | `#14171A` | `#F7F4EF` | Editor canvas, gutter, terminal |
| `surface` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Panels, tab bar, status bar |
| `elevated` | `#16191C` | `#22272C` | `#FFFFFF` | Menus, popovers |
| `text` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Primary content |
| `muted` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Comments, line numbers, punctuation |
| `ghost` | `#7B838A` | `#868F97` | `#636A72` | Predictive text, placeholders, ANSI dim text |
| `disabled` | `#5C646B` | `#646C74` | `#8B939B` | Inert controls, invisibles |
| `border` | `#23282D` | `#2C3238` | `#D9D3CA` | Dividers, hover |
| `border_hi` | `#39424A` | `#414A52` | `#B9B1A6` | Active rails, pressed |
| `accent` | `#4FE3C1` | `#3FD3B4` | `#0C7763` | Identity, focus, types, hints |
| `blue` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | Functions, info, links, titles, renamed |
| `green` | `#7BE38B` | `#6FD47F` | `#17714A` | Strings, created, success, added |
| `yellow` | `#F2C94C` | `#E6BA45` | `#8A5A00` | Numbers, constants, modified, debugger line |
| `orange` | `#FFB067` | `#F0A05E` | `#B4470F` | Attributes, warning, conflict |
| `red` | `#FF7B72` | `#F2736B` | `#C0342B` | Errors, deleted, breakpoints |
| `purple` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | Keywords, tags, macros, visual mode |
| `sel` | `#123A38` | `#1D3B39` | `#CFE8E1` | Selection, search hit |
| `active_ln` | `#0B0E10` | `#1A1E22` | `#EFECE6` | Cursor line |

Two values differ from the design brief on purpose (`ghost` is new; Subsonic `accent` is two steps darker). Every departure from the brief is explained in [`docs/decisions.md`](docs/decisions.md).

## Power model

- **Hypersonic** is a genuine OLED battery saver. A black pixel is an unlit pixel, so the canvas, gutter, toolbar and terminal are all `#000000`. Chrome surfaces are near-neutral greys rather than navy, and the accent is a green-dominant teal rather than blue, because blue subpixels are the least efficient per nit.
- **Supersonic** gives real but modest OLED savings, tuned for multi-hour comfort.
- **Subsonic** is not a battery saver. On LCD it is power-neutral; on OLED it is the most expensive of the three. Its justification is daylight legibility and glare tolerance.

## Build and validate

No dependencies beyond Python 3.10+.

```sh
python3 build/build_theme.py            # regenerate themes/turbine.json (current schema, 189 keys)
python3 build/build_theme.py --site     # inject the theme JSON into the showcase site
python3 build/build_theme.py --check    # confirm the committed JSON and site match the token source
python3 build/build_theme.py --report   # write docs/contrast.md, fail on any AA miss
python3 build/validate_turbine.py themes/turbine.json build/schema_keys.txt
```

The last command is the schema and contrast gate from the brief. It checks that every style key is real, that no key is left unset, and that the core text pairs and every syntax capture clear 4.5:1. Expected output ends with `PASS — ready to ship`. The generator also refuses to run if its key map drifts from `build/schema_keys.txt`. CI runs all of this on every push.

### Which schema

Two key lists live in `build/`:

| File | Keys | Source |
|---|---|---|
| `schema_keys.txt` | 189 | Zed's `ThemeStyleContent` on the main branch, extracted from `crates/settings_content/src/theme.rs` (September 2026). Excludes the deprecated `scrollbar_thumb.background` alias. |
| `schema_keys_v0.2.0.txt` | 142 | The published v0.2.0 schema, as pinned by the brief. |

The shipped file targets the current schema, so git gutter marks, diff rows, minimap, vim mode pills and the active search match are all on-palette. Zed ignores unknown keys, so the same file loads on older builds with those features at Zed's defaults. To produce and check a v0.2.0-only file:

```sh
python3 build/build_theme.py --strict --out /tmp/turbine-v0.2.0.json
python3 build/validate_turbine.py /tmp/turbine-v0.2.0.json build/schema_keys_v0.2.0.txt
```

Note that running the validator on the shipped file with the v0.2.0 list will list the 47 newer keys as unknown. That is the list being stale, not the theme.

## Repository layout

```
turbine-theme/
  extension.toml                Zed extension manifest
  install.sh                    installer and daily updater for Zed's user themes folder
  themes/turbine.json           the theme family (generated, committed)
  build/build_theme.py          token model, key map, generator, contrast report
  build/validate_turbine.py     schema + WCAG validator from the brief
  build/schema_keys.txt         current Zed schema key list
  build/schema_keys_v0.2.0.txt  pinned v0.2.0 key list
  site/index.html               showcase site (GitHub Pages), themed live from the JSON
  site/assets/                  logo and favicons
  docs/design-brief-v2.md       the build-ready design brief
  docs/decisions.md             where the build departs from the brief, and why
  docs/contrast.md              generated contrast report
```

## Licence

MIT. See [`LICENSE`](LICENSE).

#turbine #zed-theme #design-system
