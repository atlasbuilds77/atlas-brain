#!/usr/bin/env python3
"""
Head closeup render - show LED eyes and details
"""
import bpy
import math

# Use existing scene setup
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 2560
bpy.context.scene.render.resolution_y = 1440
bpy.context.scene.cycles.use_denoising = True

# Remove existing cameras
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create closeup camera focused on head
bpy.ops.object.camera_add(location=(1.2, -2.5, 2.9))
cam_head = bpy.context.active_object
cam_head.name = "Camera_Head_Closeup"
cam_head.rotation_euler = (math.radians(85), 0, math.radians(25))
cam_head.data.lens = 85  # Telephoto for closeup

# Set as active camera
bpy.context.scene.camera = cam_head

print("🎬 Rendering head closeup...")

# Render
output_path = "/Users/atlasbuilds/clawd/atlas-body/atlas_head_closeup.png"
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

print(f"✅ Head closeup complete: {output_path}")
