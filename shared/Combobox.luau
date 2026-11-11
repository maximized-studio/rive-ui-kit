-- Combobox behaviour: filters `options` by what is typed and picks one.
--
-- `options` is the app's list of Combo Options (a `label` each). While the field has focus the
-- panel is `open` and `_results` holds the options whose label contains `query` (any case, at
-- most MAX). Up / Down move the highlight (`_active` on a result; the pointer moves it too), Enter
-- or a click picks it: `value` and `query` become its label, the panel closes and the option is
-- marked `selected`. Escape closes; the chevron (`_toggle`) opens and closes. When the field loses
-- focus the panel closes a moment later, so a click on a result still lands.

local MAX = 6
local CLOSE_DELAY = 0.2

type Combo = {
    context: Context?,
    options: PropertyList?,
    results: PropertyList?,
    value: Property<string>?,
    query: Property<string>?,
    open: Property<boolean>?,
    empty: Property<boolean>?,
    focused: Property<boolean>?,
    disabled: Property<boolean>?,
    active: number,
    pending: { up: number, down: number, enter: boolean, escape: boolean, toggle: boolean, pick: string? },
    shownQuery: string,
    wasFocused: boolean,
    closeIn: number,
    dirty: boolean,
}

local function wake(self: Combo)
    self.dirty = true
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function str(p: Property<string>?): string
    return if p ~= nil then p.value else ''
end

local function labelOf(item: ViewModel): string
    local p = item:getString('label')
    return if p ~= nil then p.value else ''
end

local function setBool(p: Property<boolean>?, v: boolean)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

local function highlight(self: Combo)
    local results = self.results
    if results == nil then
        return
    end
    for k = 1, results.length do
        setBool(results[k]:getBoolean('_active'), k == self.active)
    end
end

local function filter(self: Combo)
    local options, results = self.options, self.results
    if options == nil or results == nil then
        return
    end
    local q = string.lower(str(self.query))
    -- right after a pick the query is the chosen label: show everything again
    if str(self.query) == str(self.value) then
        q = ''
    end
    local matches: { string } = {}
    for k = 1, options.length do
        local label = labelOf(options[k])
        if q == '' or string.find(string.lower(label), q, 1, true) ~= nil then
            table.insert(matches, label)
            if #matches >= MAX then
                break
            end
        end
    end
    while results.length > #matches do
        results:pop()
    end
    while results.length < #matches do
        local item = Data.ComboOption.new()
        local n = results.length + 1
        local pick = item:getTrigger('_pick')
        if pick ~= nil then
            pick:addListener(item, function()
                self.pending.pick = labelOf(item)
                wake(self)
            end)
        end
        local hover = item:getBoolean('_hover')
        if hover ~= nil then
            hover:addListener(item, function()
                if hover.value then
                    self.active = n
                    highlight(self)
                end
            end)
        end
        results:push(item)
    end
    local chosen = str(self.value)
    for k, label in ipairs(matches) do
        local item = results[k]
        local p = item:getString('label')
        if p ~= nil and p.value ~= label then
            p.value = label
        end
        setBool(item:getBoolean('selected'), label == chosen)
    end
    self.active = math.max(0, math.min(self.active, #matches))
    if self.active == 0 and #matches > 0 then
        self.active = 1
    end
    highlight(self)
    setBool(self.empty, #matches == 0)
end

local function pick(self: Combo, label: string)
    if self.value ~= nil then
        self.value.value = label
    end
    if self.query ~= nil then
        self.query.value = label
    end
    self.shownQuery = label
    setBool(self.open, false)
    -- mark the chosen one in the app's options too
    local options = self.options
    if options ~= nil then
        for k = 1, options.length do
            setBool(options[k]:getBoolean('selected'), labelOf(options[k]) == label)
        end
    end
end

function init(self: Combo, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.options = vm:getList('options')
    self.results = vm:getList('_results')
    self.value = vm:getString('value')
    self.query = vm:getString('query')
    self.open = vm:getBoolean('open')
    self.empty = vm:getBoolean('_empty')
    self.focused = vm:getBoolean('_focused')
    self.disabled = vm:getBoolean('disabled')
    self.shownQuery = str(self.query)
    for _, name in { '_up', '_down', '_enter', '_escape', '_toggle' } do
        local t = vm:getTrigger(name)
        if t ~= nil then
            t:addListener(vm, function()
                if name == '_up' then
                    self.pending.up += 1
                elseif name == '_down' then
                    self.pending.down += 1
                elseif name == '_enter' then
                    self.pending.enter = true
                elseif name == '_escape' then
                    self.pending.escape = true
                else
                    self.pending.toggle = true
                end
                wake(self)
            end)
        end
    end
    for _, p in { self.query, self.value } do
        if p ~= nil then
            p:addListener(vm, function()
                wake(self)
            end)
        end
    end
    for _, p in { self.focused, self.open } do
        if p ~= nil then
            p:addListener(vm, function()
                wake(self)
            end)
        end
    end
    if self.options ~= nil then
        self.options:addListener(vm, function()
            wake(self)
        end)
    end
    filter(self)
    return true
end

function advance(self: Combo, seconds: number): boolean
    local open = self.open
    if open == nil then
        return false
    end
    local keepAwake = false
    local off = self.disabled ~= nil and self.disabled.value
    local focused = self.focused ~= nil and self.focused.value and not off
    -- focus opens the panel; losing it closes the panel a moment later
    if focused and not self.wasFocused then
        open.value = true
        self.closeIn = -1
        -- a press on the chevron also focuses the field: that press only opens
        self.pending.toggle = false
    elseif not focused and self.wasFocused then
        self.closeIn = CLOSE_DELAY
    end
    self.wasFocused = focused
    local p = self.pending
    if p.pick ~= nil then
        pick(self, p.pick)
        p.pick = nil
        self.closeIn = -1
    end
    if self.closeIn >= 0 then
        self.closeIn -= seconds
        if self.closeIn < 0 then
            open.value = false
        else
            keepAwake = true
        end
    end
    -- typing opens the panel and starts the highlight at the top
    local q = str(self.query)
    if q ~= self.shownQuery then
        self.shownQuery = q
        if focused then
            open.value = true
        end
        self.active = 1
    end
    if p.toggle then
        p.toggle = false
        open.value = not open.value and not off
    end
    if p.escape then
        p.escape = false
        open.value = false
    end
    if p.down > 0 or p.up > 0 then
        if not open.value then
            open.value = true
        end
        filter(self)
        local n = if self.results ~= nil then self.results.length else 0
        if n > 0 then
            self.active = ((self.active - 1 + p.down - p.up) % n) + 1
        end
        p.down, p.up = 0, 0
        highlight(self)
    end
    if p.enter then
        p.enter = false
        local results = self.results
        if open.value and results ~= nil and self.active >= 1 and self.active <= results.length then
            pick(self, labelOf(results[self.active]))
        end
    end
    filter(self)
    self.dirty = false
    return keepAwake
end

function draw(self: Combo, renderer: Renderer) end

return function(context: Context): Layout<Combo>
    return {
        context = nil,
        options = nil,
        results = nil,
        value = nil,
        query = nil,
        open = nil,
        empty = nil,
        focused = nil,
        disabled = nil,
        active = 1,
        pending = { up = 0, down = 0, enter = false, escape = false, toggle = false, pick = nil },
        shownQuery = '',
        wasFocused = false,
        closeIn = -1,
        dirty = false,
        init = init,
        advance = advance,
        draw = draw,
    }
end
