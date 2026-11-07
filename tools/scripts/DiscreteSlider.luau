-- Discrete Slider behaviour: drag to a value that snaps to `step` within `min`..`max`.
--
-- The look is native and bound; this script only does what bindings can't:
--   * maps a press / drag on the track to `value` (snapped and clamped),
--   * keeps `_fraction` (0-1, drives the thumb and the fill) in step with `value`, also when the
--     app writes `value`, `min`, `max` or `step`,
--   * sets `_dragging` while the pointer is held and `_hover` while it is over the track,
--   * fills `_ticks` with one Slider Tick per step (none above 50 steps or with showTicks off),
--     each `on` up to the value.
-- Keys and the screen reader step `value` natively; the script snaps and follows.

type Slider = {
    context: Context?,
    value: Property<number>?,
    min: Property<number>?,
    max: Property<number>?,
    step: Property<number>?,
    fraction: Property<number>?,
    dragging: Property<boolean>?,
    hover: Property<boolean>?,
    disabled: Property<boolean>?,
    showTicks: Property<boolean>?,
    ticks: PropertyList?,
    width: number,
    height: number,
    down: boolean,
    dirty: boolean,
}

local PAD = 10 -- the thumb's radius: the track runs from PAD to width - PAD
local MAX_TICKS = 51

local function num(p: Property<number>?, fallback: number): number
    return if p ~= nil then p.value else fallback
end

local function range(self: Slider): (number, number, number)
    local lo = num(self.min, 0)
    local hi = math.max(num(self.max, 100), lo)
    local st = num(self.step, 1)
    return lo, hi, st
end

local function snap(self: Slider, v: number): number
    local lo, hi, st = range(self)
    if st > 0 then
        v = lo + math.floor((v - lo) / st + 0.5) * st
        -- avoid 0.30000000000000004 from decimal steps
        v = math.floor(v * 1000 + 0.5) / 1000
    end
    return math.max(lo, math.min(hi, v))
end

local function sync(self: Slider)
    self.dirty = false
    local valueProp = self.value
    if valueProp == nil then
        return
    end
    local lo, hi, st = range(self)
    local v = snap(self, valueProp.value)
    if v ~= valueProp.value then
        valueProp.value = v
    end
    local f = if hi > lo then (v - lo) / (hi - lo) else 0
    if self.fraction ~= nil and self.fraction.value ~= f then
        self.fraction.value = f
    end
    local list = self.ticks
    if list == nil then
        return
    end
    local want = 0
    if st > 0 and (self.showTicks == nil or self.showTicks.value) then
        want = math.floor((hi - lo) / st + 0.5) + 1
        if want > MAX_TICKS or want < 2 then
            want = 0
        end
    end
    while list.length > want do
        list:pop()
    end
    while list.length < want do
        list:push(Data.SliderTick.new())
    end
    for i = 1, list.length do
        local on = list[i]:getBoolean('on')
        if on ~= nil then
            local isOn = lo + (i - 1) * st <= v + 1e-6
            if on.value ~= isOn then
                on.value = isOn
            end
        end
    end
end

local function wake(self: Slider)
    self.dirty = true
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function inside(self: Slider, event: PointerEvent): boolean
    local p = event.position
    return p.x >= 0 and p.y >= 0 and p.x <= self.width and p.y <= self.height
end

local function writeFrom(self: Slider, event: PointerEvent)
    local valueProp = self.value
    if valueProp == nil then
        return
    end
    local lo, hi = range(self)
    local span = math.max(1, self.width - 2 * PAD)
    local f = math.max(0, math.min(1, (event.position.x - PAD) / span))
    local v = snap(self, lo + f * (hi - lo))
    if v ~= valueProp.value then
        valueProp.value = v
    end
    sync(self)
end

local function setBool(p: Property<boolean>?, v: boolean)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

function init(self: Slider, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.value = vm:getNumber('value')
    self.min = vm:getNumber('min')
    self.max = vm:getNumber('max')
    self.step = vm:getNumber('step')
    self.fraction = vm:getNumber('_fraction')
    self.dragging = vm:getBoolean('_dragging')
    self.hover = vm:getBoolean('_hover')
    self.disabled = vm:getBoolean('disabled')
    self.showTicks = vm:getBoolean('showTicks')
    self.ticks = vm:getList('_ticks')
    for _, prop in { self.value, self.min, self.max, self.step } do
        if prop ~= nil then
            prop:addListener(vm, function()
                wake(self)
            end)
        end
    end
    if self.showTicks ~= nil then
        self.showTicks:addListener(vm, function()
            wake(self)
        end)
    end
    sync(self)
    return true
end

function resize(self: Slider, size: Vector)
    self.width = size.x
    self.height = size.y
end

function advance(self: Slider, seconds: number): boolean
    if self.dirty then
        sync(self)
    end
    return false
end

function pointerDown(self: Slider, event: PointerEvent)
    if not inside(self, event) or (self.disabled ~= nil and self.disabled.value) then
        return
    end
    self.down = true
    setBool(self.dragging, true)
    writeFrom(self, event)
    event:hit()
end

function pointerMove(self: Slider, event: PointerEvent)
    if self.down then
        writeFrom(self, event)
        event:hit()
        return
    end
    setBool(self.hover, inside(self, event) and not (self.disabled ~= nil and self.disabled.value))
end

function pointerUp(self: Slider, event: PointerEvent)
    if self.down then
        self.down = false
        setBool(self.dragging, false)
        setBool(self.hover, inside(self, event))
        event:hit()
    end
end

function pointerExit(self: Slider, event: PointerEvent)
    if not self.down then
        setBool(self.hover, false)
    end
end

function draw(self: Slider, renderer: Renderer) end

return function(context: Context): Layout<Slider>
    return {
        context = nil,
        value = nil,
        min = nil,
        max = nil,
        step = nil,
        fraction = nil,
        dragging = nil,
        hover = nil,
        disabled = nil,
        showTicks = nil,
        ticks = nil,
        width = 0,
        height = 0,
        down = false,
        dirty = false,
        init = init,
        resize = resize,
        advance = advance,
        draw = draw,
        pointerDown = pointerDown,
        pointerMove = pointerMove,
        pointerUp = pointerUp,
        pointerExit = pointerExit,
    }
end
