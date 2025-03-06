import bpy
import os
import mathutils
import math
import json

# 清空场景（删除所有对象）
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 添加相机
cam_json = "cam.json"
with open(cam_json) as f:
    params = json.load(f)
camera_data = bpy.data.cameras.new(name="CustomCamera")
camera_object = bpy.data.objects.new("CustomCamera", camera_data)
bpy.context.scene.collection.objects.link(camera_object)

# 设置相机的位置
camera_object.location = params["position"]

# 计算相机的旋转
target = mathutils.Vector(params["target"])
position = mathutils.Vector(params["position"])
direction = target - position
rotation = direction.to_track_quat('-Z', 'Y')  # 设置相机朝向目标
camera_object.rotation_mode = 'QUATERNION'
camera_object.rotation_quaternion = rotation

# 设置相机的视场角（FOV）
if "fov" in params:
    fov = params["fov"]
else:
    fov = 45

vertical_fov_radians = math.radians(fov)
aspect_ratio = 16 / 9  # 相机宽高比

# 计算水平 FOV (blender中是垂直fov 与 sketchFab中是水平fov 需要换算)
horizontal_fov_radians = 2 * math.atan(math.tan(vertical_fov_radians / 2) * aspect_ratio)
camera_data.lens_unit = 'FOV'
camera_data.angle = math.radians(math.degrees(horizontal_fov_radians))

# 设置裁剪范围
if "nearFarRatio" in params:
    camera_data.clip_start = params["nearFarRatio"]
camera_data.clip_end = 1000000

# 设置作渲染用
bpy.context.scene.camera = camera_object

# 加载 .obj 文件
obj_path = "a.obj"  # 替换成你的 .obj 路径
bpy.ops.wm.obj_import(filepath=obj_path)

# 设置渲染参数
bpy.context.scene.render.engine = 'BLENDER_EEVEE'  # 使用 Cycles 渲染器（可改为 'BLENDER_EEVEE'）
bpy.context.scene.eevee.taa_render_samples = 1  # 最终渲染时的采样数
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.filepath = "a.png"  # 输出 PNG 路径
bpy.context.scene.render.image_settings.file_format = 'PNG'  # 输出格式为 PNG
bpy.context.scene.render.image_settings.color_mode = 'RGBA'
with open("resolution.txt", "r") as f:
    a = f.readlines()
bpy.context.scene.render.resolution_x = int(a[0])  # 设置分辨率
bpy.context.scene.render.resolution_y = int(a[1])

# 运行渲染
bpy.ops.render.render(write_still=True)
