"""Generates the Calendar (shared/58-Calendar.rml) and its day cell (shared/57-CalendarDay.rml).

The month grid comes from the Luau script "Calendar": it fills `_days` with 42 Calendar Days
(Monday first, the days around the month muted), writes `_title`, turns a click on a day into
`value` (an ISO date, "2026-11-07") and steps the month on the Previous / Next Buttons.
Ids: 410 (view models, converters, script), 411 (day artboard), 412 (calendar artboard).
Range mode (`range` true): the first click sets `value`, the second `endValue`; the days between get a soft
band, the two ends a disc, and hovering previews the range while the end is still open."""
import itertools, math, re

T = lambda p: f'10:7-{p}'
TEXT, MUTED, BORDER, SURF, HOVER = '10:7422', '10:7426', '10:7418', '10:7406', '10:7416'
BRAND, BRAND50, TEXT2 = '10:2104', '10:2092', '10:7424'
SOFT = '10:2094'  # _brand100: pale in light mode, deep (brand 950) in dark
TOGGLE_ON = '9:145'

DAY_VM, CAL_VM = '410:100', '410:200'
D = dict(day='410:101', label='410:102', inMonth='410:103', today='410:104', selected='410:105', _hover='410:106', _pick='410:107',
         inRange='410:108', rangeStart='410:109', rangeEnd='410:110')
C = dict(year='410:201', month='410:202', value='410:203', today='410:204', label='410:205', a11yHidden='410:206',
         _title='410:207', _days='410:208', _prev='410:209', _next='410:210', range='410:211', endValue='410:212')
dp = lambda k: f'{DAY_VM}-{D[k]}'
cp = lambda k: f'{CAL_VM}-{C[k]}'

def ids(client):
    c = itertools.count(1)
    return lambda: f'{client}:{next(c)}'

def color(n, tok, fb):
    return f'<SolidColor colorValue="{fb}" id="{n()}"><DataBindContext sourcePathIds="{T(tok)}" propertyKey="37" id="{n()}"/></SolidColor>'

def fill(n, tok, fb):
    return f'<Fill fillRule="clockwise" id="{n()}">{color(n, tok, fb)}</Fill>'

def circle_path(n, d):
    r, k = d / 2, d / 2 * 0.5523
    v = ''.join(f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{rot}" distance="{k}" id="{n()}"/>'
                for (x, y), rot in zip([(0, -r), (r, 0), (0, r), (-r, 0)], [0, math.pi / 2, math.pi, -math.pi / 2]))
    return f'<PointsPath isClosed="true" id="{n()}">{v}</PointsPath>'

def text(n, name, run, size, weight, tok, fb, bind=None, conv='', extra='', lp='hug', tid=None, style='Medium'):
    sid = n()
    b = ''
    if bind:
        c = f' converterId="{conv}"' if conv else ''
        b = f'<DataBindContext sourcePathIds="{bind}" propertyKey="268" nameBased="true"{c} id="{n()}"/>'
    return (f'<Text name="{name}" {extra} id="{tid or n()}">'
            f'<TextStylePaint fontSize="{size}" fontAssetId="0:7" familyName="Inter" styleName="{style}" id="{sid}">'
            f'{fill(n, tok, fb)}<TextStyleAxis tag="1869640570" axisValue="14" id="{n()}"/>'
            f'<TextStyleAxis tag="2003265652" axisValue="{weight}" id="{n()}"/></TextStylePaint>'
            f'<TextValueRun styleId="{sid}" text="{run}" id="{n()}">{b}</TextValueRun>'
            f'<LayoutParticipant layoutWidthScaleType="{lp}" layoutHeightScaleType="hug" id="{n()}"/></Text>')

def bool_cond(n, path, value):
    v = ' value="true"' if value else ''
    return (f'<TransitionViewModelCondition id="{n()}"><TransitionPropertyViewModelComparator id="{n()}">'
            f'<BindablePropertyBoolean id="{n()}"><DataBindContext sourcePathIds="{path}" propertyKey="634" id="{n()}"/></BindablePropertyBoolean>'
            f'</TransitionPropertyViewModelComparator><TransitionValueBooleanComparator{v} id="{n()}"/></TransitionViewModelCondition>')

def kf(n, obj, prop, v):
    return f'<KeyedObject objectId="{obj}" id="{n()}"><KeyedProperty propertyKey="{prop}" id="{n()}"><KeyFrameDouble value="{v}" id="{n()}"/></KeyedProperty></KeyedObject>'

def set_bool(n, path, v):
    pv = ' propertyValue="true"' if v else ''
    return (f'<ListenerViewModelChange id="{n()}"><BindablePropertyBoolean{pv} id="{n()}">'
            f'<DataBindContext sourcePathIds="{path}" propertyKey="634" direction="true" id="{n()}"/></BindablePropertyBoolean></ListenerViewModelChange>')

CELL = 36

# ---------------------------------------------------------------- day
def day():
    n = ids(411)
    ab, st, sm = n(), n(), n()
    cell, cell_st = n(), n()
    t_sel, t_day, t_mut = n(), n(), n()
    a_sel, a_norm, a_mut = n(), n(), n()
    texts_st = n()
    texts = (f'<LayoutComponent styleId="{texts_st}" name="Number" id="{n()}">'
             + text(n, 'Selected', '7', 14, 600, BRAND50, 'FFEFF6FF', dp('label') and None, extra='opacity="0"', tid=t_sel)
             + text(n, 'Day', '7', 14, 500, TEXT, 'FFFAFAFA', tid=t_day)
             + text(n, 'Outside', '7', 14, 400, MUTED, 'FFA1A1AA', extra='opacity="0"', tid=t_mut)
             + f'<LayoutComponentStyle layoutAlignmentType="center" intrinsicallySizedValue="true" layoutTypeValue="stack" '
               f'layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{texts_st}"/></LayoutComponent>')
    # every number text shows `day`
    texts = re.sub(r'(<TextValueRun styleId="[^"]+" text="7" id="[^"]+">)(</TextValueRun>)',
                   lambda m: m.group(1) + f'<DataBindContext sourcePathIds="{dp("day")}" propertyKey="268" nameBased="true" converterId="410:300" id="{n()}"/>' + m.group(2), texts)
    sel = (f'<Shape name="Selected" id="{n()}">{circle_path(n, 32)}{fill(n, BRAND, "FF2563EB")}'
           f'<DataBindContext sourcePathIds="{dp("selected")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></Shape>')
    ring = (f'<Shape name="Today" id="{n()}">{circle_path(n, 31)}<Stroke thickness="1.5" id="{n()}">{color(n, BRAND, "FF2563EB")}</Stroke>'
            f'<DataBindContext sourcePathIds="{dp("today")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></Shape>')
    hov = (f'<Shape name="Hover" id="{n()}">{circle_path(n, 32)}{fill(n, HOVER, "FF27272A")}'
           f'<DataBindContext sourcePathIds="{dp("_hover")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></Shape>')
    b = ids(411)
    for _ in range(499):
        b()

    def band(name, x, w, prop):
        return (f'<Shape x="{x}" name="{name}" id="{b()}"><Rectangle width="{w}" height="32" id="{b()}"/>{fill(b, SOFT, "FF172554")}'
                f'<DataBindContext sourcePathIds="{dp(prop)}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{b()}"/></Shape>')
    # the cell is 36 wide with 4 between cells: a full band is 40 so neighbours join up
    bands = band('Band', 0, CELL + 4, 'inRange') + band('Band Start', (CELL + 4) / 4, (CELL + 4) / 2, 'rangeStart') \
        + band('Band End', -(CELL + 4) / 4, (CELL + 4) / 2, 'rangeEnd')
    art = f'<Node x="{CELL / 2}" y="{CELL / 2}" name="Art" id="{n()}">{sel}{ring}{hov}{bands}</Node>'
    sem = (f'<SemanticData role="button" name="Semantics" id="{n()}">'
           f'<DataBindContext sourcePathIds="{dp("label")}" propertyKey="983" nameBased="true" id="{n()}"/>'
           f'<DataBindContext sourcePathIds="{dp("selected")}" propertyKey="997" nameBased="true" id="{n()}"/></SemanticData>')
    body = (f'<LayoutComponent width="{CELL}" height="{CELL}" styleId="{cell_st}" name="Cell" id="{cell}">{texts}{art}{sem}'
            f'<LayoutComponentStyle layoutAlignmentType="center" widthUnitsValue="points" heightUnitsValue="points" id="{cell_st}"/></LayoutComponent>')
    lst = lambda name, inputs, action: f'<StateMachineListener targetId="{cell}" name="{name}" id="{n()}">{inputs}{action}</StateMachineListener>'
    listeners = (lst('Pick', f'<ListenerInputType listenerTypeValue="click" id="{n()}"/>'
                             f'<ListenerInputTypeSemantic listenerTypeValue="semanticAction" id="{n()}"><SemanticInput id="{n()}"/></ListenerInputTypeSemantic>',
                     set_bool(n, dp('_pick'), True))
                 + lst('Hover On', f'<ListenerInputType id="{n()}"/><ListenerInputType listenerTypeValue="move" id="{n()}"/>',
                       set_bool(n, dp('_hover'), True) + set_bool(n, '10:7-63:244', True))
                 + lst('Hover Off', f'<ListenerInputType listenerTypeValue="exit" id="{n()}"/>',
                       set_bool(n, dp('_hover'), False) + set_bool(n, '10:7-63:244', False)))
    s_sel, s_norm, s_mut = n(), n(), n()
    look = (f'<StateMachineLayer name="Look" id="{n()}"><AnyState id="{n()}">'
            f'<StateTransition stateToId="{s_sel}" id="{n()}">{bool_cond(n, dp("selected"), True)}</StateTransition>'
            f'<StateTransition stateToId="{s_norm}" id="{n()}">{bool_cond(n, dp("selected"), False)}{bool_cond(n, dp("inMonth"), True)}</StateTransition>'
            f'<StateTransition stateToId="{s_mut}" id="{n()}">{bool_cond(n, dp("selected"), False)}{bool_cond(n, dp("inMonth"), False)}</StateTransition>'
            f'</AnyState><ExitState id="{n()}"/><EntryState id="{n()}"><StateTransition stateToId="{s_norm}" id="{n()}"/></EntryState>'
            f'<AnimationState animationId="{a_sel}" stateName="Selected" id="{s_sel}"/><AnimationState animationId="{a_norm}" stateName="Day" id="{s_norm}"/>'
            f'<AnimationState animationId="{a_mut}" stateName="Outside" id="{s_mut}"/></StateMachineLayer>')
    anims = ''.join(f'<LinearAnimation loopValue="loop" name="{nm}" id="{aid}">{kf(n, t_sel, 18, a)}{kf(n, t_day, 18, b)}{kf(n, t_mut, 18, c)}</LinearAnimation>'
                    for nm, aid, a, b, c in (('Selected', a_sel, 1, 0, 0), ('Day', a_norm, 0, 1, 0), ('Outside', a_mut, 0, 0, 1)))
    return f'''<Rive version="1" kind="fragment">
<Artboard defaultStateMachineId="{sm}" viewModelId="{DAY_VM}" viewModelInstanceId="410:150" isComponent="true" spaceId="1:5601" width="{CELL}" height="{CELL}" styleId="{st}" x="4400" y="0" name="Calendar Day" id="{ab}">
<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="00000000" id="{n()}"/></Fill>
<LayoutComponentStyle intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{st}"/>
{body}
<StateMachine name="State Machine 1" id="{sm}">{listeners}{look}</StateMachine>
{anims}
</Artboard>
</Rive>
'''

# ---------------------------------------------------------------- calendar
BTN_PROPS = [('String', '1:549'), ('Boolean', '1:587'), ('Trigger', '1:1321'), ('Boolean', '7:1'), ('Boolean', '7:3'),
             ('Number', '33:164'), ('Boolean', '33:169'), ('Number', '99:100'), ('String', '112:14'), ('Number', '118:1'),
             ('Number', '136:1'), ('Trigger', '134:10')]

def button(n, name, label, icon, trig):
    vals = {'1:549': label, '33:164': icon, '33:169': 'true', '118:1': 2}
    inst = ''
    for typ, pid in BTN_PROPS:
        v = vals.get(pid)
        pv = f' propertyValue="{v}"' if v is not None else ''
        bind = (f'<DataBindContext sourcePathIds="{cp(trig)}" propertyKey="687" twoWay="true" nameBased="true" id="{n()}"/>'
                if pid == '1:1321' else '')
        inst += f'<ViewModelInstance{typ}{pv} viewModelPropertyId="{pid}" id="{n()}">{bind}</ViewModelInstance{typ}>' if bind else \
                f'<ViewModelInstance{typ}{pv} viewModelPropertyId="{pid}" id="{n()}"/>'
    st = n()
    return (f'<LayoutComponent styleId="{st}" name="{name}" id="{n()}">'
            f'<NestedArtboardLayout instanceWidthScaleType="hug" instanceHeightScaleType="hug" artboardId="1:122" isStateful="true" name="Button" id="{n()}">'
            f'<NestedStateMachine animationId="1:127" id="{n()}"/>'
            f'<ViewModelInstance viewModelId="1:151" exports="true" name="{name} Button" id="{n()}">{inst}</ViewModelInstance></NestedArtboardLayout>'
            f'<LayoutComponentStyle intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{st}"/></LayoutComponent>')

def calendar():
    n = ids(412)
    ab, st, sm = n(), n(), n()
    GRID_W = 7 * CELL + 6 * 4
    head_st = n()
    header = (f'<LayoutComponent styleId="{head_st}" name="Header" id="{n()}">'
              + text(n, 'Title', 'November 2026', 16, 600, TEXT, 'FFFAFAFA', cp('_title'), lp='fill', style='SemiBold')
              + button(n, 'Previous', 'Previous month', 2, '_prev') + button(n, 'Next', 'Next month', 3, '_next')
              + f'<LayoutComponentStyle gapHorizontal="4" layoutAlignmentType="centerLeft" intrinsicallySizedValue="true" paddingLeft="6" '
                f'layoutWidthScaleType="fill" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{head_st}"/></LayoutComponent>')
    wd_st = n()
    days = ''
    for d in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']:
        s2 = n()
        days += (f'<LayoutComponent width="{CELL}" height="20" styleId="{s2}" name="{d}" id="{n()}">'
                 + text(n, d, d, 12, 500, MUTED, 'FFA1A1AA')
                 + f'<LayoutComponentStyle layoutAlignmentType="center" widthUnitsValue="points" heightUnitsValue="points" id="{s2}"/></LayoutComponent>')
    weekdays = (f'<LayoutComponent styleId="{wd_st}" name="Weekdays" id="{n()}">{days}'
                f'<LayoutComponentStyle gapHorizontal="4" intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{wd_st}"/></LayoutComponent>')
    grid_st = n()
    grid = (f'<LayoutComponent width="{GRID_W}" styleId="{grid_st}" name="Grid" id="{n()}">'
            f'<ArtboardComponentList participatesInLayout="true" id="{n()}"><DataBindContext sourcePathIds="{cp("_days")}" propertyKey="800" id="{n()}"/></ArtboardComponentList>'
            f'<LayoutComponentStyle gapHorizontal="4" gapVertical="4" flexWrapValue="wrap" intrinsicallySizedValue="true" widthUnitsValue="points" '
            f'layoutHeightScaleType="hug" heightUnitsValue="auto" id="{grid_st}"/>'
            f'<SemanticData role="group" name="Semantics" id="{n()}"><DataBindContext sourcePathIds="{cp("_title")}" propertyKey="983" nameBased="true" id="{n()}"/></SemanticData>'
            f'</LayoutComponent>')
    scr_st = n()
    script = (f'<LayoutComponent styleId="{scr_st}" name="Grid Script" id="{n()}"><ScriptedLayout scriptAssetId="410:400" name="Calendar" id="{n()}"/>'
              f'<LayoutComponentStyle positionTypeValue="absolute" widthUnitsValue="points" heightUnitsValue="points" id="{scr_st}"/></LayoutComponent>')
    card_st = n()
    card = (f'<LayoutComponent styleId="{card_st}" name="Card" id="{n()}">{script}{header}{weekdays}{grid}'
            f'{fill(n, SURF, "FF18181B")}<Stroke id="{n()}">{color(n, BORDER, "FF27272A")}</Stroke>'
            f'<LayoutComponentStyle gapVertical="8" flexDirectionValue="column" paddingLeft="12" paddingRight="12" paddingTop="12" paddingBottom="12" '
            f'intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{card_st}">'
            f'<DataBindContext sourcePathIds="10:7-901:7" propertyKey="640" converterId="0:0" id="{n()}"/></LayoutComponentStyle>'
            f'<SemanticData role="group" name="Semantics" id="{n()}"><DataBindContext sourcePathIds="{cp("label")}" propertyKey="983" nameBased="true" id="{n()}"/>'
            f'<DataBindContext sourcePathIds="{cp("a11yHidden")}" propertyKey="1004" nameBased="true" id="{n()}"/></SemanticData></LayoutComponent>')
    layer, anim = n(), n()
    return f'''<Rive version="1" kind="fragment">
<Artboard defaultStateMachineId="{sm}" viewModelId="{CAL_VM}" viewModelInstanceId="410:250" isComponent="true" spaceId="1:5601" width="300" height="336" styleId="{st}" x="4400" y="200" name="Calendar" id="{ab}">
<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="00000000" id="{n()}"/></Fill>
<LayoutComponentStyle intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{st}"/>
{card}
<StateMachine name="State Machine 1" id="{sm}"><StateMachineLayer name="Layer 1" id="{layer}"><AnimationState animationId="{anim}" id="{n()}"/><AnyState id="{n()}"/><ExitState id="{n()}"/><EntryState id="{n()}"/></StateMachineLayer></StateMachine>
<LinearAnimation name="Idle" id="{anim}"/>
</Artboard>
</Rive>
'''

def root_parts():
    c = itertools.count(500)
    nid = lambda: f'410:{next(c)}'
    c2 = itertools.count(600)
    nid2 = lambda: f'410:{next(c2)}'
    NEW = {"inRange", "rangeStart", "rangeEnd", "range", "endValue"}
    types = {'label': 'String', 'inMonth': 'Boolean', 'today': 'Boolean', 'selected': 'Boolean', '_hover': 'Boolean', '_pick': 'Boolean',
             'inRange': 'Boolean', 'rangeStart': 'Boolean', 'rangeEnd': 'Boolean'}
    vm = f'    <ViewModel defaultInstanceId="410:150" name="CalendarDay" groupId="1:2673" id="{DAY_VM}">\n'
    vm += ''.join(f'        <ViewModelProperty{types.get(k, "Number")} name="{k}" id="{pid}"/>\n' for k, pid in D.items())
    vm += f'        <ViewModelInstance exports="true" name="Day" id="410:150">\n'
    vals = {'day': 7, 'label': '7 November 2026', 'inMonth': 'true'}
    for k, pid in D.items():
        v = vals.get(k)
        pv = f' propertyValue="{v}"' if v is not None else ''
        vm += f'            <ViewModelInstance{types.get(k, "Number")}{pv} viewModelPropertyId="{pid}" id="{nid() if k not in NEW else nid2()}"/>\n'
    vm += '        </ViewModelInstance>\n    </ViewModel>\n'
    ctypes = {'value': 'String', 'today': 'String', 'label': 'String', 'a11yHidden': 'Boolean', '_title': 'String', '_days': 'List',
              '_prev': 'Trigger', '_next': 'Trigger', 'range': 'Boolean', 'endValue': 'String'}
    vm += f'    <ViewModel defaultInstanceId="410:250" name="Calendar" groupId="1:2673" id="{CAL_VM}">\n'
    vm += ''.join(f'        <ViewModelProperty{ctypes.get(k, "Number")} name="{k}" id="{pid}"/>\n' for k, pid in C.items())
    vm += f'        <ViewModelInstance exports="true" name="Date" id="410:250">\n'
    vals = {'year': 2026, 'month': 11, 'value': '2026-11-12', 'today': '2026-11-07', 'label': 'Date', '_title': 'November 2026'}
    for k, pid in C.items():
        v = vals.get(k)
        pv = f' propertyValue="{v}"' if v is not None else ''
        vm += f'            <ViewModelInstance{ctypes.get(k, "Number")}{pv} viewModelPropertyId="{pid}" id="{nid() if k not in NEW else nid2()}"/>\n'
    vm += '        </ViewModelInstance>\n'
    vm += f'        <ViewModelInstance exports="true" name="Date range" id="410:260">\n'
    vals = {'year': 2026, 'month': 11, 'value': '2026-11-12', 'endValue': '2026-11-18', 'today': '2026-11-07', 'label': 'Stay',
            '_title': 'November 2026', 'range': 'true'}
    for k, pid in C.items():
        v = vals.get(k)
        pv = f' propertyValue="{v}"' if v is not None else ''
        vm += f'            <ViewModelInstance{ctypes.get(k, "Number")}{pv} viewModelPropertyId="{pid}" id="{nid2()}"/>\n'
    vm += '        </ViewModelInstance>\n    </ViewModel>\n'
    conv = '    <DataConverterToString round="true" name="Calendar · Day (to text)" groupId="1:2674" id="410:300"/>\n'
    script = '    <ScriptAsset file="Calendar.luau" name="Calendar" groupId="327:1" id="410:400"/>\n'
    return conv + script + vm

if __name__ == '__main__':
    open('shared/57-CalendarDay.rml', 'w').write(day())
    open('shared/58-Calendar.rml', 'w').write(calendar())
    p = 'shared/99-_root.rml'
    s = open(p).read()
    s = re.sub(r'    <!-- calendar -->.*?<!-- /calendar -->\n', '', s, flags=re.S)
    s = s.replace('\n</Rive>', '\n    <!-- calendar -->\n' + root_parts() + '    <!-- /calendar -->\n</Rive>')
    open(p, 'w').write(s)
    print('ok')
