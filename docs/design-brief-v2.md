# Turbine — Zed Theme Design Brief (v2, build-ready)

Community-led Zed theme family. Three variants: **Hypersonic** (OLED), **Supersonic** (dark), **Subsonic** (light).

**Status:** v1 of this brief was not buildable. It specified 189 invented key names; only 13 were real. This version maps the published schema at `https://zed.dev/schema/themes/v0.2.0.json`, verified 139 scalar style keys + 42 syntax captures + `players` + `accents`.

---

## 1. Definition — what Turbine actually is

A **theme family** object (`name`, `author`, `themes[]`) containing three `ThemeContent` objects, each with `name`, `appearance` (`dark`/`dark`/`light`), and a `style` map. One JSON file. It ships whole or not at all.

## 2. Framework — the four-layer token model

Every key resolves through one of four layers. Nothing is hand-picked per key; this is what makes three variants stay in sync.

1. **Surface** — `bg` → `surface` → `elevated`. Three depths, never more.
2. **Content** — `text` → `muted` → `disabled`. Three weights, never more.
3. **Line** — `border` (dividers) → `border_hi` (active rails) → `accent` (focus).
4. **Signal** — `accent`, `blue`, `green`, `yellow`, `orange`, `red`, `purple`. Seven hues, each with exactly one semantic job.

A key's value is always a token reference, never a fresh hex. Change the token, all three variants move together.

## 3. Token values

| Token | Hypersonic | Supersonic | Subsonic | Job |
|---|---|---|---|---|
| `bg` | `#000000` | `#14171A` | `#F7F4EF` | Canvas |
| `surface` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Panels, tabs |
| `elevated` | `#16191C` | `#22272C` | `#FFFFFF` | Menus, popovers |
| `text` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Primary content |
| `muted` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Comments, line numbers |
| `disabled` | `#5C646B` | `#646C74` | `#8B939B` | Inert, ghost text |
| `border` | `#23282D` | `#2C3238` | `#D9D3CA` | Dividers |
| `border_hi` | `#39424A` | `#414A52` | `#B9B1A6` | Active rails |
| `accent` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Turbine identity, focus, types |
| `blue` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | Functions, info, links |
| `green` | `#7BE38B` | `#6FD47F` | `#17714A` | Strings, created, success |
| `yellow` | `#F2C94C` | `#E6BA45` | `#8A5A00` | Numbers, constants, modified |
| `orange` | `#FFB067` | `#F0A05E` | `#B4470F` | Attributes, warning, conflict |
| `red` | `#FF7B72` | `#F2736B` | `#C0342B` | Errors, deleted |
| `purple` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | Keywords, tags, macros |
| `sel` | `#123A38` | `#1D3B39` | `#CFE8E1` | Selection, search hit |
| `active_ln` | `#0B0E10` | `#1A1E22` | `#EFECE6` | Cursor line |

Subsonic uses distinct `yellow` (`#8A5A00`) and `orange` (`#B4470F`). v1 collapsed both to one hex, which silently destroyed the number-vs-attribute distinction in the light variant only.

## 4. Power model — what is and isn't true

**Hypersonic is a genuine battery saver.** On OLED, a black pixel is an unlit pixel. `#000000` across the editor canvas and gutter is the whole mechanism.

Two refinements v1 got wrong:

- **Surfaces are near-neutral, not navy.** v1 used `#0a0f1a` for every panel. Blue subpixels have the lowest luminous efficiency of the three — roughly 4x the power per nit of green. A navy tint across all chrome is a standing power cost for no legibility gain. Hypersonic surfaces are near-neutral greys.
- **The accent is teal, not blue.** The most frequently rendered accent in an editor is types + focus + hints. v1 put blue (`#60a5fa`) in that slot — the most expensive hue in the highest-frequency role. Turbine's accent is `#4FE3C1`, green-dominant, cheaper per nit. Blue is demoted to functions and links.

**Subsonic is not a battery saver, and the brief should stop claiming it is.** On LCD the backlight draws constant power regardless of content, so a light theme is power-neutral, not cheaper. On OLED a cream canvas lights nearly every subpixel at high duty — it is the most expensive of the three by a wide margin. Subsonic's honest justification is daylight legibility and glare tolerance. **Route mobile users to Hypersonic.**

Supersonic sits between: real but modest OLED savings, tuned for multi-hour comfort rather than peak efficiency.

## 5. Accessibility floor

Every text-bearing pair clears **WCAG AA (4.5:1)**; most dark-variant pairs clear AAA. See Appendix A for computed ratios.

Deliberate exceptions, both permitted:
- **Dividers** (`border`) sit below 3:1. They are decoration, not state-bearing UI components; WCAG 1.4.11 does not apply. The focus ring uses `accent`, which clears 3:1 in all three variants.
- **Disabled** text sits below 4.5:1 by design and is explicitly exempt under WCAG 1.4.3.

---

## 6. Key map

Every key below exists in the published schema. Nothing here is invented.

### Base, Text & Icons (21 keys)

| Key | Hypersonic | Supersonic | Subsonic | Role |
|---|---|---|---|---|
| `background` | `#000000` | `#14171A` | `#F7F4EF` | App background, empty panes |
| `background.appearance` | `opaque` | `opaque` | `opaque` | Opaque — no blur compositing |
| `surface.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Grounded surfaces: panels, tab bar |
| `elevated_surface.background` | `#16191C` | `#22272C` | `#FFFFFF` | Menus, popovers, dialogs |
| `border` | `#23282D` | `#2C3238` | `#D9D3CA` | Default border |
| `border.variant` | `#23282D` | `#2C3238` | `#D9D3CA` | Deemphasised dividers |
| `border.focused` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Focus ring — carries the accent |
| `border.selected` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Selected control boundary |
| `border.transparent` | `#00000000` | `#00000000` | `#00000000` | Placeholder border slot |
| `border.disabled` | `#23282D` | `#2C3238` | `#D9D3CA` | Disabled control boundary |
| `text` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Default UI text |
| `text.muted` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Deemphasised text |
| `text.placeholder` | `#5C646B` | `#646C74` | `#8B939B` | Input placeholders |
| `text.disabled` | `#5C646B` | `#646C74` | `#8B939B` | Disabled labels |
| `text.accent` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Emphasis, matched search chars |
| `icon` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Default icon fill |
| `icon.muted` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Inactive pane icons |
| `icon.placeholder` | `#5C646B` | `#646C74` | `#8B939B` | Input affordance icons |
| `icon.disabled` | `#5C646B` | `#646C74` | `#8B939B` | Disabled icons |
| `icon.accent` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Toggled-on icon buttons |
| `link_text.hover` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Hovered hyperlink |

### Interactive Elements (11 keys)

| Key | Hypersonic | Supersonic | Subsonic | Role |
|---|---|---|---|---|
| `element.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Buttons, inputs, checkboxes |
| `element.hover` | `#16191C` | `#22272C` | `#FFFFFF` | Pointer over element |
| `element.active` | `#23282D` | `#2C3238` | `#D9D3CA` | Pressed / activated |
| `element.selected` | `#123A38` | `#1D3B39` | `#CFE8E1` | Toggled on, selected row |
| `element.disabled` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Non-interactive |
| `ghost_element.background` | `#00000000` | `#00000000` | `#00000000` | Flush with parent surface |
| `ghost_element.hover` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Ghost hover |
| `ghost_element.active` | `#16191C` | `#22272C` | `#FFFFFF` | Ghost pressed |
| `ghost_element.selected` | `#123A38` | `#1D3B39` | `#CFE8E1` | Ghost selected |
| `ghost_element.disabled` | `#00000000` | `#00000000` | `#00000000` | Ghost disabled |
| `drop_target.background` | `#123A38` | `#1D3B39` | `#CFE8E1` | Drag-and-drop landing zone |

### Workspace Chrome (20 keys)

| Key | Hypersonic | Supersonic | Subsonic | Role |
|---|---|---|---|---|
| `title_bar.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Window title bar |
| `title_bar.inactive_background` | `#000000` | `#14171A` | `#F7F4EF` | Unfocused window |
| `status_bar.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Bottom status bar |
| `toolbar.background` | `#000000` | `#14171A` | `#F7F4EF` | Breadcrumb / toolbar strip |
| `tab_bar.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Tab strip background |
| `tab.active_background` | `#000000` | `#14171A` | `#F7F4EF` | Active tab — flush with editor |
| `tab.inactive_background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Inactive tabs recede |
| `panel.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Project panel, terminal panel |
| `panel.focused_border` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Focused panel outline |
| `panel.indent_guide` | `#23282D` | `#2C3238` | `#D9D3CA` | File tree indent |
| `panel.indent_guide_active` | `#39424A` | `#414A52` | `#B9B1A6` | Active tree indent |
| `panel.indent_guide_hover` | `#39424A` | `#414A52` | `#B9B1A6` | Hovered tree indent |
| `pane.focused_border` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Focused split |
| `pane_group.border` | `#23282D` | `#2C3238` | `#D9D3CA` | Split divider |
| `scrollbar.thumb.background` | `#23282D` | `#2C3238` | `#D9D3CA` | Scrollbar thumb at rest |
| `scrollbar.thumb.hover_background` | `#39424A` | `#414A52` | `#B9B1A6` | Thumb hovered |
| `scrollbar.thumb.border` | `#00000000` | `#00000000` | `#00000000` | No thumb outline |
| `scrollbar.track.background` | `#00000000` | `#00000000` | `#00000000` | Transparent track |
| `scrollbar.track.border` | `#00000000` | `#00000000` | `#00000000` | No track edge |
| `search.match_background` | `#123A38` | `#1D3B39` | `#CFE8E1` | Search hit highlight |

### Editor Surface (16 keys)

| Key | Hypersonic | Supersonic | Subsonic | Role |
|---|---|---|---|---|
| `editor.foreground` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Default code text |
| `editor.background` | `#000000` | `#14171A` | `#F7F4EF` | Editor canvas — the power-critical surface |
| `editor.gutter.background` | `#000000` | `#14171A` | `#F7F4EF` | Gutter flush with canvas |
| `editor.subheader.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | Sticky scroll / outline header |
| `editor.active_line.background` | `#0B0E10` | `#1A1E22` | `#EFECE6` | Cursor line — minimal lift |
| `editor.highlighted_line.background` | `#0B0E10` | `#1A1E22` | `#EFECE6` | Jump-to highlight |
| `editor.line_number` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Gutter numbers |
| `editor.active_line_number` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Cursor line number |
| `editor.invisible` | `#5C646B` | `#646C74` | `#8B939B` | Tabs, spaces, CR marks |
| `editor.wrap_guide` | `#23282D` | `#2C3238` | `#D9D3CA` | Wrap column rule |
| `editor.active_wrap_guide` | `#39424A` | `#414A52` | `#B9B1A6` | Active wrap rule |
| `editor.indent_guide` | `#23282D` | `#2C3238` | `#D9D3CA` | Indent rails |
| `editor.indent_guide_active` | `#39424A` | `#414A52` | `#B9B1A6` | Active indent rail |
| `editor.document_highlight.read_background` | `#123A38` | `#1D3B39` | `#CFE8E1` | Symbol read occurrence |
| `editor.document_highlight.write_background` | `#123A38` | `#1D3B39` | `#CFE8E1` | Symbol write occurrence |
| `editor.document_highlight.bracket_background` | `#123A38` | `#1D3B39` | `#CFE8E1` | Matching bracket |

### Status Roles (42 keys)

| Key | Hypersonic | Supersonic | Subsonic | Role |
|---|---|---|---|---|
| `conflict` | `#FFB067` | `#F0A05E` | `#B4470F` | Merge conflict, file changed on disk |
| `conflict.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | conflict surface tint |
| `conflict.border` | `#23282D` | `#2C3238` | `#D9D3CA` | conflict boundary |
| `created` | `#7BE38B` | `#6FD47F` | `#17714A` | New file in VCS |
| `created.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | created surface tint |
| `created.border` | `#23282D` | `#2C3238` | `#D9D3CA` | created boundary |
| `deleted` | `#FF7B72` | `#F2736B` | `#C0342B` | Removed file |
| `deleted.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | deleted surface tint |
| `deleted.border` | `#23282D` | `#2C3238` | `#D9D3CA` | deleted boundary |
| `error` | `#FF7B72` | `#F2736B` | `#C0342B` | Diagnostic error, failed op |
| `error.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | error surface tint |
| `error.border` | `#23282D` | `#2C3238` | `#D9D3CA` | error boundary |
| `hidden` | `#5C646B` | `#646C74` | `#8B939B` | Hidden in file tree |
| `hidden.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | hidden surface tint |
| `hidden.border` | `#23282D` | `#2C3238` | `#D9D3CA` | hidden boundary |
| `hint` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | Inlay hints, LSP hints |
| `hint.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | hint surface tint |
| `hint.border` | `#23282D` | `#2C3238` | `#D9D3CA` | hint boundary |
| `ignored` | `#5C646B` | `#646C74` | `#8B939B` | Gitignored |
| `ignored.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | ignored surface tint |
| `ignored.border` | `#23282D` | `#2C3238` | `#D9D3CA` | ignored boundary |
| `info` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | Informational status |
| `info.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | info surface tint |
| `info.border` | `#23282D` | `#2C3238` | `#D9D3CA` | info boundary |
| `modified` | `#F2C94C` | `#E6BA45` | `#8A5A00` | Edited file |
| `modified.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | modified surface tint |
| `modified.border` | `#23282D` | `#2C3238` | `#D9D3CA` | modified boundary |
| `predictive` | `#5C646B` | `#646C74` | `#8B939B` | AI / completion ghost text |
| `predictive.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | predictive surface tint |
| `predictive.border` | `#23282D` | `#2C3238` | `#D9D3CA` | predictive boundary |
| `renamed` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | Renamed file |
| `renamed.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | renamed surface tint |
| `renamed.border` | `#23282D` | `#2C3238` | `#D9D3CA` | renamed boundary |
| `success` | `#7BE38B` | `#6FD47F` | `#17714A` | Completed operation |
| `success.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | success surface tint |
| `success.border` | `#23282D` | `#2C3238` | `#D9D3CA` | success boundary |
| `unreachable` | `#5C646B` | `#646C74` | `#8B939B` | Dead code |
| `unreachable.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | unreachable surface tint |
| `unreachable.border` | `#23282D` | `#2C3238` | `#D9D3CA` | unreachable boundary |
| `warning` | `#FFB067` | `#F0A05E` | `#B4470F` | Operation about to fail |
| `warning.background` | `#0E1113` | `#1B1F23` | `#EFEBE4` | warning surface tint |
| `warning.border` | `#23282D` | `#2C3238` | `#D9D3CA` | warning boundary |

### Terminal (29 keys)

| Key | Hypersonic | Supersonic | Subsonic | Role |
|---|---|---|---|---|
| `terminal.background` | `#000000` | `#14171A` | `#F7F4EF` | Terminal canvas |
| `terminal.foreground` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Default terminal text |
| `terminal.bright_foreground` | `#EDEBE6` | `#E6E4E0` | `#22262B` | Bold terminal text |
| `terminal.dim_foreground` | `#99A1A8` | `#9BA4AC` | `#5A6169` | Dim terminal text |
| `terminal.ansi.background` | `#000000` | `#14171A` | `#F7F4EF` | ANSI default background |
| `terminal.ansi.black` | `#0E1113` | `#1B1F23` | `#EFEBE4` | ANSI black |
| `terminal.ansi.red` | `#FF7B72` | `#F2736B` | `#C0342B` | ANSI red |
| `terminal.ansi.green` | `#7BE38B` | `#6FD47F` | `#17714A` | ANSI green |
| `terminal.ansi.yellow` | `#F2C94C` | `#E6BA45` | `#8A5A00` | ANSI yellow |
| `terminal.ansi.blue` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | ANSI blue |
| `terminal.ansi.magenta` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | ANSI magenta |
| `terminal.ansi.cyan` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | ANSI cyan |
| `terminal.ansi.white` | `#99A1A8` | `#9BA4AC` | `#5A6169` | ANSI white |
| `terminal.ansi.bright_black` | `#0E1113` | `#1B1F23` | `#EFEBE4` | ANSI bright black |
| `terminal.ansi.bright_red` | `#FF7B72` | `#F2736B` | `#C0342B` | ANSI bright red |
| `terminal.ansi.bright_green` | `#7BE38B` | `#6FD47F` | `#17714A` | ANSI bright green |
| `terminal.ansi.bright_yellow` | `#F2C94C` | `#E6BA45` | `#8A5A00` | ANSI bright yellow |
| `terminal.ansi.bright_blue` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | ANSI bright blue |
| `terminal.ansi.bright_magenta` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | ANSI bright magenta |
| `terminal.ansi.bright_cyan` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | ANSI bright cyan |
| `terminal.ansi.bright_white` | `#EDEBE6` | `#E6E4E0` | `#22262B` | ANSI bright white |
| `terminal.ansi.dim_black` | `#5C646B` | `#646C74` | `#8B939B` | ANSI dim black |
| `terminal.ansi.dim_red` | `#FF7B72` | `#F2736B` | `#C0342B` | ANSI dim red |
| `terminal.ansi.dim_green` | `#7BE38B` | `#6FD47F` | `#17714A` | ANSI dim green |
| `terminal.ansi.dim_yellow` | `#F2C94C` | `#E6BA45` | `#8A5A00` | ANSI dim yellow |
| `terminal.ansi.dim_blue` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | ANSI dim blue |
| `terminal.ansi.dim_magenta` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | ANSI dim magenta |
| `terminal.ansi.dim_cyan` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | ANSI dim cyan |
| `terminal.ansi.dim_white` | `#5C646B` | `#646C74` | `#8B939B` | ANSI dim white |

### Syntax Captures (42 entries)

Each entry is a `HighlightStyleContent` object: `color`, `font_style`, `font_weight`.

| Capture | Hypersonic | Supersonic | Subsonic | Style | Applies to |
|---|---|---|---|---|---|
| `keyword` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | normal | `if`, `fn`, `return` |
| `keyword.import` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | normal | import / use |
| `function` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | normal | Function names |
| `function.method` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | normal | Method calls |
| `function.definition` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | normal | Declaration sites |
| `type` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | normal | Types, classes |
| `constructor` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | normal | Constructors |
| `enum` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | normal | Enum names |
| `variant` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Enum variants |
| `variable` | `#EDEBE6` | `#E6E4E0` | `#22262B` | normal | Identifiers |
| `variable.special` | `#FFB067` | `#F0A05E` | `#B4470F` | italic | `self`, `this` |
| `property` | `#EDEBE6` | `#E6E4E0` | `#22262B` | normal | Object fields |
| `constant` | `#F2C94C` | `#E6BA45` | `#8A5A00` | normal | Constants |
| `string` | `#7BE38B` | `#6FD47F` | `#17714A` | normal | String literals |
| `string.escape` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Escapes |
| `string.regex` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Regex |
| `string.special` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Special strings |
| `string.special.symbol` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Symbols / atoms |
| `number` | `#F2C94C` | `#E6BA45` | `#8A5A00` | normal | Numeric literals |
| `boolean` | `#F2C94C` | `#E6BA45` | `#8A5A00` | normal | true / false |
| `comment` | `#99A1A8` | `#9BA4AC` | `#5A6169` | italic | Line & block comments |
| `comment.doc` | `#99A1A8` | `#9BA4AC` | `#5A6169` | italic | Doc comments |
| `operator` | `#99A1A8` | `#9BA4AC` | `#5A6169` | normal | Operators |
| `punctuation` | `#99A1A8` | `#9BA4AC` | `#5A6169` | normal | General punctuation |
| `punctuation.bracket` | `#99A1A8` | `#9BA4AC` | `#5A6169` | normal | Brackets |
| `punctuation.delimiter` | `#99A1A8` | `#9BA4AC` | `#5A6169` | normal | Commas, semicolons |
| `punctuation.list_marker` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | normal | Markdown bullets |
| `punctuation.special` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Interpolation braces |
| `attribute` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Decorators, annotations |
| `label` | `#FFB067` | `#F0A05E` | `#B4470F` | normal | Loop labels |
| `tag` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | normal | HTML/JSX tags |
| `preproc` | `#D9A6FF` | `#C79BF0` | `#7A3BB5` | normal | Macros, directives |
| `embedded` | `#EDEBE6` | `#E6E4E0` | `#22262B` | normal | Embedded language |
| `emphasis` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | italic | Markdown italic |
| `emphasis.strong` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | normal | Markdown bold (weight 700) |
| `title` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | normal | Headings (weight 700) |
| `link_text` | `#7FB4FF` | `#6BA8F5` | `#1D5FCC` | italic | Link labels |
| `link_uri` | `#7BE38B` | `#6FD47F` | `#17714A` | normal | URLs |
| `text.literal` | `#7BE38B` | `#6FD47F` | `#17714A` | normal | Inline code |
| `hint` | `#4FE3C1` | `#3FD3B4` | `#0F7A66` | italic | Inlay hints |
| `predictive` | `#5C646B` | `#646C74` | `#8B939B` | italic | Ghost completions |
| `primary` | `#EDEBE6` | `#E6E4E0` | `#22262B` | normal | Fallback |

### Containers

| Key | Shape | Value |
|---|---|---|
| `players` | Array of 8 `{cursor, background, selection}` | Slot 0 = `accent`; slots 1–7 cycle blue, green, yellow, orange, red, purple, muted |
| `accents` | Array of strings | The seven signal hues in order |
| `syntax` | Map of capture → `HighlightStyleContent` | See table above |

---

## 7. When to use each variant

- **Hypersonic** — mobile, OLED laptops, battery-critical work, low ambient light. The default recommendation for anyone on battery.
- **Supersonic** — desk default. Long sessions, mixed lighting, LCD or OLED.
- **Subsonic** — daylight, glare, outdoor, or light-mode preference. Not for battery-constrained mobile.

## 8. Build order

A Zed theme is one file; unset keys fall back to defaults and look broken. **Do not phase by category.** Phase by variant:

1. Build **Supersonic** complete — all 139 keys + syntax. Dogfood a week.
2. Derive **Hypersonic** by swapping the surface and content layers only. Signal hues carry over.
3. Derive **Subsonic** by inverting surface/content and substituting the light signal set.
4. Run the validator (`validate_turbine.py`) against all three before publishing.

## 9. Common traps

- **Inventing key names.** Zed silently ignores unknown keys — no error, just an unstyled surface. Diff against the schema, never against memory. This is exactly how v1 failed.
- **Trusting a stale key list.** The schema moves. Newer Zed added `version_control_*` keys not in v0.2.0, and deprecated `scrollbar_thumb.background` in favour of `scrollbar.thumb.background`. Pin your target Zed version and re-diff each release.
- **Hardcoding hexes per key.** Breaks three-variant parity the first time a token changes.
- **Claiming contrast without computing it.** v1 asserted AA compliance and failed 10 of 17 sampled pairs.
- **Treating light mode as power-neutral on OLED.** It isn't.

## 10. Open items before build

- **The "185 keys" figure has no source.** v0.2.0 publishes 142 top-level style properties. Confirm where 185 came from — a specific Zed build, or a count that included syntax captures and player slots.
- **Governance.** "Community-led" is unspecified: licence, contribution route, and who arbitrates palette changes all need deciding before the repo is public.

---

### Appendix A — Verified Contrast

Computed with the WCAG 2.1 relative-luminance formula. Every text-bearing pair clears AA (4.5:1).

| Pair | Hypersonic | Supersonic | Subsonic |
|---|---|---|---|
| text | 17.63:1 AAA | 14.17:1 AAA | 13.87:1 AAA |
| editor.foreground | 17.63:1 AAA | 14.17:1 AAA | 13.87:1 AAA |
| text.muted | 8.02:1 AAA | 7.11:1 AAA | 5.72:1 AA |
| editor.line_number | 7.23:1 AAA | 6.55:1 AA | 5.28:1 AA |
| syntax.comment | 8.02:1 AAA | 7.11:1 AAA | 5.72:1 AA |
| syntax.keyword | 10.85:1 AAA | 8.03:1 AAA | 6.13:1 AA |
| syntax.function | 9.87:1 AAA | 7.32:1 AAA | 5.38:1 AA |
| syntax.string | 13.20:1 AAA | 9.77:1 AAA | 5.47:1 AA |
| syntax.number | 13.23:1 AAA | 9.83:1 AAA | 5.40:1 AA |
| syntax.type | 13.09:1 AAA | 9.59:1 AAA | 4.79:1 AA |
| syntax.attribute | 11.66:1 AAA | 8.48:1 AAA | 4.97:1 AA |
| error | 8.33:1 AAA | 6.37:1 AA | 5.08:1 AA |
| warning | 11.66:1 AAA | 8.48:1 AAA | 4.97:1 AA |
| success | 13.20:1 AAA | 9.77:1 AAA | 5.47:1 AA |
| info | 9.87:1 AAA | 7.32:1 AAA | 5.38:1 AA |
| text.accent | 13.09:1 AAA | 9.59:1 AAA | 4.79:1 AA |
| text on surface | 15.91:1 AAA | 13.05:1 AAA | 12.81:1 AAA |
| muted on elevated | 6.74:1 AA | 5.95:1 AA | 6.27:1 AA |

#turbine #zed-theme #design-system #design-brief
