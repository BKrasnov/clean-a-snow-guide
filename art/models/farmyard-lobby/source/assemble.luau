--!strict
-- Studio authoring, run in Edit with `payload` decoded from ../export/parts.json.
-- This file is not deployed as a game script. Export the saved LobbyArea afterwards.
assert(game.Name == 'NaLovi.rbxl' and game.PlaceId == 0, 'Unexpected Studio place')
assert(game:GetService('RunService'):IsEdit(), 'Author only the Edit DataModel')
local root = assert(workspace:FindFirstChild('LobbyArea'), 'Expected authored lobby')
assert(#root.QueueStations:GetChildren() == 6, 'Expected six existing queues')
local plaza = root.WinterPlaza
assert(not plaza:FindFirstChild('Farmyard'), 'Farmyard already assembled: restore baseline before rerunning')
local origin = Vector3.new(unpack(payload.origin))
local function hex(value)
	return Color3.fromRGB(tonumber(value:sub(1,2),16),tonumber(value:sub(3,4),16),tonumber(value:sub(5,6),16))
end
local yard = Instance.new('Model')
yard.Name = 'Farmyard'
yard:SetAttribute('SourceReference','art/refs/farm-lobby/01-farmyard.png')
yard.Parent = plaza
local groups = {}
for _, row in payload.parts do
	local group = groups[row.group]
	if not group then
		group = Instance.new('Model');group.Name=row.group;group.Parent=yard;groups[row.group]=group
	end
	local part = Instance.new(if row.kind=='WedgePart' then 'WedgePart' else 'Part')
	part.Name=row.name
	if row.kind=='Ball' then
		local mesh=Instance.new('SpecialMesh');mesh.MeshType=Enum.MeshType.Sphere;mesh.Scale=Vector3.one;mesh.Parent=part
	end
	part.Size=Vector3.new(unpack(row.size))
	part.CFrame=CFrame.new(origin.X+row.at[1],origin.Y+row.at[2],origin.Z+row.at[3],unpack(row.rotation))
	part.Color=hex(row.rgb)
	part.Material=Enum.Material.SmoothPlastic
	part.Anchored=true;part.CanCollide=row.collide;part.CanTouch=false;part.CanQuery=row.collide
	part.TopSurface=Enum.SurfaceType.Smooth;part.BottomSurface=Enum.SurfaceType.Smooth
	part.Parent=group
	if row.name:match('Light$') then
		part.Material=Enum.Material.Neon
		local light=Instance.new('PointLight');light.Color=hex('FAD66E');light.Brightness=.6;light.Range=12;light.Shadows=false;light.Parent=part
	end
end
-- Bring the side stalls into sight from the entrance, inside the lines of the buildings.
groups.Rewards:PivotTo(groups.Rewards:GetPivot()+Vector3.new(23,0,8))
groups.Upgrades:PivotTo(groups.Upgrades:GetPivot()+Vector3.new(6,0,2))
groups.Classes:PivotTo(groups.Classes:GetPivot()+Vector3.new(-28,0,6))
local function label(part,text,width,height)
	local gui=Instance.new('SurfaceGui');gui.Name='FarmyardLabel';gui.Face=Enum.NormalId.Back
	gui.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize;gui.CanvasSize=Vector2.new(width or 1200,height or 180)
	gui.LightInfluence=.2;gui.AlwaysOnTop=false;gui.Parent=part
	local title=Instance.new('TextLabel');title.Name='Title';title.BackgroundTransparency=1
	title.Size=UDim2.fromScale(.95,.9);title.Position=UDim2.fromScale(.025,.05)
	title.Text=text;title.TextColor3=hex('FFFDF5');title.TextStrokeTransparency=.55;title.TextStrokeColor3=hex('2B1A11')
	title.Font=Enum.Font.FredokaOne;title.TextScaled=true;title.Parent=gui
end
label(groups.Garage.GarageSign,'GARAGE')
label(groups.LaunchArch.Sign,'START GAME')
for _, name in {'Rewards','Upgrades','Classes'} do label(groups[name].Sign,string.upper(name),900,170) end
for index=1,6 do
	local id=string.format('Station%02d',index)
	local zone=root.QueueStations[id].Zone
	local oldSize=zone.Size
	for _,attachment in zone:GetChildren() do
		if attachment:IsA('Attachment') then
			local at=attachment.Position
			attachment.Position=Vector3.new(at.X*14/oldSize.X,at.Y,at.Z*12/oldSize.Z)
		elseif attachment:IsA('ProximityPrompt') then attachment.MaxActivationDistance=8 end
	end
	for _,beam in root.QueueStations[id]:GetDescendants() do
		if beam:IsA('Beam') then
			local width=nil
			if beam.Name=='FloorGlow' then width=14
			elseif beam.Name=='Rising1' or beam.Name=='Rising3' then width=14.2
			elseif beam.Name=='Rising2' or beam.Name=='Rising4' then width=12.2
			elseif beam.Name:match('^Edge') then width=.28
			elseif beam.Name:match('^Glow') then width=.55
			elseif beam.Name:match('^Halo') then width=1 end
			if width then beam.Width0=width;beam.Width1=width end
		end
	end
	zone.Size=Vector3.new(14,oldSize.Y,12)
	zone.CFrame=CFrame.new(14000-42.5+(index-1)*17,120.94,-32)
	local pad=Instance.new('Part');pad.Name=id..'Pad';pad.Size=Vector3.new(14.7,.2,12.7)
	pad.CFrame=CFrame.new(zone.Position.X,120.84,-32);pad.Color=hex('FFFDF5')
	pad.Anchored=true;pad.CanCollide=false;pad.CanTouch=false;pad.CanQuery=false;pad.Parent=yard
	pad.TopSurface=Enum.SurfaceType.Smooth;pad.BottomSurface=Enum.SurfaceType.Smooth
	local fill=pad:Clone();fill.Name=id..'Inset';fill.Size=Vector3.new(13.9,.12,11.9)
	fill.CFrame=pad.CFrame+Vector3.new(0,.15,0);fill.Color=hex('77C98D');fill.Parent=yard
	local frame=groups[string.format('MapFrame%02d',index)]
	label(frame.MapCrossbar,'FROSTWOOD '..tostring(index),900,100)
end
plaza.PlazaSurface.Size=Vector3.new(208,.26,166)
plaza.PlazaSurface.CFrame=CFrame.new(14000,120.59,8)
plaza.PlazaSurface.Color=hex('F3F6F5');plaza.PlazaSurface.Material=Enum.Material.Snow
plaza.EntrancePath.Size=Vector3.new(16,.22,126)
plaza.EntrancePath.CFrame=CFrame.new(14000,120.74,30)
plaza.EntrancePath.Color=hex('B3C2D4');plaza.EntrancePath.Material=Enum.Material.Concrete
root.LobbySpawn.CFrame=CFrame.new(14000,121.13,85)
local imported=plaza.ImportedModels
local function place(model,x,z,factor,yaw)
	model:ScaleTo(model:GetScale()*factor)
	local pivot=model:GetPivot()
	model:PivotTo(CFrame.new(pivot.Position)*CFrame.Angles(0,math.rad(yaw or 0),0)*pivot.Rotation)
	local cf,size=model:GetBoundingBox()
	model:PivotTo(model:GetPivot()+Vector3.new(14000+x-cf.Position.X,120.75-(cf.Position.Y-size.Y/2),z-cf.Position.Z))
end
-- Preserve each kiosk's interaction object and its attributes/prompt. Only the failed
-- private visual meshes are replaced by the newly authored solids above.
for name,at in {Upgrades_Node={-71,-34},Classes_Node={50,-4},Rewards_Node={-55,-4}} do
	local model=assert(imported:FindFirstChild(name))
	local interaction=model:FindFirstChild('Interaction')
	if interaction then interaction.CFrame=CFrame.new(14000+at[1],124.5,at[2]+5) end
	for _,part in model:GetChildren() do if part:IsA('MeshPart') then part:Destroy() end end
end
place(imported.PrizeWheel_Kiosk_Node,78,-38,.72,0)
place(imported.Leaderboard01_Node,-68,-51,.62,0)
place(root.SoloRecordsStand,-89,-47,.62,0)
place(imported.Leaderboard03_Node,68,-58,.62,0)
if imported:FindFirstChild('Part') then imported.Part:Destroy() end
-- Existing fences are resized as paired wood/snow meshes, keeping their authored colours.
local function fence(node,at,width,depth)
	local items={}
	local oldCf,oldSize=node:GetBoundingBox()
	for _,part in node:GetDescendants() do
		if part:IsA('BasePart') then table.insert(items,{part=part,cf=part.CFrame,size=part.Size}) end
	end
	for _,row in items do
		local localAt=oldCf:PointToObjectSpace(row.cf.Position)
		row.part.Size=Vector3.new(row.size.X*width/oldSize.X,row.size.Y,row.size.Z*depth/oldSize.Z)
		row.part.CFrame=CFrame.new(14000+at[1]+localAt.X*width/oldSize.X,row.cf.Position.Y,at[2]+localAt.Z*depth/oldSize.Z)*row.cf.Rotation
	end
end
fence(imported.Fence_Back_Node,{0,-72},208,2)
fence(imported.Fence_Left_Node,{-103,8},2,160)
fence(imported.Fence_Right_Node,{103,8},2,160)
fence(imported.Fence_Entry_Left_Node,{-59,89},88,2)
fence(imported.Fence_Entry_Right_Node,{59,89},88,2)
place(imported.OpenGate_Left_Node,-14,91,1,0)
place(imported.OpenGate_Right_Node,14,91,1,0)
-- Clear the widened yard by moving only intruding decorative firs; preserve all 184 trees.
for _,tree in plaza.SnowFirs:GetChildren() do
	local x,z=tree.Position.X-14000,tree.Position.Z
	if math.abs(x)<112 and z>-83 and z<102 then
		local sign=if x<0 then -1 else 1
		local radius=math.sqrt(tree.Size.X^2+tree.Size.Z^2)/2
		tree.CFrame=tree.CFrame+Vector3.new(sign*(117+radius)-x,0,0)
	end
end
root:SetAttribute('FarmyardLayout','2026-11-25')
-- Existing assets are reused as static exhibits, with no seats, remotes or purchase prompts.
local dressing=Instance.new('Model');dressing.Name='GarageExhibits';dressing.Parent=yard
local truckSource=assert(workspace:FindFirstChild('CartoonPickup'),'Missing existing pickup visual')
local truck=Instance.new('Model');truck.Name='ParkedSnowTruck';truck.Parent=dressing
for _,part in truckSource:GetDescendants() do
	if part:IsA('MeshPart') then
		local copy=part:Clone()
		for _,child in copy:GetChildren() do child:Destroy() end
		for key in copy:GetAttributes() do if not key:match('^RBX_') then copy:SetAttribute(key,nil) end end
		copy.Anchored=true;copy.CanCollide=false;copy.CanTouch=false;copy.CanQuery=false
		if part.Name=='Cabin' or part.Name=='Body.001' then copy.Color=hex('FFCE43') end
		copy.Parent=truck
	end
end
truck:ScaleTo(.8)
local truckFrame,truckSize=truck:GetBoundingBox()
truck:PivotTo(CFrame.new(13934,121.85+truckSize.Y/2,33)*CFrame.Angles(0,math.rad(192),0)*truckFrame:Inverse()*truck:GetPivot())
local weapons=game.ReplicatedStorage.CleanSnowAssets.Weapons
for index,name in {'SnowSpoon','SnowShovel','IceAxe'} do
	local exhibit=weapons[name]:Clone();exhibit.Name='Decor'..name;exhibit.Parent=dressing
	for _,item in exhibit:GetDescendants() do
		if item:IsA('BaseScript') or item:IsA('ProximityPrompt') or item:IsA('Constraint') or item:IsA('JointInstance') then item:Destroy()
		elseif item:IsA('BasePart') then item.Anchored=true;item.CanCollide=false;item.CanTouch=false;item.CanQuery=false end
	end
	for key in exhibit:GetAttributes() do if not key:match('^RBX_') then exhibit:SetAttribute(key,nil) end end
	local _,size=exhibit:GetBoundingBox()
	exhibit:ScaleTo(exhibit:GetScale()*4.4/math.max(size.X,size.Y,size.Z))
	local frame,_=exhibit:GetBoundingBox()
	local to=CFrame.new(13925+(index-1)*3.1,126,23)*CFrame.Angles(0,math.rad(12),math.rad(-12))
	exhibit:PivotTo(to*frame:Inverse()*exhibit:GetPivot())
end
local firSource=plaza.SnowFirs:GetChildren()[1]
for index=1,6 do
	local frame=groups[string.format('MapFrame%02d',index)]
	for treeIndex=1,3 do
		local fir=firSource:Clone();fir.Name='MapFir'
		local height=if treeIndex==2 then 3.3 else 2.7
		fir.Size=fir.Size*height/fir.Size.Y
		fir.CFrame=CFrame.new(14000-42.5+(index-1)*17+(treeIndex-2)*3.4,120.75+5+height/2,-42.1)*fir.CFrame.Rotation
		fir.Anchored=true;fir.CanCollide=false;fir.CanTouch=false;fir.CanQuery=false;fir.CastShadow=false;fir.Parent=frame
	end
end
local qa=game.StarterPlayer.StarterPlayerScripts:FindFirstChild('_FarmyardQA')
if qa then qa:Destroy() end
print(game:GetService('HttpService'):JSONEncode({parts=#payload.parts,queues=#root.QueueStations:GetChildren(),trees=#plaza.SnowFirs:GetChildren()}))
game:GetService('ChangeHistoryService'):SetWaypoint('Farmyard lobby composition')
return 'farmyard assembled in Edit'
