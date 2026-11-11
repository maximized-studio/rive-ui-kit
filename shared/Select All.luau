-- Checkbox Group behaviour: the "All" row.
--
-- With `selectAll` on, the group shows an All checkbox above its options. This script keeps it in
-- step: checked when every option is, `_mixed` (a dash) when some are. Clicking All checks or
-- clears every option. Options stay ordinary Checkboxes the app reads as before.

type Group = {
    options: PropertyList?,
    all: Property<boolean>?,
    mixed: Property<boolean>?,
    last: boolean?,
}

local function setBool(p: Property<boolean>?, v: boolean)
    if p ~= nil and p.value ~= v then
        p.value = v
    end
end

function init(self: Group, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.options = vm:getList('options')
    self.all = vm:getBoolean('_all')
    self.mixed = vm:getBoolean('_mixed')
    return true
end

function advance(self: Group, seconds: number): boolean
    local list, all = self.options, self.all
    if list == nil or all == nil then
        return true
    end
    -- the All row was clicked: apply it to every option
    if self.last ~= nil and all.value ~= self.last then
        for i = 1, list.length do
            setBool(list[i]:getBoolean('_active'), all.value)
        end
        setBool(self.mixed, false)
        self.last = all.value
        return true
    end
    local on = 0
    for i = 1, list.length do
        local active = list[i]:getBoolean('_active')
        if active ~= nil and active.value then
            on += 1
        end
    end
    local every = list.length > 0 and on == list.length
    setBool(all, every)
    setBool(self.mixed, on > 0 and not every)
    self.last = every
    return true
end

function draw(self: Group, renderer: Renderer) end

return function(context: Context): Layout<Group>
    return { options = nil, all = nil, mixed = nil, last = nil, init = init, advance = advance, draw = draw }
end
