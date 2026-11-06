"""Adds a component to the Showcase in shared/99-_root.rml: a tile, a slide, a sidebar nav item and the
slide's breadcrumbs, in its category A-Z. Later slots move up by one.

Usage: python3 tools/showcase_add.py "<Title>" <Section> <vmId> <slideInstanceId> <tileInstanceId> <zoom> <idClient>
  e.g. python3 tools/showcase_add.py "Chip Group" Inputs 141:9 141:70 141:70 1.8 142
New objects take ids <idClient>:<1..>, so pick a client number no .rml uses yet (one per component).
Section is one of the categories (Actions, Display, Feedback, Inputs, Navigation)."""
import re, sys, itertools

ROOT = 'shared/99-_root.rml'
SLIDE_VM, TILE_VM, NAV_VM, CRUMB_ITEM_VM, CRUMBS_VM = '10:5163', '10:3612', '41:862', '111:1', '111:9'
STAGE, NAV, CRUMB_SEL = '10:5193', '10:4585', '114:3'
SLOT = {'S': '10:5175', 'T': '10:4567', 'Nav': '41:870'}

title, section, vm, slide_inst, tile_inst, zoom, client = sys.argv[1:8]
ids = itertools.count(1)
def n(): return f'{client}:{next(ids)}'
s = open(ROOT).read()
if f'name="S {title}"' in s: sys.exit(f'{title} is already in the Showcase')

def block(name):
    m = re.search(r'( *)<ViewModelInstance exports="true" name="%s" id="([^"]+)">.*?</ViewModelInstance>\n' % re.escape(name), s, re.S)
    return m
def slot_of(prefix, name):
    m = block(f'{prefix} {name}')
    return int(re.search(r'propertyValue="([^"]+)" viewModelPropertyId="%s"' % SLOT[prefix], m.group(0)).group(1))

# Section tiles (ShowcaseSection "Sec <Section>") give the A-Z place and the slot
sec = block(f'Sec {section}')
tile_ids = re.findall(r'viewModelInstanceId="([^"]+)"', sec.group(0))
names = [re.search(r'name="T ([^"]+)" id="%s"' % re.escape(t), s).group(1) for t in tile_ids]
pos = sum(1 for x in names if x.lower() < title.lower())
slot = slot_of('T', names[pos - 1]) + 1 if pos else slot_of('T', names[0])
after = names[pos - 1] if pos else None
print(f'{title}: {section} position {pos}, slot {slot}')

# 1. Every slot >= the new one moves up by one (slides, tiles, nav items)
def bump(m):
    body = m.group(0)
    for prefix, key in SLOT.items():
        if m.group(1).startswith(prefix + ' '):
            body = re.sub(r'propertyValue="(\d+)" viewModelPropertyId="%s"' % key,
                          lambda k: f'propertyValue="{int(k.group(1)) + 1}" viewModelPropertyId="{key}"'
                          if int(k.group(1)) >= slot else k.group(0), body)
    return body
s = re.sub(r'<ViewModelInstance exports="true" name="((?:S|T|Nav) [^"]+)" id="[^"]+">.*?</ViewModelInstance>', bump, s, flags=re.S)

def num(prop, v): return f'<ViewModelInstanceNumber propertyValue="{v}" viewModelPropertyId="{prop}" id="{n()}"/>' if v != 0 else f'<ViewModelInstanceNumber viewModelPropertyId="{prop}" id="{n()}"/>'
def insert_after_instance(name, xml, fallback_vm):
    """Insert an instance block after instance `name` (same indent), or before the closing tag of `fallback_vm`."""
    global s
    m = block(name) if name else None
    if m:
        ind = m.group(1)
        s = s[:m.end()] + ''.join(ind + l + '\n' for l in xml) + s[m.end():]
    else:
        m = re.search(r'( *)<ViewModel [^>]*id="%s">.*?\n( *)</ViewModel>' % fallback_vm, s, re.S)
        ind = m.group(2) + '    '
        cut = m.end() - len(m.group(2)) - len('</ViewModel>')
        s = s[:cut] + ''.join(ind + l + '\n' for l in xml) + s[cut:]

# 2. Breadcrumbs: "All components" › <Title>
crumbs, c_all, c_cur = n(), n(), n()
item = lambda iid, label, cur: [
    f'<ViewModelInstance exports="true" name="Showcase {title} / {label}" id="{iid}">',
    f'    <ViewModelInstanceString propertyValue="{label}" viewModelPropertyId="111:2" id="{n()}"/>',
    f'    <ViewModelInstanceBoolean{" propertyValue=" + chr(34) + "true" + chr(34) if cur else ""} viewModelPropertyId="111:3" id="{n()}"/>',
    f'    <ViewModelInstanceSymbolListIndex viewModelPropertyId="111:4" id="{n()}"/>',
    f'    <ViewModelInstanceViewModel propertyValue="{CRUMB_SEL}" viewModelPropertyId="111:5" id="{n()}"/>',
    f'    <ViewModelInstanceBoolean viewModelPropertyId="111:6" id="{n()}"/>',
    f'    <ViewModelInstanceBoolean viewModelPropertyId="111:8" id="{n()}"/>',
    '</ViewModelInstance>']
insert_after_instance(None, item(c_all, 'All components', False) + item(c_cur, title, True), CRUMB_ITEM_VM)
insert_after_instance(None, [
    f'<ViewModelInstance exports="true" name="Showcase {title}" id="{crumbs}">',
    f'    <ViewModelInstanceList viewModelPropertyId="111:10" id="{n()}">',
    f'        <ViewModelInstanceListItem viewModelId="{CRUMB_ITEM_VM}" viewModelInstanceId="{c_all}" id="{n()}"/>',
    f'        <ViewModelInstanceListItem viewModelId="{CRUMB_ITEM_VM}" viewModelInstanceId="{c_cur}" id="{n()}"/>',
    '    </ViewModelInstanceList>',
    f'    <ViewModelInstanceNumber propertyValue="-1" viewModelPropertyId="111:11" id="{n()}"/>',
    f'    <ViewModelInstanceString propertyValue="Breadcrumb" viewModelPropertyId="111:12" id="{n()}"/>',
    f'    <ViewModelInstanceBoolean viewModelPropertyId="111:13" id="{n()}"/>',
    f'    <ViewModelInstanceViewModel propertyValue="{CRUMB_SEL}" viewModelPropertyId="111:15" id="{n()}"/>',
    '</ViewModelInstance>'], CRUMBS_VM)

# 3. Slide, tile and nav item instances, next to their A-Z neighbour
sid, tid, nid = n(), n(), n()
insert_after_instance(f'S {after}' if after else None, [
    f'<ViewModelInstance exports="true" name="S {title}" id="{sid}">',
    f'    <ViewModelInstanceString propertyValue="{title}" viewModelPropertyId="10:5171" id="{n()}"/>',
    f'    <ViewModelInstanceList viewModelPropertyId="10:5173" id="{n()}">',
    f'        <ViewModelInstanceListItem viewModelId="{vm}" viewModelInstanceId="{slide_inst}" id="{n()}"/>',
    '    </ViewModelInstanceList>',
    '    ' + num('10:5175', slot),
    f'    <ViewModelInstanceNumber propertyValue="{zoom}" viewModelPropertyId="10:5177" id="{n()}"/>',
    f'    <ViewModelInstanceViewModel propertyValue="{STAGE}" viewModelPropertyId="10:5179" id="{n()}"/>',
    f'    <ViewModelInstanceViewModel propertyValue="{crumbs}" viewModelPropertyId="114:1" id="{n()}"/>',
    '</ViewModelInstance>'], SLIDE_VM)
insert_after_instance(f'T {after}' if after else None, [
    f'<ViewModelInstance exports="true" name="T {title}" id="{tid}">',
    f'    <ViewModelInstanceString propertyValue="{title}" viewModelPropertyId="10:3614" id="{n()}"/>',
    f'    <ViewModelInstanceList viewModelPropertyId="10:3861" id="{n()}">',
    f'        <ViewModelInstanceListItem viewModelId="{vm}" viewModelInstanceId="{tile_inst}" id="{n()}"/>',
    '    </ViewModelInstanceList>',
    f'    <ViewModelInstanceBoolean viewModelPropertyId="10:4507" id="{n()}"/>',
    '    ' + num('10:4567', slot),
    f'    <ViewModelInstanceViewModel propertyValue="{NAV}" viewModelPropertyId="10:4589" id="{n()}"/>',
    '</ViewModelInstance>'], TILE_VM)
insert_after_instance(f'Nav {after}' if after else None, [
    f'<ViewModelInstance exports="true" name="Nav {title}" id="{nid}">',
    f'    <ViewModelInstanceString propertyValue="{title}" viewModelPropertyId="41:868" id="{n()}"/>',
    '    ' + num('41:870', slot),
    f'    <ViewModelInstanceViewModel propertyValue="{NAV}" viewModelPropertyId="41:872" id="{n()}"/>',
    f'    <ViewModelInstanceBoolean viewModelPropertyId="41:874" id="{n()}"/>',
    '</ViewModelInstance>'], NAV_VM)

# 4. List entries: the section's tiles, the sidebar group's items (and its count), the Showcase's slides
def add_list_item(container_name, list_prop, index, line):
    global s
    m = block(container_name)
    lst = re.search(r'( *)<ViewModelInstanceList viewModelPropertyId="%s" id="[^"]+">\n(.*?)\1</ViewModelInstanceList>' % list_prop, m.group(0), re.S)
    rows = lst.group(2).splitlines(keepends=True)
    ind = re.match(r' *', rows[0]).group(0) if rows else lst.group(1) + '    '
    rows.insert(index, ind + line + '\n')
    new = m.group(0)[:lst.start(2)] + ''.join(rows) + m.group(0)[lst.end(2):]
    s = s[:m.start()] + new + s[m.end():]
add_list_item(f'Sec {section}', '100:3', pos, f'<ViewModelInstanceListItem viewModelId="{TILE_VM}" viewModelInstanceId="{tid}" id="{n()}"/>')
add_list_item(section, '41:886', pos, f'<ViewModelInstanceListItem name="Nav {title}" viewModelId="{NAV_VM}" viewModelInstanceId="{nid}" id="{n()}"/>')
add_list_item('Showcase', '10:5181', slot, f'<ViewModelInstanceListItem viewModelId="{SLIDE_VM}" viewModelInstanceId="{sid}" id="{n()}"/>')

def inc(container_name, prop):
    global s
    m = block(container_name)
    new = re.sub(r'propertyValue="(\d+)" viewModelPropertyId="%s"' % prop,
                 lambda k: f'propertyValue="{int(k.group(1)) + 1}" viewModelPropertyId="{prop}"', m.group(0), count=1)
    s = s[:m.start()] + new + s[m.end():]
inc(section, '41:882')      # NavGroup count
inc('Showcase', '10:5576')  # _count
open(ROOT, 'w').write(s)
print(f'added: slide {sid}, tile {tid}, nav {nid}, crumbs {crumbs}')
