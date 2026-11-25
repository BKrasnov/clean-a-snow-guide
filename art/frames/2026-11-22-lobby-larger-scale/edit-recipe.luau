assert(game.PlaceId == 0 and game.Name == "NaLovi.rbxl" and not game:GetService("RunService"):IsRunning(), "expected the local NaLovi editor")
local old = workspace.LobbyArea
local lobby = old:Clone()
local plaza = lobby.WinterPlaza
local floor = plaza.PlazaSurface
assert(floor.Size.X == 104 and floor.Size.Z == 88, "unexpected source size")
local factor = 1.5
local ground = floor.Position.Y + floor.Size.Y / 2
local function spread(position)
	return Vector3.new(6500 + (position.X - 6500) * factor, position.Y, 72 + (position.Z - 72) * factor)
end
floor.Size = Vector3.new(156, floor.Size.Y, 132)
floor.Position = Vector3.new(6500, floor.Position.Y, 6)
local imported = plaza.ImportedModels
for _, model in imported:GetChildren() do
	if model.Name:match("^Fence_") or model.Name:match("^OpenGate_") then
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") then
				part.CFrame = CFrame.new(spread(part.Position)) * part.CFrame.Rotation
				part.Size = Vector3.new(part.Size.X * factor, part.Size.Y, part.Size.Z * factor)
			end
		end
	elseif model.Name:match("^SnowFir") then
		local pivot = model:GetPivot()
		model:PivotTo(pivot + spread(pivot.Position) - pivot.Position)
	end
end
for _, tree in plaza.SnowFirs:GetChildren() do
	if tree:IsA("BasePart") then tree.CFrame = CFrame.new(spread(tree.Position)) * tree.CFrame.Rotation end
end

local measurements = {}
local function enlarge(model, scale, horizontalSpacing)
	local bounds, size = model:GetBoundingBox()
	local base = Vector3.new(bounds.X, bounds.Y - size.Y / 2, bounds.Z)
	local nextBase = spread(base)
	if horizontalSpacing then nextBase = Vector3.new(6500 + (base.X - 6500) * horizontalSpacing, nextBase.Y, nextBase.Z) end
	local comparisons = {}
	for _, item in model:GetDescendants() do
		if item:IsA("BasePart") then
			local frame = item.CFrame
			local previousSize = item.Size
			item.Size = previousSize * scale
			item.CFrame = CFrame.new(nextBase + (frame.Position - base) * scale) * frame.Rotation
			assert((item.Size - previousSize * scale).Magnitude < 0.001, "incorrect scale: " .. item.Name)
			if item:IsA("MeshPart") then
				table.insert(comparisons, {name = item.Name, previous = {previousSize.X, previousSize.Y, previousSize.Z}, current = {item.Size.X, item.Size.Y, item.Size.Z}})
			end
		elseif item:IsA("Attachment") then
			item.CFrame = CFrame.new(item.CFrame.Position * scale) * item.CFrame.Rotation
		end
	end
	local after, afterSize = model:GetBoundingBox()
	assert(math.abs((after.Y - afterSize.Y / 2) - base.Y) < 0.01, "model floats over the plaza: " .. model.Name)
	table.insert(measurements, {name = model.Name, scale = scale, meshes = comparisons})
end
for _, name in {"Rewards_Node", "Upgrades_Node", "PrizeWheel_Kiosk_Node", "Classes_Node"} do enlarge(imported[name], 1.5) end
for _, name in {"Leaderboard01_Node", "Leaderboard03_Node"} do enlarge(imported[name], 2, 2) end
enlarge(lobby.SoloRecordsStand, 2)

for _, station in lobby.QueueStations:GetChildren() do
	local zone = station.Zone
	local position = spread(zone.Position)
	local x = if zone.Position.X < 6500 then 6448 else 6552
	zone.Size = Vector3.new(36, zone.Size.Y, 16.5)
	zone.CFrame = CFrame.new(x, position.Y, position.Z) * zone.CFrame.Rotation
	for _, item in zone:GetDescendants() do
		if item:IsA("Attachment") then
			local at = item.CFrame.Position
			item.CFrame = CFrame.new(at.X * factor, at.Y, at.Z * factor) * item.CFrame.Rotation
		elseif item:IsA("Beam") and (item.Name:match("^Rising") or item.Name == "FloorGlow") then
			item.Width0 *= factor
			item.Width1 *= factor
		end
	end
	local gap = floor.Size.X / 2 - math.abs(x - 6500) - zone.Size.X / 2
	assert(gap == 8, "incorrect side clearance")
end
for _, name in {"Upgrades_Node", "Classes_Node", "PrizeWheel_Kiosk_Node"} do
	local at = imported[name].Interaction
	local prompt = at:FindFirstChildOfClass("ProximityPrompt")
	for _, station in lobby.QueueStations:GetChildren() do
		local zone = station.Zone
		local point = zone.CFrame:PointToObjectSpace(at.Position)
		local dx = math.max(math.abs(point.X) - zone.Size.X / 2, 0)
		local dz = math.max(math.abs(point.Z) - zone.Size.Z / 2, 0)
		assert(math.sqrt(dx * dx + dz * dz) > prompt.MaxActivationDistance + 1, name .. " overlaps " .. station.Name)
	end
end
local history = game:GetService("ChangeHistoryService")
local recording = assert(history:TryBeginRecording("LargerLobbyScale", "Enlarge the lobby and move start zones to the sides"))
old.Parent = nil
lobby.Parent = workspace
history:FinishRecording(recording, Enum.FinishRecordingOperation.Commit)
return game:GetService("HttpService"):JSONEncode({surface = {156, 132}, startZone = {36, 16.5}, sideGap = 8, models = measurements})
