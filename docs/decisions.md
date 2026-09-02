# Turbine — build decisions

Where the shipped theme departs from `design-brief-v2.md`, and why. Each entry follows the same shape: **what changed → why → evidence → cost**. Everything here was checked against Zed's source on the main branch (September 2026), not remembered.

## 1. A `ghost` token was added to the content layer

- **What changed:** A fourth content weight, `ghost`, sits between `muted` and `disabled`. It drives predictive text (`predictive`, `syntax.predictive`), input placeholders (`text.placeholder`, `icon.placeholder`) and the terminal's dim-text slots (`bright_black`, `dim_white`).
- **Why:** The brief maps all of these to `disabled`, but its own validator requires every syntax capture to clear 4.5:1 against the canvas. `disabled` scores 3.49:1, 3.37:1 and 2.84:1 across the variants, so the brief as written fails its own gate on `syntax.predictive`. Placeholders are read too ("Search files…" in the command palette), and that input sits on the elevated surface.
- **Evidence:** Values were chosen by walking the straight line from `disabled` toward `muted` and stopping at the first point that clears 4.55:1 on all three surfaces: `#7B838A`, `#868F97`, `#636A72`. Worst case is 4.58:1 on the dark elevated surface.
- **Cost:** One extra token. `text.disabled`, `icon.disabled`, `hidden`, `ignored`, `unreachable` and `editor.invisible` still use `disabled`, so the brief's "disabled sits below 4.5:1 by design" exception is untouched.

## 2. Subsonic `accent` darkened from `#0F7A66` to `#0C7763`

- **What changed:** Two steps darker per channel.
- **Why:** The brief only checked `text.accent` on the canvas (4.79:1). It also renders on `surface` (tab bar, status bar, matched characters in pickers) where the original scored 4.42:1 and missed AA. Section 5 of the brief promises every text-bearing pair clears AA; honouring that beat honouring the literal hex.
- **Evidence:** `#0C7763` gives 4.61:1 on `surface`, 4.99:1 on `bg`, 5.48:1 on `elevated`. The dark accents were already above 8:1 everywhere and are unchanged.
- **Cost:** A barely perceptible shift in the light variant's identity colour.

## 3. One interaction ramp: hover is `border`, pressed is `border_hi`

- **What changed:** `element.hover` and `ghost_element.hover` use `border`; `element.active` and `ghost_element.active` use `border_hi`. The brief had ghost hover at `surface` and element hover at `elevated`.
- **Why:** Ghost elements are the rows in the project panel, the outline panel and every toolbar, and those panels are painted `surface`. A `surface` hover on a `surface` panel is invisible in all three variants. `elevated` was no better: menus and popovers are `elevated`, so hovering a menu item would also vanish.
- **Evidence:** The two neutrals are visible on every surface: `border` sits at least one step above `elevated` in the dark variants and one step below `surface` in Subsonic (a conventional darker hover on a light theme). Text on hover is at least 10:1 and on pressed at least 7:1 in every variant.
- **Cost:** `border` and `border_hi` now serve as fills as well as lines. The brief already used them that way for the pressed state and the scrollbar thumb, so the ramp is a generalisation, not a new idea.

## 4. Status backgrounds carry their hue

- **What changed:** Every `*.background` status key is its hue at 12 % alpha; every `*.border` is the hue at 40 %. The brief set all fourteen backgrounds to flat `surface` and all borders to flat `border`.
- **Why:** Zed uses these for diagnostic hover popovers, edit-prediction diff previews, tinted buttons and inlay-hint chips. A flat grey loses the error-versus-warning distinction and makes predicted deletions look like predicted insertions.
- **Evidence:** `ui::TintColor` paints `text` on these backgrounds and reserves the hue for icons and borders, so the text pairs are all above 10:1 and the icon pairs clear the 3:1 non-text floor (worst case 3.90:1 on Subsonic). Zed's own fallback derives these from the foreground at 25 %; 12 % keeps Turbine quieter and matches Zed's diff-row defaults.
- **Cost:** None to the token count.

## 5. Editor highlights are translucent and distinct

- **What changed:** `editor.highlighted_line.background` is `accent` at 15 % (was identical to the cursor line, so jump-to-line and bookmarks were invisible). Document highlights use `accent` at 20 % for reads and `yellow` at 20 % for writes (the brief used opaque `sel` for both, hiding the read/write distinction the language server provides). `drop_target.background` is `accent` at 20 % so the pane under a drag stays readable.
- **Cost:** `sel` is still the selection, the search hit and the bracket match, exactly as the brief specifies.

## 6. Terminal dim-text slots use `ghost`

- **What changed:** `terminal.ansi.bright_black` (the brief had `surface`) and `terminal.ansi.dim_white` (the brief had `disabled`).
- **Why:** Bright black is the de-facto dim-text slot: zsh autosuggestions, fish completions, git metadata and most TUI secondary text. With the brief's mapping that text would be `#0E1113` on a `#000000` terminal in Hypersonic. Faint text (SGR 2) is still text you are meant to read.
- **Cost:** `terminal.ansi.black` still maps to `surface` and `dim_black` to `disabled`, both background-family slots by convention.

## 7. Player selections

- **What changed:** Slot 0 (the local user) uses the opaque `sel` token as the brief specifies. Slots 1–7 (collaborators) use their hue at 25 % alpha.
- **Why:** Collaborator selections overlay your own text and cursor line. Zed's `apply_theme_color_defaults` derives `element.selection_background` from slot 0 and forces 25 % alpha if it is opaque, so opaque `sel` in slot 0 is safe.

## 8. Extra syntax captures

- **What changed:** Seven captures that Zed's bundled One theme styles but the brief omitted were added, all through existing tokens: `variable.parameter` and `namespace` → `text`; `selector` → `purple`; `selector.pseudo` → `orange`; `punctuation.markup` → `muted`; `diff.plus` → `green`; `diff.minus` → `red`.
- **Cost:** None; every one clears AA.

## 9. The shipped file targets Zed's current schema, not v0.2.0

- **What changed:** `themes/turbine.json` carries all 189 keys of Zed's current `ThemeStyleContent`. The brief's pinned v0.2.0 list (142 keys) is kept as `build/schema_keys_v0.2.0.txt`, and `--strict` emits a file limited to it. CI validates both.
- **Why:** Zed's `fallback_themes.rs` gives unset `version_control.*` keys hardcoded stock colours rather than deriving them from `created` and `deleted`. A v0.2.0-only file therefore shows Zed's green and red in the git gutter and diff rows, off-palette and untested for contrast. The same is true of the minimap thumb, the active search match and the debugger line.
- **Evidence:** The key list was extracted from the `rename = "…"` attributes of `ThemeStyleContent`, `ThemeColorsContent` and `StatusColorsContent` in `crates/settings_content/src/theme.rs`, excluding the deprecated `scrollbar_thumb.background` alias. `ThemeStyleContent` has no `deny_unknown_fields`, so older Zed builds load the same file and ignore what they do not know. The generator refuses to build if its key map and that list ever disagree.
- **How the 47 newer keys are mapped:**

| Group | Mapping |
|---|---|
| `version_control.*` | added `green`, deleted `red`, modified `yellow`, renamed `blue`, conflict `orange`, ignored `disabled`; word marks at 35 %, conflict regions at 15 % |
| `editor.diff_hunk.*` | `green` and `red` at 12 % filled, 6 % hollow, 36 % hollow border (Zed's own ratios) |
| `search.active_match_background` | `accent` at 40 %, stronger than the `sel` match colour |
| `editor.hover_line_number` | `text` |
| `editor.debugger_active_line.background` | `yellow` at 20 %; `debugger.accent` is `red` for breakpoints |
| `minimap.thumb.*` | `border_hi` at 40 / 60 / 70 %, opaque `border_hi` edge |
| `scrollbar.thumb.active_background` | `disabled`, the next neutral step after `border_hi` |
| `panel.overlay_*` | `surface` and `border`, same as panels |
| `element.selection_background` | `accent` at 25 % |
| `drop_target.border` | `accent` |
| `vim.*` | see §10 |

## 10. Vim mode pills

- **What changed:** Each vim mode gets a tinted pill in the status bar: normal and helix-normal `accent`, insert `green`, replace `red`, visual modes and helix-select `purple`, all at 20 % with `text` on top. Yank flashes `yellow` at 25 %; helix jump labels are `red`.
- **Why:** Mode awareness is the whole game in modal editing. Zed's default is no colour at all.
- **Evidence:** `vim/src/mode_indicator.rs` only paints a custom pill when both background and foreground are non-transparent, so the keys are safe to set. Text on every pill is above 8:1.
- **Cost:** Non-vim users never see them.

## 11. Open items from the brief

- **"185 keys":** Not reproduced. The v0.2.0 list has 142 top-level style properties (139 colour/appearance keys plus `players`, `accents`, `syntax`). 139 + 42 brief captures + 3 containers = 184, which is the closest plausible origin. Zed's current schema has 189.
- **Governance:** Licence is MIT (see `LICENSE`). Contribution route and palette arbitration remain undecided.

#turbine #zed-theme #design-brief
