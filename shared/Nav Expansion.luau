-- Sidebar behaviour: the button that expands or collapses every section.
--
-- Sections open and close themselves (each header toggles its own `open`). This script watches
-- them and writes what the button should say: with any section open, `expansion.anyOpen` is true
-- and `_toggleLabel` reads "Collapse all"; with none open it reads "Expand all". The button
-- fires `_toggleAll`; the script then closes every section, or opens them all when none was open.

type Nav = {
    sections: PropertyList?,
    anyOpen: Property<boolean>?,
    label: Property<string>?,
    pending: boolean,
}

local function openOf(item: ViewModel): Property<boolean>?
    return item:getBoolean('open')
end

local function setAll(self: Nav, value: boolean)
    local list = self.sections
    if list == nil then
        return
    end
    for i = 1, list.length do
        local open = openOf(list[i])
        if open ~= nil and open.value ~= value then
            open.value = value
        end
    end
end

function init(self: Nav, context: Context): boolean
    -- init runs twice; the view model is only there the second time
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.sections = vm:getList('sections')
    self.label = vm:getString('_toggleLabel')
    local expansion = vm:getViewModel('expansion')
    if expansion ~= nil then
        self.anyOpen = expansion.value:getBoolean('anyOpen')
    end
    local toggle = vm:getTrigger('_toggleAll')
    if toggle ~= nil then
        toggle:addListener(vm, function()
            -- handled in advance, where the sections' current state is known
            self.pending = true
            context:markNeedsUpdate()
        end)
    end
    return true
end

function advance(self: Nav, seconds: number): boolean
    local list = self.sections
    if list == nil then
        return true
    end
    local any = false
    for i = 1, list.length do
        local open = openOf(list[i])
        if open ~= nil and open.value then
            any = true
        end
    end
    if self.pending then
        self.pending = false
        any = not any
        setAll(self, any)
    end
    if self.anyOpen ~= nil and self.anyOpen.value ~= any then
        self.anyOpen.value = any
    end
    local text = if any then 'Collapse all' else 'Expand all'
    if self.label ~= nil and self.label.value ~= text then
        self.label.value = text
    end
    -- stays awake: sections toggle themselves
    return true
end

function draw(self: Nav, renderer: Renderer) end

return function(context: Context): Layout<Nav>
    return {
        sections = nil,
        anyOpen = nil,
        label = nil,
        pending = false,
        init = init,
        advance = advance,
        draw = draw,
    }
end
