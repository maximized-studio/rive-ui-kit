# Rive UI Kit

Native, data-bound UI components for [Rive](https://rive.app), written as text (RML) and built into a `.riv` file. Accessible out of the box, themeable at runtime.

<img src="docs/default.png" alt="Rive UI Kit Showcase: sidebar with component list, component cards, Theme panel" width="720">

The kit is also on the [Rive Community](https://rive.app/community/files/25701-55058/). This repo ships the **Default** theme; more themes will follow.

## Components

- **Inputs:** Button · Switch / Switch List · Slider · Dropdown · Radio Option / Radio Group · Checkbox / Checkbox Group
- **Display:** Badge · Label · Avatar
- **Building blocks:** List Item · Tile · Slide · Segment · Segmented Control · Nav Item · Accordion · Sidebar · Toolbar

Every component is driven by view models (data binding), not by state machine inputs. The **Theme** panel in the Showcase switches mode (light/dark), brand colour, roundness and shadow at runtime, and previews every component as enabled or disabled.

## Accessibility

The components carry Rive semantics, so screen readers get a real accessibility tree instead of a canvas:

| Component | Role | Exposed |
|---|---|---|
| Button, Dropdown | `button` | label |
| Switch | `switchControl` | label, on/off |
| Checkbox | `checkbox` | label, checked |
| Radio Option / Radio Group | `radioButton` / `radioGroup` | label, selected |
| Slider | `slider` | label, value |
| Switch List, Checkbox Group | `group` | group label |
| List Item | `list` / `listItem` | label |
| Label, Badge | `text` | text |
| Avatar | `image` | label |

Labels are bound to the same view model properties as the visible text, so they stay correct when you change the copy. Check the tree headless:

```bash
rive build/default --semantics=$PWD/build/default.semantics.json
```

## How it is organised

```
shared/            the kit: one .rml file per artboard, 99-_root.rml
                   (view models, assets, interpolators) and image assets
themes/<name>/     only what that theme changes (Default changes nothing)
tools/             Python helpers: retheming, RML generation, splitting
build.sh           assembles and verifies every theme into build/<name>/
```

**Override rule:** a file in `themes/<name>/` with the same filename as one in `shared/` replaces it. Anything else is added. A replacing file keeps the ids of the original, so references from other artboards keep working.

## Build

Requirements: macOS (zsh), Python 3 and the Rive CLI (`rive`, expected at `~/.rive/bin/rive`; override with `RIVE=/path/to/rive`).

```bash
./build.sh                       # build and verify all themes
PREVIEW=1 ./build.sh default     # embeds Inter so text renders in local screenshots
rive build/default --screenshot --advance=2s
```

Do not publish a `PREVIEW` build: an embedded custom font blocks publishing to the Rive Community.

## Make your own theme

1. Create `themes/<name>/palette.json` (format below).
2. Run `PREVIEW=1 ./build.sh <name>` and take a screenshot.
3. Only if a component must change shape: copy its file from `shared/` into `themes/<name>/` and edit it there. Give new objects their own id range (for example `800:*`) so they never collide with shared ids.

### palette.json

```json
{
  "defaults": { "roundness": 2, "shadow": 1 },
  "mode": {
    "Dark":  { "_bg": "#0B0B0F", "_surface": "#16161C", "_border": "#2A2A33", "_text": "#F4F4F5" },
    "Light": { "_bg": "#FAFAFA", "_surface": "#FFFFFF", "_border": "#E4E4E7", "_text": "#18181B" }
  },
  "brands": {
    "Blue": ["#EFF6FF", "#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6",
             "#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A", "#172554"]
  }
}
```

- `mode.Light` / `mode.Dark`: surface, border and text tokens (`_bg`, `_surface`, `_surfaceMuted`, `_border`, `_text`, `_textMuted`, …). Any token may be left out.
- `brands`: one ramp of 11 steps (50–950) per brand slot (`Blue`, `Violet`, `Emerald`, `Orange`, `Rose`, `Zinc`).
- `defaults` (optional): starting `roundness` and `shadow` (0–3). They are baked into the written values, so the editor canvas and the Community thumbnail show them too.

`tools/retheme.py` turns the palette into the theme's Theme Driver. Known gap: the brand swatches in the Theme panel keep their default colours.

## For maintainers

`./push.sh <theme> "label"` builds a theme and pushes it to its own Rive file (linked in `themes/<theme>/push.yaml`). It refuses to push to the original Community file or to push a `PREVIEW` build. It needs access to the Maximized Studio workspace.

The editor file is the source of truth. After editing in Rive, run `./pull.sh` before committing: it pulls the file read-only, re-splits it into `shared/` and builds.

## License

[MIT](LICENSE) © Maximized Studio. The preview font `preview-assets/Inter.ttf` is licensed under the SIL Open Font License.
