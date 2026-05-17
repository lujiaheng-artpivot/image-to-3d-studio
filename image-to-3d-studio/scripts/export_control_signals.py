"""
AI 视频控制信号一键导出脚本
在 Blender 中运行，从当前场景导出深度图、法线图、mask、多角度参考帧、运镜视频
"""
import bpy
import os
import math

def export_control_signals(output_dir="./control_signals", num_angles=8, video_seconds=5, fps=24):
    """一键导出完整控制信号包"""
    
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene
    
    # 保存原始设置
    orig_engine = scene.render.engine
    orig_res_x = scene.render.resolution_x
    orig_res_y = scene.render.resolution_y
    orig_filepath = scene.render.filepath
    
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    
    # ===== 1. 深度图 =====
    print("[1/5] 导出深度图...")
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.use_nodes = True
    tree = scene.node_tree
    
    # 启用 Z pass
    bpy.context.view_layer.use_pass_z = True
    
    # 设置合成节点导出深度
    nodes = tree.nodes
    links = tree.links
    
    rl = None
    for n in nodes:
        if n.type == 'R_LAYERS':
            rl = n
            break
    if not rl:
        rl = nodes.new('CompositorNodeRLayers')
    
    normalize = nodes.new('CompositorNodeNormalize')
    depth_out = nodes.new('CompositorNodeOutputFile')
    depth_out.base_path = os.path.join(output_dir, "depth")
    depth_out.format.file_format = 'PNG'
    depth_out.format.color_mode = 'BW'
    
    links.new(rl.outputs['Depth'], normalize.inputs[0])
    links.new(normalize.outputs[0], depth_out.inputs[0])
    
    scene.render.filepath = os.path.join(output_dir, "depth", "depth_")
    bpy.ops.render.render(write_still=False)
    
    # 清理临时节点
    nodes.remove(normalize)
    nodes.remove(depth_out)
    
    # ===== 2. 法线图 =====
    print("[2/5] 导出法线图...")
    bpy.context.view_layer.use_pass_normal = True
    
    normal_out = nodes.new('CompositorNodeOutputFile')
    normal_out.base_path = os.path.join(output_dir, "normal")
    normal_out.format.file_format = 'PNG'
    normal_out.format.color_mode = 'RGB'
    
    links.new(rl.outputs['Normal'], normal_out.inputs[0])
    
    bpy.ops.render.render(write_still=False)
    nodes.remove(normal_out)
    
    # ===== 3. 物体 Mask =====
    print("[3/5] 导出物体遮挡 mask...")
    # 给每个物体分配不同的 pass index
    for i, obj in enumerate(bpy.data.objects):
        if obj.type == 'MESH':
            obj.pass_index = i + 1
    
    bpy.context.view_layer.use_pass_object_index = True
    
    idx_out = nodes.new('CompositorNodeOutputFile')
    idx_out.base_path = os.path.join(output_dir, "mask")
    idx_out.format.file_format = 'PNG'
    
    links.new(rl.outputs['IndexOB'], idx_out.inputs[0])
    
    bpy.ops.render.render(write_still=False)
    nodes.remove(idx_out)
    
    # ===== 4. 多角度参考帧 =====
    print(f"[4/5] 渲染 {num_angles} 个角度参考帧...")
    scene.cycles.samples = 128
    
    # 找到场景中心
    center = (0, 0, 0)
    radius = 5.0  # 相机到中心的距离
    
    cam = scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("RefCam")
        cam = bpy.data.objects.new("RefCam", cam_data)
        scene.collection.objects.link(cam)
        scene.camera = cam
    
    ref_dir = os.path.join(output_dir, "reference_frames")
    os.makedirs(ref_dir, exist_ok=True)
    
    for i in range(num_angles):
        angle = (2 * math.pi * i) / num_angles
        cam.location = (
            center[0] + radius * math.cos(angle),
            center[1] + radius * math.sin(angle),
            center[2] + 1.5  # 略高于地面
        )
        # 看向中心
        direction = (center[0] - cam.location[0], 
                     center[1] - cam.location[1], 
                     center[2] - cam.location[2])
        cam.rotation_euler = (
            math.atan2(math.sqrt(direction[0]**2 + direction[1]**2), -direction[2]),
            0,
            math.atan2(direction[0], -direction[1])
        )
        
        scene.render.filepath = os.path.join(ref_dir, f"ref_angle_{i:02d}.png")
        bpy.ops.render.render(write_still=True)
    
    # ===== 5. 相机轨迹视频 =====
    print(f"[5/5] 渲染 {video_seconds}s 运镜视频...")
    scene.render.fps = fps
    total_frames = video_seconds * fps
    scene.frame_start = 1
    scene.frame_end = total_frames
    
    # 创建圆形路径
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius)
    path = bpy.context.active_object
    path.name = "CameraPath"
    
    # 相机跟随路径
    constraint = cam.constraints.new(type='FOLLOW_PATH')
    constraint.target = path
    constraint.use_curve_follow = True
    
    # 动画
    override = {'constraint': constraint}
    path.data.path_duration = total_frames
    
    scene.render.filepath = os.path.join(output_dir, "camera_trajectory", "traj_")
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(output_dir, "camera_trajectory.mp4")
    
    bpy.ops.render.render(animation=True)
    
    # 恢复设置
    scene.render.engine = orig_engine
    scene.render.resolution_x = orig_res_x
    scene.render.resolution_y = orig_res_y
    scene.render.filepath = orig_filepath
    
    print(f"\n完成！所有控制信号已导出到 {output_dir}/")
    print(f"  depth/     - 深度图")
    print(f"  normal/    - 法线图")
    print(f"  mask/      - 物体遮挡 mask")
    print(f"  reference_frames/ - {num_angles} 个角度参考帧")
    print(f"  camera_trajectory.mp4 - {video_seconds}s 运镜视频")


if __name__ == "__main__":
    export_control_signals()
