"""Make the Theme view model global and drive it from one Theme Driver.

Usage: python3 tools/globalize_theme.py <dir>     (rewrites the .rml files in <dir> in place; run it on a copy or on shared/)

What it does (safe to run again on an already converted folder):
1. Marks Theme (10:7) as a global view model: one instance every artboard reads, owned by none.
2. Rewrites every bind path that went through a component's own `theme` property
   (`<VM>-<theme prop>-<token>`) to read the global directly (`10:7-<token>`), without name-based lookup.
3. Deletes those per-component `theme` properties and their instance values: components keep only their own data.
4. Removes the Theme Driver copy nested in each component and places one in the Showcase
   (right after the thumbnail cover, which must stay the first child).
5. Unbinds the Theme Driver artboard itself: its binds already start at the global.
"""
import glob, os, re, sys

THEME, DRIVER_AB, DRIVER_SM = '10:7', '10:14621', '10:14626'
SHOWCASE = '11-Showcase.rml'
DRIVER_ID = ('900:1', '900:2')  # fixed ids in an unused block, so a second run (and a push/pull round trip) keeps them

d = sys.argv[1]
files = {f: open(f, encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(d, '*.rml')))}
everything = ''.join(files.values())
refs = set(re.findall(r'<ViewModelPropertyViewModel viewModelReferenceId="%s"[^>]*\bid="([^"]+)"' % THEME, everything))
used_ids = set(re.findall(r'\bid="([^"]+)"', everything))
already = 'name="Theme Driver" id="%s"' % DRIVER_ID[0] in everything
for i in DRIVER_ID:
    assert already or i not in used_ids, 'id %s is already taken; pick another block for DRIVER_ID' % i

PATH = re.compile(r'((?:sourcePathIds|dataBindPathIds|viewModelPathIds)=")([^"]+)"')
NESTED_DRIVER = re.compile(r'\n[ \t]*<NestedArtboard artboardId="%s"[^>]*>\s*<NestedStateMachine[^>]*/>\s*</NestedArtboard>' % DRIVER_AB)
stats = dict(paths=0, props=0, values=0, drivers=0)


def global_path(m):
    ids = m.group(2).split('-')
    for i, x in enumerate(ids):
        if x in refs and i + 1 < len(ids):
            stats['paths'] += 1
            return '%s%s-%s"' % (m.group(1), THEME, '-'.join(ids[i + 1:]))
    return m.group(0)


for f, s in files.items():
    name = os.path.basename(f)
    s = PATH.sub(global_path, s)
    # A bind into the global is absolute: drop name-based lookup, or it resolves `roundness` etc. through the
    # placement's own data (the Theme panel's segments came out square, its slider half disabled).
    s = re.sub(r'(<DataBindContext sourcePathIds="%s-[^"]*"[^>]*?) nameBased="true"' % THEME, r'\1', s)
    s, n = re.subn(r'\n[ \t]*<ViewModelPropertyViewModel viewModelReferenceId="%s"[^>]*/>' % THEME, '', s)
    stats['props'] += n
    if refs:
        s, n = re.subn(r'\n[ \t]*<ViewModelInstanceViewModel[^>]*viewModelPropertyId="(?:%s)"[^>]*/>'
                       % '|'.join(map(re.escape, refs)), '', s)
        stats['values'] += n
    s = s.replace('<ViewModel defaultInstanceId="10:63" name="Theme"',
                  '<ViewModel viewModelType="global" defaultInstanceId="10:63" name="Theme"')
    if name == '18-ThemeDriver.rml':
        s = s.replace(' viewModelId="%s" viewModelInstanceId="10:63"' % THEME, '', 1)
    if name != SHOWCASE:
        s, n = NESTED_DRIVER.subn('', s)
        stats['drivers'] += n
    elif 'id="%s"' % DRIVER_ID[0] not in s:
        cover = re.search(r'\n[ \t]*<Image [^>]*name="Cover \(thumbnail only\)"[^>]*/>', s)
        at = cover.end() if cover else s.index('>', s.index('<Artboard ')) + 1
        s = s[:at] + ('\n        <NestedArtboard artboardId="%s" name="Theme Driver" id="%s">'
                      '\n            <NestedStateMachine animationId="%s" id="%s"/>'
                      '\n        </NestedArtboard>') % (DRIVER_AB, DRIVER_ID[0], DRIVER_SM, DRIVER_ID[1]) + s[at:]
    files[f] = s

left = sum(1 for s in files.values() for m in PATH.finditer(s) if set(m.group(2).split('-')) & refs)
assert left == 0, '%d bind paths still go through a theme property' % left
for f, s in files.items():
    open(f, 'w', encoding='utf-8').write(s)
print('globalize_theme: %(paths)d paths rewritten, %(props)d theme properties and %(values)d values removed, '
      '%(drivers)d nested drivers removed' % stats)
