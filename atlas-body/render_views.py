#!/usr/bin/env python3
"""
Render Atlas from multiple angles
"""
import bpy
import math

# Set render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Get camera
camera = bpy.data.objects['Camera']

# FRONT VIEW
camera.location = (0, -8, 2.5)
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera
bpy.context.scene.render.filepath = "/Users/atlasbuilds/clawd/atlas-body/atlas_front.png"
bpy.ops.render.render(write_still=True)
print("✅ Front view rendered")

# SIDE VIEW (Right)
camera.location = (8, 0, 2.5)
camera.rotation_euler = (math.radians(90), 0, math.radians(90))
bpy.context.scene.render.filepath = "/Users/atlasbuilds/clawd/atlas-body/atlas_side.png"
bpy.ops.render.render(write_still=True)
print("✅ Side view rendered")

# TOP VIEW
camera.location = (0, 0, 10)
camera.rotation_euler = (0, 0, 0)
bpy.context.scene.render.filepath = "/Users/atlasbuilds/clawd/atlas-body/atlas_top.png"
bpy.ops.render.render(write_still=True)
print("✅ Top view rendered")

print("\n🤖 All views complete!")
