#!/usr/bin/env python3
"""
Save Atlas model and render preview images
"""
import bpy
import os

# Save the blend file
blend_path = "/Users/atlasbuilds/clawd/atlas-body/atlas_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"✅ Saved: {blend_path}")

# Set up render settings for quick preview
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

# Render from current camera view
output_path = "/Users/atlasbuilds/clawd/atlas-body/atlas_render.png"
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
print(f"✅ Rendered: {output_path}")

print("\n🤖 ATLAS V1 COMPLETE!")
print(f"📁 Files saved to: /Users/atlasbuilds/clawd/atlas-body/")
