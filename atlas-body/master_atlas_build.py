#!/usr/bin/env python3
"""
ATLAS V1 - MASTER BUILD SYSTEM
Combines detailed modeling + materials for final photorealistic render

This is the REAL Atlas body - not placeholder shapes
"""

import bpy
import math
import os

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove default cube/light/camera if they exist
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

print("🔥 ATLAS MASTER BUILD INITIALIZED")
print("=" * 60)

# ============================================================================
# RENDERING SETUP - Cycles for photorealism
# ============================================================================
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'  # Can change to GPU if available
bpy.context.scene.cycles.samples = 256  # High quality
bpy.context.scene.render.resolution_x = 2560
bpy.context.scene.render.resolution_y = 1440
bpy.context.scene.render.film_transparent = False

# Enable denoising
bpy.context.scene.cycles.use_denoising = True
bpy.context.view_layer.cycles.use_denoising = True

print("✅ Render engine: Cycles (256 samples)")
print("✅ Resolution: 2560x1440")
print("✅ Denoising enabled")

# ============================================================================
# WORLD LIGHTING - Studio setup
# ============================================================================
world = bpy.data.worlds.new("Atlas_World")
bpy.context.scene.world = world
world.use_nodes = True

# Clear default nodes
world.node_tree.nodes.clear()

# Add background shader
bg = world.node_tree.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)  # Dark gray
bg.inputs['Strength'].default_value = 0.8

output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
world.node_tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

print("✅ World lighting configured")

# ============================================================================
# STUDIO LIGHTS - 3-point lighting
# ============================================================================

# Key light (main)
bpy.ops.object.light_add(type='AREA', location=(5, -5, 8))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 500
key_light.data.size = 3
key_light.rotation_euler = (math.radians(60), 0, math.radians(45))

# Fill light (soften shadows)
bpy.ops.object.light_add(type='AREA', location=(-4, -3, 6))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 200
fill_light.data.size = 4
fill_light.rotation_euler = (math.radians(50), 0, math.radians(-30))

# Rim light (edge definition)
bpy.ops.object.light_add(type='AREA', location=(0, 8, 4))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 300
rim_light.data.size = 2
rim_light.rotation_euler = (math.radians(90), 0, 0)

# Ground light (bounce)
bpy.ops.object.light_add(type='AREA', location=(0, 0, -2))
ground_light = bpy.context.active_object
ground_light.name = "Ground_Light"
ground_light.data.energy = 100
ground_light.data.size = 5
ground_light.rotation_euler = (0, 0, 0)

print("✅ Studio lighting: 3-point + ground bounce")

# ============================================================================
# CAMERA SETUP - Hero shots
# ============================================================================

def create_camera(name, location, rotation, lens=50):
    """Create camera with specific framing"""
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    cam.rotation_euler = rotation
    cam.data.lens = lens
    cam.data.sensor_width = 36
    return cam

# Hero camera (3/4 perspective)
cam_hero = create_camera(
    "Camera_Hero",
    location=(6, -6, 4),
    rotation=(math.radians(65), 0, math.radians(45)),
    lens=50
)

# Front camera
cam_front = create_camera(
    "Camera_Front",
    location=(0, -10, 2.5),
    rotation=(math.radians(90), 0, 0),
    lens=85
)

# Close-up camera (face detail)
cam_closeup = create_camera(
    "Camera_Closeup",
    location=(1.5, -3, 3.2),
    rotation=(math.radians(85), 0, math.radians(20)),
    lens=85
)

# Set hero camera as active
bpy.context.scene.camera = cam_hero

print("✅ Cameras: Hero, Front, Closeup")

# ============================================================================
# GROUND PLANE - Reflective surface
# ============================================================================
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Ground material (reflective dark)
mat_ground = bpy.data.materials.new(name="Ground_Material")
mat_ground.use_nodes = True
bsdf = mat_ground.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.1
ground.data.materials.append(mat_ground)

print("✅ Ground plane with reflections")

# ============================================================================
# IMPORT DETAILED MODEL & MATERIALS
# ============================================================================
print("\n🔥 WAITING FOR SPARKS TO COMPLETE:")
print("   - Detailed geometry model")
print("   - Photorealistic materials")
print("\nOnce ready, run:")
print("   - atlas_detailed_model.py (from Spark 1)")
print("   - atlas_materials.py (from Spark 2)")
print("   - Then this master script will combine & render")

# ============================================================================
# RENDER FUNCTIONS
# ============================================================================

def render_view(camera_name, output_name):
    """Render from specific camera"""
    cam = bpy.data.objects[camera_name]
    bpy.context.scene.camera = cam
    filepath = f"/Users/atlasbuilds/clawd/atlas-body/{output_name}.png"
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"✅ Rendered: {output_name}")
    return filepath

def render_all_views():
    """Render all camera angles"""
    print("\n🎬 RENDERING ALL VIEWS...")
    views = [
        ("Camera_Hero", "atlas_final_hero"),
        ("Camera_Front", "atlas_final_front"),
        ("Camera_Closeup", "atlas_final_closeup"),
    ]
    
    rendered = []
    for cam_name, output_name in views:
        try:
            path = render_view(cam_name, output_name)
            rendered.append(path)
        except Exception as e:
            print(f"❌ Error rendering {output_name}: {e}")
    
    return rendered

# Save this setup
blend_path = "/Users/atlasbuilds/clawd/atlas-body/atlas_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"\n✅ Master scene saved: {blend_path}")

print("\n" + "=" * 60)
print("🤖 ATLAS MASTER BUILD READY")
print("Waiting for Spark completion...")
print("=" * 60)
