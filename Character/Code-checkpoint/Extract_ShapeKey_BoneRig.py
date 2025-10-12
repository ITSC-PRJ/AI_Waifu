import bpy
import json
import os

# Config
blend_file = r"F:\_Self-project\ITSC\Character\Code\demo_vroid_avatar.blend"  # Đường dẫn tuyệt đối đến .blend
output_json = r"F:\_Self-project\ITSC\Character\Code\shapes_and_bones.json"  # Đường dẫn tuyệt đối đến output

# Đảm bảo thư mục tồn tại
output_dir = os.path.dirname(output_json)
if not os.path.exists(output_dir):
    print(f"Error: Thư mục {output_dir} không tồn tại!")
    exit(1)

# Hàm lấy danh sách shape keys và bones
def extract_shapes_and_bones():
    # Tìm armature và mesh
    armature = None
    mesh = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
        if obj.type == 'MESH' and obj.data.shape_keys:
            mesh = obj
    
    if not armature or not mesh:
        print("Error: Không tìm thấy Armature hoặc Mesh với shape keys!")
        return None

    # Lấy danh sách shape keys
    shape_keys = []
    if mesh.data.shape_keys:
        for key in mesh.data.shape_keys.key_blocks:
            shape_keys.append({
                "name": key.name,
                "value_range": [key.slider_min, key.slider_max]
            })

    # Lấy danh sách bones
    bones = []
    for bone in armature.data.bones:
        bones.append({
            "name": bone.name,
            "parent": bone.parent.name if bone.parent else None,
            "head": list(bone.head_local),
            "is_deform": bone.use_deform
        })

    return {
        "armature_name": armature.name,
        "mesh_name": mesh.name,
        "shape_keys": shape_keys,
        "bones": bones
    }

# Chạy và lưu kết quả
try:
    result = extract_shapes_and_bones()
    if result:
        # In ra console để kiểm tra
        print("=== Shape Keys ===")
        for sk in result["shape_keys"]:
            print(f"Shape Key: {sk['name']}, Range: {sk['value_range']}")
        
        print("\n=== Bones ===")
        for bone in result["bones"]:
            print(f"Bone: {bone['name']}, Parent: {bone['parent']}, Deform: {bone['is_deform']}")

        # Lưu thành JSON
        with open(output_json, 'w') as f:
            json.dump(result, f, indent=4)
        print(f"\nDanh sách đã lưu vào: {output_json}")
    else:
        print("Failed to extract shapes and bones!")
except PermissionError as e:
    print(f"PermissionError: Không thể ghi file {output_json}. Kiểm tra quyền truy cập hoặc đóng chương trình đang dùng file.")
except Exception as e:
    print(f"Error: {str(e)}")