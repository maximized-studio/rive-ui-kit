# Rive UI Kit

Native, data-bound UI components for [Rive](https://rive.app), written as text (RML) and built into a `.riv` file. Accessible out of the box, themeable at runtime.

**[▶ Try it live](https://www.maximized.studio/rive/ui-starter-kit)**: switch mode, brand colour, roundness and shadow in your browser.

<a href="https://www.maximized.studio/rive/ui-starter-kit"><img src="docs/default.png" alt="Rive UI Kit Showcase: sidebar with component list, component cards, Theme panel" width="720"></a>

The kit is also on the [Rive Community](https://rive.app/community/files/25701-55058/). This repo ships the **Default** theme; more themes will follow.

## Components

- **Actions:** Button · Button Group
- **Display:** Avatar · Badge · Label
- **Inputs:** Checkbox / Checkbox Group · Dropdown · Radio Option / Radio Group · Slider · Switch / Switch List
- **Navigation:** Pagination
- **Building blocks:** Accordion · List Item · Nav Item · Page Item · Segment · Segmented Control · Showcase Section · Sidebar · Slide · Tile · Toolbar

Categories and the components in them are sorted A–Z. In the Showcase a category is data: a `ShowcaseSection` (title, tile list; the count is the list length) in `sections`, and an `Accordion` in the Sidebar's `sections`.

Every component is driven by view models (data binding), not by state machine inputs. The **Theme** panel in the Showcase switches mode (light/dark), brand colour, roundness and shadow at runtime, and previews every component as enabled or disabled.

## Accessibility

The components carry Rive semantics, so screen readers get a real accessibility tree instead of a canvas:

| Component | Role | Exposed |
|---|---|---|
| Avatar | `image` | label |
| Badge, Label | `text` | text |
| Button, Dropdown, Page Item | `button` | label |
| Button Group, Checkbox Group, Pagination, Switch List | `group` | group label |
| Checkbox | `checkbox` | label, checked |
| List Item | `list` / `listItem` | label |
| Radio Option / Radio Group | `radioButton` / `radioGroup` | label, selected |
| Slider | `slider` | label, value |
| Switch | `switchControl` | label, on/off |

Labels are bound to the same view model properties as the visible text, so they stay correct when you change the copy. Check the tree headless:

```bash
rive build/default --semantics=$PWD/build/default.semantics.json
```

## Button Group

A row of kit Buttons joined into one control: the outer corners follow the theme roundness, the inner corners are square, and the group casts one shadow. Primary and secondary Buttons both work and may be mixed.

- View model `ButtonGroup`: `label` (screen reader name), `buttons` (a list of `Button` instances), `a11yHidden`, `theme`.
- Set `group` on every Button in the list: `1` first, `2` middle, `3` last (`0`, the default, is a standalone Button). It rounds only the outer corners and draws a divider before middle and last buttons; secondary borders merge into one line.
- Each Button keeps its own `_pressed` trigger, hover, press ripple and disabled state, so you handle clicks per button as you would for a single Button.

## Pagination

Previous and next Buttons around a row of page items. The current page is filled with the brand colour.

- View model `Pagination`: `selection` (a `PageSelection`; `selection/page` is the current page), `pageCount`, `pages` (a list of `PageItem`), `label` (screen reader name), `a11yHidden`, `theme`, and `_prev` / `_next` (the two Button instances).
- `PageItem`: `label` (the visible text), `value` (the page it opens), `group` (the same `PageSelection` as the Pagination), `disabled`. For a gap, add an item with label `…` and `disabled = true`.
- Clicking a page sets `selection/page` to its `value`; previous and next step by one and stop at 1 and `pageCount`. Listen to `selection/page` in your app to load that page.

## Pointer cursor

A canvas can't change the mouse cursor by itself, so the kit tells your app when to. `theme/cursorPointer` (a boolean on the shared Theme view model) is `true` while the pointer is over something clickable: an accordion header, a button, checkbox, dropdown and its items, nav item, page item, radio option, segment, slider, switch or tile. Disabled controls leave it `false`. The path below is the Showcase's; in your own artboard it is wherever your view model holds the Theme.

```js
const flag = rive.viewModelInstance.boolean("theme/cursorPointer");
flag.on(() => (canvas.style.cursor = flag.value ? "pointer" : ""));
```

With `@rive-app/react-*`: `useViewModelInstanceBoolean("theme/cursorPointer", rive?.viewModelInstance)` and toggle a `cursor-pointer` class. Use the same flag for a hover pointer on iPad or desktop apps.

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
