-- Context Menu behaviour: a press held still for 0.45 s opens the menu at the pointer.
--
-- Places the kit Menu (`menu`) at `_menuX` / `_menuY`, kept inside the area, and opens it through
-- the menu's own `state.open` (choosing an item closes it, as in every kit Menu). A press outside
-- the open menu closes it. Hosts that want a right-click open it with `x`, `y` and `openAt`.

type Ctx = {
    context: Context?,
    menuX: Property<number>?,
    menuY: Property<number>?,
    x: Property<number>?,
    y: Property<number>?,
    open: Property<boolean>?,
    items: PropertyList?,
    width: number,
    pressing: boolean,
    held: number,
    px: number,
    py: number,
}

local HOLD = 0.45
local SLOP = 6
local ITEM_H = 40
local PAD = 8

local function menuH(self: Ctx): number
    local n = if self.items ~= nil then self.items.length else 4
    return n * ITEM_H + 8
end

local function isOpen(self: Ctx): boolean
    return self.open ~= nil and self.open.value
end

local function openAt(self: Ctx, x: number, y: number)
    local mx = math.clamp(x, PAD, math.max(PAD, self.width - MENU_W - PAD))
    local my = math.clamp(y, PAD, math.max(PAD, self.height - menuH(self) - PAD))
    if self.menuX ~= nil then
        self.menuX.value = mx
    end
    if self.menuY ~= nil then
        self.menuY.value = my
    end
    if self.open ~= nil then
        self.open.value = true
    end
end

local function insideMenu(self: Ctx, x: number, y: number): boolean
    local mx = if self.menuX ~= nil then self.menuX.value else 0
    local my = if self.menuY ~= nil then self.menuY.value else 0
    return x >= mx and x <= mx + MENU_W and y >= my and y <= my + menuH(self)
end

function init(self: Ctx, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.menuX = vm:getNumber('_menuX')
    self.menuY = vm:getNumber('_menuY')
    self.x = vm:getNumber('x')
    self.y = vm:getNumber('y')
    local menu = vm:getViewModel('menu')
    if menu ~= nil then
        local m = menu.value
        self.items = m:getList('items')
        local state = m:getViewModel('state')
        if state ~= nil then
            self.open = state.value:getBoolean('open')
        end
    end
    local trigger = vm:getTrigger('openAt')
    if trigger ~= nil then
        trigger:addListener(vm, function()
            openAt(self, if self.x ~= nil then self.x.value else 0, if self.y ~= nil then self.y.value else 0)
        end)
    end
    return true
end

function resize(self: Ctx, size: Vector)
    self.width = size.x
    self.height = size.y
end

function pointerDown(self: Ctx, event: PointerEvent)
    local x, y = event.position.x, event.position.y
    if x < 0 or y < 0 or x > self.width or y > self.height then
        return
    end
    if isOpen(self) then
        if not insideMenu(self, x, y) and self.open ~= nil then
            self.open.value = false
        end
        return
    end
    self.pressing = true
    self.held = 0
    self.px, self.py = x, y
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

function pointerMove(self: Ctx, event: PointerEvent)
    if self.pressing and (math.abs(event.position.x - self.px) > SLOP or math.abs(event.position.y - self.py) > SLOP) then
        self.pressing = false
    end
end

function pointerUp(self: Ctx, event: PointerEvent)
    self.pressing = false
end

function advance(self: Ctx, seconds: number): boolean
    if not self.pressing then
        return false
    end
    self.held += seconds
    if self.held >= HOLD then
-- Tooltip Placement: the side the Tooltip Button's bubble really shows on.
        openAt(self, self.px, self.py)
        return false
    end
    return true
end

function draw(self: Ctx, renderer: Renderer) end
return function(context: Context): Layout<Ctx>
    return {
        context = nil,
        menuX = nil,
        menuY = nil,
        x = nil,
        y = nil,
        open = nil,
        items = nil,
        width = 360,
        height = 240,
        pressing = false,
        held = 0,
        px = 0,
        py = 0,
        init = init,
        resize = resize,
        advance = advance,
        draw = draw,
        pointerDown = pointerDown,
        pointerMove = pointerMove,
        pointerUp = pointerUp,
    }
end
