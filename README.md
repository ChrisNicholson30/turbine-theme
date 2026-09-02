# Turbine

A community-led theme family for [Zed](https://zed.dev). Three variants, one token model, one JSON file.

| Variant | Appearance | Canvas | Use it for |
|---|---|---|---|
| **Turbine Hypersonic** | dark | `#000000` (OLED black) | Battery-critical work, OLED laptops, low light |
| **Turbine Supersonic** | dark | `#14171A` | Desk default, long sessions, mixed lighting |
| **Turbine Subsonic** | light | `#F7F4EF` (warm cream) | Daylight, glare, light-mode preference |

Every text-bearing pair in every variant clears WCAG AA (4.5:1). Most dark-variant pairs clear AAA. See [`docs/contrast.md`](docs/contrast.md) for the computed table.

## Install

**As a dev extension (now):**

1. Clone this repository.
2. In Zed run `zed: install dev extension` and pick the cloned folder.
3. Open `theme selector` and choose a Turbine variant.

**From the extension store:** not yet published. `extension.toml` is ready for submission to [zed-industries/extensions](https://github.com/zed-industries/extensions).

## How the theme is built

Turbine is generated, not hand-written. `themes/turbine.json` is the output of `build/build_theme.py`, which resolves every schema key through a four-layer token model. Change a token and all three variants move together.

### The four-layer token model

| Layer | Tokens | Rule |
|---|---|---|
| **Surface** | `bg` → `surface` → `elevated` | Three depths, never more |
| **Content** | `text` → `muted` → `ghost` → `disabled` | Four weights (`ghost` is the legible floor for predictive text) |
| **Line** | `border` → `border_hi` → `accent` | Dividers → active rails → focus |
| **Signal** | `accent`, `blue`, `green`, `yellow`, `orange`, `red`, `purple` | Seven hues, one semantic job each |

Plus two state tokens: `sel` (selection, search hits, document highlights) and `active_ln` (cursor line).

### Token values

| Token | Hypersonic | Supersonic | Subsonic | Job |
|---|---|---|---|---|
| `bg` | `#000000` | `#14171A` | `#F7F4EF` | Editor canvas, gutter, terminal |
| `surface` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Panels, tab bar, status bar |
| `elevated` | `#16191C` | `#22272C` | `#FFFFFF` | Menus, popovers, hover |
| `text` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Primary content |
| `muted` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Comments, line numbers, punctuation |
| `ghost` | `#6F777E` | `#79828A` | `#686F77` | Predictive / ghost text |
| `disabled` | `#5C646B` | `#646C74` | `#8B939B` | Inert controls, invisibles |
| `border` | `#23282D` | `#2C3238` | `#D9D3CA` | Dividers |
| `border_hi` | `#39424A` | `#414A52` | `#B9B1A6` | Active rails |
| `accent` | `#4FE3C1` | `#3FD3B4` | `#0C7763` | Identity, focus, types, hints |
| `blue` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | Functions, info, links, titles |
| `green` | `#7BE38B` | `#6FD47F` | `#17714A` | Strings, created, success |
| `yellow` | `#F2C94C` | `#E6BA45` | `#8A5A00` | Numbers, constants, modified |
| `orange` | `#FFB067` | `#F0A05E` | `#B4470F` | Attributes, warning, conflict |
| `red` | `#FF7B72` | `#F2736B` | `#C0342B` | Errors, deleted |
| `purple` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | Keywords, tags, macros |
| `sel` | `#123A38` | `#1D3B39` | `#CFE8E1` | Selection, search hit |
| `active_ln` | `#0B0E10` | `#1A1E22` | `#EFECE6` | Cursor line |

Two values differ from the design brief on purpose (`ghost` is new; Subsonic `accent` is two steps darker). Both are explained in [`docs/decisions.md`](docs/decisions.md).

## Power model

- **Hypersonic** is a genuine OLED battery saver. A black pixel is an unlit pixel, so the canvas, gutter, toolbar and terminal are all `#000000`. Chrome surfaces are near-neutral greys rather than navy, and the accent is a green-dominant teal rather than blue, because blue subpixels are the least efficient per nit.
- **Supersonic** gives real but modest OLED savings, tuned for multi-hour comfort.
- **Subsonic** is not a battery saver. On LCD it is power-neutral; on OLED it is the most expensive of the three. Its justification is daylight legibility and glare tolerance.

## Build and validate

No dependencies beyond Python 3.10+.

```sh
python3 build/build_theme.py            # regenerate themes/turbine.json (v0.2.0 keys)
python3 build/build_theme.py --check    # confirm the committed JSON matches the token source
python3 build/build_theme.py --report   # write docs/contrast.md, fail on any AA miss
python3 build/validate_turbine.py themes/turbine.json build/schema_keys.txt
```

The last command is the schema and contrast gate from the brief. It checks that every style key is a real v0.2.0 key, that no key is left unset, and that the core text pairs and every syntax capture clear 4.5:1. Expected output ends with `PASS — ready to ship`. CI runs all four commands on every push.

### Newer Zed keys

Zed's current theme schema carries keys that v0.2.0 does not, such as `version_control.*` and `search.active_match_background`. The shipped file targets v0.2.0 so it validates against the pinned key list. To emit the nine newer keys whose names are verified against Zed's own bundled themes:

```sh
python3 build/build_theme.py --extended
python3 build/validate_turbine.py themes/turbine.json build/schema_keys_extended.txt
```

## Repository layout

```
turbine-theme/
  extension.toml              Zed extension manifest
  themes/turbine.json         the theme family (generated, committed)
  build/build_theme.py        token model and generator
  build/validate_turbine.py   schema + WCAG validator from the brief
  build/schema_keys.txt       pinned v0.2.0 key list
  build/schema_keys_extended.txt  v0.2.0 list plus verified newer keys
  docs/design-brief-v2.md     the build-ready design brief
  docs/decisions.md           where the build departs from the brief, and why
  docs/contrast.md            generated contrast report
```

## Licence

MIT. See [`LICENSE`](LICENSE).

#turbine #zed-theme #design-system
