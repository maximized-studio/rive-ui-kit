-- PIN Input behaviour: spreads `value` over the six cells.
--
-- One hidden TextInput takes the typing (its text is bound two-way to `value`). This script keeps
-- `value` to digits only (at most six), writes each digit into `_c1` … `_c6`, sets `complete` when
-- all six are there, and tells the look which cell is active: `_ring` (the cell with the brand
-- ring) and `_caret` (the empty cell that shows the blinking caret), both -1 while the field has
-- no focus. Everything visible is native and bound to those values.

local CELLS = 6

type Pin = {
    value: Property<string>?,
    focused: Property<boolean>?,
    complete: Property<boolean>?,
    ring: Property<number>?,
    caret: Property<number>?,
    cells: { Property<string>? },
}

local function setNumber(p: Property<number>?, v: number)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

local function sync(self: Pin)
    local valueProp = self.value
    if valueProp == nil then
        return
    end
    local digits = string.gsub(valueProp.value, '%D', '')
    if #digits > CELLS then
        digits = string.sub(digits, 1, CELLS)
    end
    if digits ~= valueProp.value then
        valueProp.value = digits
    end
    for k = 1, CELLS do
        local cell = self.cells[k]
        local ch = string.sub(digits, k, k)
        if cell ~= nil and cell.value ~= ch then
            cell.value = ch
        end
    end
    local length = #digits
    if self.complete ~= nil and self.complete.value ~= (length == CELLS) then
        self.complete.value = length == CELLS
    end
    local focused = self.focused ~= nil and self.focused.value
    setNumber(self.ring, if focused then math.min(length, CELLS - 1) else -1)
    setNumber(self.caret, if focused and length < CELLS then length else -1)
end

function init(self: Pin, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.value = vm:getString('value')
    self.focused = vm:getBoolean('_focused')
    self.complete = vm:getBoolean('complete')
    self.ring = vm:getNumber('_ring')
    self.caret = vm:getNumber('_caret')
    for k = 1, CELLS do
        self.cells[k] = vm:getString('_c' .. k)
    end
    if self.value ~= nil then
        self.value:addListener(vm, function()
            sync(self)
        end)
    end
    if self.focused ~= nil then
        self.focused:addListener(vm, function()
            sync(self)
        end)
    end
    sync(self)
    return true
end

function advance(self: Pin, seconds: number): boolean
    return false
end

function draw(self: Pin, renderer: Renderer) end

return function(context: Context): Layout<Pin>
    return {
        value = nil,
        focused = nil,
        complete = nil,
        ring = nil,
        caret = nil,
        cells = {},
        init = init,
        advance = advance,
        draw = draw,
    }
end
