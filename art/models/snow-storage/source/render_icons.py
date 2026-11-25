"""Render five existing SnowStorage meshes as isolated 512 px inventory icons."""
from pathlib import Path

import bpy
from mathutils import Vector


ICONS = {
    'dustpan': ('Dustpan_Body', (.65, -1, .86), -.96),
    'chip-packet': ('ChipPacket_Body', (.36, -1, .40), -.58),
    'plastic-bag': ('PlasticCarrier_Body', (.68, -1, .69), -.81),
    'metal-bucket': ('MetalPail_Body', (.43, -1, .79), -.63),
    'burlap-sack': ('BurlapSack_Body', (.41, -1, .69), -.69),
}
SIZE = 512


def softbox(scene, name, position, energy, width, color):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy = energy
    light.shape = 'DISK'
    light.size = width
    light.color = color
    obj = bpy.data.objects.new(name, light)
    scene.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (-obj.location).to_track_quat('-Z', 'Y').to_euler()


def frame(camera, obj, direction):
    points = [vertex.co for vertex in obj.data.vertices]
    # Fit the visible projection instead of the eight corners of the bounding box.
    rotation = Vector(direction).to_track_quat('Z', 'Y')
    inverse = rotation.inverted()
    projected = [inverse @ point for point in points]
    spans = [(min(p[i] for p in projected), max(p[i] for p in projected)) for i in range(3)]
    center = rotation @ Vector([(low + high) / 2 for low, high in spans])
    camera.location = center + rotation @ Vector((0, 0, 5))
    camera.rotation_euler = rotation.to_euler()
    camera.data.ortho_scale = max(high - low for low, high in spans[:2]) / .84


def render():
    source = bpy.data.collections['SnowStorage']
    scene = bpy.data.scenes.new('Snow storage inventory cards')
    bpy.context.window.scene = scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = SIZE
    scene.render.resolution_y = SIZE
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'

    scene.world = bpy.data.worlds.new('Diffuse studio sky')
    scene.world.use_nodes = True
    sky = scene.world.node_tree.nodes['Background']
    sky.inputs['Color'].default_value = (.56, .70, .89, 1)
    sky.inputs['Strength'].default_value = .45
    softbox(scene, 'Warm key', (-1.45, -1.8, 2.25), 176, 1.18, (1, .92, .79))
    softbox(scene, 'Cool front fill', (1.6, -1.15, .95), 47, 1.5, (.79, .89, 1))
    softbox(scene, 'Edge light', (.44, 1.25, 1.73), 114, .92, (.82, .92, 1))

    data = bpy.data.cameras.new('Icon projection')
    data.type = 'ORTHO'
    camera = bpy.data.objects.new('Icon projection', data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    out = Path(__file__).resolve().parent.parent / 'icons'
    out.mkdir(exist_ok=True)
    for name, (mesh_name, direction, exposure) in ICONS.items():
        obj = bpy.data.objects.new(name, source.objects[mesh_name].data)
        scene.collection.objects.link(obj)
        frame(camera, obj, direction)
        scene.view_settings.exposure = exposure
        scene.render.filepath = str(out / f'{name}.png')
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(obj, do_unlink=True)


render()
