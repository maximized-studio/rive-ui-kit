-- Date Field behaviour: the shown date, and closing the calendar after a pick.
--
-- Reads `value` (an ISO date, "2026-11-12", empty for none) and writes `_display`
-- ("12 Nov 2026") and `_hasValue`. When `value` changes while the calendar is `open` (a day was
-- picked in the nested Calendar, whose `value` is bound to this one), it closes it.

type Field = {
    value: Property<string>?,
    display: Property<string>?,
    hasValue: Property<boolean>?,
    open: Property<boolean>?,
    last: string?,
}

local MONTHS = { 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' }

local function format(s: string): string
    local y, m, d = string.match(s, '^(%d+)%-(%d+)%-(%d+)')
    local month = tonumber(m or '')
    if y == nil or month == nil or MONTHS[month] == nil then
        return ''
    end
    return string.format('%d %s %s', tonumber(d) or 0, MONTHS[month], y)
end

function init(self: Field, context: Context): boolean
    -- init runs twice; the view model is only there the second time
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.value = vm:getString('value')
    self.display = vm:getString('_display')
    self.hasValue = vm:getBoolean('_hasValue')
    self.open = vm:getBoolean('open')
    return true
end

function advance(self: Field, seconds: number): boolean
    local value = self.value
    if value == nil then
        return true
    end
    if value.value ~= self.last then
        local text = format(value.value)
        if self.display ~= nil and self.display.value ~= text then
            self.display.value = text
        end
        if self.hasValue ~= nil then
            self.hasValue.value = text ~= ''
        end
        -- a new value while open is a picked day: close the calendar
        if self.last ~= nil and self.open ~= nil and self.open.value then
            self.open.value = false
        end
        self.last = value.value
    end
    return true
end

function draw(self: Field, renderer: Renderer) end

return function(context: Context): Layout<Field>
    return { value = nil, display = nil, hasValue = nil, open = nil, last = nil, init = init, advance = advance, draw = draw }
end
