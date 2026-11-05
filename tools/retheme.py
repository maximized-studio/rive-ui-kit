"""Write a themed Theme Driver from the shared one and a palette.json.

palette.json:
  "mode":   {"Light": {"_bg": "#rrggbb" | "#aarrggbb", ...}, "Dark": {...}}   (any token may be left out)
  "brands": {"Blue": ["#50", "#100", ..., "#950"], ...}                       (11 stops, names = Theme Bar slots)
  "defaults": {"roundness": 0-3, "shadow": 0-3}                                (optional: the Theme's starting values)
Optional 4th/5th args (99-_root.rml in/out) also set the Theme view model instance's stored colours, which is what
captures and Community thumbnails show (they render without the state machine).
Brand Light/Dark variants follow the base kit's rule: Dark puts 950/900 in the 100/200 slots;
soft tokens are 100/300/600 (Light) and 200/300/900 (Dark); info tokens are 50/200/700 (Light) and 950/800/400 (Dark).
Semantic mode tokens (_successBg/_successBorder/_successText, _warning…, _error…) and the Button tokens
(_primaryBg/_primaryHover/_primaryText, _danger…) go in "mode" like the others.
"""
import json, re, sys
src, palette_path, out = sys.argv[1:4]
pos = [a for a in sys.argv[4:] if not a.startswith('--')]
if '--bake' in sys.argv: pos = [a for a in pos if a != sys.argv[sys.argv.index('--bake') + 1]]
root_src, root_out = (pos + [None, None])[:2]  # optional: also theme the stored Theme instance values
s = open(src, encoding='utf-8').read()
pal = json.load(open(palette_path))

# Theme view model property ids (10:7 = Theme)
PROPS = {'_bg': '10:7402', '_bgClear': '10:7404', '_surface': '10:7406', '_surfaceMuted': '10:7408',
         '_surfaceMutedClear': '10:7410', '_surfaceSubtle': '10:7412', '_surfaceRaised': '10:7414',
         '_surfaceHover': '10:7416', '_border': '10:7418', '_borderStrong': '10:7420', '_text': '10:7422',
         '_textSecondary': '10:7424', '_textMuted': '10:7426', '_softBg': '10:8486', '_softBorder': '10:8488',
         '_softText': '10:8490',
         '_infoBg': '110:1', '_infoBorder': '110:2', '_infoText': '110:3',
         '_successBg': '110:4', '_successBorder': '110:5', '_successText': '110:6',
         '_warningBg': '110:7', '_warningBorder': '110:8', '_warningText': '110:9',
         '_errorBg': '110:10', '_errorBorder': '110:11', '_errorText': '110:12',
         '_primaryBg': '118:2', '_primaryHover': '118:3', '_primaryText': '118:4',
         '_dangerBg': '118:5', '_dangerHover': '118:6', '_dangerText': '118:7'}
STOPS = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900', '950']
for i, st in enumerate(STOPS):
    PROPS['_brand' + st] = f'10:{2092 + 2 * i}'

def argb(c):
    c = c.lstrip('#').upper()
    return ('FF' + c) if len(c) == 6 else c

def brand(ramp, dark):
    r = dict(zip(STOPS, ramp))
    t = {'_brand' + k: v for k, v in r.items()}
    if dark:
        t.update(_brand100=r['950'], _brand200=r['900'], _softBg=r['200'], _softBorder=r['300'], _softText=r['900'],
                 _infoBg=r['950'], _infoBorder=r['800'], _infoText=r['400'])
    else:
        t.update(_softBg=r['100'], _softBorder=r['300'], _softText=r['600'],
                 _infoBg=r['50'], _infoBorder=r['200'], _infoText=r['700'])
    return t

targets = {}  # animation name -> {prop id: ARGB}
for mode, toks in pal.get('mode', {}).items():
    targets[f'Mode {mode}'] = {PROPS[k]: argb(v) for k, v in toks.items()}
for name, ramp in pal.get('brands', {}).items():
    assert len(ramp) == 11, f'{name}: need 11 stops'
    for mode in ('Light', 'Dark'):
        targets[f'Brand {name} {mode}'] = {PROPS[k]: argb(v) for k, v in brand(ramp, mode == 'Dark').items()}

# solid color id -> prop id
sc = {m.group(1): m.group(2) for m in re.finditer(
    r'<SolidColor colorValue="\w+" id="([\d:]+)">\s*<DataBindContext sourcePathIds="10:7-([\d:]+)"', s)}

base_from = {}
def anim(m):
    name, body = m.group(2), m.group(3)
    t = targets.get(name)
    if not t:
        return m.group(0)
    def kf(k):
        prop = sc.get(k.group(1))
        return k.group(0) if prop not in t else re.sub(r'(<KeyFrameColor value=")\w+', r'\g<1>' + t[prop], k.group(0))
    body = re.sub(r'<KeyedObject objectId="([\d:]+)".*?</KeyedObject>', kf, body, flags=re.S)
    return m.group(1) + body + '</LinearAnimation>'
s = re.sub(r'(<LinearAnimation[^>]*name="([^"]+)"[^>]*>)(.*?)</LinearAnimation>', anim, s, flags=re.S)

# Base (design-time) values = the default state: Dark mode + first brand, so captures/thumbnails match.
base = {}
base.update(targets.get('Mode Dark', {}))
first = next(iter(pal.get('brands', {})), None)
if first:
    base.update(targets[f'Brand {first} Dark'])
s = re.sub(r'(<SolidColor colorValue=")(\w+)(" id="([\d:]+)">)',
           lambda m: m.group(1) + base.get(sc.get(m.group(4)), m.group(2)) + m.group(3), s)
open(out, 'w', encoding='utf-8').write(s)
print(f'{out}: {len(targets)} animations themed')

if root_src:
    r = open(root_src, encoding='utf-8').read()
    n = 0
    def inst(m):
        global n
        c = base.get(m.group(2))
        if not c:
            return m.group(0)
        n += 1
        return re.sub(r'(propertyValue|playbackValue)="\w+"', lambda k: f'{k.group(1)}="{c}"', m.group(0))
    r = re.sub(r'<ViewModelInstanceColor ([^>]*)viewModelPropertyId="([\d:]+)"[^>]*/>', inst, r)
    NUMS = {'roundness': '10:2086', 'shadow': '10:2088', 'mode': '10:7400', 'brandIndex': '10:2090'}
    for key, val in pal.get('defaults', {}).items():
        def num(m):
            attrs = re.sub(r' ?(propertyValue|playbackValue)="[^"]*"', '', m.group(1))
            v = f' propertyValue="{val}" playbackValue="{val}"' if val else ''
            return f'<ViewModelInstanceNumber{v}{attrs} viewModelPropertyId="{NUMS[key]}"'
        r, k = re.subn(r'<ViewModelInstanceNumber([^>]*?) viewModelPropertyId="' + NUMS[key] + '"', num, r)
        print(f'{root_out}: default {key} = {val} ({k}x)')
    open(root_out, 'w', encoding='utf-8').write(r)
    print(f'{root_out}: {n} stored Theme colours themed')

# Optional --bake <dir>: also write the base colours into every SolidColor bound to a Theme colour,
# so the editor stage, captures and thumbnails (which show authored values) match the theme.
if '--bake' in sys.argv:
    import glob, os
    bake_dir = sys.argv[sys.argv.index('--bake') + 1]
    total = 0
    for f in sorted(glob.glob(os.path.join(bake_dir, '*.rml'))):
        t = open(f, encoding='utf-8').read()
        cnt = 0
        def solid(m):
            global cnt
            c = base.get(m.group(4).split('-')[-1])
            if not c:
                return m.group(0)
            cnt += 1
            # keep the authored alpha: hover/highlight overlays are authored transparent on purpose
            return m.group(1) + m.group(2)[:2] + c[2:] + m.group(3)
        t2 = re.sub(r'(<SolidColor colorValue=")(\w+)("[^>]*>\s*<DataBindContext sourcePathIds="([\d:\-]+)" propertyKey="37")', solid, t)
        if cnt:
            open(f, 'w', encoding='utf-8').write(t2)
            total += cnt
    print(f'{bake_dir}: {total} bound colours baked')

    # Theme Bar swatches are plain fills (no bind): show each brand slot's 600 stop.
    for f in glob.glob(os.path.join(bake_dir, '*ThemeBar*.rml')):
        t = open(f, encoding='utf-8').read()
        def dot(m):
            ramp = pal.get('brands', {}).get(m.group(2))
            return m.group(0) if not ramp else re.sub(r'(<SolidColor colorValue=")\w+', r'\g<1>' + argb(ramp[6]), m.group(0), count=1)
        t, n = re.subn(r'(name="Dot (\w+)".*?<SolidColor colorValue="\w+" id="[\d:]+"/>)', dot, t, flags=re.S)
        open(f, 'w', encoding='utf-8').write(t)
        print(f'{f}: {n} swatches')

# With --bake and "defaults": also write what the roundness/shadow binds compute (corner radii, shadow feather,
# segment highlights) into the authored values, so the editor and thumbnail show the theme's starting look.
if '--bake' in sys.argv and pal.get('defaults'):
    import glob, math, os, xml.dom.minidom as md
    bake_dir = sys.argv[sys.argv.index('--bake') + 1]
    SRC = {'10:2086': 'roundness', '10:2088': 'shadow'}
    ATTR = {'640': 'cornerRadiusTL', '31': 'cornerRadiusTL', '18': 'opacity', '749': 'strength', '751': 'offsetY'}
    FN = ['min', 'max', 'rnd', 'math.ceil', 'math.floor', 'math.sqrt', 'pow', 'math.exp', 'math.log', 'math.cos',
          'math.sin', 'math.tan', 'math.acos', 'math.asin', 'math.atan', 'math.atan2']
    OPS = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/', 'modulo': '%'}
    rnd = lambda v: math.floor(v + 0.5)
    root_xml = open(os.path.join(bake_dir, '99-_root.rml'), encoding='utf-8').read()
    formulas = {}
    for m in re.finditer(r'<DataConverterFormula [^>]*id="([\d:]+)">(.*?)</DataConverterFormula>', root_xml, re.S):
        expr = ''
        for tok, attrs in re.findall(r'<(FormulaToken\w+)([^>]*?)/?>', m.group(2)):
            a = dict(re.findall(r'(\w+)="([^"]*)"', attrs))
            if tok == 'FormulaTokenInput': expr += 'x'
            elif tok == 'FormulaTokenValue': expr += a.get('operationValue', '1')
            elif tok == 'FormulaTokenOperation': expr += OPS[a.get('operationType', 'add')]
            elif tok == 'FormulaTokenFunction':
                ft = a.get('functionType', 'min')
                ft = int(ft) if ft.isdigit() else ['min', 'max', 'round', 'ceil', 'floor', 'sqrt', 'pow', 'exp', 'log', 'cosine',
                      'sine', 'tangent', 'acosine', 'asine', 'atangent', 'atangent2'].index(ft)
                expr += FN[ft] + '('
            elif tok == 'FormulaTokenParenthesisOpen': expr += '('
            elif tok == 'FormulaTokenParenthesisClose': expr += ')'
            elif tok == 'FormulaTokenArgumentSeparator': expr += ','
        formulas[m.group(1)] = expr
    baked = 0
    for f in sorted(glob.glob(os.path.join(bake_dir, '*.rml'))):
        doc = md.parse(f)
        changed = False
        for b in doc.getElementsByTagName('DataBindContext'):
            src = b.getAttribute('sourcePathIds').split('-')[-1]
            key, conv = b.getAttribute('propertyKey'), b.getAttribute('converterId')
            if src not in SRC or key not in ATTR or SRC[src] not in pal['defaults']:
                continue
            x = pal['defaults'][SRC[src]]
            try:
                v = eval(formulas[conv], {'math': math, 'rnd': rnd, 'x': x}) if conv else x
            except Exception as e:
                print(f'  skip {conv}: {formulas.get(conv)} ({e})'); continue
            target = b.parentNode
            target.setAttribute(ATTR[key], f'{v:g}')
            changed = True; baked += 1
        if changed:
            out = doc.toxml().replace('<?xml version="1.0" ?>', '', 1).lstrip()
            open(f, 'w', encoding='utf-8').write(out)
    print(f'{bake_dir}: {baked} roundness/shadow values baked')
