#!/usr/bin/env python3
"""
Final render with studio lighting and Cycles
"""
import bpy
import math

# ============================================================================
# RENDER SETTINGS - Cycles Photorealistic
# ============================================================================

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128  # Good quality, reasonable time
bpy.context.scene.render.resolution_x = 2560
bpy.context.scene.render.resolution_y = 1440
bpy.context.scene.cycles.use_denoising = True

print("✅ Render engine: Cycles (128 samples)")

# ============================================================================
# WORLD LIGHTING
# ============================================================================

world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
    bg_node.inputs['Strength'].default_value = 0.5

print("✅ World lighting configured")

# ============================================================================
# STUDIO LIGHTS (3-point + rim)
# ============================================================================

# Clear existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Key light (main)
bpy.ops.object.light_add(type='AREA', location=(4, -4, 6))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 400
key_light.data.size = 3
key_light.rotation_euler = (math.radians(55), 0, math.radians(40))

# Fill light (soft shadows)
bpy.ops.object.light_add(type='AREA', location=(-3, -2, 4))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 150
fill_light.data.size = 4

# Rim light (edge definition)
bpy.ops.object.light_add(type='AREA', location=(0, 6, 3))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 250
rim_light.data.size = 2

# Ground bounce
bpy.ops.object.light_add(type='AREA', location=(0, 0, -1))
ground_light = bpy.context.active_object
ground_light.name = "Ground_Light"
ground_light.data.energy = 80
ground_light.data.size = 6

print("✅ Studio lighting (4 lights)")

# ============================================================================
# GROUND PLANE (Reflective)
# ============================================================================

# Clear existing planes
for obj in bpy.data.objects:
    if obj.name.startswith("Ground") and obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Reflective material
mat_ground = bpy.data.materials.new(name="Ground_Material")
mat_ground.use_nodes = True
bsdf = mat_ground.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.15
ground.data.materials.append(mat_ground)

print("✅ Ground plane added")

# ============================================================================
# CAMERAS
# ============================================================================

# Clear existing cameras
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Hero camera (3/4 view)
bpy.ops.object.camera_add(location=(5, -5, 3.5))
cam_hero = bpy.context.active_object
cam_hero.name = "Camera_Hero"
cam_hero.rotation_euler = (math.radians(70), 0, math.radians(45))
cam_hero.data.lens = 50

# Set as active
bpy.context.scene.camera = cam_hero

print("✅ Camera positioned")

# ============================================================================
# RENDER
# ============================================================================

print("\n" + "="*60)
print("🎬 RENDERING ATLAS FINAL...")
print("="*60)

output_path = "/Users/atlasbuilds/clawd/atlas-body/atlas_final_production.png"
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

print(f"✅ Render complete: {output_path}")
print("="*60)
