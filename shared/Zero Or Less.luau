-- Converter: true when the number is zero or less.
--
-- Rive has no number → boolean converter, so a bool such as a Button's `disabled` can't follow
-- a comparison on its own. Put a Formula in front that is zero or less when the bool should be
-- on (e.g. `min(value - min, 1 - disabled)` for "at the minimum, or disabled"), then this.

type ZeroOrLess = {}

local function convert(self: ZeroOrLess, input: DataValueNumber): DataValueBoolean
    local out = DataValue.boolean()
    out.value = input.value <= 0
    return out
end

-- The way back (required by the protocol): on → 0, off → 1.
local function reverseConvert(self: ZeroOrLess, input: DataValueBoolean): DataValueNumber
    local out = DataValue.number()
    out.value = if input.value then 0 else 1
    return out
end

return function(): Converter<ZeroOrLess, DataValueNumber, DataValueBoolean>
    return { convert = convert, reverseConvert = reverseConvert }
end
