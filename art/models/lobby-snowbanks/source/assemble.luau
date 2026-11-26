--!strict
-- Edit-only authoring. The caller supplies payload from export/placement.json.
assert(game.Name=='NaLovi.rbxl' and game.PlaceId==0 and game:GetService('RunService'):IsEdit())
local root=assert(workspace:FindFirstChild('LobbyArea'))
assert(root.SoloRecordsStand:FindFirstChild('Leaderboard2_Node'), 'Expected owner layout checkpoint')
local plaza=root.WinterPlaza
local previous=plaza:FindFirstChild('Snowbanks')
if previous then assert(previous:GetAttribute('AuthoringOwner')=='lobby-snowbanks-20261126','Unowned snow folder') end
assert(#payload.groups>=36 and #payload.parts<=180)
local folder=Instance.new('Folder');folder.Name='Snowbanks'
folder:SetAttribute('AuthoringOwner','lobby-snowbanks-20261126')
folder:SetAttribute('OwnerLayoutBaseline',payload.ownerLayoutBaseline)
local groups={}
for _,row in payload.groups do
	local group=Instance.new('Model');group.Name=row.id;group:SetAttribute('Template',row.template)
	group:SetAttribute('PlacementKind',row.category);group.Parent=folder;groups[row.id]=group
end
for _,row in payload.parts do
	local part=Instance.new('Part');part.Name=row.name
	part.Size=Vector3.new(unpack(row.size))
	part.CFrame=CFrame.new(payload.origin[1]+row.at[1],payload.origin[2]+row.at[2],payload.origin[3]+row.at[3],unpack(row.rotation))
	part.Color=Color3.fromHex(row.rgb);part.Material=Enum.Material.SmoothPlastic
	part.Anchored=true;part.CanCollide=false;part.CanTouch=false;part.CanQuery=false;part.CastShadow=true
	part.TopSurface=Enum.SurfaceType.Smooth;part.BottomSurface=Enum.SurfaceType.Smooth
	local mesh=Instance.new('SpecialMesh');mesh.MeshType=Enum.MeshType.Sphere;mesh.Scale=Vector3.one;mesh.Parent=part
	part.Parent=assert(groups[row.group])
end
if previous then previous:Destroy() end
folder.Parent=plaza
return 'Installed '..#payload.groups..' snowbank groups ('..#payload.parts..' non-contact parts), owner layout untouched'
