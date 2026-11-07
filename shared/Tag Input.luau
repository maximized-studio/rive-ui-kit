-- Tag Input behaviour: turns typed text into tags and removes them again.
--
-- The field's TextInput writes `draft`. Enter (which fires `_commit`) or a comma adds the draft
-- as a Tag to `tags` (trimmed, skipped when empty or already there, case-insensitively) and
-- clears it. Each Tag's remove button fires its own `_remove`; the script takes that tag out.
-- `disabled` is passed on to every tag, so their remove buttons stop too. Apps read and write
-- `tags` (a list of Tag view models with a `label`) like any other list.

type TagInput = {
    context: Context?,
    tags: PropertyList?,
    draft: Property<string>?,
    disabled: Property<boolean>?,
    listening: { [ViewModel]: boolean },
    removeLabel: string?,
    commit: boolean,
}

local function trim(s: string): string
    return (string.gsub(s, '^%s*(.-)%s*$', '%1'))
end

local function wake(self: TagInput)
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function labelOf(item: ViewModel): string
    local p = item:getString('label')
    return if p ~= nil then p.value else ''
end

local function watch(self: TagInput, item: ViewModel)
    if self.listening[item] then
        return
    end
    self.listening[item] = true
    local remove = item:getTrigger('_remove')
    if remove ~= nil then
        remove:addListener(item, function()
            self.removeLabel = labelOf(item)
            wake(self)
        end)
    end
end

local function syncTags(self: TagInput)
    local tags = self.tags
    if tags == nil then
        return
    end
    local off = self.disabled ~= nil and self.disabled.value
    for k = 1, tags.length do
        local item = tags[k]
        watch(self, item)
        local d = item:getBoolean('disabled')
        if d ~= nil and d.value ~= off then
            d.value = off
        end
    end
end

local function add(self: TagInput, text: string)
    local tags = self.tags
    local label = trim(text)
    if tags == nil or label == '' then
        return
    end
    for k = 1, tags.length do
        if string.lower(labelOf(tags[k])) == string.lower(label) then
            return
        end
    end
    local item = Data.Tag.new()
    local p = item:getString('label')
    if p ~= nil then
        p.value = label
    end
    tags:push(item)
end

function init(self: TagInput, context: Context): boolean
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.tags = vm:getList('tags')
    self.draft = vm:getString('draft')
    self.disabled = vm:getBoolean('disabled')
    local commit = vm:getTrigger('_commit')
    if commit ~= nil then
        commit:addListener(vm, function()
            self.commit = true
            wake(self)
        end)
    end
    if self.draft ~= nil then
        self.draft:addListener(vm, function()
            wake(self)
        end)
    end
    if self.disabled ~= nil then
        self.disabled:addListener(vm, function()
            wake(self)
        end)
    end
    if self.tags ~= nil then
        self.tags:addListener(vm, function()
            wake(self)
        end)
    end
    syncTags(self)
    return true
end

function advance(self: TagInput, seconds: number): boolean
    local tags, draft = self.tags, self.draft
    if tags == nil or draft == nil then
        return false
    end
    -- a comma anywhere in the draft adds everything before it
    local text = draft.value
    if string.find(text, ',', 1, true) ~= nil then
        local rest = ''
        for piece in string.gmatch(text .. ',', '([^,]*),') do
            rest = piece
        end
        for piece in string.gmatch(text, '([^,]*),') do
            add(self, piece)
        end
        draft.value = rest
    end
    if self.commit then
        self.commit = false
        add(self, draft.value)
        draft.value = ''
    end
    local label = self.removeLabel
    if label ~= nil then
        self.removeLabel = nil
        for k = tags.length, 1, -1 do
            if labelOf(tags[k]) == label then
                tags:removeAt(k)
                break
            end
        end
    end
    syncTags(self)
    return false
end

function draw(self: TagInput, renderer: Renderer) end

return function(context: Context): Layout<TagInput>
    return {
        context = nil,
        tags = nil,
        draft = nil,
        disabled = nil,
        listening = {},
        removeLabel = nil,
        commit = false,
        init = init,
        advance = advance,
        draw = draw,
    }
end
