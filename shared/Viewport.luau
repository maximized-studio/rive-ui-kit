-- Viewport: tells the kit components how big the played artboard is and where the pointer is in it.
--
-- Lives in the Theme Driver, which the host places once as a fill overlay at the artboard's top left,
-- so this layout's box and its local coordinates are the artboard's. Writes four values on the
-- global Theme: `_viewWidth`, `_viewHeight` (the artboard size) and `_pointerX`, `_pointerY` (the
-- last pointer position, in artboard coordinates). It never claims a pointer event, so everything under it still
-- gets them. A component compares that pointer position with the one it sees itself to learn where
-- it sits (Tooltip Placement does this).

type Viewport = {
    context: Context?,
    width: Property<number>?,
    height: Property<number>?,
    pointerX: Property<number>?,
    pointerY: Property<number>?,
    size: Vector,
    tries: number,
}

-- The global Theme is only there once something has bound it, which can be after init: keep asking
-- for a while (each frame) and then give up, so a file without Theme binds does not keep this awake.
local function connect(self: Viewport): boolean
    if self.width ~= nil then
        return true
    end
    local context = self.context
    if context == nil or self.tries <= 0 then
        return false
    end
    self.tries -= 1
    local theme = context:globalViewModel('Theme')
    if theme == nil then
        context:markNeedsUpdate()
        return false
    end
    self.width = theme:getNumber('_viewWidth')
    self.height = theme:getNumber('_viewHeight')
    self.pointerX = theme:getNumber('_pointerX')
    self.pointerY = theme:getNumber('_pointerY')
    return self.width ~= nil
end

local function writeSize(self: Viewport)
    if not connect(self) then
        return
    end
    if self.width ~= nil and self.width.value ~= self.size.x then
        self.width.value = self.size.x
    end
    if self.height ~= nil and self.height.value ~= self.size.y then
        self.height.value = self.size.y
    end
end

local function writePointer(self: Viewport, event: PointerEvent)
    if not connect(self) then
        return
    end
    if self.pointerX ~= nil then
        self.pointerX.value = event.position.x
    end
    if self.pointerY ~= nil then
        self.pointerY.value = event.position.y
    end
end

function init(self: Viewport, context: Context): boolean
    self.context = context
    writeSize(self)
    return true
end

function resize(self: Viewport, size: Vector, scale: number)
    self.size = size
    writeSize(self)
end

function advance(self: Viewport, seconds: number): boolean
    writeSize(self)
    return false
end

function pointerMove(self: Viewport, event: PointerEvent)
    writePointer(self, event)
end

function pointerDown(self: Viewport, event: PointerEvent)
    writePointer(self, event)
end

function pointerUp(self: Viewport, event: PointerEvent)
    writePointer(self, event)
end

function draw(self: Viewport, renderer: Renderer) end

return function(context: Context): Layout<Viewport>
    return {
        context = nil,
        width = nil,
        height = nil,
        pointerX = nil,
        pointerY = nil,
        size = Vector.xy(0, 0),
        tries = 120,
        init = init,
        resize = resize,
        advance = advance,
        pointerMove = pointerMove,
        pointerDown = pointerDown,
        pointerUp = pointerUp,
        draw = draw,
    }
end
