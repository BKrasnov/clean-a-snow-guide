--!strict
-- Restore the existing board contract around the owner's visual, without moving it.
assert(game.Name=='NaLovi.rbxl' and game.PlaceId==0 and game:GetService('RunService'):IsEdit())
local root=workspace.LobbyArea;assert(not root:FindFirstChild('SoloRecordsStand'))
local source=assert(root.WinterPlaza.ImportedModels:FindFirstChild('Leaderboard2_Node'))
local mesh=assert(source:FindFirstChildWhichIsA('MeshPart',true))
local before={};for _,p in source:GetDescendants()do if p:IsA('BasePart')then before[p]={p.CFrame,p.Size}end end
local wrapper=Instance.new('Model');wrapper.Name='SoloRecordsStand';wrapper.Parent=root
wrapper:PivotTo(source:GetPivot());source.Parent=wrapper
local unit=mesh.Size.X/9.91
local face=Instance.new('Part');face.Name='Face';face.Size=Vector3.new(8.05*unit,12.30*unit,.06)
face.CFrame=mesh.CFrame*CFrame.new(0,7.25*unit-mesh.Size.Y/2,-.208*unit)
face.Transparency=1;face.Anchored=true;face.CanCollide=false;face.CanTouch=false;face.CanQuery=false;face.CastShadow=false;face.Parent=wrapper
wrapper:SetAttribute('OwnerLayoutDate','2026-11-26')
for p,old in before do assert(p.CFrame==old[1] and p.Size==old[2],'Owner visual moved')end
return 'Owner Leaderboard2_Node now provides SoloRecordsStand.Face; original visual transforms unchanged'
