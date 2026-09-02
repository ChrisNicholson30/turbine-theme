# Turbine — build decisions

Where the shipped theme departs from `design-brief-v2.md`, and why. Each entry follows the same shape: **what changed → why → evidence → cost**.

## 1. A `ghost` token was added to the content layer

- **What changed:** A fourth content weight, `ghost`, sits between `muted` and `disabled`. It drives `predictive` (status), `syntax.predictive`, `terminal.ansi.bright_black` and `terminal.ansi.dim_white`.
- **Why:** The brief maps predictive ghost text to `disabled`, but its own validator requires every syntax capture to clear 4.5:1 against `editor.background`. `disabled` scores 3.49:1, 3.37:1 and 2.84:1 across the three variants, so the brief as written fails its own gate on `syntax.predictive`.
- **Evidence:** `ghost` values were chosen by walking the straight line from `disabled` toward `muted` and stopping at the first point that clears 4.6:1: `#6F777E`, `#79828A`, `#686F77`. They read as dimmer than comments but stay legible.
- **Cost:** One extra token. `text.disabled`, `icon.disabled`, `hidden`, `ignored`, `unreachable` and `editor.invisible` still use `disabled`, so the brief's "disabled sits below 4.5:1 by design" exception is untouched.

## 2. Subsonic `accent` darkened from `#0F7A66` to `#0C7763`

- **What changed:** Two steps darker per channel.
- **Why:** The brief only checked `text.accent` on the canvas (4.79:1). `text.accent` also renders on `surface` (tab bar, status bar, panel headers, matched characters in pickers) where the original scored 4.42:1 and missed AA. §5 of the brief promises every text-bearing pair clears AA; honouring that promise beat honouring the literal hex.
- **Evidence:** `#0C7763` gives 4.61:1 on `surface`, 4.99:1 on `bg`, 5.48:1 on `elevated`. Hypersonic and Supersonic accents were already above 8:1 on every surface and are unchanged.
- **Cost:** A barely perceptible shift in the light variant's identity colour.

## 3. `terminal.ansi.bright_black` uses `ghost`, not `surface`

- **What changed:** ANSI slot 8 (bright black) is `ghost` instead of the panel surface colour.
- **Why:** Bright black is the de-facto "dim text" slot in terminals. zsh autosuggestions, `fish` completions, `git` metadata and most TUI secondary text render in it. With the brief's mapping, that text would be `#0E1113` on a `#000000` terminal in Hypersonic, effectively invisible.
- **Evidence:** Every mainstream terminal palette treats bright black as a mid grey for this reason.
- **Cost:** None to the palette; `terminal.ansi.black` still maps to `surface` as the brief intends.

## 4. `terminal.ansi.dim_white` uses `ghost`, not `disabled`

- **What changed:** Faint default text (SGR 2) uses the legible floor.
- **Why:** `disabled` scores as low as 2.84:1 on Subsonic. Faint text is still text you are meant to read.
- **Cost:** `dim_black` stays at `disabled`; it belongs to the black family, which is a background slot by convention, and is marked exempt in the report.

## 5. Player selections

- **What changed:** Slot 0 (the local user) uses the opaque `sel` token as the brief specifies. Slots 1–7 (collaborators) use their hue at 24% alpha (`3D`), matching Zed's bundled themes.
- **Why:** Collaborator selections overlay your own text and cursor line. An opaque hue would hide both. Zed's `apply_theme_color_defaults` also derives `element.selection_background` from slot 0 and forces 25% alpha if it is opaque, so opaque `sel` in slot 0 is safe.

## 6. Extra syntax captures

- **What changed:** Seven captures that Zed's bundled One theme styles but the brief omitted were added, all through existing tokens: `variable.parameter` and `namespace` → `text`; `selector` → `purple`; `selector.pseudo` → `orange`; `punctuation.markup` → `muted`; `diff.plus` → `green`; `diff.minus` → `red`.
- **Why:** Unset captures fall back to `primary` and lose distinction in CSS, diffs and markup.
- **Cost:** None; the validator ignores unknown syntax captures and every one clears AA.

## 7. Pinned to v0.2.0, with an opt-in extended build

- **What changed:** The shipped `themes/turbine.json` contains exactly the 142 keys in `build/schema_keys.txt`. `--extended` adds nine more.
- **Why:** The brief's build order says to validate against the pinned list before publishing, and the validator flags any key outside that list as invented. The nine extra names were verified against `assets/themes/one/one.json` on Zed's main branch, not from memory. Only names seen in that file were included; `minimap.*`, `debugger.*` and `vim.*` exist in the Rust structs but their JSON names were not verified, so they were left out.
- **Evidence:** Zed's `fallback_themes.rs` gives unset `version_control.*` keys hardcoded green/red/yellow defaults rather than deriving them from `created`/`deleted`/`modified`. On a current Zed build the strict file therefore shows Zed's stock git-gutter colours, not Turbine's. Use `--extended` when you want the gutter on-palette.

## 8. Open items from the brief

- **"185 keys":** Not reproduced. The v0.2.0 list here has 142 top-level style properties (139 colour/appearance keys plus `players`, `accents`, `syntax`). 139 + 42 brief captures + 3 containers = 184, which is the closest plausible origin.
- **Governance:** Licence is MIT (see `LICENSE`). Contribution route and palette arbitration remain undecided.

#turbine #zed-theme #design-brief
