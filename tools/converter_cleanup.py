"""Tidy the converters that remain after theme_scales.py and binds_to_states.py.

Usage: python3 tools/converter_cleanup.py <dir>     (rewrites the .rml files in <dir> in place; safe to run again)

1. The Button group corners (left/right) carried their own copy of the Button radius table: they now read the
   `_radiusButton` token and only add the group part.
2. Renames every converter to "<Part> · <what it does>". Converters only the Showcase uses start with "Showcase".
Run it after tools/theme_scales.py (it needs `_radiusButton`).
"""
import glob, os, re, sys

THEME = '10:7'
RENAME = {
    # Showcase only
    'CanvasOpacity': 'Showcase · Canvas opacity',
    'GridTileWidth': 'Showcase · Grid tile width',
    'NextIdx': 'Showcase · Next slide',
    'PrevIdx': 'Showcase · Previous slide',
    'TrackOffsetPct': 'Showcase · Slide track offset',
    'PanelFullWidth': 'Showcase · Panel width',
    'PanelFullTmp': 'Showcase · Panel width (formula)',
    'DisabledNumberA': 'Showcase · Panel width / Disabled · Shield (to number)',
    'Hover Tint': 'Showcase · Hover tint',
    'Convert to Number 1': 'Showcase · Hover tint (to number)',
    'Formula 1': 'Showcase · Hover tint (formula)',
    'IndexLabelClean': 'Showcase · Slide number text',
    'PlusOne': 'Showcase · Slide number (+1)',
    'ToText': 'Showcase · Slide number (to text)',
    'NoZeros': 'Showcase · Slide number (no decimals)',
    'TileCountText': 'Showcase · Tile count text',
    'TileCount': 'Showcase · Tile count',
    # Shared text
    'CountTextClean': 'Text · Count',
    'CountText': 'Text · Count (to text)',
    'NoZeros2': 'Text · Count (no decimals)',
    # Disabled look, shared by many components
    'DisabledOn': 'Disabled · On (to number)',
    'DisabledShowShield': 'Disabled · Shield',
    'DisabledToDisplay': 'Disabled · Shield (formula)',
    'DisabledNoShadow': 'Disabled · No shadow',
    'DisabledNumberC': 'Disabled · No shadow (to number)',
    'ShadowAlpha': 'Disabled · No shadow (formula)',
    # Button
    'DisabledNoShadowGrouped': 'Button · No shadow in a group',
    'DisabledNumberG': 'Button · No shadow in a group (to number)',
    'ShadowAlphaGrouped': 'Button · No shadow in a group (formula)',
    'RadButtonLeft': 'Button · Group corner left',
    'RadButtonRight': 'Button · Group corner right',
    'GroupDividerHide': 'Button · Group divider',
    'IconOnlyPad': 'Button · Icon-only padding',
    'IconOnlyNum': 'Button · Icon-only padding (to number)',
    'IconOnlyPadF': 'Button · Icon-only padding (formula)',
    'SecondaryStroke': 'Button · Secondary border',
    'SecondaryNum': 'Button · Secondary border (to number)',
    'SecondaryStrokeF': 'Button · Secondary border (formula)',
    'IconNoneHide': 'Icon · Hide when none',
    # Checkbox, Slider
    'BoolToChecked': 'Checkbox · Checked (to number)',
    'RadOn': 'Slider · Rounded',
    'RadOff': 'Slider · Square',
    'SliderPercent': 'Slider · Percent',
    'SliderPercentString': 'Slider · Percent (to text)',
    'SliderPercentText': 'Slider · Percent text',
    'SliderPositionToPercentage': 'Slider · Position (0–1)',
    # Utils
    'Toggle': 'Utils · Toggle',
    'Trigger 1': 'Utils · Fire trigger',
}

d = sys.argv[1]
paths = sorted(glob.glob(os.path.join(d, '*.rml')))
files = {p: open(p, encoding='utf-8').read() for p in paths}
root_p = os.path.join(d, '99-_root.rml')
root = files[root_p]
ids = {n: i for n, i in re.findall(r'<DataConverter\w+ name="([^"]*)"[^>]*?\bid="([^"]+)"', root)}
done = []

# 2. Button group corners read the radius token; their formula keeps only the group part
tok = re.search(r'<ViewModelPropertyNumber name="_radiusButton" id="([^"]+)"', root)
assert tok, 'run tools/theme_scales.py first'
block = 911
counter = [0]
for name in ('RadButtonLeft', 'RadButtonRight'):
    cid = ids.get(name) or ids.get(RENAME[name])
    m = re.search(r'(<DataConverterFormula [^>]*\bid="%s">)(.*?)(</DataConverterFormula>)' % re.escape(cid), root, re.S)
    body = m.group(2)
    toks = list(re.finditer(r'\n[ \t]*<FormulaToken(\w+)[^>]*?(/?)>(?:\s*<DataBindContext[^>]*/>\s*</FormulaToken\w+>)?', body))
    if toks[0].group(1) == 'ParenthesisOpen':  # still starts with the lookup table "( 4*... + 8*... + 20*... )"
        depth = 0
        for j, t in enumerate(toks):
            depth += {'ParenthesisOpen': 1, 'Function': 1, 'ParenthesisClose': -1}.get(t.group(1), 0)
            if depth == 0:
                break
        counter[0] += 1
        indent = re.match(r'\n[ \t]*', toks[0].group(0)).group(0)
        body = body[:toks[0].start()] + '%s<FormulaTokenInput id="%d:%d"/>' % (indent, block, counter[0]) + body[toks[j].end():]
        root = root[:m.start(2)] + body + root[m.end(2):]
        done.append('%s reads _radiusButton' % name)
    files[root_p] = root
    for p, s in files.items():
        files[p] = re.sub(r'(<DataBindContext sourcePathIds=")%s-10:2086("[^>]*converterId="%s")' % (THEME, re.escape(cid)),
                          r'\g<1>%s-%s\2' % (THEME, tok.group(1)), s)
root = files[root_p]

# 3. Names
n = 0
for old, new in RENAME.items():
    root, k = re.subn(r'(<DataConverter\w+ )name="%s"' % re.escape(old), r'\1name="%s"' % new, root)
    n += k
files[root_p] = root
done.append('%d converters renamed' % n)

for p, s in files.items():
    open(p, 'w', encoding='utf-8').write(s)
print('converter_cleanup: ' + ', '.join(done))
