"""Removes a component from the Showcase in shared/99-_root.rml: its tile, slide, sidebar nav item and breadcrumbs.
Later slots move down by one. The counterpart of showcase_add.py.
Usage: python3 tools/showcase_remove.py "<Title>" <Section>"""
import re, sys

ROOT = 'shared/99-_root.rml'
SLOT = {'S': '10:5175', 'T': '10:4567', 'Nav': '41:870'}
title, section = sys.argv[1:3]
s = open(ROOT).read()

def block(name):
    return re.search(r'\n *<ViewModelInstance exports="true" name="%s" id="([^"]+)">.*?</ViewModelInstance>' % re.escape(name), s, re.S)
slot = int(re.search(r'propertyValue="(\d+)" viewModelPropertyId="%s"' % SLOT['T'], block(f'T {title}').group(0)).group(1)) \
    if re.search(r'propertyValue="(\d+)" viewModelPropertyId="%s"' % SLOT['T'], block(f'T {title}').group(0)) else 0
ids = {}
for name in (f'S {title}', f'T {title}', f'Nav {title}', f'Showcase {title}', f'Showcase {title} / All components', f'Showcase {title} / {title}'):
    m = block(name)
    if not m: sys.exit(f'missing instance {name}')
    ids[name] = m.group(1)
    s = s[:m.start()] + s[m.end():]
for iid in ids.values():   # list entries that pointed at them
    s = re.sub(r'\n *<ViewModelInstanceListItem [^>]*viewModelInstanceId="%s"[^>]*/>' % re.escape(iid), '', s)

def bump(m):
    body = m.group(0)
    for prefix, key in SLOT.items():
        if m.group(1).startswith(prefix + ' '):
            body = re.sub(r'propertyValue="(\d+)" viewModelPropertyId="%s"' % key,
                          lambda k: f'propertyValue="{int(k.group(1)) - 1}" viewModelPropertyId="{key}"' if int(k.group(1)) > slot else k.group(0), body)
            body = body.replace(f'propertyValue="0" viewModelPropertyId="{key}"', f'viewModelPropertyId="{key}"')
    return body
s = re.sub(r'<ViewModelInstance exports="true" name="((?:S|T|Nav) [^"]+)" id="[^"]+">.*?</ViewModelInstance>', bump, s, flags=re.S)
def dec(container, prop):
    global s
    m = re.search(r'<ViewModelInstance exports="true" name="%s" id="[^"]+">.*?</ViewModelInstance>' % re.escape(container), s, re.S)
    new = re.sub(r'propertyValue="(\d+)" viewModelPropertyId="%s"' % prop, lambda k: f'propertyValue="{int(k.group(1)) - 1}" viewModelPropertyId="{prop}"', m.group(0), count=1)
    s = s[:m.start()] + new + s[m.end():]
dec(section, '41:882'); dec('Showcase', '10:5576')
open(ROOT, 'w').write(s)
print(f'removed {title} (slot {slot})')
