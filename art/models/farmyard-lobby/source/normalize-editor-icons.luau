--!strict
-- Studio may add an empty ExplorerIconContent field to authoring folders/models.
-- In a place, rbx_binary then adds the field to every instance of that class,
-- changing otherwise untouched layers. Remove only that empty editor field.
local fs = require('@lune/fs')
local roblox = require('@lune/roblox')
local process = require('@lune/process')
local input, output = process.args[1], process.args[2]
assert(input and output, 'usage: normalize-editor-icons <input.rbxm> <output.rbxm>')
local xml = roblox.serializeModel(roblox.deserializeModel(fs.readFile(input)), true)
local clean, count = xml:gsub('%s*<Content name="ExplorerIconContent">%s*<null>%s*</null>%s*</Content>', '')
fs.writeFile(output, roblox.serializeModel(roblox.deserializeModel(clean), false))
print('Removed empty editor icon fields: '..count)
