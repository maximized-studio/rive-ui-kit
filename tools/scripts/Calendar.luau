-- Calendar behaviour: the month grid.
--
-- Reads `year` and `month` (1-12, the month on screen), `value` (the chosen date, "2026-11-07",
-- empty for none) and `today` (set by the app, same format). Fills `_days` with 42 Calendar Days,
-- Monday first, with the days of the months around it muted, and writes `_title`
-- ("November 2026"). A click on a day sets that day's `_pick`; the script turns it into `value`
-- (and shows that month). `_prev` / `_next` (fired by the header Buttons) step the month.

type Cell = { y: number, m: number, d: number }

type Cal = {
    context: Context?,
    year: Property<number>?,
    month: Property<number>?,
    value: Property<string>?,
    today: Property<string>?,
    title: Property<string>?,
    days: PropertyList?,
    cells: { Cell },
    dirty: boolean,
}

local MONTHS = {
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
}

local function isLeap(y: number): boolean
    return (y % 4 == 0 and y % 100 ~= 0) or y % 400 == 0
end

local function daysIn(y: number, m: number): number
    local lengths = { 31, if isLeap(y) then 29 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
    return lengths[m]
end

-- 0 = Monday ... 6 = Sunday (Sakamoto's method)
local OFFSETS = { 0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4 }
local function weekday(y: number, m: number, d: number): number
    if m < 3 then
        y -= 1
    end
    local sunday0 = (y + y // 4 - y // 100 + y // 400 + OFFSETS[m] + d) % 7
    return (sunday0 + 6) % 7
end

local function parse(s: string?): (number, number, number)
    if s == nil then
        return 0, 0, 0
    end
    local y, m, d = string.match(s, '^(%d+)%-(%d+)%-(%d+)')
    if y == nil then
        return 0, 0, 0
    end
    return tonumber(y) or 0, tonumber(m) or 0, tonumber(d) or 0
end

local function iso(y: number, m: number, d: number): string
    return string.format('%04d-%02d-%02d', y, m, d)
end

local function shown(self: Cal): (number, number)
    local y = math.floor(if self.year ~= nil then self.year.value else 2026)
    local m = math.floor(if self.month ~= nil then self.month.value else 1)
    -- keep month in 1..12 if the app (or a step) wrote 0 or 13
    while m < 1 do
        m += 12
        y -= 1
    end
    while m > 12 do
        m -= 12
        y += 1
    end
    return y, m
end

local function setNum(p: Property<number>?, v: number)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

local function setBool(item: ViewModel, name: string, v: boolean)
    local p = item:getBoolean(name)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

local function sync(self: Cal)
    self.dirty = false
    local list = self.days
    if list == nil then
        return
    end
    local y, m = shown(self)
    setNum(self.year, y)
    setNum(self.month, m)
    if self.title ~= nil then
        self.title.value = MONTHS[m] .. ' ' .. tostring(y)
    end
    local vy, vm, vd = parse(if self.value ~= nil then self.value.value else nil)
    local ty, tm, td = parse(if self.today ~= nil then self.today.value else nil)

    local py, pm = if m == 1 then y - 1 else y, if m == 1 then 12 else m - 1
    local ny, nm = if m == 12 then y + 1 else y, if m == 12 then 1 else m + 1
    local lead = weekday(y, m, 1)
    local dim, pdim = daysIn(y, m), daysIn(py, pm)
    local cells: { Cell } = {}
    for i = 1, 42 do
        local n = i - lead
        if n < 1 then
            cells[i] = { y = py, m = pm, d = pdim + n }
        elseif n > dim then
            cells[i] = { y = ny, m = nm, d = n - dim }
        else
            cells[i] = { y = y, m = m, d = n }
        end
    end
    self.cells = cells

    while list.length > 42 do
        list:pop()
    end
    while list.length < 42 do
        list:push(Data.CalendarDay.new())
    end
    for i, c in ipairs(cells) do
        local item = list[i]
        local dayProp = item:getNumber('day')
        if dayProp ~= nil and dayProp.value ~= c.d then
            dayProp.value = c.d
        end
        local label = item:getString('label')
        if label ~= nil then
            label.value = tostring(c.d) .. ' ' .. MONTHS[c.m] .. ' ' .. tostring(c.y)
        end
        setBool(item, 'inMonth', c.m == m)
        setBool(item, 'today', c.y == ty and c.m == tm and c.d == td)
        setBool(item, 'selected', c.y == vy and c.m == vm and c.d == vd)
        setBool(item, '_pick', false)
    end
end

local function wake(self: Cal)
    self.dirty = true
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function step(self: Cal, by: number)
    local y, m = shown(self)
    m += by
    if m < 1 then
        m, y = 12, y - 1
    elseif m > 12 then
        m, y = 1, y + 1
    end
    setNum(self.month, m)
    setNum(self.year, y)
    wake(self)
end

function init(self: Cal, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.year = vm:getNumber('year')
    self.month = vm:getNumber('month')
    self.value = vm:getString('value')
    self.today = vm:getString('today')
    self.title = vm:getString('_title')
    self.days = vm:getList('_days')
    for _, prop in { self.year, self.month } do
        if prop ~= nil then
            prop:addListener(vm, function()
                wake(self)
            end)
        end
    end
    for _, prop in { self.value, self.today } do
        if prop ~= nil then
            prop:addListener(vm, function()
                wake(self)
            end)
        end
    end
    local prev, nxt = vm:getTrigger('_prev'), vm:getTrigger('_next')
    if prev ~= nil then
        prev:addListener(vm, function()
            step(self, -1)
        end)
    end
    if nxt ~= nil then
        nxt:addListener(vm, function()
            step(self, 1)
        end)
    end
    sync(self)
    return true
end

function advance(self: Cal, seconds: number): boolean
    local list = self.days
    if list ~= nil then
        -- a clicked day carries `_pick`: read and reset it here (not in a listener)
        for i = 1, list.length do
            local pick = list[i]:getBoolean('_pick')
            if pick ~= nil and pick.value then
                pick.value = false
                local c = self.cells[i]
                if c ~= nil and self.value ~= nil then
                    self.value.value = iso(c.y, c.m, c.d)
                    setNum(self.year, c.y)
                    setNum(self.month, c.m)
                    self.dirty = true
                end
            end
        end
    end
    if self.dirty then
        sync(self)
    end
    return true
end

function draw(self: Cal, renderer: Renderer) end

return function(context: Context): Layout<Cal>
    return {
        context = nil,
        year = nil,
        month = nil,
        value = nil,
        today = nil,
        title = nil,
        days = nil,
        cells = {},
        dirty = false,
        init = init,
        advance = advance,
        draw = draw,
    }
end
