--!strict
-- Authoring helper, run in Edit with profile JSON in local payload; never a game script.
local function apply(lighting: any, profile: any)
 for name,properties in profile do
  local object=if name=='Lighting' then lighting else assert(lighting:FindFirstChild(name),'Missing effect '..name)
  for property,value in properties do
   if type(value)=='string' and value:sub(1,1)=='#' then value=Color3.fromHex(value) end
   object[property]=value
  end
 end
end
return apply
