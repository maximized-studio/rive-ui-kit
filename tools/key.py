"""Rewrites shared/83-Key.rml: the Key component (keyboard cap, Xbox / PlayStation face buttons, shoulder pill).
Existing 830 ids are kept; new objects take ids from client 979. Run from the repo root."""
import itertools, math
import xml.dom.minidom

c = itertools.count(1)
n = lambda: f'979:{next(c)}'
VM = '830:1'
KEYS, HID = '830:2', '830:3'
TYPE, GLYPH, LABEL = n(), n(), n()
p = lambda k: f'{VM}-{k}'
Q = '"'
FACE, LIP, RING, INK = 'FF2A2A2E', 'FF111113', 'FF4A4A52', 'FFE4E4E7'
XBOX = [('A', 'FF6CCB3A'), ('B', 'FFF0483E'), ('X', 'FF3D9BF0'), ('Y', 'FFF7C81E')]
PS = [('Cross', 'FF7FB6F2'), ('Circle', 'FFF2666C'), ('Square', 'FFDC8FC4'), ('Triangle', 'FF3FD6B0')]


def solid(col):
    return f'<SolidColor colorValue="{col}" id="{n()}"/>'


def fill(col):
    return f'<Fill fillRule="clockwise" id="{n()}">{solid(col)}</Fill>'


def stroke(col, w=1.6):
    return f'<Stroke thickness="{w}" cap="round" join="round" id="{n()}">{solid(col)}</Stroke>'


def path(pts, closed=True):
    v = ''.join(f'<StraightVertex x="{x}" y="{y}" id="{n()}"/>' for x, y in pts)
    return f'<PointsPath isClosed="{"true" if closed else "false"}" id="{n()}">{v}</PointsPath>'


def circle(r):
    k = r * 0.5523
    v = ''.join(f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{rot}" distance="{k}" id="{n()}"/>'
                for (x, y), rot in zip([(0, -r), (r, 0), (0, r), (-r, 0)], [0, math.pi / 2, math.pi, -math.pi / 2]))
    return f'<PointsPath isClosed="true" id="{n()}">{v}</PointsPath>'


def hidden(i):
    return '' if i == 0 else ' opacity="0"'


# ---- round face button (Xbox letters / PlayStation shapes)
letters, letter_ids = '', []
for i, (ch, col) in enumerate(XBOX):
    tid, sid = n(), n()
    letter_ids.append(tid)
    letters += (f'<Text sizingValue="fixed" width="22" height="22" alignValue="center" verticalAlignValue="middle" x="-11" y="-11"{hidden(i)} name="{ch}" id="{tid}">'
                f'<TextStylePaint fontSize="13" fontAssetId="0:7" familyName="Inter" styleName="Bold" id="{sid}">{fill(col)}'
                f'<TextStyleAxis tag="1869640570" axisValue="14" id="{n()}"/><TextStyleAxis tag="2003265652" axisValue="700" id="{n()}"/></TextStylePaint>'
                f'<TextValueRun styleId="{sid}" text="{ch}" id="{n()}"/></Text>')
shapes, shape_ids = '', []
geo = [path([(-3.4, -3.4), (3.4, 3.4)], False) + path([(3.4, -3.4), (-3.4, 3.4)], False),
       circle(4.3),
       path([(-3.7, -3.7), (3.7, -3.7), (3.7, 3.7), (-3.7, 3.7)]),
       path([(0, -4.5), (4.5, 3.3), (-4.5, 3.3)])]
for i, ((nm, col), g) in enumerate(zip(PS, geo)):
    sid = n()
    shape_ids.append(sid)
    yy = ' y="-0.4"' if nm == 'Triangle' else ''
    shapes += f'<Shape{yy}{hidden(i)} name="{nm}" id="{sid}">{g}{stroke(col)}</Shape>'
xg, pg = n(), n()
round_st, round_face_st, round_id = n(), n(), n()
round_btn = (f'<LayoutComponent styleId="{round_st}" name="Face Button" id="{round_id}">'
             f'<LayoutComponent width="22" height="22" styleId="{round_face_st}" name="Face" id="{n()}">'
             f'<Node x="11" y="11" name="Glyph" id="{n()}">'
             f'<Node opacity="0" name="Xbox" id="{xg}">{letters}</Node>'
             f'<Node opacity="0" name="PlayStation" id="{pg}">{shapes}</Node></Node>'
             f'<Stroke id="{n()}">{solid(RING)}</Stroke>{fill(FACE)}'
             f'<LayoutComponentStyle cornerRadiusTL="11" widthUnitsValue="points" heightUnitsValue="points" id="{round_face_st}"/></LayoutComponent>'
             f'{fill(LIP)}'
             f'<LayoutComponentStyle displayValue="none" paddingBottom="2" intrinsicallySizedValue="true" cornerRadiusTL="11" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{round_st}"/>'
             f'</LayoutComponent>')

# ---- shoulder / trigger pill
sh_st, sh_face_st, sh_ts = n(), n(), n()
shoulder = (f'<LayoutComponent styleId="{sh_st}" name="Shoulder" id="{n()}">'
            f'<LayoutComponent height="22" styleId="{sh_face_st}" name="Face" id="{n()}">'
            f'<Text name="Keys" id="{n()}"><TextStylePaint fontSize="12" fontAssetId="0:7" familyName="Inter" styleName="SemiBold" id="{sh_ts}">{fill(INK)}'
            f'<TextStyleAxis tag="1869640570" axisValue="14" id="{n()}"/><TextStyleAxis tag="2003265652" axisValue="600" id="{n()}"/></TextStylePaint>'
            f'<TextValueRun styleId="{sh_ts}" text="LB" id="{n()}"><DataBindContext sourcePathIds="{p(KEYS)}" propertyKey="268" nameBased="true" id="{n()}"/></TextValueRun>'
            f'<LayoutParticipant layoutWidthScaleType="hug" layoutHeightScaleType="hug" id="{n()}"/></Text>'
            f'<Stroke id="{n()}">{solid(RING)}</Stroke>{fill(FACE)}'
            f'<LayoutComponentStyle paddingLeft="10" paddingRight="10" layoutAlignmentType="center" cornerRadiusTL="11" minWidth="36" minWidthUnitsValue="points" layoutWidthScaleType="hug" widthUnitsValue="auto" id="{sh_face_st}"/></LayoutComponent>'
            f'{fill(LIP)}'
            f'<LayoutComponentStyle displayValue="none" paddingBottom="2" intrinsicallySizedValue="true" cornerRadiusTL="11" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{sh_st}"/>'
            f'</LayoutComponent>')

# ---- keyboard cap (unchanged, ids kept; its semantics move to the wrapper)
cap = '''<LayoutComponent styleId="830:35" name="Cap" id="830:36">
<LayoutComponent height="22" styleId="830:29" name="Face" id="830:30">
<Text name="Keys" id="830:14">
<TextStylePaint fontAssetId="0:7" familyName="Inter" styleName="Medium" id="830:12">
<Fill fillRule="clockwise" id="830:15"><SolidColor colorValue="FF888888" id="830:16"><DataBindContext sourcePathIds="10:7-10:7424" propertyKey="37" id="830:17"/></SolidColor></Fill>
<TextStyleAxis tag="1869640570" axisValue="14" id="830:18"/><TextStyleAxis tag="2003265652" axisValue="500" id="830:19"/>
</TextStylePaint>
<TextValueRun styleId="830:12" text="⌘ K" id="830:20"><DataBindContext sourcePathIds="830:1-830:2" propertyKey="268" nameBased="true" id="830:13"/></TextValueRun>
<LayoutParticipant layoutWidthScaleType="hug" layoutHeightScaleType="hug" id="830:21"/>
</Text>
<Stroke join="round" id="830:22"><SolidColor colorValue="FF27272A" id="830:23"><DataBindContext sourcePathIds="10:7-10:7418" propertyKey="37" id="830:24"/></SolidColor></Stroke>
<Fill fillRule="clockwise" id="830:25"><SolidColor colorValue="FF27272A" id="830:26"><DataBindContext sourcePathIds="10:7-10:7414" propertyKey="37" id="830:27"/></SolidColor></Fill>
<LayoutComponentStyle paddingLeft="7" paddingRight="7" layoutAlignmentType="center" cornerRadiusTL="6" minWidth="22" minWidthUnitsValue="points" layoutWidthScaleType="hug" widthUnitsValue="auto" id="830:29"><DataBindContext sourcePathIds="10:7-901:21" propertyKey="640" id="830:28"/></LayoutComponentStyle>
</LayoutComponent>
<Fill fillRule="clockwise" id="830:31"><SolidColor colorValue="FF3F3F46" id="830:32"><DataBindContext sourcePathIds="10:7-10:7420" propertyKey="37" id="830:33"/></SolidColor></Fill>
<LayoutComponentStyle paddingBottom="2" intrinsicallySizedValue="true" cornerRadiusTL="6" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="830:35"><DataBindContext sourcePathIds="10:7-901:21" propertyKey="640" id="830:34"/></LayoutComponentStyle>
</LayoutComponent>'''

wrap_st = n()
wrapper = (f'<LayoutComponent styleId="{wrap_st}" name="Key" id="{n()}">{cap}{shoulder}{round_btn}'
           f'<LayoutComponentStyle intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{wrap_st}"/>'
           f'<SemanticData role="text" name="Semantics" id="830:11">'
           f'<DataBindContext sourcePathIds="{p(LABEL)}" propertyKey="983" nameBased="true" id="830:9"/>'
           f'<DataBindContext sourcePathIds="{p(HID)}" propertyKey="1004" nameBased="true" id="830:10"/></SemanticData></LayoutComponent>')


# ---- state machine: Type picks the look, Glyph the face glyph
def kd(obj, v):
    return (f'<KeyedObject objectId="{obj}" id="{n()}"><KeyedProperty propertyKey="18" id="{n()}">'
            f'<KeyFrameDouble value="{v}" interpolationType="linear" id="{n()}"/></KeyedProperty></KeyedObject>')


def ku(obj, v):
    val = ' value="1"' if v else ''
    return f'<KeyedObject objectId="{obj}" id="{n()}"><KeyedProperty propertyKey="596" id="{n()}"><KeyFrameUint{val} id="{n()}"/></KeyedProperty></KeyedObject>'


def cond(prop, v):
    val = f' value="{v}"' if v else ''
    return (f'<TransitionViewModelCondition id="{n()}"><TransitionPropertyViewModelComparator id="{n()}"><BindablePropertyNumber id="{n()}">'
            f'<DataBindContext sourcePathIds="{p(prop)}" propertyKey="636" id="{n()}"/></BindablePropertyNumber></TransitionPropertyViewModelComparator>'
            f'<TransitionValueNumberComparator{val} id="{n()}"/></TransitionViewModelCondition>')


def layer(name, prop, states, first_id=None, first_anim=None):
    anims, sts, trans = '', '', ''
    first = None
    for i, (nm, keyed) in enumerate(states):
        aid = first_anim if (i == 0 and first_anim) else n()
        sid = first_id if (i == 0 and first_id) else n()
        first = first or sid
        anims += f'<LinearAnimation loopValue="loop" name="{name} {nm}" id="{aid}">{keyed}</LinearAnimation>'
        sts += f'<AnimationState animationId="{aid}" stateName="{nm}" id="{sid}"/>'
        trans += f'<StateTransition stateToId="{sid}" id="{n()}">{cond(prop, i)}</StateTransition>'
    return first, sts, trans, anims


CAP = '830:35'
type_states = [
    ('Keyboard', ku(CAP, 0) + ku(sh_st, 1) + ku(round_st, 1) + kd(xg, 0) + kd(pg, 0)),
    ('Xbox', ku(CAP, 1) + ku(sh_st, 1) + ku(round_st, 0) + kd(xg, 1) + kd(pg, 0)),
    ('PlayStation', ku(CAP, 1) + ku(sh_st, 1) + ku(round_st, 0) + kd(xg, 0) + kd(pg, 1)),
    ('Shoulder', ku(CAP, 1) + ku(sh_st, 0) + ku(round_st, 1) + kd(xg, 0) + kd(pg, 0)),
]
t_first, t_sts, t_trans, t_anims = layer('Type', TYPE, type_states, first_id='830:37', first_anim='830:8')
glyph_states = [(str(i), ''.join(kd(o, 1 if j == i else 0) for j, o in enumerate(letter_ids))
                 + ''.join(kd(o, 1 if j == i else 0) for j, o in enumerate(shape_ids))) for i in range(4)]
g_first, g_sts, g_trans, g_anims = layer('Glyph', GLYPH, glyph_states)
sm = (f'<StateMachine name="State Machine 1" id="830:7">'
      f'<StateMachineLayer name="Type" id="830:38">{t_sts}<AnyState id="830:39">{t_trans}</AnyState><ExitState id="830:40"/>'
      f'<EntryState id="830:41"><StateTransition stateToId="830:37" id="830:42"/></EntryState></StateMachineLayer>'
      f'<StateMachineLayer name="Glyph" id="{n()}">{g_sts}<AnyState id="{n()}">{g_trans}</AnyState><ExitState id="{n()}"/>'
      f'<EntryState id="{n()}"><StateTransition stateToId="{g_first}" id="{n()}"/></EntryState></StateMachineLayer></StateMachine>')


# ---- view model and instances
def num(prop, v):
    val = f' propertyValue="{v}"' if v else ''
    return f'<ViewModelInstanceNumber{val} viewModelPropertyId="{prop}" id="{n()}"/>'


def inst(iid, name, keys, typ, glyph, label, kid=None, hid=None):
    return (f'<ViewModelInstance exports="true" name="{name}" id="{iid}">'
            f'<ViewModelInstanceString propertyValue="{keys}" viewModelPropertyId="{KEYS}" id="{kid or n()}"/>'
            f'<ViewModelInstanceBoolean viewModelPropertyId="{HID}" id="{hid or n()}"/>'
            f'{num(TYPE, typ)}{num(GLYPH, glyph)}'
            f'<ViewModelInstanceString propertyValue="{label}" viewModelPropertyId="{LABEL}" id="{n()}"/></ViewModelInstance>')


new_ids = {}
insts = (inst('830:4', 'Command K', '⌘ K', 0, 0, 'Command K', '830:46', '830:47')
         + inst('830:5', 'Escape', 'Esc', 0, 0, 'Escape', '830:48', '830:49'))
for i, (ch, _) in enumerate(XBOX):
    iid = n()
    new_ids[f'Xbox {ch}'] = iid
    insts += inst(iid, f'Xbox {ch}', ch, 1, i, f'{ch} button')
for i, (nm, _) in enumerate(PS):
    iid = n()
    new_ids[f'PlayStation {nm}'] = iid
    insts += inst(iid, f'PlayStation {nm}', nm, 2, i, f'{nm} button')
for keys, label in (('LB', 'Left bumper'), ('R2', 'R2 trigger')):
    iid = n()
    new_ids[keys] = iid
    insts += inst(iid, keys, keys, 3, 0, label)
vm = (f'<ViewModel defaultInstanceId="830:4" name="Key" groupId="1:2673" id="{VM}">'
      f'<ViewModelPropertyString name="keys" id="{KEYS}"/><ViewModelPropertyBoolean name="a11yHidden" id="{HID}"/>'
      f'<ViewModelPropertyNumber name="type" id="{TYPE}"/><ViewModelPropertyNumber name="glyph" id="{GLYPH}"/>'
      f'<ViewModelPropertyString name="label" id="{LABEL}"/>{insts}</ViewModel>')

doc = f'''<Rive version="1" kind="fragment">
<Artboard defaultStateMachineId="830:7" viewModelId="830:1" viewModelInstanceId="830:4" isComponent="true" spaceId="1:5601" width="40" height="24" styleId="830:43" x="8400" name="Key" id="830:6">
<Fill fillRule="clockwise" id="830:44"><SolidColor colorValue="00000000" id="830:45"/></Fill>
<LayoutComponentStyle intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="830:43"/>
{wrapper}
{sm}
{t_anims}{g_anims}
</Artboard>
{vm}
</Rive>
'''
out = xml.dom.minidom.parseString(doc.encode('utf-8')).toprettyxml(indent='    ')
out = '\n'.join(l for l in out.split('\n')[1:] if l.strip()) + '\n'
open('shared/83-Key.rml', 'w').write(out)
print(new_ids)
