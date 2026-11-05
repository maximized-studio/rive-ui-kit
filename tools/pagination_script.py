"""Give Pagination its behaviour as one Luau script instead of 14 slot formulas and a trigger relay.

Usage: python3 tools/pagination_script.py <dir>     (rewrites <dir> in place; safe to run again)

- Copies tools/scripts/PaginationPages.luau into <dir> and declares it as a ScriptAsset.
- Pagination gets a `_pages` list; the seven fixed "Slot" layouts become one list of Page Items.
- A small absolute layout holds the script (a ScriptedLayout, so it can read and write the view model).
- The Previous/Next layers, their four listeners and the `_atStart` … `_notAtEnd` triggers go: the script
  sets `_prevDisabled` / `_nextDisabled` itself.
- Converters nothing uses any more (the PageSlot formulas) are deleted.
"""
import glob, os, re, shutil, sys

d = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
SCRIPT = 'PaginationPages.luau'
VM, ARTBOARD_FILE, INSTANCE = '102:7', '27-Pagination.rml', '102:20'
IDS = dict(prop='912:1', value='912:2', asset='912:3', host='912:4', script='912:5', style='912:6', list='912:7', bind='912:8')
TRIGGERS = ['102:15', '102:16', '102:17', '102:18']

root_p, pg_p = os.path.join(d, '99-_root.rml'), os.path.join(d, ARTBOARD_FILE)
root, pg = open(root_p, encoding='utf-8').read(), open(pg_p, encoding='utf-8').read()
shutil.copy(os.path.join(here, 'scripts', SCRIPT), os.path.join(d, SCRIPT))
if 'id="%s"' % IDS['prop'] in root:
    print('pagination_script: already converted (script file refreshed)')
    sys.exit(0)


def drop_block(s, tag, pattern):
    """Remove every <tag> element whose attributes match pattern, with its children."""
    n = 0
    while True:
        m = re.search(r'\n[ \t]*<(%s) ' % tag + pattern + r'[^>]*?(/?)>', s)
        if not m:
            return s, n
        if m.group(2):
            end = m.end()
        else:
            depth, pos = 1, m.end()
            for t in re.finditer(r'<(/?)%s\b[^>]*?(/?)>' % m.group(1), s[pos:]):
                if t.group(2):
                    continue
                depth += -1 if t.group(1) else 1
                if depth == 0:
                    end = pos + t.end()
                    break
        s = s[:m.start()] + s[end:]
        n += 1


# view model: the list, without the trigger relay
vm_open = re.search(r'<ViewModel [^>]*\bid="%s">' % VM, root)
last_prop = list(re.finditer(r'\n[ \t]*<ViewModelProperty\w+ [^>]*/>', root[vm_open.end():root.index('<ViewModelInstance ', vm_open.end())]))[-1]
at = vm_open.end() + last_prop.end()
root = root[:at] + '\n        <ViewModelPropertyList name="_pages" id="%s"/>' % IDS['prop'] + root[at:]
inst = re.search(r'<ViewModelInstance [^>]*\bid="%s">' % INSTANCE, root)
root = root[:inst.end()] + '\n            <ViewModelInstanceList viewModelPropertyId="%s" id="%s"/>' % (IDS['prop'], IDS['value']) + root[inst.end():]
for t in TRIGGERS:
    root = re.sub(r'\n[ \t]*<ViewModelPropertyTrigger [^>]*\bid="%s"/>' % t, '', root)
    root = re.sub(r'\n[ \t]*<ViewModelInstanceTrigger [^>]*viewModelPropertyId="%s"[^>]*/>' % t, '', root)
first = re.search(r'\n[ \t]*<(AssetGroup|ComponentAsset|ScriptAsset)\b', root)
root = root[:first.start()] + '\n    <ScriptAsset file="%s" name="Pagination Pages" id="%s"/>' % (SCRIPT, IDS['asset']) + root[first.start():]

# artboard: one list instead of seven slots, the script host, no trigger relay
first_slot = re.search(r'\n[ \t]*<LayoutComponent [^>]*name="Slot 1"', pg).start()
pg, slots = drop_block(pg, 'LayoutComponent', r'[^>]*name="Slot \d"')
pg = pg[:first_slot] + ('\n                <ArtboardComponentList name="Pages" participatesInLayout="true" id="%s">'
                        '\n                    <DataBindContext sourcePathIds="%s-%s" propertyKey="800" id="%s"/>'
                        '\n                </ArtboardComponentList>') % (IDS['list'], VM, IDS['prop'], IDS['bind']) + pg[first_slot:]
pg, listeners = drop_block(pg, 'StateMachineListener', r'[^>]*name="(?:Disable|Enable) (?:previous|next)"')
pg, layers = drop_block(pg, 'StateMachineLayer', r'name="(?:Previous|Next)"')
sm = pg.index('\n        <StateMachine ')
pg = pg[:sm] + ('\n        <LayoutComponent width="1" height="1" styleId="%s" name="Pagination Pages (script)" id="%s">'
                '\n            <ScriptedLayout scriptAssetId="%s" name="Pagination Pages" id="%s"/>'
                '\n            <LayoutComponentStyle positionTypeValue="absolute" id="%s"/>'
                '\n        </LayoutComponent>') % (IDS['style'], IDS['host'], IDS['asset'], IDS['script'], IDS['style']) + pg[sm:]
assert not any('viewModelPathIds="%s-%s"' % (VM, t) in pg for t in TRIGGERS), 'trigger still used'

open(root_p, 'w', encoding='utf-8').write(root)
open(pg_p, 'w', encoding='utf-8').write(pg)

# converters nothing uses any more
removed = 0
while True:
    everything = ''.join(open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(d, '*.rml')))
    used = set(re.findall(r'converterId="([^"]+)"', everything))
    root = open(root_p, encoding='utf-8').read()
    dead = [i for i in re.findall(r'<DataConverterFormula name="Pagination[^"]*"[^>]*?\bid="([^"]+)"', root) +
            re.findall(r'<DataConverterFormula name="PageSlot[^"]*"[^>]*?\bid="([^"]+)"', root) if i not in used]
    if not dead:
        break
    for i in dead:
        root, _ = drop_block(root, 'DataConverterFormula', r'[^>]*\bid="%s"' % re.escape(i))
        removed += 1
    open(root_p, 'w', encoding='utf-8').write(root)
print('pagination_script: %d slots -> 1 list, %d listeners and %d layers removed, %d converters removed'
      % (slots, listeners, layers, removed))
