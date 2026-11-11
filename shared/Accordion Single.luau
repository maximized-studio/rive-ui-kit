-- Accordion behaviour: with `single` on, opening an item closes the others.
--
-- Items open and close themselves (each header toggles its own `open`); this script only
-- watches for an item that just opened and closes the rest. With `single` off it does nothing.

type Acc = {
    single: Property<boolean>?,
    items: PropertyList?,
    was: { boolean },
}

function init(self: Acc, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.single = vm:getBoolean('single')
    self.items = vm:getList('items')
    return true
end

function advance(self: Acc, seconds: number): boolean
    local list = self.items
    if list == nil then
        return true
    end
    local single = self.single ~= nil and self.single.value
    local opened = 0
    local now: { boolean } = {}
    for i = 1, list.length do
        local open = list[i]:getBoolean('open')
        now[i] = open ~= nil and open.value
        if now[i] and not self.was[i] then
            opened = i
        end
    end
    if single and opened > 0 then
        for i = 1, list.length do
            if i ~= opened and now[i] then
                local open = list[i]:getBoolean('open')
                if open ~= nil then
                    open.value = false
                end
                now[i] = false
            end
        end
    end
    self.was = now
    -- stays awake: items toggle themselves, and an app may swap the list
    return true
end

function draw(self: Acc, renderer: Renderer) end

return function(context: Context): Layout<Acc>
    return { single = nil, items = nil, was = {}, init = init, advance = advance, draw = draw }
end
