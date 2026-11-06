---
name: rive-ui-kit
description: Build Rive UIs from the Rive UI Kit by Maximized Studio, a set of native, data-bound, accessible and themeable components written in RML (Accordion, Alert, Avatar, Badge, Breadcrumbs, Button, Button Group, Checkbox, Dropdown, Label, Pagination, Radio Group, Slider, Switch, Tooltip and more). Use when a user wants buttons, forms, navigation or other UI controls in a Rive file or RML project, asks for the "Rive UI Kit", or wants to theme, compose, update or fork its components.
---

# Rive UI Kit

Native Rive components driven by view models (data binding), not by state machine inputs. One global `Theme` view model styles all of them at runtime.

- Source: https://github.com/maximized-studio/rive-ui-kit (RML in `shared/`, one file per artboard, view models in `99-_root.rml`)
- Live demo: https://www.maximized.studio/rive/ui-starter-kit
- Every component's ids, properties, events and a paste-ready snippet: [references/components.md](references/components.md). Read a component's section before you use it.
- A working screen to start from: [templates/60-Screen.rml](templates/60-Screen.rml) (Theme Driver, Alert, Button, Switch).

## The rule: depend, don't copy

The kit must stay updatable. Build **on top of** the repo, never inside it, and treat `shared/` as reference source: read it, don't edit it.

1. **Start:** fork or clone the repo and keep it as `upstream`:
   ```bash
   git clone https://github.com/maximized-studio/rive-ui-kit my-app && cd my-app
   git remote rename origin upstream
   ```
2. **Your work goes in one folder:** `themes/<app>/`. `./build.sh <app>` assembles `shared/` plus that folder into `build/<app>/`. A file there with a new name is added; a file with the same name as one in `shared/` replaces it.
3. **Update:** `git pull upstream main`, then `./build.sh <app>`. Nothing conflicts as long as you never edited `shared/`.
4. **Deviate only by building your own copy.** Change the look through the Theme first (mode, brand, roundness, shadow, a `palette.json`): that keeps you on upstream. Only if a component must change shape, copy its file into `themes/<app>/` under a **new filename and artboard name**, with ids in your own range. That copy is yours and no longer receives updates, so tell the user before you make it. Overriding a kit file under its own name also works but freezes that component; prefer a new name.

Never run `./pull.sh` or `./push.sh` from the template as-is: they belong to the kit's maintainers.

## Your first screen

1. `mkdir themes/<app>` and copy [templates/60-Screen.rml](templates/60-Screen.rml) into it.
2. Write the artboard name into `themes/<app>/main.txt` (`Screen`), so the build plays it instead of the kit's Showcase.
3. Add components from the snippets in the reference. Number ids from `60000:` upward; every id is unique across the whole document (kit ids stay below `1000:`).
4. `PREVIEW=1 ./build.sh <app>`, then `rive build/<app> --screenshot --advance=2s` and look at `build/<app>/build/*.png`. `PREVIEW` embeds the Inter font so text renders locally; don't publish a `PREVIEW` build.

## Traps (each one seen while testing this skill)

- **Your artboard needs a state machine.** Without one, the binds in it never run: the background ignores the Theme and nested components keep stale values. The template has a minimal one.
- **Keep every property in a nested instance.** A property you leave out leaves its binds unset: a Button without its `group` line loses its rounded corners and brand colour. The snippets list them all.
- **Text that wraps collapses under `hug`.** Give Alert, Accordion and Tooltip `instanceWidthScaleType="fill"` or a fixed width.
- **The stored Theme is dark** (`mode` `1`). Set `mode` at runtime, or expect dark screenshots.
- **Place the Theme Driver once**, in the artboard you play, as an absolute layout that fills it. Without it the colour tokens keep their stored values and Tooltip Button can't flip sides.
- Attribute names are the runtime's, not CSS: `flexDirectionValue`, `gapHorizontal`, `paddingLeft`. Copy them from `shared/` when unsure, or `rive schema <Type>`.

## Composing components

- **Lists hold the items.** Accordion `items`, Breadcrumbs `items`, Button Group `buttons`, Dropdown `list`, and the `options` of Checkbox Group, Radio Group and Switch Group take a list of their item view model. Fill the list; an empty list renders an empty card.
- **Shared selection instances.** In a Radio Group, point the `group` of every option at the **same** `RadioSelection` instance as the group's `selection`. Same for every Breadcrumb Item and its Breadcrumbs. A copy per item breaks the selection.
- **Button Group:** set `group` on each Button in the list: `1` first, `2` middle, `3` last.
- **Tooltip:** use **Tooltip Button** for a button with a tooltip. A bare Tooltip is only the bubble; its host sets `open`.
- **Events:** properties named `_pressed` are triggers. Listen to them in your app; Breadcrumbs `selected` and Pagination `page` are numbers you listen to.
- Properties starting with `_` are internal state. Read them only when the reference says so, never write them.
- Bind your own shapes and text to Theme tokens (the reference lists their ids) so they follow mode and brand.

## Theme at runtime

```js
// @rive-app/* 2.49+, with autoBind: true
const theme = rive.globalViewModelInstance("Theme");
theme.number("mode").value = 0;              // light

const flag = theme.boolean("cursorPointer"); // true over anything clickable
flag.on(() => (canvas.style.cursor = flag.value ? "pointer" : ""));
```

## Scripts

Pagination (**Pagination Pages**), Tooltip Button (**Tooltip Placement**) and the Theme Driver (**Viewport**) carry small Luau scripts. They run in the editor and the Rive runtimes, in a `.riv` exported from the editor or built with `rive --publish`. A plain CLI build (`--once`) does not run them, so a Pagination there shows no page buttons.

## Checking your work

- Screenshot every change (step 4 above) and look at it before you report a screen as done.
- `rive build/<app> --semantics=$PWD/build/semantics.json` dumps the accessibility tree. Kit components carry roles and labels bound to their text; keep `label` properties filled so screen readers get real names.
