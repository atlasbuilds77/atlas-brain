#!/usr/bin/env python3
"""
ATLAS V1 - Desktop Robot Body Generator
Generates a buildable robot design in Blender

Design: Titan builder aesthetic
- Tracked base (stable, powerful)
- Humanoid upper body with arms
- LED matrix head
- Industrial, honest materials
- Actually buildable with real hardware
"""

import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_material(name, color):
    """Create a simple material with given color"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.3
    return mat

# Materials
mat_body = create_material("Body", (0.2, 0.2, 0.25))  # Dark gray
mat_accent = create_material("Accent", (1.0, 0.3, 0.0))  # Orange (Atlas energy)
mat_track = create_material("Track", (0.1, 0.1, 0.12))  # Almost black
mat_eyes = create_material("Eyes", (0.0, 0.8, 1.0))  # Cyan LEDs

# === BASE PLATFORM (Tracked) ===
# Main chassis
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
chassis = bpy.context.active_object
chassis.name = "Chassis"
chassis.scale = (2.0, 1.5, 0.3)  # Wide, stable base
chassis.data.materials.append(mat_body)

# Left track
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.1, 0, 0.3))
left_track = bpy.context.active_object
left_track.name = "Track_Left"
left_track.scale = (0.15, 1.8, 0.5)
left_track.data.materials.append(mat_track)

# Right track
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.1, 0, 0.3))
right_track = bpy.context.active_object
right_track.name = "Track_Right"
right_track.scale = (0.15, 1.8, 0.5)
right_track.data.materials.append(mat_track)

# === TORSO ===
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
torso = bpy.context.active_object
torso.name = "Torso"
torso.scale = (1.2, 0.8, 1.0)
torso.data.materials.append(mat_body)

# Torso accent stripe
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.82, 1.5))
stripe = bpy.context.active_object
stripe.name = "Stripe"
stripe.scale = (1.22, 0.03, 1.02)
stripe.data.materials.append(mat_accent)

# === HEAD ===
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.8))
head = bpy.context.active_object
head.name = "Head"
head.scale = (0.9, 0.7, 0.6)
head.data.materials.append(mat_body)

# LED Eyes (left)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.3, 0.72, 2.85))
eye_left = bpy.context.active_object
eye_left.name = "Eye_Left"
eye_left.scale = (0.25, 0.05, 0.15)
eye_left.data.materials.append(mat_eyes)

# LED Eyes (right)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.3, 0.72, 2.85))
eye_right = bpy.context.active_object
eye_right.name = "Eye_Right"
eye_right.scale = (0.25, 0.05, 0.15)
eye_right.data.materials.append(mat_eyes)

# === LEFT ARM ===
# Shoulder
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(-1.3, 0, 2.2))
shoulder_left = bpy.context.active_object
shoulder_left.name = "Shoulder_Left"
shoulder_left.rotation_euler = (0, math.radians(90), 0)
shoulder_left.data.materials.append(mat_accent)

# Upper arm
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 0, 1.7))
upper_arm_left = bpy.context.active_object
upper_arm_left.name = "UpperArm_Left"
upper_arm_left.scale = (0.15, 0.15, 0.6)
upper_arm_left.data.materials.append(mat_body)

# Elbow joint
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.2, location=(-1.6, 0, 1.1))
elbow_left = bpy.context.active_object
elbow_left.name = "Elbow_Left"
elbow_left.rotation_euler = (0, math.radians(90), 0)
elbow_left.data.materials.append(mat_accent)

# Forearm
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 0, 0.6))
forearm_left = bpy.context.active_object
forearm_left.name = "Forearm_Left"
forearm_left.scale = (0.12, 0.12, 0.5)
forearm_left.data.materials.append(mat_body)

# Gripper base
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 0, 0.2))
gripper_base_left = bpy.context.active_object
gripper_base_left.name = "Gripper_Base_Left"
gripper_base_left.scale = (0.15, 0.15, 0.1)
gripper_base_left.data.materials.append(mat_body)

# === RIGHT ARM (mirror of left) ===
# Shoulder
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(1.3, 0, 2.2))
shoulder_right = bpy.context.active_object
shoulder_right.name = "Shoulder_Right"
shoulder_right.rotation_euler = (0, math.radians(90), 0)
shoulder_right.data.materials.append(mat_accent)

# Upper arm
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.6, 0, 1.7))
upper_arm_right = bpy.context.active_object
upper_arm_right.name = "UpperArm_Right"
upper_arm_right.scale = (0.15, 0.15, 0.6)
upper_arm_right.data.materials.append(mat_body)

# Elbow joint
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.2, location=(1.6, 0, 1.1))
elbow_right = bpy.context.active_object
elbow_right.name = "Elbow_Right"
elbow_right.rotation_euler = (0, math.radians(90), 0)
elbow_right.data.materials.append(mat_accent)

# Forearm
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.6, 0, 0.6))
forearm_right = bpy.context.active_object
forearm_right.name = "Forearm_Right"
forearm_right.scale = (0.12, 0.12, 0.5)
forearm_right.data.materials.append(mat_body)

# Gripper base
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.6, 0, 0.2))
gripper_base_right = bpy.context.active_object
gripper_base_right.name = "Gripper_Base_Right"
gripper_base_right.scale = (0.15, 0.15, 0.1)
gripper_base_right.data.materials.append(mat_body)

# === LIGHTING ===
# Add lights for better visualization
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0

bpy.ops.object.light_add(type='AREA', location=(-3, -3, 5))
fill = bpy.context.active_object
fill.data.energy = 100

# === CAMERA ===
bpy.ops.object.camera_add(location=(6, -6, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

# Set viewport shading to solid with MatCap
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'
                space.shading.light = 'MATCAP'

print("✅ ATLAS V1 body generated!")
print("📐 Dimensions: ~18\" tall (scaled 1 unit = 6 inches)")
print("🎨 Materials: Industrial gray body, orange accents, cyan LED eyes")
print("💾 Save as: atlas_v1.blend")
