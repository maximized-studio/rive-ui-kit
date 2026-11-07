"""Generates the Range Discrete Slider (shared/56b-RangeDiscreteSlider.rml): two thumbs on the Discrete Slider's track.

Same look and approach as the Discrete Slider (tools/discrete_slider.py, whose helpers, Slider Tick and converters it
reuses): the look is native and bound, and the Luau script "Range Discrete Slider" maps drags to `low` / `high`
(snapped to `step` within min..max, never crossing), writes the thumbs' fractions and fills `_ticks` (on between
the thumbs). Ids: 345 (view model, converters, script), 346 (artboard). Run from the repo root."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from discrete_slider import (ids, color, fill, circle, text, bool_cond, keyframes, ABS, T, TEXT, TEXT2, BORDER, BSTRONG,
                             BRAND, BRAND300, SH_BLUR, SH_Y, TOGGLE_ON, TRACK_W, PAD, BG_TOKEN, TICK_VM)

VM = '345:100'
P = dict(low='345:101', high='345:102', min='345:103', max='345:104', step='345:105', label='345:106', disabled='345:107',
         a11yHidden='345:108', showTicks='345:109', _lowFraction='345:110', _highFraction='345:111', _span='345:112',
         _hoverLow='345:113', _hoverHigh='345:114', _dragLow='345:115', _dragHigh='345:116', _ticks='345:117',
         _keyUp='345:118', _keyDown='345:119')
TYPES = {'label': 'String', 'disabled': 'Boolean', 'a11yHidden': 'Boolean', 'showTicks': 'Boolean', '_hoverLow': 'Boolean',
         '_hoverHigh': 'Boolean', '_dragLow': 'Boolean', '_dragHigh': 'Boolean', '_ticks': 'List', '_keyUp': 'Trigger', '_keyDown': 'Trigger'}
vp = lambda k: f'{VM}-{P[k]}'
VALUE_TEXT, THUMB_X, PERCENT = '403:300', '403:301', '403:302'   # the Discrete Slider's converters
SCRIPT = '345:400'


def knob(n):
    pts = [(0, -9, 0), (9, 0, 1.5707963), (0, 9, 3.1415927), (-9, 0, -1.5707963)]
    path = lambda: (f'<PointsPath isClosed="true" id="{n()}">'
                    + ''.join(f'<CubicMirroredVertex x="{x}" y="{y}" rotation="{r}" distance="4.97" id="{n()}"/>' for x, y, r in pts) + '</PointsPath>')
    k = (f'<Shape name="Knob" id="{n()}">{path()}'
         f'<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="40000000" id="{n()}"/>'
         f'<Feather strength="4" offsetY="1" id="{n()}"><DataBindContext sourcePathIds="{T(SH_BLUR)}" propertyKey="749" converterId="0:0" id="{n()}"/>'
         f'<DataBindContext sourcePathIds="{T(SH_Y)}" propertyKey="751" converterId="0:0" id="{n()}"/></Feather></Fill>'
         f'<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="FFFFFFFF" id="{n()}"/></Fill>'
         f'<Stroke thickness="2" id="{n()}">{color(n, BRAND, "FF2563EB")}</Stroke></Shape>')
    kd = (f'<Shape name="Disabled Knob" id="{n()}">{path()}{fill(n, BSTRONG, "FF3F3F46")}<Stroke thickness="2" id="{n()}">{color(n, BORDER, "FF27272A")}</Stroke>'
          f'<DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></Shape>')
    return kd + k


def thumb(n, name, which):
    bubble = n()
    b = (f'<Node y="-28" opacity="0" scaleX="0.8" scaleY="0.8" name="Bubble" id="{bubble}">'
         + text(n, 'Bubble Value', '40', 12, 600, BG_TOKEN, 'FF09090B', vp(which), VALUE_TEXT,
                extra='sizingValue="fixed" width="36" height="20" alignValue="center" verticalAlignValue="middle" x="-18" y="-10"')
         + f'<Shape name="Tip" id="{n()}"><PointsPath isClosed="true" id="{n()}">'
           f'<StraightVertex x="-5" y="9" id="{n()}"/><StraightVertex x="5" y="9" id="{n()}"/><StraightVertex x="0" y="14" id="{n()}"/></PointsPath>'
           f'{fill(n, TEXT, "FFFAFAFA")}</Shape>'
         + f'<Shape name="Body" id="{n()}"><Rectangle width="36" height="20" cornerRadiusTL="6" linkCornerRadius="true" id="{n()}"/>{fill(n, TEXT, "FFFAFAFA")}</Shape></Node>')
    halo = circle(n, 32, 'Halo', fill(n, BRAND300, 'FF93C5FD'), 'opacity="0"')
    hid = halo.split('id="', 1)[1].split('"', 1)[0]
    frac = '_lowFraction' if which == 'low' else '_highFraction'
    xml = (f'<Node x="{PAD}" y="12" name="{name}" id="{n()}">{b}{knob(n)}{halo}'
           f'<DataBindContext sourcePathIds="{vp(frac)}" propertyKey="13" nameBased="true" converterId="{THUMB_X}" id="{n()}"/></Node>')
    return xml, bubble, hid


def slider():
    n = ids(346)
    ab, st, sm, area, area_st = n(), n(), n(), n(), n()
    low_xml, low_bubble, low_halo = thumb(n, 'Low Thumb', 'low')
    high_xml, high_bubble, high_halo = thumb(n, 'High Thumb', 'high')
    ticks_st = n()
    ticks = (f'<LayoutComponent height="4" styleId="{ticks_st}" name="Ticks" id="{n()}">'
             f'<ArtboardComponentList participatesInLayout="true" id="{n()}"><DataBindContext sourcePathIds="{vp("_ticks")}" propertyKey="800" id="{n()}"/></ArtboardComponentList>'
             f'<LayoutComponentStyle {ABS} positionLeft="{PAD - 2}" positionRight="{PAD - 2}" positionTop="10" heightUnitsValue="points" '
             f'layoutAlignmentType="spaceBetweenCenter" layoutWidthScaleType="fill" widthUnitsValue="auto" id="{ticks_st}"/>'
             f'<DataBindContext sourcePathIds="{vp("showTicks")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></LayoutComponent>')
    track_st, fill_st, dst = n(), n(), n()
    track = (f'<LayoutComponent clip="true" height="4" styleId="{track_st}" name="Track" id="{n()}">'
             f'<LayoutComponent width="40" styleId="{fill_st}" name="Fill" id="{n()}">'
             f'<LayoutComponent styleId="{dst}" name="Disabled Fill" id="{n()}">{fill(n, BSTRONG, "FF3F3F46")}'
             f'<LayoutComponentStyle {ABS} edgeConstraints="84" layoutWidthScaleType="fill" layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto" id="{dst}"/>'
             f'<DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="18" nameBased="true" converterId="{TOGGLE_ON}" id="{n()}"/></LayoutComponent>'
             f'<Fill fillRule="clockwise" id="{n()}">{color(n, BRAND, "FF2563EB")}</Fill>'
             f'<LayoutComponentStyle positionLeftUnitsValue="percent" positionTopUnitsValue="points" positionBottomUnitsValue="points" positionTypeValue="absolute" '
             f'layoutHeightScaleType="fill" widthUnitsValue="percent" heightUnitsValue="auto" id="{fill_st}">'
             f'<DataBindContext sourcePathIds="{vp("_lowFraction")}" propertyKey="516" nameBased="true" converterId="{PERCENT}" id="{n()}"/></LayoutComponentStyle>'
             f'<DataBindContext sourcePathIds="{vp("_span")}" propertyKey="7" nameBased="true" converterId="{PERCENT}" id="{n()}"/></LayoutComponent>'
             f'{fill(n, BORDER, "FF27272A")}'
             f'<LayoutComponentStyle {ABS} positionLeft="{PAD}" positionRight="{PAD}" positionTop="10" heightUnitsValue="points" '
             f'cornerRadiusTL="2" layoutWidthScaleType="fill" widthUnitsValue="auto" id="{track_st}"/></LayoutComponent>')
    script_st = n()
    script = (f'<LayoutComponent styleId="{script_st}" name="Drag" id="{n()}">'
              f'<ScriptedLayout scriptAssetId="{SCRIPT}" name="Range Discrete Slider" id="{n()}"/>'
              f'<LayoutComponentStyle {ABS} edgeConstraints="84" layoutWidthScaleType="fill" layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto" id="{script_st}"/></LayoutComponent>')
    sem = (f'<SemanticData role="slider" traitFlags="32" name="Semantics" id="{n()}">'
           f'<DataBindContext sourcePathIds="{vp("label")}" propertyKey="983" nameBased="true" id="{n()}"/>'
           f'<DataBindContext sourcePathIds="{vp("a11yHidden")}" propertyKey="1004" nameBased="true" id="{n()}"/>'
           f'<DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="1002" nameBased="true" id="{n()}"/></SemanticData>'
           f'<FocusData name="Focus" id="{n()}"><DataBindContext sourcePathIds="{vp("disabled")}" propertyKey="953" nameBased="true" converterId="1:1018" id="{n()}"/></FocusData>')
    header_st, hv = n(), n()
    value_st = n()
    header = (f'<LayoutComponent styleId="{header_st}" name="Header" id="{n()}">'
              + text(n, 'Label', 'Price', 14, 500, TEXT, 'FFFAFAFA', vp('label'), lp='fill')
              + f'<LayoutComponent styleId="{value_st}" name="Values" id="{hv}">'
              + text(n, 'Low', '20', 14, 400, TEXT2, 'FFD4D4D8', vp('low'), VALUE_TEXT)
              + text(n, 'Dash', ' – ', 14, 400, TEXT2, 'FFD4D4D8', vp('label')).replace(
                  f'<DataBindContext sourcePathIds="{vp("label")}" propertyKey="268" nameBased="true"', '<X', 1)
              + text(n, 'High', '80', 14, 400, TEXT2, 'FFD4D4D8', vp('high'), VALUE_TEXT)
              + f'<LayoutComponentStyle intrinsicallySizedValue="true" layoutWidthScaleType="hug" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{value_st}"/></LayoutComponent>'
              + f'<LayoutComponentStyle gapHorizontal="12" intrinsicallySizedValue="true" layoutWidthScaleType="fill" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{header_st}"/></LayoutComponent>')
    # the dash is plain text: drop the bind the shared text() helper always adds
    import re
    header = re.sub(r'<X id="[^"]+"/>', '', header)
    frame_st = n()
    body = (f'<LayoutComponent styleId="{frame_st}" name="Frame" id="{n()}">{header}'
            f'<LayoutComponent height="24" styleId="{area_st}" name="Track Area" id="{area}">{script}{low_xml}{high_xml}{ticks}{track}{sem}'
            f'<LayoutComponentStyle layoutWidthScaleType="fill" widthUnitsValue="auto" heightUnitsValue="points" id="{area_st}"/></LayoutComponent>'
            f'<LayoutComponentStyle gapVertical="6" flexDirectionValue="column" intrinsicallySizedValue="true" layoutWidthScaleType="fill" layoutHeightScaleType="hug" widthUnitsValue="auto" heightUnitsValue="auto" id="{frame_st}"/></LayoutComponent>')

    def lst(name, inputs, action):
        return f'<StateMachineListener targetId="{area}" name="{name}" id="{n()}">{inputs}{action}</StateMachineListener>'
    cur = lambda v: (f'<ListenerViewModelChange id="{n()}"><BindablePropertyBoolean{" propertyValue=" + chr(34) + "true" + chr(34) if v else ""} id="{n()}">'
                     f'<DataBindContext sourcePathIds="10:7-63:244" propertyKey="634" direction="true" id="{n()}"/></BindablePropertyBoolean></ListenerViewModelChange>')
    fire = lambda prop: (f'<ListenerViewModelChange fromViewModelProperty="true" fromDataBindId="{(d := n())}" id="{n()}"><BindablePropertyTrigger id="{n()}">'
                         f'<DataBindContext sourcePathIds="{vp(prop)}" propertyKey="686" id="{d}"/>'
                         f'<DataBindContext sourcePathIds="{vp(prop)}" propertyKey="686" direction="true" converterId="1:1332" id="{n()}"/></BindablePropertyTrigger></ListenerViewModelChange>')
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
                           f'<ListenerInputTypeKeyboard listenerTypeValue="keyboard" id="{n()}"><KeyboardInput keyType="down" keyPhase="3" id="{n()}"/><KeyboardInput keyType="left" keyPhase="3" id="{n()}"/></ListenerInputTypeKeyboard>', fire('_keyDown')))

    def look(name, drag, hover, bubble, halo):
        a_rest, a_hover, a_drag = n(), n(), n()
        s_rest, s_hover, s_drag = n(), n(), n()
        layer = (f'<StateMachineLayer name="{name}" id="{n()}"><AnyState id="{n()}">'
                 f'<StateTransition stateToId="{s_drag}" duration="120" id="{n()}">{bool_cond(n, vp(drag), True)}</StateTransition>'
                 f'<StateTransition stateToId="{s_hover}" duration="120" id="{n()}">{bool_cond(n, vp(drag), False)}{bool_cond(n, vp(hover), True)}</StateTransition>'
                 f'<StateTransition stateToId="{s_rest}" duration="160" id="{n()}">{bool_cond(n, vp(drag), False)}{bool_cond(n, vp(hover), False)}</StateTransition>'
                 f'</AnyState><ExitState id="{n()}"/><EntryState id="{n()}"><StateTransition stateToId="{s_rest}" id="{n()}"/></EntryState>'
                 f'<AnimationState animationId="{a_rest}" stateName="Rest" id="{s_rest}"/><AnimationState animationId="{a_hover}" stateName="Hover" id="{s_hover}"/>'
                 f'<AnimationState animationId="{a_drag}" stateName="Drag" id="{s_drag}"/></StateMachineLayer>')
        anims = ''
        for aid, nm, op, sc, ho in ((a_rest, 'Rest', 0, 0.8, 0), (a_hover, 'Hover', 1, 1, 0.25), (a_drag, 'Drag', 1, 1, 0.4)):
            anims += (f'<LinearAnimation fps="60" duration="1" loopValue="loop" name="{name} {nm}" id="{aid}">'
                      f'{keyframes(n, bubble, 18, [(0, op)])}{keyframes(n, bubble, 16, [(0, sc)])}{keyframes(n, bubble, 17, [(0, sc)])}'
                      f'{keyframes(n, halo, 18, [(0, ho)])}</LinearAnimation>')
        return layer, anims
    low_layer, low_anims = look('Low Thumb', '_dragLow', '_hoverLow', low_bubble, low_halo)
    high_layer, high_anims = look('High Thumb', '_dragHigh', '_hoverHigh', high_bubble, high_halo)
    art = f'''<Artboard defaultStateMachineId="{sm}" viewModelId="{VM}" viewModelInstanceId="345:150" isComponent="true" spaceId="1:5601" width="280" height="56" styleId="{st}" x="12000" y="0" name="Range Discrete Slider" id="{ab}">
<Fill fillRule="clockwise" id="{n()}"><SolidColor colorValue="00000000" id="{n()}"/></Fill>
<LayoutComponentStyle intrinsicallySizedValue="true" layoutHeightScaleType="hug" heightUnitsValue="auto" id="{st}"/>
{body}
<StateMachine name="State Machine 1" id="{sm}">{listeners}{low_layer}{high_layer}</StateMachine>
{low_anims}{high_anims}
</Artboard>'''
    return art


def view_model():
    c = iter(range(500, 10000))
    nid = lambda: f'345:{next(c)}'

    def inst(iid, name, vals):
        out = f'<ViewModelInstance exports="true" name="{name}" id="{iid}">'
        for k, pid in P.items():
            v = vals.get(k)
            pv = f' propertyValue="{v}"' if v is not None else ''
            out += f'<ViewModelInstance{TYPES.get(k, "Number")}{pv} viewModelPropertyId="{pid}" id="{nid()}"/>'
        return out + '</ViewModelInstance>'
    vm = f'<ViewModel defaultInstanceId="345:150" name="RangeDiscreteSlider" groupId="1:2673" id="{VM}">'
    vm += ''.join(f'<ViewModelProperty{TYPES.get(k, "Number")} name="{k}" id="{pid}"/>' for k, pid in P.items())
    vm += inst('345:150', 'Price', dict(low=20, high=80, min=0, max=100, step=10, label='Price', showTicks='true',
                                        _lowFraction=0.2, _highFraction=0.8, _span=0.6))
    vm += '</ViewModel>'
    script = f'<ScriptAsset file="Range Discrete Slider.luau" name="Range Discrete Slider" groupId="327:1" id="{SCRIPT}"/>'
    return vm + script


if __name__ == '__main__':
    sys.path.insert(0, 'tools')
    from rmlgen import pretty
    doc = f'<Rive version="1" kind="fragment">{slider()}{view_model()}</Rive>'
    open('shared/56b-RangeDiscreteSlider.rml', 'w').write(pretty(doc))
    print('ok')
