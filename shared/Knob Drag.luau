-- Knob behaviour: turns a pointer drag on the dial into `value`.
--
-- Lives in the Knob's Dial as a fill layout, so its box is the dial. A press inside the round
-- dial starts a drag: moving up or right raises `value`, down or left lowers it (160 points
-- cover the whole range, like most audio knobs). A mouse wheel over the dial steps it too.
-- `value` is kept between `min` and `max` and snapped to `step`. While dragging, `_active` is
-- true (the look shows a halo). `_increase` and `_decrease` (fired by the arrow keys and the
-- screen reader, gated by `disabled` in the state machine) step it by one `step`.
-- The dial's look (arc, indicator, number) is bound natively to `value`; this script only
-- writes the number.

type Knob = {
    context: Context?,
    value: Property<number>?,
    min: Property<number>?,
    max: Property<number>?,
    step: Property<number>?,
    disabled: Property<boolean>?,
    active: Property<boolean>?,
    size: Vector,
    down: boolean,
    startValue: number,
    startPos: Vector,
}

local DRAG = 160 -- points of pointer travel for the full range

local function num(p: Property<number>?, fallback: number): number
    if p == nil then
        return fallback
    end
    return p.value
end

local function set(self: Knob, v: number)
    local value = self.value
    if value == nil then
        return
    end
    local lo, hi = num(self.min, 0), num(self.max, 100)
    if hi < lo then
        lo, hi = hi, lo
    end
    local step = num(self.step, 1)
    if step > 0 then
        v = lo + math.floor((v - lo) / step + 0.5) * step
    end
    v = math.max(lo, math.min(hi, v))
    if value.value ~= v then
        value.value = v
    end
end

local function isDisabled(self: Knob): boolean
    local d = self.disabled
    return d ~= nil and d.value
end

local function inside(self: Knob, p: Vector): boolean
    local r = math.min(self.size.x, self.size.y) / 2
    local dx, dy = p.x - self.size.x / 2, p.y - self.size.y / 2
    return dx * dx + dy * dy <= r * r
end

local function setActive(self: Knob, on: boolean)
    if self.active ~= nil and self.active.value ~= on then
        self.active.value = on
    end
end

function init(self: Knob, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.value = vm:getNumber('value')
    self.min = vm:getNumber('min')
    self.max = vm:getNumber('max')
    self.step = vm:getNumber('step')
    self.disabled = vm:getBoolean('disabled')
    self.active = vm:getBoolean('_active')
    local up, down = vm:getTrigger('_increase'), vm:getTrigger('_decrease')
    if up ~= nil then
        up:addListener(vm, function()
            local s = num(self.step, 1)
            set(self, num(self.value, 0) + (if s > 0 then s else 1))
        end)
    end
    if down ~= nil then
        down:addListener(vm, function()
            local s = num(self.step, 1)
            set(self, num(self.value, 0) - (if s > 0 then s else 1))
        end)
    end
    return true
end

function resize(self: Knob, size: Vector, scale: number)
    self.size = size
end

function advance(self: Knob, seconds: number): boolean
    return false
end

function pointerDown(self: Knob, event: PointerEvent)
    if isDisabled(self) or not inside(self, event.position) then
        return
    end
    self.down = true
    self.startValue = num(self.value, 0)
    self.startPos = event.position
    setActive(self, true)
    event:hit()
end

function pointerMove(self: Knob, event: PointerEvent)
    if not self.down then
        return
    end
    local range = num(self.max, 100) - num(self.min, 0)
    local travel = (event.position.x - self.startPos.x) - (event.position.y - self.startPos.y)
    set(self, self.startValue + travel * range / DRAG)
    event:hit()
end

function pointerUp(self: Knob, event: PointerEvent)
    if not self.down then
        return
    end
    self.down = false
    setActive(self, false)
    event:hit()
end

function pointerExit(self: Knob, event: PointerEvent)
    -- a drag keeps going outside the dial; only a release ends it
end

function pointerScroll(self: Knob, event: ScrollEvent)
    if isDisabled(self) or not inside(self, event.position) then
        return
    end
    local s = num(self.step, 1)
    local dir = if event.delta.y > 0 then 1 elseif event.delta.y < 0 then -1 else 0
    if dir ~= 0 then
        set(self, num(self.value, 0) + dir * (if s > 0 then s else 1))
        event:hit()
    end
end

function draw(self: Knob, renderer: Renderer) end

return function(context: Context): Layout<Knob>
    return {
        context = nil,
        value = nil,
        min = nil,
        max = nil,
        step = nil,
        disabled = nil,
        active = nil,
        size = Vector.xy(96, 96),
        down = false,
        startValue = 0,
        startPos = Vector.xy(0, 0),
        init = init,
        resize = resize,
        advance = advance,
        pointerDown = pointerDown,
        pointerMove = pointerMove,
        pointerUp = pointerUp,
        pointerExit = pointerExit,
        pointerScroll = pointerScroll,
        draw = draw,
    }
end
