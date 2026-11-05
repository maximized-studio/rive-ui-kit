"""Replace the per-component roundness/shadow formulas with Theme scale tokens.

Usage: python3 tools/theme_scales.py <dir>     (rewrites the .rml files in <dir> in place; safe to run again)

Reads tools/scales.json (token -> four values, one per roundness/shadow step) and:
1. Adds each token to the global Theme as a number, stored at the value for the Theme's current step.
2. Adds a Roundness and a Shadow layer to the Theme Driver: one state per step that writes every token
   of that scale (state actions, no keyframes).
3. Points every bind that read `roundness`/`shadow` through one of the replaced formulas at its token,
   without a converter.
4. Deletes converters that nothing uses any more.
Run it after tools/globalize_theme.py (it expects the global Theme, id 10:7).
"""
import glob, json, os, re, sys

THEME, DRIVER, BLOCK = '10:7', '18-ThemeDriver.rml', 901
SOURCES = {'roundness': '10:2086', 'shadow': '10:2088'}
here = os.path.dirname(os.path.abspath(__file__))
scales = json.load(open(os.path.join(here, 'scales.json')))
d = sys.argv[1]
paths = sorted(glob.glob(os.path.join(d, '*.rml')))
files = {p: open(p, encoding='utf-8').read() for p in paths}
root_p = os.path.join(d, '99-_root.rml')
drv_p = os.path.join(d, DRIVER)
root = files[root_p]

# Fixed ids: block 901, numbered in scales.json order, so a re-run and a push/pull round trip keep them.
counter = [0]
def nid():
    counter[0] += 1
    return '%d:%d' % (BLOCK, counter[0])

tokens = []  # (scale, name, values, replaces, prop_id, value_id)
for scale in ('roundness', 'shadow'):
    for name, spec in scales[scale].items():
        tokens.append((scale, name, spec['values'], spec['replaces'], nid(), nid()))

theme_start = root.index('name="Theme"')
theme_end = root.index('</ViewModel>', theme_start)
already = 'name="%s"' % tokens[0][1] in root[theme_start:theme_end]
if not already:
    taken = set(re.findall(r'\bid="(%d:\d+)"' % BLOCK, ''.join(files.values())))
    assert not taken, 'id block %d is in use: %s' % (BLOCK, sorted(taken)[:5])


def stored(src_id):
    m = re.search(r'<ViewModelInstanceNumber ([^>]*)viewModelPropertyId="%s"' % src_id, root[theme_start:theme_end])
    v = re.search(r'propertyValue="([^"]*)"', m.group(1)) if m else None
    return int(float(v.group(1))) if v else 0


step = {s: stored(i) for s, i in SOURCES.items()}
stats = dict(tokens=0, binds=0, removed=0)

if not already:
    props = ''.join('\n            <ViewModelPropertyNumber name="%s" id="%s"/>' % (n, p) for _, n, _, _, p, _ in tokens)
    anchor = re.search(r'\n[ \t]*<ViewModelPropertyNumber name="shadow" id="10:2088"/>', root)
    root = root[:anchor.end()] + props + root[anchor.end():]
    vals = ''.join('\n                <ViewModelInstanceNumber%s viewModelPropertyId="%s" id="%s"/>'
                   % ((' propertyValue="%g"' % v[step[s]]) if v[step[s]] else '', p, vi)
                   for s, _, v, _, p, vi in tokens)
    anchor = re.search(r'\n[ \t]*<ViewModelInstanceNumber [^>]*viewModelPropertyId="10:2088"[^>]*/>', root)
    root = root[:anchor.end()] + vals + root[anchor.end():]
    stats['tokens'] = len(tokens)

# Theme Driver: one layer per scale, a state per step that writes that step's values.
drv = files[drv_p]
if 'name="Roundness"' not in drv:
    hold = nid()
    def cond(src, k):
        a, b, c, e, f = nid(), nid(), nid(), nid(), nid()
        val = ' value="%d"' % k if k else ''
        return ('<TransitionViewModelCondition id="%s"><TransitionPropertyViewModelComparator id="%s">'
                '<BindablePropertyNumber id="%s"><DataBindContext sourcePathIds="%s-%s" propertyKey="636" id="%s"/>'
                '</BindablePropertyNumber></TransitionPropertyViewModelComparator>'
                '<TransitionValueNumberComparator%s id="%s"/></TransitionViewModelCondition>') % (a, b, c, THEME, src, e, val, f)
    layers = ''
    for x, scale in enumerate(('roundness', 'shadow')):
        src = SOURCES[scale]
        layer_id, any_id, exit_id, entry_id = nid(), nid(), nid(), nid()
        state_ids = [nid() for _ in range(4)]
        entry = ''.join('<StateTransition stateToId="%s" id="%s">%s</StateTransition>' % (state_ids[k], nid(), cond(src, k))
                        for k in range(4))
        anyt = ''.join('<StateTransition stateToId="%s" id="%s">%s</StateTransition>' % (state_ids[k], nid(), cond(src, k))
                       for k in range(4))
        states = ''
        for k in range(4):
            acts = ''.join('<ListenerViewModelChange id="%s"><BindablePropertyNumber propertyValue="%g" id="%s">'
                           '<DataBindContext sourcePathIds="%s-%s" propertyKey="636" direction="true" id="%s"/>'
                           '</BindablePropertyNumber></ListenerViewModelChange>' % (nid(), v[k], nid(), THEME, p, nid())
                           for s, _, v, _, p, _ in tokens if s == scale)
            states += '<AnimationState animationId="%s" x="%d" y="%d" stateName="%s %d" id="%s">%s</AnimationState>' % (
                hold, 160, -150 + 100 * k, scale.capitalize(), k, state_ids[k], acts)
        layers += ('<StateMachineLayer name="%s" id="%s"><AnyState x="400" id="%s">%s</AnyState><ExitState x="480" id="%s"/>'
                   '<EntryState id="%s">%s</EntryState>%s</StateMachineLayer>') % (
            scale.capitalize(), layer_id, any_id, anyt, exit_id, entry_id, entry, states)
    i = drv.index('</StateMachine>')
    drv = drv[:i] + layers + drv[i:]
    i = drv.index('<StateMachine ')
    drv = drv[:i] + '<LinearAnimation name="Scale Hold" id="%s"/>\n        ' % hold + drv[i:]
files[drv_p] = drv
files[root_p] = root

# Rebind: roundness/shadow + replaced formula -> the token, no converter.
conv_ids = {n: i for n, i in re.findall(r'<DataConverter\w+ name="([^"]*)"[^>]*?\bid="([^"]+)"', root)}
swap = {}
for s, _, _, reps, p, _ in tokens:
    for r in reps:
        if r in conv_ids:
            swap[(SOURCES[s], conv_ids[r])] = p
def rebind(m):
    tag = m.group(0)
    src = re.search(r'sourcePathIds="%s-([^"]+)"' % THEME, tag)
    cv = re.search(r' converterId="([^"]+)"', tag)
    key = (src.group(1), cv.group(1)) if src and cv else None
    if key not in swap:
        return tag
    stats['binds'] += 1
    tag = tag.replace(cv.group(0), '')
    return tag.replace('sourcePathIds="%s-%s"' % (THEME, key[0]), 'sourcePathIds="%s-%s"' % (THEME, swap[key]))
for p in files:
    files[p] = re.sub(r'<DataBindContext [^>]*/>', rebind, files[p])

# Delete converters nothing references any more (repeat: a group's items can free other converters).
while True:
    everything = ''.join(files.values())
    used = set(re.findall(r'converterId="([^"]+)"', everything))
    root = files[root_p]
    dead = [i for _, i in re.findall(r'\n[ \t]*<(DataConverter(?!GroupItem)\w+) [^>]*?\bid="([^"]+)"', root) if i not in used]
    if not dead:
        break
    for i in dead:
        m = re.search(r'\n[ \t]*<(DataConverter\w+) [^>]*?\bid="%s"[^>]*?(/?)>' % re.escape(i), root)
        end = m.end() if m.group(2) else root.index('</%s>' % m.group(1), m.end()) + len('</%s>' % m.group(1))
        root = root[:m.start()] + root[end:]
        stats['removed'] += 1
    files[root_p] = root

for p, s in files.items():
    open(p, 'w', encoding='utf-8').write(s)
print('theme_scales: %(tokens)d tokens added, %(binds)d binds now read a token, %(removed)d unused converters removed' % stats)
