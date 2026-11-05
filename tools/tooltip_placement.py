"""Give Tooltip Button automatic placement: the bubble flips to the opposite side when it would leave the artboard.

Usage: python3 tools/tooltip_placement.py <dir>     (rewrites <dir> in place; safe to run again)

A script cannot ask Rive where its node is on screen, so two small Luau scripts work it out together:
- Viewport (tools/scripts/Viewport.luau), in the Theme Driver: the driver becomes a fill overlay at the
  Showcase's top left, so the script's box is the artboard. It writes four new values on the global
  Theme: `_viewWidth`, `_viewHeight`, `_pointerX`, `_pointerY`. (Theme, not a global of its own: the
  runtime only hands a script a global view model that something binds to.)
- Tooltip Placement (tools/scripts/TooltipPlacement.luau), twice in Tooltip Button: over the trigger it
  learns the trigger's place from the pointer and decides; around the bubble (input `bubble` on) it
  measures the bubble.
TooltipButton gets `_placement` (the side shown), `_bubbleWidth` and `_bubbleHeight`. The overlay
direction, the Tooltip's `placement` and the Placement layer now follow `_placement`; `placement`
stays the app's preference.
"""
import os, re, shutil, sys

d = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = {'Viewport.luau': 'Viewport.luau', 'TooltipPlacement.luau': 'Tooltip Placement.luau'}  # tools name -> pulled name
TB_VM, TB_PLACEMENT, TB_INSTANCES = '112:7', '112:10', ['112:16', '112:17']
THEME_VM, THEME_INSTANCE, DRIVER_AB, DRIVER_SM, DRIVER_STYLE = '10:7', '10:63', '10:14621', '10:14626', '10:14624'
OLD_DRIVER = re.compile(r'\n([ \t]*)<NestedArtboard artboardId="%s"[^>]*>\s*<NestedStateMachine[^>]*/>\s*</NestedArtboard>' % DRIVER_AB)
VIEW = [('w', '_viewWidth'), ('h', '_viewHeight'), ('x', '_pointerX'), ('y', '_pointerY')]
V = {k: '913:%d' % i for i, k in enumerate(
    'w h x y iw ih ix iy asset host hstyle script wrap wstyle nested nsm'.split(), 1)}
T = {k: '914:%d' % i for i, k in enumerate(
    'shown bw bh a1 a2 a3 b1 b2 b3 asset host hstyle script bubble bstyle mhost mstyle mscript minput'.split(), 1)}
FILL = ('positionLeftUnitsValue="points" positionRightUnitsValue="points" positionTopUnitsValue="points" '
        'positionBottomUnitsValue="points" positionTypeValue="absolute" layoutWidthScaleType="fill" '
        'layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto"')
HUG = 'intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto"'

p = {n: os.path.join(d, n) for n in ['99-_root.rml', '11-Showcase.rml', '18-ThemeDriver.rml', '34-TooltipButton.rml']}
src = {n: open(f, encoding='utf-8').read() for n, f in p.items()}
for mine, pulled in SCRIPTS.items():
    shutil.copy(os.path.join(here, 'scripts', mine), os.path.join(d, pulled))
if 'id="%s"' % T['shown'] in src['99-_root.rml']:
    print('tooltip_placement: already converted (script files refreshed)')
    sys.exit(0)
used = set(re.findall(r'\bid="([^"]+)"', ''.join(src.values())))
assert not used & (set(V.values()) | set(T.values())), 'ids taken: %s' % sorted(used & (set(V.values()) | set(T.values())))


def after(s, pattern, text):
    m = re.search(pattern, s)
    assert m, 'not found: ' + pattern
    return s[:m.end()] + text + s[m.end():]


def before(s, pattern, text):
    m = re.search(pattern, s)
    assert m, 'not found: ' + pattern
    return s[:m.start()] + text + s[m.start():]


# --- root: where the pointer is and how big the artboard is, on the global Theme; the TooltipButton props; the scripts
root = src['99-_root.rml']
root = after(root, r'<ViewModel [^>]*name="Theme" groupId="[^"]*" id="%s">' % THEME_VM, ''.join(
    '\n            <ViewModelPropertyNumber name="%s" id="%s"/>' % (name, V[k]) for k, name in VIEW))
root = after(root, r'<ViewModelInstance [^>]*\bid="%s">' % THEME_INSTANCE, ''.join(
    '\n                <ViewModelInstanceNumber viewModelPropertyId="%s" id="%s"/>' % (V[k], V['i' + k]) for k, _ in VIEW))
root = after(root, r'<ViewModelPropertyNumber name="icon" id="117:265"/>',
             '\n        <ViewModelPropertyNumber name="_placement" id="%s"/>'
             '\n        <ViewModelPropertyNumber name="_bubbleWidth" id="%s"/>'
             '\n        <ViewModelPropertyNumber name="_bubbleHeight" id="%s"/>' % (T['shown'], T['bw'], T['bh']))
for inst, ids in zip(TB_INSTANCES, [('a1', 'a2', 'a3'), ('b1', 'b2', 'b3')]):
    root = after(root, r'<ViewModelInstance [^>]*\bid="%s">' % inst, ''.join(
        '\n            <ViewModelInstanceNumber viewModelPropertyId="%s" id="%s"/>' % (T[prop], T[i])
        for prop, i in zip(['shown', 'bw', 'bh'], ids)))
root = after(root, r'\n[ \t]*<ScriptAsset [^>]*name="Pagination Pages"[^>]*/>',
             '\n    <ScriptAsset file="Tooltip Placement.luau" name="Tooltip Placement" id="%s"/>'
             '\n    <ScriptAsset file="Viewport.luau" name="Viewport" id="%s"/>' % (T['asset'], V['asset']))

# --- Theme Driver: the Viewport script in a box that fills the driver
drv = src['18-ThemeDriver.rml']
drv = before(drv, r'\n[ \t]*<LayoutComponentStyle id="%s"/>' % DRIVER_STYLE, '''
        <LayoutComponent styleId="{hstyle}" name="Viewport (script)" id="{host}">
            <ScriptedLayout scriptAssetId="{asset}" name="Viewport" id="{script}"/>
            <LayoutComponentStyle {fill} id="{hstyle}"/>
        </LayoutComponent>'''.format(fill=FILL, **V))

# --- Showcase: the driver as a fill overlay (still right after the thumbnail cover)
sc = src['11-Showcase.rml']
m = OLD_DRIVER.search(sc)
assert m, 'Theme Driver placement not found in the Showcase'
sc = sc[:m.start()] + '''
        <LayoutComponent styleId="{wstyle}" name="Theme Driver" id="{wrap}">
            <NestedArtboardLayout instanceWidthScaleType="fill" instanceHeightScaleType="fill" artboardId="{ab}" name="Theme Driver" id="{nested}">
                <NestedStateMachine animationId="{sm}" id="{nsm}"/>
            </NestedArtboardLayout>
            <LayoutComponentStyle {fill} id="{wstyle}"/>
        </LayoutComponent>'''.format(fill=FILL, ab=DRIVER_AB, sm=DRIVER_SM, **V) + sc[m.end():]

# --- Tooltip Button: everything that showed `placement` now shows `_placement`, plus the two script boxes
tb = src['34-TooltipButton.rml']
old_path, new_path = 'sourcePathIds="%s-%s"' % (TB_VM, TB_PLACEMENT), 'sourcePathIds="%s-%s"' % (TB_VM, T['shown'])
retargeted = tb.count(old_path)
tb = tb.replace(old_path, new_path)
nested = re.search(r'\n([ \t]*)<NestedArtboardLayout [^>]*artboardId="112:188"[^>]*>.*?</NestedArtboardLayout>', tb, re.S)
assert nested, 'Tooltip placement not found in Tooltip Button'
ind = nested.group(1)
inner = '\n'.join(('    ' + l if l.strip() else l) for l in nested.group(0).lstrip('\n').split('\n'))
tb = tb[:nested.start()] + '''
{i}<LayoutComponent styleId="{bstyle}" name="Bubble" id="{bubble}">
{inner}
{i}    <LayoutComponent styleId="{mstyle}" name="Bubble Size (script)" id="{mhost}">
{i}        <ScriptedLayout scriptAssetId="{asset}" name="Tooltip Placement" id="{mscript}">
{i}            <ScriptInputBoolean propertyValue="true" name="bubble" id="{minput}"/>
{i}        </ScriptedLayout>
{i}        <LayoutComponentStyle {fill} id="{mstyle}"/>
{i}    </LayoutComponent>
{i}    <LayoutComponentStyle {hug} id="{bstyle}"/>
{i}</LayoutComponent>'''.format(i=ind, inner=inner, fill=FILL, hug=HUG, **T) + tb[nested.end():]
tb = before(tb, r'\n[ \t]*<LayoutComponentStyle [^>]*id="112:307"/>', '''
            <LayoutComponent styleId="{hstyle}" name="Placement (script)" id="{host}">
                <ScriptedLayout scriptAssetId="{asset}" name="Tooltip Placement" id="{script}"/>
                <LayoutComponentStyle {fill} id="{hstyle}"/>
            </LayoutComponent>'''.format(fill=FILL, **T))
assert old_path not in tb

for n, s in [('99-_root.rml', root), ('18-ThemeDriver.rml', drv), ('11-Showcase.rml', sc), ('34-TooltipButton.rml', tb)]:
    open(p[n], 'w', encoding='utf-8').write(s)
print('tooltip_placement: Theme view values + Viewport script, Theme Driver as fill overlay, %d binds now follow _placement, '
      '2 Tooltip Placement boxes' % retargeted)
