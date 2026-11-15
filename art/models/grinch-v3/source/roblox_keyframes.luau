--!strict
-- Grinch v3 (card e49171): the five clips as KeyframeSequences in Studio, from the JSON of roblox_clips.py.
-- Run in the Edit data model of a place with the imported Grinch (Import 3D of export/Grinch.fbx, Scale Unit Meter),
-- while the JSON folder is served on localhost:
--     python3 -m http.server 8777 --bind 127.0.0.1   (in art/models/grinch-v3/export/roblox-clips)
-- Writes Workspace.Grinch.AnimSaves.Grinch_<Clip>: the Animation Editor loads them from there and publishes them.
-- Blender (x, y, z) maps to the body space of Grinch_Body as (-x, z, y), measured on the imported bones; 1 m = 1/0.28 studs.
local HttpService = game:GetService("HttpService")
local grinch = workspace:WaitForChild("Grinch")
local body = grinch:WaitForChild("Grinch_Body") :: BasePart
local STUDS = 1 / 0.28
local CLIPS = { "Idle", "Walk", "Attack", "Hit", "Stunned" }
local PRIORITY = {
	Idle = Enum.AnimationPriority.Idle,
	Walk = Enum.AnimationPriority.Movement,
	Attack = Enum.AnimationPriority.Action,
	Hit = Enum.AnimationPriority.Action,
	Stunned = Enum.AnimationPriority.Idle,
}

-- The bones' rest frames in body space (every Transform back to identity first).
local restRot: { [string]: CFrame } = {}
local restPos: { [string]: Vector3 } = {}
for _, d in body:GetDescendants() do
	if d:IsA("Bone") then
		d.Transform = CFrame.identity
	end
end
for _, d in body:GetDescendants() do
	if d:IsA("Bone") then
		local here = body.CFrame:ToObjectSpace(d.WorldCFrame)
		restRot[d.Name] = here.Rotation
		restPos[d.Name] = here.Position
	end
end

local function turn(q: { number }): CFrame
	-- A proper rotation maps a quaternion's axis like a vector.
	return CFrame.new(0, 0, 0, -q[2], q[4], q[3], q[1])
end
local function move(v: { number }): Vector3
	return Vector3.new(-v[1], v[3], v[2]) * STUDS
end

local saves = grinch:FindFirstChild("AnimSaves") or Instance.new("Folder")
saves.Name = "AnimSaves"
saves.Parent = grinch
for _, clip in CLIPS do
	local data: any = HttpService:JSONDecode(HttpService:GetAsync("http://127.0.0.1:8777/" .. clip .. ".json"))
	local seq = Instance.new("KeyframeSequence")
	seq.Name = "Grinch_" .. clip
	seq.Loop = data.loop
	seq.Priority = PRIORITY[clip]
	for _, key in data.keys do
		local frame = Instance.new("Keyframe")
		frame.Time = key.t
		local rootPose = Instance.new("Pose")
		rootPose.Name = body.Name
		rootPose.Weight = 0
		rootPose.Parent = frame
		local function visit(bone: Bone, parentAnim: CFrame, parentPose: Pose)
			local q = key.q[bone.Name]
			local base = parentAnim * bone.CFrame
			local target = base
			if q then
				local position = if bone.Name == "mixamorig:Hips" then restPos[bone.Name] + move(key.hips) else base.Position
				target = CFrame.new(position) * turn(q) * restRot[bone.Name]
			end
			local pose = Instance.new("Pose")
			pose.Name = bone.Name
			pose.CFrame = base:Inverse() * target
			pose.Parent = parentPose
			for _, child in bone:GetChildren() do
				if child:IsA("Bone") then
					visit(child, target, pose)
				end
			end
		end
		for _, child in body:GetChildren() do
			if child:IsA("Bone") then
				visit(child, CFrame.identity, rootPose)
			end
		end
		frame.Parent = seq
	end
	local old = saves:FindFirstChild(seq.Name)
	if old then
		old:Destroy()
	end
	seq.Parent = saves
end
