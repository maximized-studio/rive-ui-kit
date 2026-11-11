--
-- Reads `page` and `pageCount`, fills `_pages` with Page Items: every page up to 7 pages,
-- otherwise 1 … 4 5 6 … 20 (an item with value 0 is the ellipsis). Sets `_prevDisabled` on
-- the first page and `_nextDisabled` on the last. A click on a page item writes that item's
-- `current`; the script turns it into `page`, so apps only ever read and write `page`.

type Pager = {
    context: Context?,
    vm: ViewModel?,
    page: Property<number>?,
    count: Property<number>?,
    pages: PropertyList?,
    prevOff: Property<boolean>?,
    nextOff: Property<boolean>?,
    shownPage: number,
    shownCount: number,
}

local MAX_BUTTONS = 7

-- The page number per button for this page and count; 0 is an ellipsis.
local function buttons(page: number, count: number): { number }
    local out: { number } = {}
    if count <= MAX_BUTTONS then
        for i = 1, count do
            table.insert(out, i)
        end
        return out
    end
    -- three pages around the current one, kept clear of the first two and last two buttons
    local first = math.max(3, math.min(page - 1, count - 4))
    return {
        1,
        if first == 3 then 2 else 0,
        first,
        first + 1,
        first + 2,
        if first == count - 4 then count - 1 else 0,
        count,
    }
end

local function wake(self: Pager)
    if self.context ~= nil then
        self.context:markNeedsUpdate()
    end
end

local function sync(self: Pager)
    local pageProp, countProp, pages = self.page, self.count, self.pages
    if pageProp == nil or countProp == nil or pages == nil then
        return
    end
    local count = math.max(0, math.floor(countProp.value))
    local page = math.max(1, math.min(math.floor(pageProp.value), math.max(count, 1)))
    if page ~= pageProp.value then
        pageProp.value = page
    end
    local want = buttons(page, count)
    while pages.length > #want do
        pages:pop()
    end
    while pages.length < #want do
        local item = Data.PageItem.new()
        local current = item:getNumber('current')
        if current ~= nil then
            -- a click writes the item's `current`: wake the script to turn it into `page`
            current:addListener(item, function()
                wake(self)
            end)
        end
        pages:push(item)
    end
    for i, number in ipairs(want) do
        local item = pages[i]
        local value = item:getNumber('value')
        local current = item:getNumber('current')
        if value ~= nil then
            value.value = number
        end
        if current ~= nil then
            current.value = page
        end
    end
    if self.prevOff ~= nil then
        self.prevOff.value = page <= 1
    end
    if self.nextOff ~= nil then
        self.nextOff.value = page >= count
    end
    self.shownPage = page
    self.shownCount = count
end

function init(self: Pager, context: Context): boolean
    -- init runs twice; the view model is only there the second time
    local vm = context:viewModel()
    if vm == nil then
        return true
    end
    self.context = context
    self.vm = vm
    self.page = vm:getNumber('page')
    self.count = vm:getNumber('pageCount')
    self.pages = vm:getList('_pages')
    self.prevOff = vm:getBoolean('_prevDisabled')
    self.nextOff = vm:getBoolean('_nextDisabled')
    -- the script sleeps between changes: page, pageCount and clicks wake it
    for _, prop in { self.page, self.count } do
        if prop ~= nil then
            prop:addListener(vm, function()
                wake(self)
            end)
        end
    end
    sync(self)
    return true
end

function advance(self: Pager, seconds: number): boolean
    local pageProp, countProp, pages = self.page, self.count, self.pages
    if pageProp == nil or countProp == nil or pages == nil then
        return false
    end
    -- a page item that was clicked carries its own number in `current`
    for i = 1, pages.length do
        local current = pages[i]:getNumber('current')
        if current ~= nil and current.value ~= self.shownPage then
            pageProp.value = current.value
            break
        end
    end
    if pageProp.value ~= self.shownPage or countProp.value ~= self.shownCount then
        sync(self)
    end
    return false
end

function draw(self: Pager, renderer: Renderer) end

return function(context: Context): Layout<Pager>
    return {
        context = nil,
        vm = nil,
        page = nil,
        count = nil,
        pages = nil,
        prevOff = nil,
        nextOff = nil,
        shownPage = -1,
        shownCount = -1,
        init = init,
        advance = advance,
        draw = draw,
    }
end
