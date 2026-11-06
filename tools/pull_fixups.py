"""Repair gaps in what `rive create --from-remote-file` (CLI 1.8.0) writes, so a pulled folder builds.

Usage: python3 tools/pull_fixups.py <dir>

- The editor files global view models under a "Global View Models" DataGroup (type globalViewModels), but the
  pull leaves that DataGroup out while the view model keeps its groupId. Re-add the group, next to the others.
- The same happens to the "Scripts" AssetGroup (type scripts): script assets keep a groupId with no group.
  Re-add it next to the other AssetGroups.
"""
import glob, os, re, sys

d = sys.argv[1]
root_p = os.path.join(d, '99-_root.rml')
s = open(root_p, encoding='utf-8').read()
ids = set(re.findall(r'\bid="([^"]+)"', ''.join(open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(d, '*.rml')))))
missing = sorted({g for g in re.findall(r'<ViewModel [^>]*viewModelType="global"[^>]*groupId="([^"]+)"', s) if g not in ids})
for g in missing:
    anchor = re.search(r'\n([ \t]*)<DataGroup [^>]*/>', s)
    indent = anchor.group(1) if anchor else '    '
    line = '\n%s<DataGroup name="Global View Models" type="globalViewModels" id="%s"/>' % (indent, g)
    at = anchor.end() if anchor else s.rindex('</Rive>')
    s = s[:at] + line + s[at:]
    print('pull_fixups: re-added the Global View Models DataGroup %s' % g)
missing = sorted({g for g in re.findall(r'<ScriptAsset [^>]*groupId="([^"]+)"', s) if g not in ids})
for g in missing:
    anchor = list(re.finditer(r'\n([ \t]*)<AssetGroup [^>]*/>', s))
    indent = anchor[-1].group(1) if anchor else '    '
    line = '\n%s<AssetGroup type="scripts" name="Scripts" id="%s"/>' % (indent, g)
    at = anchor[-1].end() if anchor else s.index('>', s.index('<Rive')) + 1
    s = s[:at] + line + s[at:]
    print('pull_fixups: re-added the Scripts AssetGroup %s' % g)
open(root_p, 'w', encoding='utf-8').write(s)
