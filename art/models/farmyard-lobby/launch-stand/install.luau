--!strict
-- Authoring only. Use the owner's imported LaunchStand; no game code changes.
assert(game.Name=='NaLovi.rbxl' and game.PlaceId==0 and game:GetService('RunService'):IsEdit())
local source=assert(workspace.Scene:FindFirstChild('LaunchStand'),'Missing imported stand')
local yard=workspace.LobbyArea.WinterPlaza.Farmyard
assert(not yard:GetAttribute('LaunchStandPictureInstalled'),'Stand replacement already installed')
for _,item in source:GetDescendants() do assert(not item:IsA('LuaSourceContainer') and not item:IsA('ProximityPrompt'),'Unexpected imported behavior') end
local function collider(parent: Model,name: string,size: Vector3,frame: CFrame)
 local part=Instance.new('Part');part.Name=name;part.Size=size;part.CFrame=frame
 part.Transparency=1;part.Anchored=true;part.CanCollide=true;part.CanTouch=false;part.CanQuery=true;part.CastShadow=false;part.Parent=parent
end
for index=1,6 do
 local name=string.format('MapFrame%02d',index)
 local old=assert(yard:FindFirstChild(name))
 local oldBox,oldSize=old:GetBoundingBox()
 local model=source:Clone();local _,size=model:GetBoundingBox();model:ScaleTo(model:GetScale()*15.5/size.X)
 model:PivotTo(CFrame.Angles(0,math.pi,0))
 local box,extent=model:GetBoundingBox()
 local ground=oldBox.Position.Y-oldSize.Y/2
 model:PivotTo(model:GetPivot()+Vector3.new(oldBox.Position.X-box.Position.X,ground-(box.Position.Y-extent.Y/2),oldBox.Position.Z-box.Position.Z))
 model.Name=name;model:SetAttribute('ImportedLaunchStand',true)
 for _,part in model:GetDescendants() do if part:IsA('BasePart') then part.Anchored=true;part.CanCollide=false;part.CanTouch=false;part.CanQuery=false end end
 local unit=15.5/6.65 -- ratio of the imported mesh to the authored stand dimensions
 local base=model:GetPivot()
 for _,sign in {-1,1} do
  collider(model,'PostCollider',Vector3.new(.48,7.14,.64)*unit,base*CFrame.new(sign*2.92*unit,4.05*unit,.08*unit))
  collider(model,'FootCollider',Vector3.new(.83,.64,1.12)*unit,base*CFrame.new(sign*2.92*unit,.32*unit,.07*unit))
 end
 collider(model,'BackingCollider',Vector3.new(5.45,5.26,.47)*unit,base*CFrame.new(0,4.46*unit,.08*unit))
 local plane=Instance.new('Part');plane.Name='PictureSurface';plane.Size=Vector3.new(5.18*unit,4.94*unit,.02)
 plane.CFrame=base*CFrame.new(0,4.46*unit,-.175*unit);plane.Transparency=1;plane.Anchored=true
 plane.CanCollide=false;plane.CanTouch=false;plane.CanQuery=false;plane.CastShadow=false;plane.Parent=model
 local gui=Instance.new('SurfaceGui');gui.Name='Landscape';gui.Face=Enum.NormalId.Front
 gui.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize;gui.CanvasSize=Vector2.new(1284,1225)
 gui.LightInfluence=.35;gui.AlwaysOnTop=false;gui.MaxDistance=300;gui.Parent=plane
 local picture=Instance.new('ImageLabel');picture.Name='Artwork';picture.BackgroundTransparency=1
 picture.Size=UDim2.fromScale(1,1);picture.Image='rbxassetid://123239346194001';picture.ScaleType=Enum.ScaleType.Crop;picture.Parent=gui
 model.Parent=yard;old:Destroy()
end
local scene=source.Parent;source:Destroy();if #scene:GetChildren()==0 then scene:Destroy() end
yard:SetAttribute('LaunchStandPictureInstalled',true)
workspace.CurrentCamera.CFrame=CFrame.lookAt(Vector3.new(14000,134,-10),Vector3.new(14000,130,-43))
return 'Six imported launch stands installed with owner image; queue zones untouched'
