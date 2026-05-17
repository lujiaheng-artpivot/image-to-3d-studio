# 赛璐珞 / Cel-Shading Blender 节点设置

## 核心原理

传统赛璐珞动画的视觉特征：平涂色块 + 硬边阴影 + 描线轮廓。
在 Blender 里通过 Shader to RGB 节点把连续光照离散化，再用 Freestyle 加描边。

## 步骤一：材质节点（每个物体都要改）

```python
import bpy

def setup_cel_material(obj, base_color=(0.8, 0.3, 0.2, 1.0), shadow_color=(0.4, 0.15, 0.1, 1.0)):
    """为物体设置赛璐珞材质"""
    mat = bpy.data.materials.new(name=f"Cel_{obj.name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Diffuse BSDF
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = base_color
    diffuse.location = (-400, 0)

    # Shader to RGB（关键节点：把光照信息转成颜色数据）
    shader_to_rgb = nodes.new('ShaderNodeShaderToRGB')
    shader_to_rgb.location = (-200, 0)

    # ColorRamp（离散化：2 段 = 亮面 + 阴影）
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'  # 硬切，不渐变
    ramp.color_ramp.elements[0].color = shadow_color
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].color = base_color
    ramp.color_ramp.elements[1].position = 0.4  # 阴影分界线位置

    # 输出
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)

    links.new(diffuse.outputs['BSDF'], shader_to_rgb.inputs['Shader'])
    links.new(shader_to_rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])

    # 应用材质
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# 批量应用到场景所有网格物体
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        setup_cel_material(obj)
```

## 步骤二：Freestyle 描边设置

```python
import bpy

scene = bpy.context.scene
# 启用 Freestyle
scene.render.use_freestyle = True
# 确保有 Freestyle 线集
view_layer = bpy.context.view_layer
view_layer.use_freestyle = True

if not view_layer.freestyle_settings.linesets:
    view_layer.freestyle_settings.linesets.new("CelOutline")

lineset = view_layer.freestyle_settings.linesets[0]
lineset.linestyle.thickness = 1.5          # 线宽
lineset.linestyle.color = (0.15, 0.1, 0.05)  # 深棕色描线

# 启用轮廓和边界检测
lineset.select_silhouette = True
lineset.select_border = True
lineset.select_crease = True
lineset.select_edge_mark = False
```

## 步骤三：渲染设置

```python
import bpy

scene = bpy.context.scene
# 必须用 EEVEE（Shader to RGB 只在 EEVEE 下工作）
scene.render.engine = 'BLENDER_EEVEE'

# 关闭环境光遮蔽（赛璐珞不需要）
scene.eevee.use_gtao = False

# 阴影设置：硬边
scene.eevee.shadow_cube_size = '512'
scene.eevee.use_shadow_high_bitdepth = False

# 输出
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
```

## 色阶数量调整

- **2 段**（亮面+阴影）：最经典的赛璐珞感，硬朗
- **3 段**（高光+亮面+阴影）：稍微丰富，加一个高光色阶
- **4 段**：接近手绘动画的细腻度

调整方法：在 ColorRamp 节点中增加色标数量，保持 `CONSTANT` 插值。
