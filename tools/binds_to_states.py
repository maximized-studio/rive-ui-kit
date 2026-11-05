"""Turn "pick one by number" formulas into state machine layers.

Usage: python3 tools/binds_to_states.py <dir>     (rewrites the .rml files in <dir> in place; safe to run again)

Many binds read one number (a Button's `variant`, an icon index, the Theme's `brandIndex`) through a lookup
formula such as `Is2` (1 when the number is 2, else 0) or `VariantStroke1` (1.75 when it is 1) to show one
option and hide the rest. For each job below this script:
1. builds one state per value of that number, whose animation sets every such object to what its formula gave,
2. adds those states as a layer to the artboard's state machine (Entry and Any State pick the state by value),
3. removes the binds, sets the objects' design values to the default state, and deletes converters nothing uses.
"""
import glob, math, os, re, sys

JOBS = [  # file, number it reads (bind path), layer name, id block, state names by value (None = "<layer> <n>")
    ('03-Button.rml', '1:151-118:1', 'Variant', 902, ['Primary', 'Secondary', 'Brand', 'Destructive']),
    ('03-Button.rml', '1:151-33:164', 'Icon', 903, None),
    ('32-Alert.rml', '110:223-110:226', 'Variant', 904, ['Info', 'Success', 'Warning', 'Error']),
    ('19-Segment.rml', '38:328-38:340', 'Icon', 905, None),
    ('12-Toolbar.rml', '10:7-10:2090', 'Brand Highlight', 906, ['Blue', 'Violet', 'Emerald', 'Orange', 'Rose', 'Inverse']),
    ('12-Toolbar.rml', '10:7-10:4743', 'Swatch Hover', 907, ['None', 'Blue', 'Violet', 'Emerald', 'Orange', 'Rose', 'Inverse']),
]
KEYS = {'18': ('opacity', 'KeyFrameDouble', 1.0), '47': ('thickness', 'KeyFrameDouble', 1.0),
        '596': ('displayValue', 'KeyFrameUint', 0)}
LOOKUP = re.compile(r'^(Is\d+|Hover\d+|VariantIs\d+|VariantStroke\d+|VariantHide\d+)$')

d = sys.argv[1]
root_p = os.path.join(d, '99-_root.rml')
root = open(root_p, encoding='utf-8').read()
OPS = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/', 'modulo': '%'}
FNS = {'min': 'min', 'max': 'max', 'pow': 'pow', 'round': 'round', 'floor': 'math.floor', 'ceil': 'math.ceil', 'abs': 'abs'}


def formula(body):
    e = ''
    for k, a in re.findall(r'<FormulaToken(\w+)([^>]*?)/?>', body):
        g = lambda n, dflt: (re.search(n + r'="([^"]*)"', a) or [None, dflt])[1]
        if k == 'Input': e += 'x'
        elif k == 'Value': e += g('operationValue', '1')
        elif k == 'Operation': e += OPS[g('operationType', 'add')]
        elif k == 'Function': e += FNS[g('functionType', 'min')] + '('
        elif k == 'ParenthesisOpen': e += '('
        elif k == 'ParenthesisClose': e += ')'
        elif k == 'ArgumentSeparator': e += ','
        else: return None  # reads other properties: not a pure lookup
    return e


conv = {}  # id -> (name, expression)
for m in re.finditer(r'<DataConverterFormula name="([^"]*)"[^>]*?\bid="([^"]+)">(.*?)</DataConverterFormula>', root, re.S):
    if LOOKUP.match(m.group(1)):
        e = formula(m.group(3))
        if e:
            conv[m.group(2)] = (m.group(1), e)
f_of = lambda e, x: eval(e, {'math': math, 'min': min, 'max': max, 'pow': pow, 'abs': abs, 'round': round, 'x': x})
TAG = re.compile(r'<(/?)(\w+)([^>]*?)(/?)>')


def default_value(path):
    """The value the number has in its default instance (the artboard's own, or the global Theme's)."""
    vm, prop = path.split('-')[0], path.split('-')[-1]
    m = re.search(r'<ViewModel [^>]*?defaultInstanceId="([^"]+)"[^>]*\bid="%s"' % re.escape(vm), root)
    blk = re.search(r'<ViewModelInstance [^>]*\bid="%s">(.*?)</ViewModelInstance>' % re.escape(m.group(1)), root, re.S)
    v = re.search(r'<ViewModelInstanceNumber ([^>]*)viewModelPropertyId="%s"' % re.escape(prop), blk.group(1))
    pv = re.search(r'propertyValue="([^"]*)"', v.group(1)) if v else None
    return int(float(pv.group(1))) if pv else 0


report = []
for fname, path, layer, block, labels in JOBS:
    fp = os.path.join(d, fname)
    s = open(fp, encoding='utf-8').read()
    sm_id = re.search(r'<Artboard [^>]*defaultStateMachineId="([^"]+)"', s).group(1)
    sm = re.search(r'<StateMachine [^>]*\bid="%s">' % re.escape(sm_id), s)
    sm_end = s.index('</StateMachine>', sm.end())
    if re.search(r'<StateMachineLayer name="%s"' % re.escape(layer), s[sm.end():sm_end]):
        continue
    # binds to convert, with their parent object (tracked with an element stack)
    stack, found = [], []
    for t in TAG.finditer(s):
        close, tag, attrs, selfc = t.groups()
        if close:
            stack.pop(); continue
        if tag == 'DataBindContext':
            src = re.search(r'sourcePathIds="([^"]+)"', attrs)
            cv = re.search(r'converterId="([^"]+)"', attrs)
            key = re.search(r'propertyKey="(\d+)"', attrs).group(1)
            if src and cv and src.group(1) == path and cv.group(1) in conv and key in KEYS:
                found.append((t.start(), t.end(), stack[-1], key, conv[cv.group(1)][1], conv[cv.group(1)][0]))
        if not selfc:
            stack.append((tag, (re.search(r'\bid="([^"]+)"', attrs) or [None, None])[1], t.start()))
    if not found:
        continue
    exprs = [e for *_, e, _ in found]
    top = max([x for x in range(0, 16) if any(f_of(e, x) != f_of(e, 99) for e in exprs)] + [0])
    values = list(range(top + 1))
    if labels:
        values = list(range(max(len(labels), top + 1)))
    keyed = set(re.findall(r'<KeyedObject objectId="([^"]+)"[^>]*>\s*<KeyedProperty property="(\w+)"', s))
    clash = [(o[1], KEYS[k][0]) for _, _, o, k, _, _ in found if (o[1], KEYS[k][0]) in keyed]
    assert not clash, '%s %s: already keyed elsewhere %s' % (fname, layer, clash)

    n = [0]
    def nid():
        n[0] += 1
        return '%d:%d' % (block, n[0])
    anims, states, entry, anyt = '', '', '', ''
    by_obj = {}
    for _, _, (tag, oid, _), key, e, _ in found:
        by_obj.setdefault(oid, []).append((key, e))
    state_ids = {}
    for k in values:
        aid, sid = nid(), nid()
        state_ids[k] = sid
        name = labels[k] if labels and k < len(labels) else '%s %d' % (layer, k)
        body = ''
        for oid, props in by_obj.items():
            kp = ''
            for key, e in props:
                pname, kf, _ = KEYS[key]
                v = f_of(e, k)
                v = int(round(v)) if kf == 'KeyFrameUint' else v
                kp += '<KeyedProperty property="%s" id="%s"><%s value="%g" id="%s"/></KeyedProperty>' % (pname, nid(), kf, v, nid())
            body += '<KeyedObject objectId="%s" id="%s">%s</KeyedObject>' % (oid, nid(), kp)
        anims += '\n        <LinearAnimation loopValue="loop" name="%s %s" id="%s">%s</LinearAnimation>' % (layer, name, aid, body)
        states += '<AnimationState animationId="%s" x="%d" y="%d" stateName="%s" id="%s"/>' % (aid, 160, -100 * len(values) // 2 + 100 * k, name, sid)
    def cond(k):
        val = ' value="%d"' % k if k else ''
        return ('<StateTransition stateToId="%s" id="%s"><TransitionViewModelCondition id="%s">'
                '<TransitionPropertyViewModelComparator id="%s"><BindablePropertyNumber id="%s">'
                '<DataBindContext sourcePathIds="%s" propertyKey="636" id="%s"/></BindablePropertyNumber>'
                '</TransitionPropertyViewModelComparator><TransitionValueNumberComparator%s id="%s"/>'
                '</TransitionViewModelCondition></StateTransition>') % (state_ids[k], nid(), nid(), nid(), nid(), path, nid(), val, nid())
    for k in values:
        entry += cond(k)
    for k in values:
        anyt += cond(k)
    layer_xml = ('<StateMachineLayer name="%s" id="%s"><AnyState x="400" id="%s">%s</AnyState><ExitState x="480" id="%s"/>'
                 '<EntryState id="%s">%s</EntryState>%s</StateMachineLayer>') % (layer, nid(), nid(), anyt, nid(), nid(), entry, states)

    # remove the binds (back to front) and set each object's design value to the default state
    dflt = default_value(path)
    for start, end, (tag, oid, ostart), key, e, _ in sorted(found, reverse=True):
        ls = s.rfind('\n', 0, start)
        s = s[:ls] + s[end:]
    for oid, props in by_obj.items():
        m = re.search(r'<(\w+) ([^>]*?)\bid="%s"' % re.escape(oid), s)
        attrs = m.group(2)
        for key, e in props:
            pname, kf, base = KEYS[key]
            v = f_of(e, dflt)
            attrs = re.sub(r'\s?\b%s="[^"]*"' % pname, '', attrs)
            if pname == 'displayValue':
                attrs += ('displayValue="none" ' if round(v) == 1 else '')
            elif v != base:
                attrs += '%s="%g" ' % (pname, v)
        s = s[:m.start(2)] + attrs + s[m.end(2):]
    sm_end = s.index('</StateMachine>', s.index('<StateMachine '))
    sm = re.search(r'<StateMachine [^>]*\bid="%s">' % re.escape(sm_id), s)
    sm_end = s.index('</StateMachine>', sm.end())
    s = s[:sm_end] + layer_xml + s[sm_end:]
    s = s[:sm.start()] + anims.lstrip('\n ') + '\n        ' + s[sm.start():]
    open(fp, 'w', encoding='utf-8').write(s)
    report.append('%s: layer %s, %d states, %d binds -> keys' % (fname, layer, len(values), len(found)))

# delete converters nothing references any more
removed = 0
while True:
    everything = ''.join(open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(d, '*.rml')))
    used = set(re.findall(r'converterId="([^"]+)"', everything))
    root = open(root_p, encoding='utf-8').read()
    dead = [i for i in conv if i not in used and re.search(r'\bid="%s"' % re.escape(i), root)]
    if not dead:
        break
    for i in dead:
        m = re.search(r'\n[ \t]*<DataConverterFormula [^>]*?\bid="%s">' % re.escape(i), root)
        end = root.index('</DataConverterFormula>', m.end()) + len('</DataConverterFormula>')
        root = root[:m.start()] + root[end:]
        removed += 1
    open(root_p, 'w', encoding='utf-8').write(root)
print('\n'.join(report + ['binds_to_states: %d lookup converters removed' % removed]))
