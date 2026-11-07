# Rive UI Kit

Native, data-bound UI components for [Rive](https://rive.app), written as text (RML) and built into a `.riv` file. Accessible out of the box, themeable at runtime.

**[▶ Try it live](https://www.maximized.studio/rive/ui-starter-kit)**: switch mode, brand colour, roundness and shadow in your browser.

<a href="https://www.maximized.studio/rive/ui-starter-kit"><img src="docs/default.png" alt="Rive UI Kit Showcase: sidebar with component list, component cards, Theme panel" width="720"></a>

The kit is also on the [Rive Community](https://rive.app/community/files/25701-55058/). This repo ships the **Default** theme; more themes will follow.

## Components

- **Actions:** Button · Button Group · Split Button · Toggle Button / Toggle Button Group
- **Display:** Accordion · Avatar · Avatar Group · Badge · Gauge · Kbd · Label
- **Feedback:** Alert · Dialog · Progress Bar · Spinner · Tooltip
- **Inputs:** Checkbox / Checkbox Group · Chip / Chip Group · Combobox · Date Field · Discrete Slider · Knob · Number Field · PIN Input · Radio Option / Radio Group · Range Discrete Slider · Range Slider · Rating · Select · Slider · Switch / Switch Group · Tag Input
- **Navigation:** Breadcrumbs · Context Menu · Menu · Pagination · Stepper · Tabs
- **Building blocks:** Accordion Item · Breadcrumb Item · Button Row · Calendar · Calendar Day · Combo Option · Dialog Demo · Menu Item · Nav Group · Nav Item · Page Item · Showcase Section · Sidebar · Slide · Slider Tick · Star · Step · Stepper Demo · Tab · Tag · Tile · Toolbar · Tooltip Button

Categories and the components in them are sorted A–Z. In the Showcase a category is data: a `ShowcaseSection` (title, tile list; the count is the list length) in `sections`, and a `NavGroup` in the Sidebar's `sections`.

Every component is driven by view models (data binding), not by state machine inputs. The **Theme** panel in the Showcase switches mode (light/dark), brand colour, roundness and shadow at runtime, and previews every component as enabled or disabled.

## Theme

`Theme` is a **global view model**: one instance that every component reads, so no component carries a `theme` property of its own. It holds `mode` (`0` light, `1` dark), `brandIndex`, `roundness` and `shadow` (`0`–`3`), `cursorPointer` and the colour tokens (`_bg`, `_text`, `_brand500`, …).

One **Theme Driver** turns `mode` and `brandIndex` into the colour tokens. The Showcase holds it; in your own file, place the Theme Driver component once in the artboard you play, as an absolute layout that fills the artboard (it draws nothing and never blocks input). Without it the tokens keep their stored values.

The Theme Driver also carries a small Luau script, **Viewport**, that writes the artboard size and the pointer position into `Theme` (`_viewWidth`, `_viewHeight`, `_pointerX`, `_pointerY`). Tooltip Button uses them to keep its bubble on screen.

```js
const theme = rive.globalViewModelInstance("Theme");   // @rive-app/* 2.49+, with autoBind: true
theme.number("mode").value = 0;                         // light
```

## Accessibility

The components carry Rive semantics, so screen readers get a real accessibility tree instead of a canvas:

| Component | Role | Exposed |
|---|---|---|
| Accordion | `group` / `button` per item | label; item title, expanded |
| Alert | `group` (live region), `text` | title; body |
| Avatar Group | `group` | label |
| Avatar | `image` | label |
| Badge, Label | `text` | text |
| Breadcrumbs | `group` / `link` per item, `text` for the current page | label; item label, "Current page" |
| Button Group, Checkbox Group, Chip Group, Pagination, Switch Group | `group` | group label |
| Button, Page Item | `button` | label (the page number); Button also a hint |
| Calendar / Calendar Day | `group` / `button` per day | label, the month; the full date, selected |
| Checkbox | `checkbox` | label, checked (`0`, `1` or `2` for mixed) |
| Chip | `button` (toggle) | label, on/off, disabled |
| Combobox / Combo Option | `textField` (expandable), `button`, `list` / `listItem` | label, query, expanded, disabled; "Show options"; option label, selected |
| Context Menu | `group` | label, hint (the kit Menu follows) |
| Date Field | `button` | label, the date |
| Dialog | `dialog`, `text`, `button` ×2 | title; body; the two Buttons |
| Discrete Slider, Knob, Range Discrete Slider | `slider` | label, value, disabled; increase / decrease |
| Gauge | `text` | label, value |
| Kbd | `text` | keys |
| Menu / Menu Item | `list` / `listItem` | label; item label, selected (in a Select), disabled |
| Number Field | `button` / `slider` / `button` | Decrease, label with the value, Increase; increase / decrease |
| PIN Input, Tag Input | `textField` | label, value (Tag Input: the draft), disabled |
| Progress Bar | `group` / `text` | label; percentage ("64%") |
| Radio Option / Radio Group | `radioButton` / `radioGroup` | label, selected |
| Range Slider | `group` with two `slider`s | label; Minimum / Maximum with their percentage |
| Rating | `slider` | label, value ("3 of 5"), disabled; increase / decrease |
| Select | `button` (expandable) | label, the chosen value, expanded, disabled |
| Slider | `slider` | label, value |
| Spinner | `image` | label |
| Stepper / Step | `list` / `listItem` | label; step label, selected for the active step |
| Switch | `switchControl` | label, on/off |
| Tabs / Tab | `tabList` / `tab` | label; tab label, selected, disabled |
| Toggle Button Group / Toggle Button | `radioGroup` / `radioButton` | group label; label, checked, disabled |
| Tooltip Button | `button` | label, hint (the tooltip text) |
| Tooltip | `text` | text (left out when its trigger carries it as a hint) |

Labels are bound to the same view model properties as the visible text, so they stay correct when you change the copy. Check the tree headless:

```bash
rive build/default --semantics=$PWD/build/default.semantics.json
```

## Accordion

A card of collapsible items; several can be open at once, or one at a time.

- View model `Accordion`: `items` (a list of `AccordionItem`), `single`, `label` (screen reader name), `a11yHidden`.
- `AccordionItem`: `title`, `body`, `open`. Clicking the header (or a screen reader's activate) toggles `open`; the body grows open with a short layout animation and the chevron turns.
- With `single` on, opening an item closes the others. A small Luau script, **Accordion Single**, does that; with `single` off it does nothing.
- Each header is a `button` that reports expanded or collapsed.

## Breadcrumbs

A trail of links to the pages above the current one: `Home › Components › Navigation`.

- View model `Breadcrumbs`: `items` (a list of `BreadcrumbItem`), `selected` (written when a link is clicked: the item's position, `0` for the first; `-1` until then), `selection` (a shared `BreadcrumbSelection`), `label` (screen reader name), `a11yHidden`.
- `BreadcrumbItem`: `label`, `current`, `selection`. Set `current` on the last item: it stands out in semibold text, is not clickable and is read as the current page. The other items are muted links that get a soft background on hover, like a button. A separator sits between items, never before the first.
- Point `selection` of every item at the same `BreadcrumbSelection` instance as the `Breadcrumbs` (as with Radio Group). Clicks write it and the component copies the value into `selected`.
- Listen to `selected` in your app to navigate, then replace `items` with the new trail.

## Alert

A card that stays in view with a message in one of four variants. It has no close button; for something the user dismisses, use a dialog.

- View model `Alert`: `title`, `body`, `variant` (`0` info, `1` success, `2` warning, `3` error), `a11yHidden`.
- Each variant has its own icon and colours from semantic Theme tokens: info follows the brand colour, success, warning and error have their own light and dark values (see palette.json).
- Hide or show it from your app like any other part of your layout.
- Screen readers get a `group` named by the title and marked as a live region, so a changed title is announced, with the body as text.

## Button

A button in three variants and three colours, like MUI: `variant` sets the shape, `color` the meaning. The default (contained, neutral) follows the inverse colours of the mode (light on dark, dark on light), so it never clashes with the brand colour.

- View model `Button`: `text`, `variant` (`0` contained, `1` outlined, `2` text), `color` (`0` neutral, `1` brand, `2` destructive), `icon` (`0` none, `1` arrow, `2` chevron left, `3` chevron right, `4` copy, `5` scissors, `6` clipboard, `7` save, `8` trash, `9` close, `10` chevron down, `11` minus, `12` plus, `13` send, `14` eye), `iconOnly`, `disabled`, `hint`, `group` (see Button Group), `a11yHidden`. `_pressed` fires on a click, a screen reader's activate, or Enter/Space while the Button has keyboard focus.
- A disabled Button ignores all three, and it cannot take keyboard focus. Taps and keys go through a small gate (`_activate` → the Activate layer fires `_pressed` only when `disabled` is false), because the disabled shield only stops the pointer.
- **Contained** is a filled button with the theme shadow. Neutral uses `_primaryBg` / `_primaryHover` / `_primaryText`, destructive `_dangerBg` / `_dangerHover` / `_dangerText`: Theme tokens per mode that ignore the brand. Brand uses `_brand600` with `_brand800` on hover.
- **Outlined** sits on `_surfaceRaised` with a border: `_border` for neutral, `_infoBorder` for brand, `_errorBorder` for destructive, and text in `_text`, `_infoText` or `_errorText`.
- **Text** has no surface and no border, only the coloured text; hover adds a soft background (`_surfaceHover`, `_infoBg`, `_errorBg`).
- Only the brand colour follows the brand. Destructive stays red whatever the brand is.
- Disabled looks the same in every colour: `_textMuted` on `_surfaceSubtle`, or without the surface for the text variant.
- One state machine layer, **Look**, holds one state per combination (Contained Neutral … Text Destructive).
- Breaking change from the four old variants: `1` secondary is now `variant` 1 (outlined, neutral); the old `2` brand and `3` destructive are now `variant` 0 with `color` 1 or 2.

## Button Group

A row of kit Buttons joined into one control: the outer corners follow the theme roundness, the inner corners are square, and the group casts one shadow. Every Button variant and colour works and they may be mixed; set the same `variant` on each Button for an outlined or text group (a group cannot reach into its list).

- View model `ButtonGroup`: `label` (screen reader name), `buttons` (a list of `Button` instances), `a11yHidden`.
- Set `group` on every Button in the list: `1` first, `2` middle, `3` last (`0`, the default, is a standalone Button). It rounds only the outer corners and draws a divider before middle and last buttons; secondary borders merge into one line.
- Each Button keeps its own `_pressed` trigger, hover, press ripple and disabled state, so you handle clicks per button as you would for a single Button.

## Chip

A pill you switch on and off, for filters and topics. On, it gets a check and the soft brand colours of the Label.

- View model `Chip`: `label`, `icon` (`0` none, `1` play, `2` panels, `3` link, `4` code; a leading icon that the check replaces while the chip is selected, so the chip keeps its width), `selected` (two-way: a click, a screen reader's activate, or Enter/Space while it has keyboard focus toggles it), `disabled`, `a11yHidden`.
- **Chip Group** wraps chips over as many rows as they need: view model `ChipGroup`: `chips` (a list of `Chip` instances), `label` (screen reader name), `a11yHidden`. Every chip keeps its own `selected`, so any number can be on. Read them from the list in your app.
- Off: `_surface` with a `_border` line and `_text`. On: `_softBg`, `_softBorder` and `_softText`, the colours of the Label. Hover: `_surfaceHover`. Disabled: `_surfaceSubtle` and `_textMuted`. The corners follow `_radiusButton`.
- Input goes through the same gate as the Button: every input fires `_activate`, and the Activate layer toggles only when `disabled` is false. A disabled chip also leaves keyboard focus.
- Screen readers get a toggle `button` with the label that reports on or off.

## Toggle Button Group

A row of toggle buttons on a track where exactly one is on, like the Mode and Roundness choices in the Theme panel (which are this component).

- View model `ToggleButtonGroup`: `options` (a list of `ToggleButton` instances), `selection` (a shared `ToggleSelection`), `label` (screen reader name), `a11yHidden`.
- `ToggleButton`: `label`, `value` (its position), `icon` (`0` none, `1` sun, `2` moon, `3`–`6` corner sizes, `7` check, `8` blocked, `9` align left, `10` align center, `11` align right), `iconOnly` (hides the label but keeps it for screen readers), `disabled`, `group` (a `ToggleSelection`), `a11yHidden`. Point `group` of every option at the group's `ToggleSelection`.
- `ToggleSelection`: `selected`, the value of the option that is on. A click, a screen reader's activate, or Enter/Space on a focused option writes it.
- Input goes through the same Activate gate as the Button, so a disabled option ignores every input. Disabled options turn `_textMuted`.
- The selected option sits on `_surfaceRaised`, the track on `_surfaceSubtle`; corners follow `_radiusSegment` / `_radiusSegmentInner`.
- Screen readers get a `radioGroup` with a `radioButton` per option that reports checked. For several independent on/off choices, use Chips.

## Range Slider

Two thumbs on one track for a minimum and a maximum, like a price filter. The brand line runs between them.

- View model `RangeSlider`: `label`, `low`, `high`, `minPos`, `maxPos`, `disabled`, `a11yHidden`. Like the Slider, the values are positions on the 200-point track (`minPos` 8 to `maxPos` 192); the header shows them as percentages ("20 – 80").
- Drag either thumb. `low` never passes `high` and the other way round: each thumb follows a private raw value, and a listener writes it into `low` or `high` through a clamp formula with the other value as its limit. Write `low` or `high` from your app and the thumb follows.
- Track `_borderStrong`, range `_brand600`, thumbs white with the small theme shadow; disabled uses `_textMuted` and `_surfaceSubtle`.
- Screen readers get a `group` named by `label` with a `slider` per thumb (Minimum, Maximum) and its percentage.

## Number Field

A number between a minus and a plus Button, for quantities.

- View model `NumberField`: `value`, `min`, `max`, `step`, `label` (screen reader name), `disabled`, `a11yHidden`.
- The minus and plus are kit Buttons (outlined, icon only), so they hover, press, focus and disable like every Button. Their `_pressed` fires the field's private triggers; a view model listener steps `value` through a formula that keeps it between `min` and `max`.
- The minus and plus Buttons turn off at `min` and `max` (and while the field is disabled). Rive has no number-to-boolean converter, so a tiny Luau converter, **Zero Or Less**, turns `min(value − min, 1 − disabled)` into the Button's `disabled`. Reuse it for any "turn this off at a limit" bind.
- With keyboard focus on the value, the arrow keys step it (up / right +, down / left −, held keys repeat), and a screen reader's increase and decrease do the same, through a gate that ignores them while disabled.
- The value sits on `_surface` with a `_border` line and `_radiusButton` corners; disabled turns it `_textMuted`.
- Screen readers get the two Buttons and a `slider` named by `label` with the value.

## Rating

Five stars for a score from 0 to 5.

- View model `Rating`: `stars` (a list of five `Star` instances), `state` (a shared `RatingState`), `label` (screen reader name), `a11yHidden`.
- `Star`: `value` (`1`–`5`), `group` (the rating's `RatingState`). `RatingState`: `value` (the score), `disabled`.
- Click a star to set the score; hovering previews it in `_brand500`. Filled stars use `_brand600`, empty ones a `_borderStrong` outline; disabled turns the filled stars `_textMuted` and blocks the pointer.
- With keyboard focus the arrow keys step the score (right / up +1, left / down −1, held keys repeat); a screen reader's increase and decrease do the same. Both go through a gate, so a disabled rating ignores them.
- Screen readers get a `slider` named by `label` with the value "3 of 5".

## Menu, Select and Split Button

One **Menu** serves all three: a floating panel of **Menu Items**. On its own it is a context menu; Select and Split Button place it under their trigger.

- View model `Menu`: `items` (a list of `MenuItem` instances), `state` (a `MenuState`), `label` (screen reader name), `a11yHidden`.
- `MenuItem`: `text`, `icon` (`0` none, `1` new file, `2` folder, `3` save, `4` export, `5` pencil, `6` clock, `7` copy; a leading icon in the text colour, muted when disabled), `disabled`, `group` (point it at the menu's `MenuState`), `a11yHidden`. A click, a screen reader's activate or Enter/Space chooses it: it writes `state.selected` (its position), `state.label` (its text) and `state.open = false`, and fires its own `_pressed`. A disabled item ignores every input.
- `MenuState`: `selected` (`-1` for none), `label`, `open`, `showSelection` (a check on the chosen item; on for a Select, off for menus of actions).
- **Select** (Inputs): a field that shows `menu.state.label` and opens the menu below it. View model `Select`: `menu`, `label` (screen reader name), `disabled`, `a11yHidden`. Read `menu.state.selected` in your app; set `menu.state.label` to the first value or a placeholder. Screen readers get an expandable `button` with the chosen value.
- **Split Button** (Actions): a kit Button and a chevron Button joined like a Button Group, with the menu under the chevron. View model `SplitButton`: `text`, `variant`, `color` (as on the Button), `disabled`, `menu`, `menuLabel` (screen reader name of the chevron), `a11yHidden`, and the trigger `pressed` for the main action. Listen to the items' `_pressed` or to `menu.state.selected` for the menu actions.
- The menu closes when an item is chosen or the trigger is pressed again. Rive has no "click outside" for a nested component: close it from your app (`menu.state.open = false`) when you need that.
- The panel uses `_surface`, `_border`, `_radiusDropdown` and the theme shadow; items get a soft brand hover.
- Breaking change: Dropdown is gone. Its list became the Menu; for a value use Select, for actions use Split Button or a Menu.

## Pagination

Previous and next Buttons around up to seven page buttons. Set two numbers and the component does the rest.

- View model `Pagination`: `page` (the current page, two-way: clicks write it), `pageCount`, `label` (screen reader name), `a11yHidden`.
- Up to seven pages are shown as they are. With more, the row keeps the first and last page and three around the current one, with `…` for the gaps: `1 … 4 5 6 … 20`, `1 2 3 4 5 … 20`, `1 … 16 17 18 19 20`.
- Previous and next step by one and are disabled on the first and last page.
- Listen to `page` in your app to load that page.
- The behaviour is a small Luau script, **Pagination Pages**: it fills the `_pages` list of Page Items and sets the disabled flags. Luau runs in the editor and in the Rive runtimes. Use a `.riv` exported from the editor or built with `rive --publish`: a plain CLI build (`--once`) does not run scripts. Like every script, it does not run in a Community thumbnail.

## Stepper

The steps of a wizard in a row: done steps get a check, the active one is filled, the rest wait in muted colours, with lines between them that fill as you go.

- View model `Stepper`: `steps` (a list of `Step` instances), `state` (a shared `StepperState`), `label` (screen reader name), `a11yHidden`.
- `Step`: `label`, `value` (its position: `0` for the first), `group` (the stepper's `StepperState`), `isLast` (hides the line after it). `StepperState`: `active`, the value of the current step.
- Each Step compares its `value` with `active` in one layer (Upcoming, Active, Completed), so moving `active` is all your app does. The circle shows `value + 1` or a check.
- Done and active circles use the primary tokens (`_primaryBg`, `_primaryText`), like the default Button; upcoming ones a `_borderStrong` ring with `_textMuted`.
- **Stepper Demo** is the Showcase's building block: the Stepper with Back and Next Buttons that step `active` between the first and the last step.
- Screen readers get a `list` named by `label` with a `listItem` per step; the active one is selected.

## Tabs

A row of tabs over a divider; the selected tab has full-strength text and a brand bar under it.

- View model `Tabs`: `tabs` (a list of `Tab` instances), `selection` (a shared `TabSelection`), `label` (screen reader name), `a11yHidden`.
- `Tab`: `label`, `value` (its position: `0` for the first), `disabled`, `group` (a `TabSelection`), `a11yHidden`. Point `group` of every Tab at the same `TabSelection` instance as the `Tabs` (as with Radio Group).
- `TabSelection`: `selected`, the value of the selected tab. A click, a screen reader's activate, or Enter/Space on a focused tab writes it; set it from your app to switch tabs yourself.
- The Tabs are the bar only. Rive has no slots, so show the matching content in your own layout from `selection.selected`.
- Unselected tabs use `_textSecondary`, the selected one `_text` and a `_brand600` bar; hover adds a `_surfaceHover` background with `_radiusSmall` corners. A disabled tab turns `_textMuted` and ignores every input.
- Screen readers get a `tabList` named by `label`, with a `tab` per item that reports selected and disabled.

## Dialog

A modal card over a dimmed scrim, with a title, a body and two kit Buttons. It is the dismissible counterpart of Alert.

- View model `Dialog`: `title`, `body`, `confirmText`, `cancelText`, `confirmColor` (a Button `color`: `0` neutral, `1` brand, `2` destructive; was `confirmVariant`), `confirmIcon` and `cancelIcon` (Button `icon` numbers; trash and close by default), `dim` (the 50% scrim, on by default), `open`, `a11yHidden`, and the triggers `confirmed` and `cancelled`.
- Place it once over your screen as a layout that fills the artboard, and set `open` to show it. It fades and scales in, and leaves the layout when closed, so it never blocks input while hidden.
- The confirm Button fires `confirmed`, the cancel Button and a click on the scrim fire `cancelled`; each one also sets `open` back to false. Listen to the triggers in your app.
- The Buttons' `_pressed` triggers are bound to `confirmed` and `cancelled`, so the Dialog reacts to whatever makes a Button fire: a click, a screen reader's activate, or Enter/Space.
- The card uses `_surface`, `_border`, `_radiusCard` and the theme shadow; the scrim is black at 50%.
- Screen readers get a `dialog` named by the title, the body as text and the two Buttons.
- A click outside the card closes it too, also with `dim` off.
- **Dialog Demo** is the Showcase's building block: an "Open dialog" Button with a Dialog over it, `dim` off so the card and its shadow sit on the canvas.

## Progress Bar

A label, a percentage and a bar that fills from the left.

- View model `ProgressBar`: `label`, `value` (`0`–`100`), `indeterminate`, `a11yHidden`.
- Values outside `0`–`100` are clamped; the percentage is rounded to a whole number.
- `indeterminate` hides the bar and the percentage and runs a brand segment across the track, for work of unknown length. Instance `Syncing`.
- The bar eases to a new value with a short layout animation.
- Track and fill use the same tokens as the Slider (`_borderStrong`, `_brand600`); the corners follow `_radiusSmall`, so the theme roundness applies.
- Screen readers get a `group` named by the label with the percentage as text. A chain of built-in converters makes that text (clamp, round, pad, add `%`, trim), so no script is involved.

## Tooltip

A small bubble in the inverse theme colours (`_text` background, `_bg` text) with a pointer arrow. It fades and scales in when it opens and never blocks pointer input.

- View model `Tooltip`: `text`, `placement` (`0` top, `1` bottom, `2` left, `3` right: the side of the trigger it sits on; the arrow points back at the trigger), `open`, `a11yHidden`.
- The Tooltip is the bubble only. Rive has no slots, so the host places it next to its trigger and sets `open`: `enter` and `focus` listeners on the trigger set it, `exit` and `blur` clear it.
- **Tooltip Button** is that pattern, ready to use: a kit Button with a Tooltip. View model `TooltipButton`: `label`, `tooltip`, `placement`, `a11yHidden`. Hover or keyboard focus on the Button shows the tooltip.
- In Tooltip Button the bubble sits in an absolute overlay over the trigger, so it never moves the layout. The overlay's direction follows the side shown; an empty mirror box on the far side keeps the trigger in the middle.
- **Automatic placement.** `placement` is the side you prefer. When the bubble would leave the artboard on that side and fits on the opposite one, it flips there, like a web popover with `position-try-fallbacks: flip-block, flip-inline`. The side shown is `_placement` (read it, don't set it). A small Luau script, **Tooltip Placement**, decides: Rive gives a script no screen position, so it compares the pointer as it sees it with the pointer the Theme Driver's Viewport script reports, which tells it where the trigger is. Until the pointer has moved over the artboard once (keyboard only), and in a file without the Theme Driver, the preferred side stays.
- Screen readers: the Button gets the tooltip text as its `hint` (Button has a new `hint` property) and the bubble is hidden from the tree, so the text is read once. A Tooltip on its own is a `text` node.
- Long text wraps at 240 points.

## Avatar

A round image, optionally with a status dot.

- View model `Avatar`: `image`, `status` (`0` none, `1` online, `2` away, `3` busy, `4` offline), `a11yHidden`.
- The dot sits at the bottom right in the success, warning, error or muted token, ringed in the background colour.
- Screen readers get an `image`.

## Avatar Group

Overlapping initials with a +N bubble; they fan out on hover.

- View model `AvatarGroup`: `label` (screen reader name), `initials1`–`initials4`, `extra` (the number in the +N bubble), `a11yHidden`.
- Four fixed slots, so fill them from your app and put the rest in `extra`.
- Screen readers get a `group` named by `label`.

## Calendar

A month card for picking a date.

- View model `Calendar`: `year`, `month` (`1`–`12`, the month on screen), `value` (the chosen date as `"2026-11-07"`, empty for none), `today` (same format, set by your app; it gets a brand ring), `label` (screen reader name), `a11yHidden`.
- A small Luau script, **Calendar**, fills the 6 × 7 grid (Monday first, the days of the months around it muted), writes the title ("November 2026"), turns a click on a day into `value` (a day of the next or previous month also shows that month) and steps the month on the Previous / Next kit Buttons.
- `CalendarDay` (one cell): `day`, `label` (the full date for screen readers), `inMonth`, `today`, `selected`. A Look layer picks the number style; the chosen day gets a brand disc, hover a soft tint.
- Screen readers get a `group` named by `label`, the month as a group and a `button` per day, selected for the chosen one.

## Checkbox Group

Checkboxes under one label, optionally with an All row.

- `Checkbox`: `label`, `disabled`, `mixed`, `a11yHidden`; the checked state is `_active`. `mixed` shows a brand box with a dash; screen readers get checked `0`, `1` or `2`.
- View model `CheckboxGroup`: `options` (a list of `Checkbox`), `selectAll`, `allLabel`, `a11yHidden`.
- `selectAll` shows an All checkbox above the options, which indent under it. A small Luau script, **Select All**, keeps it in step (checked when every option is, mixed when some are) and checks or clears every option when it is clicked.

## Combobox

A text field that filters a list as you type.

- View model `Combobox`: `options` (a list of `ComboOption`), `value` (the chosen label), `query` (what is typed), `label`, `placeholder`, `open`, `disabled`, `a11yHidden`.
- `ComboOption`: `label`, `selected`.
- A small Luau script, **Combobox**, opens the panel while the field has focus and fills it with the options whose label contains `query` (any case, at most six). Up / Down move the highlight, Enter or a click picks one, Escape closes; with no match the panel says "No results". The chevron opens and closes it.
- Screen readers get an expandable `textField` named by `label`, a "Show options" `button` and a `list` of the results.

## Context Menu

A press held still opens the kit Menu at the pointer.

- View model `ContextMenu`: `menu` (a kit `Menu`), `hint` (the text in the area), `label`, `a11yHidden`, and `x`, `y` and the trigger `openAt`.
- A small Luau script, **Context Menu**, opens the menu after a 0.45 s hold, kept inside the area, and closes it on a press outside. Choosing an item closes it like every kit Menu; read `menu.state.selected`.
- Rive can't tell mouse buttons apart, so a right-click needs your app: write `x` and `y` (a position in the area) and fire `openAt`.
- Screen readers get a `group` named by `label` with `hint` as its hint.

## Date Field

A field that shows a date and opens the Calendar under it.

- View model `DateField`: `label`, `value` (an ISO date, `"2026-11-12"`, empty for none), `placeholder`, `open`, `a11yHidden`.
- The Calendar is nested with its `value` bound two-way to the field's. A small Luau script, **Date Field**, writes the shown text ("12 Nov 2026") and closes the popover when a day is picked. The month arrows keep it open; a click outside closes it.
- Screen readers get a `button` named by `label` with the date.

## Discrete Slider

A slider that snaps to steps, with tick marks and a value bubble.

- View model `DiscreteSlider`: `value`, `min`, `max`, `step`, `label`, `showTicks`, `disabled`, `a11yHidden`.
- A small Luau script, **Discrete Slider**, maps a press and drag on the track to `value` (snapped to `step` within `min`..`max`), keeps the thumb and fill in step when your app writes `value`, `min`, `max` or `step`, and fills the tick list (one `SliderTick` per step, up to 50).
- Hover and drag show a bubble with the value above the thumb and a soft halo; the header value fades out meanwhile. Values print without trailing zeros (`2.5`, `40`).
- With keyboard focus the arrow keys step it, and a screen reader's increase and decrease do the same, through gates that ignore them while disabled. Disabled greys the fill and the thumb.
- Screen readers get a `slider` named by `label` with the value.

## Gauge

A semicircle meter with a needle.

- View model `Gauge`: `value` (`0`–`100`), `label`, `a11yHidden`.
- The arc and the needle follow `value` through formulas; fully native.
- Screen readers get `text` named by `label` with the value.

## Kbd

A keyboard key cap for shortcuts (`⌘ K`, `Esc`).

- View model `Kbd`: `keys`, `a11yHidden`.
- Screen readers get `keys` as `text`.

## Knob

A rotary dial from `min` to `max` with a 270° arc.

- View model `Knob`: `value`, `min`, `max`, `step`, `label`, `disabled`, `a11yHidden`.
- A small Luau script, **Knob Drag**, turns a drag on the dial into `value`: up or right raises it, down or left lowers it, 160 points cover the whole range. The mouse wheel steps it too. The arc, indicator and number are bound natively to `value`.
- With keyboard focus the arrow keys step it, and a screen reader's increase and decrease do the same, through gates that ignore them while disabled.
- Screen readers get a `slider` named by `label` with the value.

## PIN Input

Six boxes for a one-time code.

- View model `PinInput`: `value`, `complete` (read it), `error`, `label`, `disabled`, `a11yHidden`.
- One hidden text input takes the typing, bound two-way to `value`. A small Luau script, **PIN Input**, keeps `value` to six digits, spreads them over the boxes, sets `complete` at six and moves the brand ring and the caret. `error` turns the boxes red.
- Screen readers get a `textField` named by `label` with the value.

## Range Discrete Slider

Two thumbs that snap to steps, like the Discrete Slider.

- View model `RangeDiscreteSlider`: `low`, `high`, `min`, `max`, `step`, `label`, `showTicks`, `disabled`, `a11yHidden`.
- A small Luau script, **Range Discrete Slider**, picks the nearer thumb on a press and drags it (snapped, clamped, never past the other thumb) and keeps the thumbs and the fill between them in step when your app writes `low`, `high`, `min`, `max` or `step`. Ticks between the thumbs light up; the thumb you drag shows its value in a bubble.
- The screen reader's increase and decrease move the high thumb.

## Spinner

An indeterminate loader: a brand arc that turns while its length sweeps.

- View model `Spinner`: `label` (screen reader name, "Loading"), `a11yHidden`.
- Two looping layers (Spin and Sweep); nothing to drive.

## Tag Input

A field that turns what you type into tags.

- View model `TagInput`: `tags` (a list of `Tag`), `draft` (the text being typed), `label`, `placeholder`, `disabled`, `a11yHidden`.
- `Tag`: `label`, `disabled`. Its × fires `_remove`.
- A small Luau script, **Tag Input**, adds the draft as a tag on Enter or a comma (trimmed, skipped when empty or already there), removes a tag when its × is clicked and passes `disabled` on to every tag. Tags wrap over as many rows as they need.
- Screen readers get a `textField` named by `label` with the draft; each tag is text with a remove `button`.

## Pointer cursor

A canvas can't change the mouse cursor by itself, so the kit tells your app when to. `cursorPointer` (a boolean on the global Theme view model) is `true` while the pointer is over something clickable: an accordion header, a breadcrumb link, a button, checkbox, chip, menu item, select, nav group header, nav item, page item, radio option, slider, switch, tab, tile or toggle button. Disabled controls leave it `false`.

```js
const flag = rive.globalViewModelInstance("Theme").boolean("cursorPointer");
flag.on(() => (canvas.style.cursor = flag.value ? "pointer" : ""));
```

With `@rive-app/react-*`: pass `rive?.globalViewModelInstance("Theme")` to `useViewModelInstanceBoolean("cursorPointer", …)` and toggle a `cursor-pointer` class. Use the same flag for a hover pointer on iPad or desktop apps.

## Build on the kit

Build your own screens on top of this repo and keep pulling updates. Your work lives in one folder, the kit stays untouched:

```bash
git clone https://github.com/maximized-studio/rive-ui-kit my-app && cd my-app
git remote rename origin upstream
mkdir themes/myapp && cp skills/rive-ui-kit/templates/60-Screen.rml themes/myapp/
echo Screen > themes/myapp/main.txt          # the artboard the build plays
PREVIEW=1 ./build.sh myapp && rive build/myapp --screenshot --advance=2s
git pull upstream main                       # later: new components and fixes
```

Treat `shared/` as reference source: read it, don't edit it, so `git pull` never conflicts. To change a component's shape, copy it into your folder under a new name; that copy is yours and no longer receives updates.

### With an AI agent

The repo ships an agent skill in `skills/rive-ui-kit/`: how to set up a screen, every component's ids and properties with a paste-ready snippet, and the traps to avoid. Install it with

```bash
npx skills add maximized-studio/rive-ui-kit
```

then ask your agent for the screen you want. The component reference is generated from the RML by `tools/skill_reference.py`, so it always matches the kit.

## How it is organised

The kit keeps each kind of logic in one place:

- **Look comes from data.** Colours, radii and shadows are tokens on the global `Theme`; components only read them.
- **Picking one of several is a state.** A number that chooses what shows (a Button's `variant`, `color` and `icon`, an Alert's `variant`, a Tooltip's `placement`) drives a state machine layer with one state per value, such as Button › Look › Outlined Brand.
- **Behaviour is a script, when it is an algorithm.** Which pages Pagination shows, which side a tooltip fits on, which days a calendar shows. Everything else is native.
- **Converter names say where they belong:** `<Part> · <what it does>`, for example `Slider · Percent text`. The ones only the Showcase uses start with `Showcase`.

Some components carry a small Luau script for their behaviour: Accordion (**Accordion Single**), Calendar, Checkbox Group (**Select All**), Combobox, Context Menu, Date Field, Discrete Slider, Knob (**Knob Drag**), Pagination (**Pagination Pages**), PIN Input, Range Discrete Slider, Tag Input, Tooltip Button (**Tooltip Placement**) and the Theme Driver (**Viewport**). Each script starts with a comment that says what it does. Everything else is native: state machines, binds and built-in converters. Scripts run in the editor and in the Rive runtimes, not in a plain CLI build (`--once`) or a Community thumbnail. One script is a converter: **Zero Or Less** turns a number into a bool (true at zero or below). Rive has no number-to-boolean converter, so put a Formula in front that reaches zero when the bool should be on; the Number Field turns its Buttons off at the limits that way.

```
shared/            the kit: one .rml file per artboard, 99-_root.rml
                   (view models, assets, interpolators), image assets and Luau scripts
themes/<name>/     only what that theme changes (Default changes nothing)
tools/             Python helpers: retheming, RML generation, splitting
skills/rive-ui-kit/ the agent skill: SKILL.md, generated component reference, a starter screen
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
- Button tokens: `_primaryBg`, `_primaryHover`, `_primaryText`, `_dangerBg`, `_dangerHover`, `_dangerText` in `mode.Light` / `mode.Dark`.
- Semantic tokens for the Alert: `_successBg`, `_successBorder`, `_successText` and the same for `_warning…` and `_error…` go in `mode.Light` / `mode.Dark`. The `_info…` tokens follow the brand ramp (Light 50/200/700, Dark 950/800/400).
- `brands`: one ramp of 11 steps (50–950) per brand slot (`Blue`, `Violet`, `Emerald`, `Orange`, `Rose`, `Zinc`). `Zinc` is the Inverse swatch, shown first in the Theme panel; the default brand is `Blue`.
- `defaults` (optional): starting `roundness` and `shadow` (0–3). They are baked into the written values, so the editor canvas and the Community thumbnail show them too.

### Roundness and shadow scales

Each `roundness` and `shadow` step (0–3) sets a group of Theme tokens such as `_radiusButton`, `_radiusCard` or `_shadowBlur`, and components bind to those tokens directly. The values live in one table, `tools/scales.json` (for example `"_radiusButton": [0, 4, 8, 20]`). The Theme Driver's **Roundness** and **Shadow** layers hold one state per step that writes them, so in the editor you can also read and change them there. `tools/theme_scales.py` builds those layers from the table.

`tools/retheme.py` turns the palette into the theme's Theme Driver. Known gap: the brand swatches in the Theme panel keep their default colours.

## For maintainers

`./push.sh <theme> "label"` builds a theme and pushes it to its own Rive file (linked in `themes/<theme>/push.yaml`). It refuses to push to the original Community file or to push a `PREVIEW` build. It needs access to the Maximized Studio workspace.

The editor file is the source of truth. After editing in Rive, run `./pull.sh` before committing: it pulls the file read-only, re-splits it into `shared/` and builds.

## License

[MIT](LICENSE) © Maximized Studio. The preview font `preview-assets/Inter.ttf` is licensed under the SIL Open Font License. The copy, scissors, clipboard, save, send, eye, align, file, folder, upload, pencil, clock, play, panels, link and code icons are redrawn from [Lucide](https://lucide.dev) (ISC License, © Lucide Contributors).
