"""Split an editor-converted scene.rml into one file per artboard plus _root.rml."""
import re, sys, os
src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding='utf-8').read().split('\n')
assert lines[0].startswith('<Rive')
body = lines[1:lines.index('</Rive>')]
blocks, cur, name = [], [], None
for l in body:
    m = re.match(r'^    <Artboard\b.*?\bname="([^"]+)"', l)
    if m or (re.match(r'^    <[A-Z]', l) and name and not l.startswith('    </')):
        if cur: blocks.append((name, cur))
        cur, name = [], (m.group(1) if m else None)
    cur.append(l)
if cur: blocks.append((name, cur))
os.makedirs(out, exist_ok=True)
root, i = [], 0
for name, b in blocks:
    if name is None:
        root += b; continue
    i += 1
    fn = f"{i:02d}-{name.replace(' ', '')}.rml"
    open(os.path.join(out, fn), 'w').write('<Rive version="1" kind="fragment">\n' + '\n'.join(b).rstrip() + '\n</Rive>\n')
    print(fn, len(b))
open(os.path.join(out, '99-_root.rml'), 'w').write('<Rive version="1" kind="fragment">\n' + '\n'.join(root).rstrip() + '\n</Rive>\n')
print('99-_root.rml', len(root))
