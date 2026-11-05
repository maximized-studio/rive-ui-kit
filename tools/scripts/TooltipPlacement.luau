-- Tooltip Placement: the side the Tooltip Button's bubble really shows on.
--
-- `placement` is the side the app asks for (0 top, 1 bottom, 2 left, 3 right). The script writes
-- `_placement`, which the overlay, the arrow and the Placement layer follow: the asked side, or the
-- opposite one when the bubble would leave the artboard on the asked side and fits on the other
-- (like a CSS popover with `position-try-fallbacks: flip-block, flip-inline`). When neither side
-- fits, or the artboard is not known yet, the asked side stays.
--
-- Tooltip Button places it twice, both on its own view model:
-- - around the bubble, with the `bubble` input on: writes the bubble's size (`_bubbleWidth`, `_bubbleHeight`);
-- - over the trigger: its own box is the trigger, and the pointer tells where that box is. The
--   Theme Driver's Viewport script reports the pointer (on Theme) in artboard coordinates, this script sees the
--   same pointer in its own; the difference is the trigger's position in the artboard.
-- Before the first pointer move (keyboard only) that position is unknown and the asked side stays.
-- The script sleeps between changes: the pointer, `placement`, the bubble size and the artboard size wake it.

local GAP = 4 -- the overlay's gap between trigger and bubble
local MARGIN = 4 -- room the bubble keeps from the artboard edge
local OPPOSITE = { [0] = 1, [1] = 0, [2] = 3, [3] = 2 }

type Placement = {
    bubble: Input<boolean>,
    context: Context?,
    asked: Property<number>?,
    shown: Property<number>?,
    bubbleWidth: Property<number>?,
    bubbleHeight: Property<number>?,
    viewWidth: Property<number>?,
    viewHeight: Property<number>?,
    pointerX: Property<number>?,
    pointerY: Property<number>?,
    size: Vector,
    pointer: Vector?, -- the last pointer position in this box's coordinates
    seenPointer: Vector?, -- the local pointer the last position was worked out from
    seenGlobal: Vector?, -- the artboard pointer the last position was worked out from
    origin: Vector?, -- this box's top left in artboard coordinates, once known
    tries: number,
}

local function wake(self: Placement)
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function value(prop: Property<number>?): number
    if prop == nil then
        return 0
    end
    return prop.value
end

-- Is there room for the bubble (bw x bh) on `side` of the trigger at (x, y), w x h, in an aw x ah artboard?
local function fits(side: number, x: number, y: number, w: number, h: number, bw: number, bh: number, aw: number, ah: number): boolean
    if side == 0 then
        return y - GAP - bh >= MARGIN
    elseif side == 1 then
        return y + h + GAP + bh <= ah - MARGIN
    elseif side == 2 then
        return x - GAP - bw >= MARGIN
    end
    return x + w + GAP + bw <= aw - MARGIN
end

-- Where this box is, from a pointer position both this script and Viewport saw.
local function locate(self: Placement)
    local pointer = self.pointer
    if pointer == nil or self.pointerX == nil or self.pointerY == nil then
        return
    end
    local global = Vector.xy(value(self.pointerX), value(self.pointerY))
    -- only a pair that both moved since last time comes from the same event
    if self.seenPointer ~= nil and (self.seenPointer == pointer or self.seenGlobal == global) then
        return
    end
    self.seenPointer = pointer
    self.seenGlobal = global
    self.origin = global - pointer
end

local function decide(self: Placement): number
    local asked = math.clamp(math.floor(value(self.asked)), 0, 3)
    local origin = self.origin
    local aw, ah = value(self.viewWidth), value(self.viewHeight)
    local bw, bh = value(self.bubbleWidth), value(self.bubbleHeight)
    if origin == nil or aw <= 0 or ah <= 0 or bw <= 0 or bh <= 0 then
        return asked
    end
    local x, y, w, h = origin.x, origin.y, self.size.x, self.size.y
    if fits(asked, x, y, w, h, bw, bh, aw, ah) then
        return asked
    end
    local other = OPPOSITE[asked]
    if fits(other, x, y, w, h, bw, bh, aw, ah) then
        return other
    end
    return asked
end

-- The global Theme (where Viewport writes) is only there once something has bound it, which can be
-- after init: keep asking for a while, then give up (no Theme Driver: the asked side always stays).
local function connect(self: Placement)
    local context = self.context
    if self.viewWidth ~= nil or context == nil or self.tries <= 0 then
        return
    end
    self.tries -= 1
    local theme = context:globalViewModel('Theme')
    if theme == nil then
        context:markNeedsUpdate()
        return
    end
    self.viewWidth = theme:getNumber('_viewWidth')
    self.viewHeight = theme:getNumber('_viewHeight')
    self.pointerX = theme:getNumber('_pointerX')
    self.pointerY = theme:getNumber('_pointerY')
    for _, prop in { self.viewWidth, self.viewHeight } do
        if prop ~= nil then
            prop:addListener(self, function()
                wake(self)
            end)
        end
    end
end

local function sync(self: Placement)
    if self.bubble then
        local bw, bh = self.bubbleWidth, self.bubbleHeight
        if bw ~= nil and bw.value ~= self.size.x then
            bw.value = self.size.x
        end
        if bh ~= nil and bh.value ~= self.size.y then
            bh.value = self.size.y
        end
        return
    end
    connect(self)
    locate(self)
    local side = decide(self)
    if self.shown ~= nil and self.shown.value ~= side then
        self.shown.value = side
    end
end

function init(self: Placement, context: Context): boolean
    -- init runs twice; the view model is only there the second time
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.asked = vm:getNumber('placement')
    self.shown = vm:getNumber('_placement')
    self.bubbleWidth = vm:getNumber('_bubbleWidth')
    self.bubbleHeight = vm:getNumber('_bubbleHeight')
    if not self.bubble then
        for _, prop in { self.asked, self.bubbleWidth, self.bubbleHeight } do
            if prop ~= nil then
                prop:addListener(self, function()
                    wake(self)
                end)
            end
        end
    end
    sync(self)
    return true
end

function resize(self: Placement, size: Vector, scale: number)
    self.size = size
    wake(self)
end

function advance(self: Placement, seconds: number): boolean
    sync(self)
    return false
end

function pointerMove(self: Placement, event: PointerEvent)
    if not self.bubble then
        self.pointer = event.position
        wake(self)
    end
end

function draw(self: Placement, renderer: Renderer) end

return function(context: Context): Layout<Placement>
    return {
        bubble = false,
        context = nil,
        asked = nil,
        shown = nil,
        bubbleWidth = nil,
        bubbleHeight = nil,
        viewWidth = nil,
        viewHeight = nil,
        pointerX = nil,
        pointerY = nil,
        size = Vector.xy(0, 0),
        pointer = nil,
        seenPointer = nil,
        seenGlobal = nil,
        origin = nil,
        tries = 120,
        init = init,
        resize = resize,
        advance = advance,
        pointerMove = pointerMove,
        draw = draw,
    }
end
