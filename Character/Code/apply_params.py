import bpy
import json
from mathutils import Euler
import os

# Config
blend_file = r"F:\_Self-project\ITSC\Character\Code\demo_vroid_avatar.blend"
json_params = r"F:\_Self-project\ITSC\Character\Code\params_sample.json"
mapping_file = r"F:\_Self-project\ITSC\Character\Code\mapping.json"
fps = 30
output_path = r"F:\_Self-project\ITSC\Character\Code\output_animation.mp4"

# Load mapping
with open(mapping_file, 'r') as f:
    mapping = json.load(f)

# Load params
with open(json_params, 'r') as f:
    params_data = json.load(f)

# Get armature and mesh
armature = bpy.data.objects['Armature']
mesh = bpy.data.objects['Face']

# Clear animation
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.anim.keyframe_clear_v3d()

# Apply keyframes
current_frame = 1
for frame_data in params_data:
    bpy.context.scene.frame_set(current_frame)
    
    # Apply bones (using mapping)
    bones_data = frame_data.get("bones", {})
    for param_name, props in bones_data.items():
        if param_name in mapping["bones"]:
            bone_info = mapping["bones"][param_name]
            bone_name = bone_info["target"]
            axis = bone_info["axis"]
            if bone_name in armature.pose.bones:
                bone = armature.pose.bones[bone_name]
                rot = bone.rotation_euler
                axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
                rot[axis_idx] = props.get("rotation", [0])[0] * 3.14159 / 180  # Deg to rad
                bone.rotation_euler = rot
                bone.keyframe_insert(data_path="rotation_euler", frame=current_frame)
                # Set Bezier interpolation
                for fcurve in bone.id_data.animation_data.action.fcurves:
                    if fcurve.data_path == f"pose.bones[\"{bone_name}\"].rotation_euler":
                        for kp in fcurve.keyframe_points:
                            if kp.co.x == current_frame:
                                kp.interpolation = 'BEZIER'
    
    # Apply shapes (using mapping)
    shapes_data = frame_data.get("shapes", {})
    for param_name, value in shapes_data.items():
        if param_name in mapping["shapes"]:
            shape_info = mapping["shapes"][param_name]
            shape_name = shape_info["target"]
            if shape_name in mesh.data.shape_keys.key_blocks:
                key_block = mesh.data.shape_keys.key_blocks[shape_name]
                key_block.value = value
                key_block.keyframe_insert(data_path="value", frame=current_frame)
                # Set Bezier interpolation
                for fcurve in mesh.data.shape_keys.animation_data.action.fcurves:
                    if fcurve.data_path == f"key_blocks[\"{shape_name}\"].value":
                        for kp in fcurve.keyframe_points:
                            if kp.co.x == current_frame:
                                kp.interpolation = 'BEZIER'
    
    current_frame += int(fps * frame_data.get("duration", 1/fps))

bpy.context.scene.frame_end = current_frame - 1

# Render (Eevee Next, 1080p)
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.render.fps = fps
bpy.context.scene.render.filepath = output_path
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.ops.render.render(animation=True)

print(f"Animation applied! Render at {output_path}")