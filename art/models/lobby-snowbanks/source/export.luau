--!strict
-- Export only LobbyArea after Studio save; refuse any change outside our dressing.
local fs = require('@lune/fs')
local roblox = require('@lune/roblox')
local serde = require('@lune/serde')
local process = require('@lune/process')
local baseline = process.args[1] or 'build/lobby-snowbanks/LobbyArea-before.rbxm'
local source = process.args[2] or 'place/NaLovi.rbxl'
local game = roblox.deserializePlace(fs.readFile(source))
assert(not game.ServerScriptService:FindFirstChild('_SnowbanksQAServer'), 'QA server was not removed')
assert(not game.StarterPlayer.StarterPlayerScripts:FindFirstChild('_SnowbanksQAClient'), 'QA client was not removed')
local root = game.Workspace.LobbyArea
local banks = assert(root.WinterPlaza:FindFirstChild('Snowbanks'), 'saved place has no snowbanks')
assert(banks:GetAttribute('AuthoringOwner')=='lobby-snowbanks-20261126')
local function xml(nodes)
	return (roblox.serializeModel(nodes,true):gsub('%s*<Content name="ExplorerIconContent">%s*<null>%s*</null>%s*</Content>',''))
end
local function canonicalRotation(text)
	-- Studio writes sin(pi) as ±8.7e-8; binary axis-aligned frames round it to zero.
	return (text:gsub('(<R%d%d>)(.-)(</R%d%d>)',function(open,value,close)
		local n=tonumber(value)
		if n and math.abs(n)<1e-6 then value='0'
		elseif n and math.abs(n-1)<1e-6 then value='1'
		elseif n and math.abs(n+1)<1e-6 then value='-1' end
		return open..value..close
	end))
end
local before = roblox.deserializeModel(fs.readFile(baseline))
local clone = root:Clone()
clone.WinterPlaza.Snowbanks:Destroy()
local expected, actual = xml(before), xml({clone})
if expected~=actual then
	fs.writeFile('build/lobby-snowbanks/protected-before.xml',expected)
	fs.writeFile('build/lobby-snowbanks/protected-after.xml',actual)
end
assert(canonicalRotation(expected)==canonicalRotation(actual), 'Owner layout changed outside Snowbanks; inspect before exporting')
-- Retain the EXACT baseline instances/properties. Only the saved Studio folder is added.
local preserved=before[1]
banks:Clone().Parent=preserved.WinterPlaza
local bytes = roblox.serializeModel(roblox.deserializeModel(xml({preserved})))
local roundtrip=roblox.deserializeModel(bytes)[1]
roundtrip.WinterPlaza.Snowbanks:Destroy()
assert(xml({roundtrip})==expected, 'Export roundtrip changed a protected owner property')
fs.writeFile('models/lobby/Workspace/LobbyArea.rbxm',bytes)
local parts=0
for _,p in banks:GetDescendants() do if p:IsA('BasePart') then parts+=1 end end
fs.writeFile('art/frames/2026-11-26-lobby-snowbanks/preservation.json',serde.encode('json',{
	result='pass',protected='Every property outside Snowbanks retained from exact baseline; saved Studio differs only by axis-aligned matrix roundoff <1e-6',
	baselineModelSha256=serde.hash('sha256',fs.readFile(baseline)),modelSha256=serde.hash('sha256',bytes),
	groups=#banks:GetChildren(),parts=parts,
}))
print('PASS: whole owner LobbyArea unchanged outside Snowbanks; exported '..parts..' visual parts')
