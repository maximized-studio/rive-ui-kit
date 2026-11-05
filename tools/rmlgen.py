"""Small helpers for writing RML by script (ids, theme-bound paints, state machine bits, pretty printing)."""
import itertools, xml.dom.minidom

class Ids:
    def __init__(self, client, start=1):
        self.c, self.n = client, itertools.count(start)
    def __call__(self):
        return f'{self.c}:{next(self.n)}'

def pretty(doc):
    out = xml.dom.minidom.parseString(doc).toprettyxml(indent='    ')
    return '\n'.join(l for l in out.split('\n')[1:] if l.strip()) + '\n'

def color(nid, path, fallback):
    """SolidColor bound to a view model colour (path = 'vm-prop-...-prop')."""
    return (f'<SolidColor colorValue="{fallback}" id="{nid()}">'
            f'<DataBindContext sourcePathIds="{path}" propertyKey="37" id="{nid()}"/></SolidColor>')

def fill(nid, path, fb):
    return f'<Fill fillRule="clockwise" id="{nid()}">{color(nid, path, fb)}</Fill>'

def stroke(nid, path, fb, w=1):
    return f'<Stroke thickness="{w}" cap="butt" join="miter" id="{nid()}">{color(nid, path, fb)}</Stroke>'

def path(nid, pts, closed=True):
    v = ''.join(f'<StraightVertex x="{x}" y="{y}" id="{nid()}"/>' for x, y in pts)
    return f'<PointsPath isClosed="{str(closed).lower()}" id="{nid()}">{v}</PointsPath>'

ABS_FILL = ('positionLeftUnitsValue="points" positionRightUnitsValue="points" positionTopUnitsValue="points" '
            'positionBottomUnitsValue="points" edgeConstraints="84" positionTypeValue="absolute" '
            'layoutWidthScaleType="fill" layoutHeightScaleType="fill" widthUnitsValue="auto" heightUnitsValue="auto"')

def abs_layer(nid, name, inner, opacity=None, extra_style=''):
    sid = nid()
    op = f' opacity="{opacity}"' if opacity is not None else ''
    return (f'<LayoutComponent styleId="{sid}"{op} name="{name}" id="{nid()}">'
            f'<LayoutComponentStyle {ABS_FILL} {extra_style} id="{sid}"/>{inner}</LayoutComponent>')

def cond_bool(nid, path, value):
    v = ' value="true"' if value else ''
    return (f'<TransitionViewModelCondition id="{nid()}"><TransitionPropertyViewModelComparator id="{nid()}">'
            f'<BindablePropertyBoolean id="{nid()}"><DataBindContext sourcePathIds="{path}" propertyKey="634" id="{nid()}"/></BindablePropertyBoolean>'
            f'</TransitionPropertyViewModelComparator><TransitionValueBooleanComparator{v} id="{nid()}"/></TransitionViewModelCondition>')

def cond_trigger(nid, path):
    return (f'<TransitionViewModelCondition opValue="notEqual" id="{nid()}"><TransitionPropertyViewModelComparator id="{nid()}">'
            f'<BindablePropertyTrigger id="{nid()}"><DataBindContext sourcePathIds="{path}" propertyKey="686" id="{nid()}"/></BindablePropertyTrigger>'
            f'</TransitionPropertyViewModelComparator><TransitionValueTriggerComparator id="{nid()}"/></TransitionViewModelCondition>')

def opacity_anim(nid, name, aid, keys):
    """keys: [(objectId, [(frame, value), ...]), ...]"""
    objs = ''
    for obj, frames in keys:
        kfs = ''.join(f'<KeyFrameDouble value="{v}" interpolationType="{"cubic" if i == 0 else "linear"}" frame="{f}" id="{nid()}"/>'
                      for i, (f, v) in enumerate(frames))
        objs += f'<KeyedObject objectId="{obj}" id="{nid()}"><KeyedProperty property="opacity" id="{nid()}">{kfs}</KeyedProperty></KeyedObject>'
    return f'<LinearAnimation viewEnd="60" name="{name}" id="{aid}">{objs}</LinearAnimation>'

def bool_layer(nid, name, path, off_anim, on_anim, dur_on=120, dur_off=200):
    """Layer that follows a boolean: Any -> On when true, Any -> Off when false."""
    s_init, s_off, s_on = nid(), nid(), nid()
    return f'''<StateMachineLayer name="{name}" id="{nid()}">
      <AnyState id="{nid()}">
        <StateTransition stateToId="{s_on}" duration="{dur_on}" id="{nid()}">{cond_bool(nid, path, True)}</StateTransition>
        <StateTransition stateToId="{s_off}" duration="{dur_off}" id="{nid()}">{cond_bool(nid, path, False)}</StateTransition>
      </AnyState>
      <ExitState id="{nid()}"/>
      <EntryState id="{nid()}"><StateTransition stateToId="{s_init}" id="{nid()}"/></EntryState>
      <AnimationState animationId="{off_anim}" id="{s_init}"/>
      <AnimationState animationId="{off_anim}" id="{s_off}"/>
      <AnimationState animationId="{on_anim}" id="{s_on}"/>
    </StateMachineLayer>'''

def trigger_layer(nid, name, path, anim):
    """Layer that replays an animation on every trigger fire (twin states, so a fire mid-play restarts it)."""
    s1, s2 = nid(), nid()
    return f'''<StateMachineLayer name="{name}" id="{nid()}">
      <AnyState id="{nid()}"><StateTransition stateToId="{s1}" id="{nid()}">{cond_trigger(nid, path)}</StateTransition></AnyState>
      <ExitState id="{nid()}"/>
      <EntryState id="{nid()}"/>
      <AnimationState animationId="{anim}" id="{s1}"><StateTransition stateToId="{s2}" id="{nid()}">{cond_trigger(nid, path)}</StateTransition></AnimationState>
      <AnimationState animationId="{anim}" id="{s2}"/>
    </StateMachineLayer>'''
