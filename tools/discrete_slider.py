"""Generates the Discrete Slider (shared/56-DiscreteSlider.rml) and its tick (shared/55-SliderTick.rml).

Look and states are native; the Luau script "Discrete Slider" maps pointer drags to `value`
(snapped to `step` within min..max), writes `_fraction`, `_dragging`, `_hover` and fills `_ticks`.
Ids: 403 (view models, converters), 404 (tick artboard), 405 (slider artboard)."""
import itertools

T = lambda p: f'10:7-{p}'          # Theme token path
TEXT, TEXT2, MUTED = '10:7422', '10:7424', '10:7426'
BORDER, BSTRONG, SURF = '10:7418', '10:7420', '10:7406'
BRAND, BRAND300, PTEXT = '10:2104', '10:2098', '118:4'
R_SMALL, R_KNOB = '901:21', '901:15'
SH_BLUR, SH_Y = '901:31', '901:37'
TOGGLE_ON, SHIELD = '9:145', '9:90'   # bool -> number, bool -> 1 - number

VM, TICK_VM = '403:100', '403:200'
P = dict(value='403:101', min='403:102', max='403:103', step='403:104', label='403:105', disabled='403:106',
         a11yHidden='403:107', showTicks='403:108', _fraction='403:109', _dragging='403:110', _hover='403:111',
         _ticks='403:112', _keyUp='403:113', _keyDown='403:114', _doUp='403:115', _doDown='403:116')
TICK_ON = '403:201'
vp = lambda k: f'{VM}-{P[k]}'

def ids(client):
    c = itertools.count(1)
    return lambda: f'{client}:{next(c)}'

def color(n, tok, fb):
    return f'<SolidColor colorValue="{fb}" id="{n()}"><DataBindContext sourcePathIds="{T(tok)}" propertyKey="37" id="{n()}"/></SolidColor>'

def fill(n, tok, fb):
    return f'<Fill fillRule="clockwise" id="{n()}">{color(n, tok, fb)}</Fill>'

def circle(n, d, name, paint, extra=''):
    """A d x d circle centred on 0,0 drawn with 4 cubic vertices (no Ellipse: layouts resize those)."""
    r, k = d / 2, d / 2 * 0.5523
    pts = [(0, -r, -k, 0), (r, 0, 0, -k), (0, r, k, 0), (-r, 0, 0, k)]
    v = ''.join(f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{0}" distance="{k}" id="{n()}"/>' for x, y, _, _ in pts)
    # mirrored vertices: rotation = tangent angle
    import math
    v = ''
    for i, (x, y) in enumerate([(0, -r), (r, 0), (0, r), (-r, 0)]):
        rot = [0, math.pi / 2, math.pi, -math.pi / 2][i]
        v += f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{rot}" distance="{k}" id="{n()}"/>'
    return f'<Shape name="{name}" {extra} id="{n()}"><PointsPath isClosed="true" id="{n()}">{v}</PointsPath>{paint}</Shape>'

def text(n, name, run, size, weight, tok, fb, bind_path, conv='', extra='', lp='hug', tid=None):
    c = f' converterId="{conv}"' if conv else ''
    sid = n()
    return (f'<Text name="{name}" {extra} id="{tid or n()}">'
            f'<TextStylePaint fontSize="{size}" fontAssetId="0:7" familyName="Inter" styleName="Medium" id="{sid}">'
            f'{fill(n, tok, fb)}<TextStyleAxis tag="1869640570" axisValue="14" id="{n()}"/>'
            f'<TextStyleAxis tag="2003265652" axisValue="{weight}" id="{n()}"/></TextStylePaint>'
            f'<TextValueRun styleId="{sid}" text="{run}" id="{n()}"><DataBindContext sourcePathIds="{bind_path}" propertyKey="268" nameBased="true"{c} id="{n()}"/></TextValueRun>'
            f'<LayoutParticipant layoutWidthScaleType="{lp}" layoutHeightScaleType="hug" id="{n()}"/></Text>')

ABS = ('positionLeftUnitsValue="points" positionRightUnitsValue="points" positionTopUnitsValue="points" '
       'positionBottomUnitsValue="points" positionTypeValue="absolute"')

def bool_cond(n, path, value):
    v = ' value="true"' if value else ''
    return (f'<TransitionViewModelCondition id="{n()}"><TransitionPropertyViewModelComparator id="{n()}">'
            f'<BindablePropertyBoolean id="{n()}"><DataBindContext sourcePathIds="{path}" propertyKey="634" id="{n()}"/></BindablePropertyBoolean>'
            f'</TransitionPropertyViewModelComparator><TransitionValueBooleanComparator{v} id="{n()}"/></TransitionViewModelCondition>')

def trig_cond(n, path):
    return (f'<TransitionViewModelCondition opValue="notEqual" id="{n()}"><TransitionPropertyViewModelComparator id="{n()}">'
            f'<BindablePropertyTrigger id="{n()}"><DataBindContext sourcePathIds="{path}" propertyKey="686" id="{n()}"/></BindablePropertyTrigger>'
            f'</TransitionPropertyViewModelComparator><TransitionValueTriggerComparator id="{n()}"/></TransitionViewModelCondition>')

def keyframes(n, obj, prop, frames):
    kf = ''.join(f'<KeyFrameDouble value="{v}" frame="{f}" id="{n()}"/>' for f, v in frames)
    return f'<KeyedObject objectId="{obj}" id="{n()}"><KeyedProperty propertyKey="{prop}" id="{n()}">{kf}</KeyedProperty></KeyedObject>'

# ---------------------------------------------------------------- tick
def tick():
    n = ids(404)
    ab, st, sm, layer, anim = n(), n(), n(), n(), n()
    on = circle(n, 4, 'On', fill(n, '10:7402', 'FF09090B'), 'opacity="0.55"')
    off = circle(n, 4, 'Off', fill(n, MUTED, 'FFA1A1AA'))
    return f'''<Rive version="1" kind="fragment">
<Artboard defaultStateMachineId="{sm}" viewModelId="{TICK_VM}" viewModelInstanceId="403:210" isComponent="true" spaceId="1:5601" width="4" height="4" styleId="{st}" x="4000" y="200" name="Slider Tick" id="{ab}">
<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="00000000" id="{n()}"/></Fill>
<LayoutComponentStyle id="{st}"/>
<Node x="2" y="2" name="Dot" id="{n()}">
<Node name="On Wrap" id="{n()}">{on}<DataBindContext sourcePathIds="{TICK_VM}-{TICK_ON}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></Node>
<Node name="Off Wrap" id="{n()}">{off}<DataBindContext sourcePathIds="{TICK_VM}-{TICK_ON}" propertyKey="18" nameBased="true" converterId="{SHIELD}" id="{n()}"/></Node>
</Node>
<StateMachine name="State Machine 1" id="{sm}">
<StateMachineLayer name="Layer 1" id="{layer}"><AnimationState animationId="{anim}" id="{n()}"/><AnyState id="{n()}"/><ExitState id="{n()}"/><EntryState id="{n()}"/></StateMachineLayer>
</StateMachine>
<LinearAnimation name="Idle" id="{anim}"/>
</Artboard>
</Rive>
'''

# ---------------------------------------------------------------- slider
TRACK_W, PAD = 260, 10

def slider():
    n = ids(405)
    ab, st, sm = n(), n(), n()
    area, area_st = n(), n()
    thumb_node = n()
    bubble, halo, knob_dis = n(), n(), n()
    a_idle, a_show, a_up, a_down = n(), n(), n(), n()
    hv = n()
    # thumb: halo (brand300 @ 30%), knob (white with shadow + border), disabled knob twin, value bubble above
    knob = (f'<Shape name="Knob" id="{n()}"><PointsPath isClosed="true" id="{n()}">'
            + ''.join(f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{r}" distance="4.97" id="{n()}"/>'
                      for x, y, r in [(0, -9, 0), (9, 0, 1.5707963), (0, 9, 3.1415927), (-9, 0, -1.5707963)])
            + f'</PointsPath>'
            f'<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="40000000" id="{n()}"/>'
            f'<Feather strength="4" offsetY="1" id="{n()}"><DataBindContext sourcePathIds="{T(SH_BLUR)}" propertyKey="749" converterId="0:0" id="{n()}"/>'
            f'<DataBindContext sourcePathIds="{T(SH_Y)}" propertyKey="751" converterId="0:0" id="{n()}"/></Feather></Fill>'
            f'<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="FFFFFFFF" id="{n()}"/></Fill>'
            f'<Stroke thickness="2" id="{n()}">{color(n, BRAND, "FF2563EB")}</Stroke></Shape>')
    knob_d = (f'<Shape name="Disabled Knob" id="{knob_dis}"><PointsPath isClosed="true" id="{n()}">'
              + ''.join(f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{r}" distance="4.97" id="{n()}"/>'
                        for x, y, r in [(0, -9, 0), (9, 0, 1.5707963), (0, 9, 3.1415927), (-9, 0, -1.5707963)])
              + f'</PointsPath>{fill(n, BSTRONG, "FF3F3F46")}<Stroke thickness="2" id="{n()}">{color(n, BORDER, "FF27272A")}</Stroke>'
              f'<DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></Shape>')
    halo_s = circle(n, 32, 'Halo', fill(n, BRAND300, 'FF93C5FD'), f'opacity="0"')
    halo_s = halo_s.replace(f'<Shape name="Halo" opacity="0" id="', f'<Shape name="Halo" opacity="0" id="', 1)
    # the halo's own id: patch so animations can key it
    hid = halo_s.split('id="', 1)[1].split('"', 1)[0]
    bubble_s = (f'<Node y="-28" opacity="0" scaleX="0.8" scaleY="0.8" name="Bubble" id="{bubble}">'
                + text(n, 'Bubble Value', '40', 12, 600, BG_TOKEN, 'FF09090B', vp('value'), '403:300', extra='sizingValue="fixed" width="36" height="20" alignValue="center" verticalAlignValue="middle" x="-18" y="-10"')
                + f'<Shape name="Tip" id="{n()}"><PointsPath isClosed="true" id="{n()}">'
                f'<StraightVertex x="-5" y="9" id="{n()}"/><StraightVertex x="5" y="9" id="{n()}"/><StraightVertex x="0" y="14" id="{n()}"/></PointsPath>'
                f'{fill(n, TEXT, "FFFAFAFA")}</Shape>'
                f'<Shape name="Body" id="{n()}"><Rectangle width="36" height="20" cornerRadiusTL="6" linkCornerRadius="true" id="{n()}"/>{fill(n, TEXT, "FFFAFAFA")}</Shape>'
                                + f'</Node>')
    thumb = (f'<Node x="{PAD}" y="12" name="Thumb" id="{thumb_node}">{bubble_s}{knob_d}{knob}{halo_s}'
             f'<DataBindContext sourcePathIds="{vp("_fraction")}" propertyKey="13" nameBased="true" converterId="403:301" id="{n()}"/></Node>')
    ticks_l, ticks_st = n(), n()
    ticks = (f'<LayoutComponent height="4" styleId="{ticks_st}" name="Ticks" id="{ticks_l}">'
             f'<ArtboardComponentList participatesInLayout="true" id="{n()}"><DataBindContext sourcePathIds="{vp("_ticks")}" propertyKey="800" id="{n()}"/></ArtboardComponentList>'
             f'<LayoutComponentStyle {ABS} positionLeft="{PAD - 2}" positionRight="{PAD - 2}" positionTop="10" heightUnitsValue="points" '
             f'layoutAlignmentType="spaceBetweenCenter" layoutWidthScaleType="fill" widthUnitsValue="auto" id="{ticks_st}"/>'
             f'<DataBindContext sourcePathIds="{vp("showTicks")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></LayoutComponent>')
    track_l, track_st, fill_l, fill_st, fill_d = n(), n(), n(), n(), n()
    track = (f'<LayoutComponent clip="true" height="4" styleId="{track_st}" name="Track" id="{track_l}">'
             f'<LayoutComponent width="40" styleId="{fill_st}" name="Fill" id="{fill_l}">'
             f'<LayoutComponent styleId="{(dst := n())}" name="Disabled Fill" id="{n()}">{fill(n, BSTRONG, "FF3F3F46")}'
             f'<LayoutComponentStyle {ABS} edgeConstraints="84" layoutWidthScaleType="fill" layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto" id="{dst}"/>'
             f'<DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></LayoutComponent>'
             f'<Fill fillRule="clockwise" id="{n()}">{color(n, BRAND, "FF2563EB")}</Fill>'
             f'<LayoutComponentStyle layoutHeightScaleType="fill" widthUnitsValue="percent" heightUnitsValue="auto" id="{fill_st}"/>'
             f'<DataBindContext sourcePathIds="{vp("_fraction")}" propertyKey="7" nameBased="true" converterId="403:302" id="{n()}"/></LayoutComponent>'
             f'{fill(n, BORDER, "FF27272A")}'
             f'<LayoutComponentStyle {ABS} positionLeft="{PAD}" positionRight="{PAD}" positionTop="10" heightUnitsValue="points" '
             f'cornerRadiusTL="2" layoutWidthScaleType="fill" widthUnitsValue="auto" id="{track_st}"/></LayoutComponent>')
    script_l, script_st = n(), n()
    script = (f'<LayoutComponent styleId="{script_st}" name="Drag" id="{script_l}">'
              f'<ScriptedLayout scriptAssetId="403:400" name="Discrete Slider" id="{n()}"/>'
              f'<LayoutComponentStyle {ABS} edgeConstraints="84" layoutWidthScaleType="fill" layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto" id="{script_st}"/></LayoutComponent>')
    sem = (f'<SemanticData role="slider" traitFlags="32" name="Semantics" id="{n()}">'
           f'<DataBindContext sourcePathIds="{vp("label")}" propertyKey="983" nameBased="true" id="{n()}"/>'
           f'<DataBindContext sourcePathIds="{vp("value")}" propertyKey="984" nameBased="true" converterId="403:300" id="{n()}"/>'
           f'<DataBindContext sourcePathIds="{vp("a11yHidden")}" propertyKey="1004" nameBased="true" id="{n()}"/>'
           f'<DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="1002" nameBased="true" id="{n()}"/></SemanticData>'
           f'<FocusData name="Focus" id="{n()}"><DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="953" nameBased="true" converterId="1:1018" id="{n()}"/></FocusData>')
    header_st = n()
    header = (f'<LayoutComponent styleId="{header_st}" name="Header" id="{n()}">'
              + text(n, 'Label', 'Volume', 14, 500, TEXT, 'FFFAFAFA', vp('label'), lp='fill')
              + text(n, 'Value', '40', 14, 400, TEXT2, 'FFD4D4D8', vp('value'), '403:300', tid=hv)
              + f'<LayoutComponentStyle gapHorizontal="12" intrinsicallySizedValue="true" layoutWidthScaleType="fill" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{header_st}"/></LayoutComponent>')
    frame_st = n()
    body = (f'<LayoutComponent styleId="{frame_st}" name="Frame" id="{n()}">{header}'
            f'<LayoutComponent height="24" styleId="{area_st}" name="Track Area" id="{area}">{script}{thumb}{ticks}{track}{sem}'
            f'<LayoutComponentStyle layoutWidthScaleType="fill" widthUnitsValue="auto" heightUnitsValue="points" id="{area_st}"/></LayoutComponent>'
            f'<LayoutComponentStyle gapVertical="6" flexDirectionValue="column" intrinsicallySizedValue="true" layoutWidthScaleType="fill" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{frame_st}"/></LayoutComponent>')

    def lst(name, inputs, action):
        return f'<StateMachineListener targetId="{area}" name="{name}" id="{n()}">{inputs}{action}</StateMachineListener>'
    cur = lambda v: (f'<ListenerViewModelChange id="{n()}"><BindablePropertyBoolean{" propertyValue=" + chr(34) + "true" + chr(34) if v else ""} id="{n()}">'
                     f'<DataBindContext sourcePathIds="10:7-63:244" propertyKey="634" direction="true" id="{n()}"/></BindablePropertyBoolean></ListenerViewModelChange>')
    fire = lambda prop: (f'<ListenerViewModelChange fromViewModelProperty="true" fromDataBindId="{(d := n())}" id="{n()}"><BindablePropertyTrigger id="{n()}">'
                         f'<DataBindContext sourcePathIds="{vp(prop)}" propertyKey="686" id="{d}"/>'
                         f'<DataBindContext sourcePathIds="{vp(prop)}" propertyKey="686" direction="true" converterId="1:1332" id="{n()}"/></BindablePropertyTrigger></ListenerViewModelChange>')
    step = lambda conv: (f'<ListenerViewModelChange fromViewModelProperty="true" fromDataBindId="{(d := n())}" id="{n()}"><BindablePropertyNumber id="{n()}">'
                         f'<DataBindContext sourcePathIds="{vp("value")}" propertyKey="636" converterId="{conv}" id="{d}"/>'
                         f'<DataBindContext sourcePathIds="{vp("value")}" propertyKey="636" direction="true" id="{n()}"/></BindablePropertyNumber></ListenerViewModelChange>')
    listeners = (
        lst('Cursor On', f'<ListenerInputType id="{n()}"/><ListenerInputType listenerTypeValue="move" id="{n()}"/>', cur(True))
        + lst('Cursor Off', f'<ListenerInputType listenerTypeValue="exit" id="{n()}"/>', cur(False))
        + f'<StateMachineListener targetId="{ab}" name="Preview Disabled" id="{n()}"><ListenerInputTypeViewModel viewModelPathIds="10:7-15:419" listenerTypeValue="viewModel" id="{n()}"/>'
          f'<ListenerViewModelChange fromViewModelProperty="true" fromDataBindId="{(pd := n())}" id="{n()}"><BindablePropertyBoolean id="{n()}">'
          f'<DataBindContext sourcePathIds="10:7-15:419" propertyKey="634" id="{pd}"/><DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="634" direction="true" id="{n()}"/>'
          f'</BindablePropertyBoolean></ListenerViewModelChange></StateMachineListener>'
        + lst('Keys Up', f'<ListenerInputTypeSemantic listenerTypeValue="semanticAction" id="{n()}"><SemanticInput actionType="increase" id="{n()}"/></ListenerInputTypeSemantic>'
                         f'<ListenerInputTypeKeyboard listenerTypeValue="keyboard" id="{n()}"><KeyboardInput keyType="up" keyPhase="3" id="{n()}"/><KeyboardInput keyType="right" keyPhase="3" id="{n()}"/></ListenerInputTypeKeyboard>', fire('_keyUp'))
        + lst('Keys Down', f'<ListenerInputTypeSemantic listenerTypeValue="semanticAction" id="{n()}"><SemanticInput actionType="decrease" id="{n()}"/></ListenerInputTypeSemantic>'
                           f'<ListenerInputTypeKeyboard listenerTypeValue="keyboard" id="{n()}"><KeyboardInput keyType="down" keyPhase="3" id="{n()}"/><KeyboardInput keyType="left" keyPhase="3" id="{n()}"/></ListenerInputTypeKeyboard>', fire('_keyDown'))
        + f'<StateMachineListener targetId="{ab}" name="Step Up" id="{n()}"><ListenerInputTypeViewModel viewModelPathIds="{vp("_doUp")}" listenerTypeValue="viewModel" id="{n()}"/>{step("403:303")}</StateMachineListener>'
        + f'<StateMachineListener targetId="{ab}" name="Step Down" id="{n()}"><ListenerInputTypeViewModel viewModelPathIds="{vp("_doDown")}" listenerTypeValue="viewModel" id="{n()}"/>{step("403:304")}</StateMachineListener>'
    )

    def gate(name, key, do):
        idle, firing, an = n(), n(), n()
        return (an, f'<StateMachineLayer name="{name}" id="{n()}">'
                f'<AnimationState animationId="{an}" stateName="Idle" id="{idle}"><StateTransition stateToId="{firing}" id="{n()}">'
                f'{trig_cond(n, vp(key))}{bool_cond(n, vp("disabled"), False)}<StateMachineFireTrigger viewModelPathIds="{vp(do)}" id="{n()}"/></StateTransition></AnimationState>'
                f'<AnimationState animationId="{an}" stateName="Fire" id="{firing}"><StateTransition stateToId="{idle}" id="{n()}"/></AnimationState>'
                f'<AnyState id="{n()}"/><ExitState id="{n()}"/><EntryState id="{n()}"><StateTransition stateToId="{idle}" id="{n()}"/></EntryState></StateMachineLayer>')
    g_up_anim, g_up = gate('Key Up Gate', '_keyUp', '_doUp')
    g_dn_anim, g_dn = gate('Key Down Gate', '_keyDown', '_doDown')

    s_hide, s_drag, s_hover = n(), n(), n()
    look = (f'<StateMachineLayer name="Thumb" id="{n()}"><AnyState id="{n()}">'
            f'<StateTransition stateToId="{s_drag}" duration="120" id="{n()}">{bool_cond(n, vp("_dragging"), True)}</StateTransition>'
            f'<StateTransition stateToId="{s_hover}" duration="120" id="{n()}">{bool_cond(n, vp("_dragging"), False)}{bool_cond(n, vp("_hover"), True)}</StateTransition>'
            f'<StateTransition stateToId="{s_hide}" duration="160" id="{n()}">{bool_cond(n, vp("_dragging"), False)}{bool_cond(n, vp("_hover"), False)}</StateTransition>'
            f'</AnyState><ExitState id="{n()}"/><EntryState id="{n()}"><StateTransition stateToId="{s_hide}" id="{n()}"/></EntryState>'
            f'<AnimationState animationId="{a_idle}" stateName="Rest" id="{s_hide}"/><AnimationState animationId="{a_up}" stateName="Hover" id="{s_hover}"/>'
            f'<AnimationState animationId="{a_show}" stateName="Drag" id="{s_drag}"/></StateMachineLayer>')
    anims = (f'<LinearAnimation fps="60" duration="1" loopValue="loop" name="Rest" id="{a_idle}">'
             f'{keyframes(n, bubble, 18, [(0, 0)])}{keyframes(n, bubble, 16, [(0, 0.8)])}{keyframes(n, bubble, 17, [(0, 0.8)])}{keyframes(n, hid, 18, [(0, 0)])}{keyframes(n, hv, 18, [(0, 1)])}</LinearAnimation>'
             f'<LinearAnimation fps="60" duration="1" loopValue="loop" name="Hover" id="{a_up}">'
             f'{keyframes(n, bubble, 18, [(0, 1)])}{keyframes(n, bubble, 16, [(0, 1)])}{keyframes(n, bubble, 17, [(0, 1)])}{keyframes(n, hid, 18, [(0, 0.25)])}{keyframes(n, hv, 18, [(0, 0)])}</LinearAnimation>'
             f'<LinearAnimation fps="60" duration="1" loopValue="loop" name="Drag" id="{a_show}">'
             f'{keyframes(n, bubble, 18, [(0, 1)])}{keyframes(n, bubble, 16, [(0, 1)])}{keyframes(n, bubble, 17, [(0, 1)])}{keyframes(n, hid, 18, [(0, 0.4)])}{keyframes(n, hv, 18, [(0, 0)])}</LinearAnimation>'
             f'<LinearAnimation name="Gate Up" id="{g_up_anim}"/><LinearAnimation name="Gate Down" id="{g_dn_anim}"/>')
    return f'''<Rive version="1" kind="fragment">
<Artboard defaultStateMachineId="{sm}" viewModelId="{VM}" viewModelInstanceId="403:150" isComponent="true" spaceId="1:5601" width="280" height="56" styleId="{st}" x="4000" y="400" name="Discrete Slider" id="{ab}">
<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="00000000" id="{n()}"/></Fill>
<LayoutComponentStyle intrinsicallySizedValue="true" layoutHeightScaleType="hug" heightUnitsValue="auto" id="{st}"/>
{body}
<StateMachine name="State Machine 1" id="{sm}">{listeners}{look}{g_up}{g_dn}</StateMachine>
{anims}
</Artboard>
</Rive>
'''

BG_TOKEN = '10:7402'

def root_parts():
    """View models, converters and the script asset (inserted into 99-_root.rml)."""
    n = ids(403)
    for _ in range(500):  # keep the generated counter clear of the fixed ids above
        pass
    tok = lambda k, conv='': (f'<FormulaTokenValue id="403:{next(c)}"><DataBindContext sourcePathIds="{vp(k)}" propertyKey="777" nameBased="true"'
                              + (f' converterId="{conv}"' if conv else '') + f' id="403:{next(c)}"/></FormulaTokenValue>')
    c = itertools.count(600)
    conv = f'''    <DataConverterToString round="true" decimals="1" name="Discrete Slider · Value (1 decimal)" groupId="1:2674" id="403:305"/>
    <DataConverterStringRemoveZeros name="Discrete Slider · No trailing zeros" groupId="1:2674" id="403:306"/>
    <DataConverterGroup name="Discrete Slider · Value (to text)" groupId="1:2674" id="403:300">
        <DataConverterGroupItem converterId="403:305" id="403:307"/>
        <DataConverterGroupItem converterId="403:306" id="403:308"/>
    </DataConverterGroup>
    <DataConverterFormula name="Discrete Slider · Thumb x" groupId="1:2674" id="403:301">
        <FormulaTokenInput id="403:{next(c)}"/><FormulaTokenOperation operationType="multiply" id="403:{next(c)}"/><FormulaTokenValue operationValue="{TRACK_W}" id="403:{next(c)}"/>
        <FormulaTokenOperation id="403:{next(c)}"/><FormulaTokenValue operationValue="{PAD}" id="403:{next(c)}"/>
    </DataConverterFormula>
    <DataConverterFormula name="Discrete Slider · Fill percent" groupId="1:2674" id="403:302">
        <FormulaTokenInput id="403:{next(c)}"/><FormulaTokenOperation operationType="multiply" id="403:{next(c)}"/><FormulaTokenValue operationValue="100" id="403:{next(c)}"/>
    </DataConverterFormula>
    <DataConverterFormula name="Discrete Slider · Step up" groupId="1:2674" id="403:303">
        <FormulaTokenFunction id="403:{next(c)}"/>{tok("max")}<FormulaTokenArgumentSeparator id="403:{next(c)}"/>
        <FormulaTokenInput id="403:{next(c)}"/><FormulaTokenOperation id="403:{next(c)}"/>{tok("step")}<FormulaTokenParenthesisClose id="403:{next(c)}"/>
    </DataConverterFormula>
    <DataConverterFormula name="Discrete Slider · Step down" groupId="1:2674" id="403:304">
        <FormulaTokenFunction functionType="max" id="403:{next(c)}"/>{tok("min")}<FormulaTokenArgumentSeparator id="403:{next(c)}"/>
        <FormulaTokenInput id="403:{next(c)}"/><FormulaTokenOperation operationType="subtract" id="403:{next(c)}"/>{tok("step")}<FormulaTokenParenthesisClose id="403:{next(c)}"/>
    </DataConverterFormula>
'''
    script = '    <ScriptAsset file="Discrete Slider.luau" name="Discrete Slider" groupId="327:1" id="403:400"/>\n'
    def inst(iid, name, vals):
        out = f'        <ViewModelInstance exports="true" name="{name}" id="{iid}">\n'
        for k, pid in P.items():
            v = vals.get(k)
            typ = {'label': 'String', 'disabled': 'Boolean', 'a11yHidden': 'Boolean', 'showTicks': 'Boolean', '_dragging': 'Boolean',
                   '_hover': 'Boolean', '_ticks': 'List', '_keyUp': 'Trigger', '_keyDown': 'Trigger', '_doUp': 'Trigger', '_doDown': 'Trigger'}.get(k, 'Number')
            pv = f' propertyValue="{v}"' if v is not None else ''
            out += f'            <ViewModelInstance{typ}{pv} viewModelPropertyId="{pid}" id="403:{next(c)}"/>\n'
        return out + '        </ViewModelInstance>\n'
    types = {'label': 'String', 'disabled': 'Boolean', 'a11yHidden': 'Boolean', 'showTicks': 'Boolean', '_dragging': 'Boolean', '_hover': 'Boolean',
             '_ticks': 'List', '_keyUp': 'Trigger', '_keyDown': 'Trigger', '_doUp': 'Trigger', '_doDown': 'Trigger'}
    vm = f'    <ViewModel defaultInstanceId="403:150" name="DiscreteSlider" groupId="1:2673" id="{VM}">\n'
    vm += ''.join(f'        <ViewModelProperty{types.get(k, "Number")} name="{k}" id="{pid}"/>\n' for k, pid in P.items())
    vm += inst('403:150', 'Volume', dict(value=40, min=0, max=100, step=10, label='Volume', showTicks='true', _fraction=0.4))
    vm += inst('403:151', 'Temperature', dict(value=21, min=16, max=26, step=1, label='Temperature', showTicks='true', _fraction=0.5))
    vm += '    </ViewModel>\n'
    vm += f'''    <ViewModel defaultInstanceId="403:210" name="SliderTick" groupId="1:2673" id="{TICK_VM}">
        <ViewModelPropertyBoolean name="on" id="{TICK_ON}"/>
        <ViewModelInstance exports="true" name="Tick" id="403:210">
            <ViewModelInstanceBoolean viewModelPropertyId="{TICK_ON}" id="403:211"/>
        </ViewModelInstance>
    </ViewModel>
'''
    return conv, script, vm

if __name__ == '__main__':
    open('shared/55-SliderTick.rml', 'w').write(tick())
    open('shared/56-DiscreteSlider.rml', 'w').write(slider())
    conv, script, vm = root_parts()
    p = 'shared/99-_root.rml'
    s = open(p).read()
    import re
    s = re.sub(r'    <!-- discrete-slider -->.*?<!-- /discrete-slider -->\n', '', s, flags=re.S)
    s = s.replace('\n</Rive>', '\n    <!-- discrete-slider -->\n' + conv + script + vm + '    <!-- /discrete-slider -->\n</Rive>')
    open(p, 'w').write(s)
    print('ok')
