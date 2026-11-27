--!strict
local roblox=require('@lune/roblox')
local Enum=roblox.Enum;local Vector3=roblox.Vector3;local M={}
function M.xml(root)
 local text=roblox.serializeModel({root},true):gsub('%s*<Content name="ExplorerIconContent">%s*<null>%s*</null>%s*</Content>','')
 text=text:gsub('%s*<BinaryString name="AttributesSerialize">%s*</BinaryString>','')
 return (text:gsub('(<R%d%d>)(.-)(</R%d%d>)',function(a,b,c)local n=tonumber(b);if n and math.abs(n)<1e-6 then b='0' elseif n and math.abs(n-1)<1e-6 then b='1' elseif n and math.abs(n+1)<1e-6 then b='-1' end;return a..b..c end))
end
function M.protected(root)
 local copy=root:Clone();local plaza=copy.WinterPlaza
 for _,name in {'Snowbanks','SnowLandscape','SnowRelief'}do local p=plaza:FindFirstChild(name);if p then p:Destroy()end end
 for _,p in plaza.SnowFirs:GetChildren()do if p:IsA('BasePart')then p.CFrame=roblox.CFrame.identity;p:SetAttribute('SnowTerrainOriginalY',nil)end end
 for _,p in {plaza.PlazaSurface,copy.SnowGround}do p.Material=Enum.Material.Snow;p.MaterialVariant='';p:SetAttribute('WhiteGrassAsset',nil)end
 -- 27.11: only these floor display fields are now owned by the local snow relief.
 plaza.PlazaSurface.Transparency=0
 plaza.EntrancePath.Transparency=0;plaza.EntrancePath.Material=Enum.Material.Concrete;plaza.EntrancePath.MaterialVariant=''
 local entrance=plaza.EntrancePath
 local frame={entrance.CFrame:GetComponents()}
 frame[2]=0
 entrance.CFrame=roblox.CFrame.new(table.unpack(frame))
 return M.xml(copy)
end
return M
