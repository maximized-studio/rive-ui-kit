-- Range Discrete Slider behaviour: two thumbs (`low`, `high`) that snap to `step` within `min`..`max`.
--
-- Same approach as the Discrete Slider: the look is native and bound, this script only
--   * picks the nearer thumb on a press and drags it (snapped, clamped, never past the other one),
--   * keeps `_lowFraction`, `_highFraction` and `_span` (0-1; the thumbs and the fill between them)
--     in step with `low` and `high`, also when the app writes them or min / max / step,
--   * sets `_dragLow` / `_dragHigh` while dragging and `_hoverLow` / `_hoverHigh` for the thumb the
--     pointer is nearest to while over the track,
--   * fills `_ticks` with Slider Ticks (one per step, none above 50), `on` between the thumbs,
--   * steps the last moved thumb (high to start with) on `_keyUp` / `_keyDown` (arrow keys and the
--     screen reader's increase / decrease).

type Range = {
    context: Context?,
    low: Property<number>?,
    high: Property<number>?,
    min: Property<number>?,
    max: Property<number>?,
    step: Property<number>?,
    lowF: Property<number>?,
    highF: Property<number>?,
    span: Property<number>?,
    dragLow: Property<boolean>?,
    dragHigh: Property<boolean>?,
    hoverLow: Property<boolean>?,
    hoverHigh: Property<boolean>?,
    disabled: Property<boolean>?,
    showTicks: Property<boolean>?,
    ticks: PropertyList?,
    width: number,
    height: number,
    active: number, -- 0 none, 1 low, 2 high (the thumb being dragged)
    last: number, -- the thumb the keys move
    dirty: boolean,
}

local PAD = 10
local MAX_TICKS = 51

local function num(p: Property<number>?, fallback: number): number
    return if p ~= nil then p.value else fallback
end

local function setNum(p: Property<number>?, v: number)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

local function setBool(p: Property<boolean>?, v: boolean)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

local function bounds(self: Range): (number, number, number)
    local lo = num(self.min, 0)
    local hi = math.max(num(self.max, 100), lo)
    return lo, hi, num(self.step, 1)
end

local function snap(self: Range, v: number): number
    local lo, hi, st = bounds(self)
    if st > 0 then
        v = lo + math.floor((v - lo) / st + 0.5) * st
        v = math.floor(v * 1000 + 0.5) / 1000
    end
    return math.max(lo, math.min(hi, v))
end

local function isOff(self: Range): boolean
    return self.disabled ~= nil and self.disabled.value
end

local function sync(self: Range)
    self.dirty = false
    if self.low == nil or self.high == nil then
        return
    end
    local lo, hi, st = bounds(self)
    local a, b = snap(self, self.low.value), snap(self, self.high.value)
    if a > b then
        a, b = b, a
    end
    setNum(self.low, a)
    setNum(self.high, b)
    local f = function(v: number): number
        return if hi > lo then (v - lo) / (hi - lo) else 0
    end
    setNum(self.lowF, f(a))
    setNum(self.highF, f(b))
    setNum(self.span, f(b) - f(a))
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
        local v = lo + (i - 1) * st
        local isOn = v >= a - 1e-6 and v <= b + 1e-6
        if on ~= nil and on.value ~= isOn then
            on.value = isOn
        end
    end
end

local function wake(self: Range)
    self.dirty = true
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function inside(self: Range, p: Vector): boolean
    return p.x >= 0 and p.y >= 0 and p.x <= self.width and p.y <= self.height
end

local function valueAt(self: Range, x: number): number
    local lo, hi = bounds(self)
    local span = math.max(1, self.width - 2 * PAD)
    local f = math.max(0, math.min(1, (x - PAD) / span))
    return snap(self, lo + f * (hi - lo))
end

-- 1 for low, 2 for high: whichever thumb is nearer to x (on a tie, the side the press is on)
local function nearest(self: Range, x: number): number
    local lo, hi = bounds(self)
    local span = math.max(1, self.width - 2 * PAD)
    local toX = function(v: number): number
        return PAD + (if hi > lo then (v - lo) / (hi - lo) else 0) * span
    end
    local lx, hx = toX(num(self.low, lo)), toX(num(self.high, hi))
    local dl, dh = math.abs(x - lx), math.abs(x - hx)
    if dl == dh then
        return if x > hx then 2 else 1
    end
    return if dl < dh then 1 else 2
end

local function moveTo(self: Range, which: number, v: number)
    if which == 1 then
        setNum(self.low, math.min(v, num(self.high, v)))
    else
        setNum(self.high, math.max(v, num(self.low, v)))
    end
    sync(self)
end

local function hoverFor(self: Range, which: number)
    setBool(self.hoverLow, which == 1)
    setBool(self.hoverHigh, which == 2)
end

local function stepKey(self: Range, dir: number)
    if isOff(self) then
        return
    end
    local _, _, st = bounds(self)
    local p = if self.last == 1 then self.low else self.high
    moveTo(self, self.last, snap(self, num(p, 0) + dir * (if st > 0 then st else 1)))
end

function init(self: Range, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.low = vm:getNumber('low')
    self.high = vm:getNumber('high')
    self.min = vm:getNumber('min')
    self.max = vm:getNumber('max')
    self.step = vm:getNumber('step')
    self.lowF = vm:getNumber('_lowFraction')
    self.highF = vm:getNumber('_highFraction')
    self.span = vm:getNumber('_span')
    self.dragLow = vm:getBoolean('_dragLow')
    self.dragHigh = vm:getBoolean('_dragHigh')
    self.hoverLow = vm:getBoolean('_hoverLow')
    self.hoverHigh = vm:getBoolean('_hoverHigh')
    self.disabled = vm:getBoolean('disabled')
    self.showTicks = vm:getBoolean('showTicks')
    self.ticks = vm:getList('_ticks')
    for _, prop in { self.low, self.high, self.min, self.max, self.step } do
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
    local up, down = vm:getTrigger('_keyUp'), vm:getTrigger('_keyDown')
    if up ~= nil then
        up:addListener(vm, function()
            stepKey(self, 1)
        end)
    end
    if down ~= nil then
        down:addListener(vm, function()
            stepKey(self, -1)
        end)
    end
    sync(self)
    return true
end

function resize(self: Range, size: Vector)
    self.width = size.x
    self.height = size.y
end

function advance(self: Range, seconds: number): boolean
    if self.dirty then
        sync(self)
    end
    return false
end

function pointerDown(self: Range, event: PointerEvent)
    if not inside(self, event.position) or isOff(self) then
        return
    end
    self.active = nearest(self, event.position.x)
    self.last = self.active
    setBool(self.dragLow, self.active == 1)
    setBool(self.dragHigh, self.active == 2)
    moveTo(self, self.active, valueAt(self, event.position.x))
    event:hit()
end

function pointerMove(self: Range, event: PointerEvent)
    if self.active ~= 0 then
        moveTo(self, self.active, valueAt(self, event.position.x))
        event:hit()
        return
    end
    if inside(self, event.position) and not isOff(self) then
        hoverFor(self, nearest(self, event.position.x))
    else
        hoverFor(self, 0)
    end
end

function pointerUp(self: Range, event: PointerEvent)
    if self.active ~= 0 then
        self.active = 0
        setBool(self.dragLow, false)
        setBool(self.dragHigh, false)
        event:hit()
    end
end

function pointerExit(self: Range, event: PointerEvent)
    if self.active == 0 then
        hoverFor(self, 0)
    end
end

function draw(self: Range, renderer: Renderer) end

return function(context: Context): Layout<Range>
    return {
        context = nil,
        low = nil,
        high = nil,
        min = nil,
        max = nil,
        step = nil,
        lowF = nil,
        highF = nil,
        span = nil,
        dragLow = nil,
        dragHigh = nil,
        hoverLow = nil,
        hoverHigh = nil,
        disabled = nil,
        showTicks = nil,
        ticks = nil,
        width = 0,
        height = 0,
        active = 0,
        last = 2,
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
