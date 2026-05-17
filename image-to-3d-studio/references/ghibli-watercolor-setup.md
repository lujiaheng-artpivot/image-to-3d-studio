# 吉卜力水彩风 Blender 节点设置

## 核心差异（vs 赛璐珞）

吉卜力风格不是硬切色阶，而是柔和渐变 + 偏色阴影 + 手绘线条 + 纸张纹理。
关键词：温暖、柔和、呼吸感、水彩渗透。

## 步骤一：材质节点（柔和渐变版）

```python
import bpy

def setup_ghibli_material(obj, base_color=(0.85, 0.75, 0.6, 1.0)):
    """吉卜力风格材质：柔和渐变 + 偏色阴影"""
    mat = bpy.data.materials.new(name=f"Ghibli_{obj.name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Diffuse
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = base_color
    diffuse.location = (-400, 0)

    # Shader to RGB
    shader_to_rgb = nodes.new('ShaderNodeShaderToRGB')
    shader_to_rgb.location = (-200, 0)

    # ColorRamp：3 段渐变（注意用 LINEAR 不是 CONSTANT）
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 0)
    ramp.color_ramp.interpolation = 'LINEAR'  # 柔和渐变

    # 暗部：偏紫蓝色（吉卜力标志性阴影色）
    ramp.color_ramp.elements[0].color = (0.35, 0.28, 0.45, 1.0)
    ramp.color_ramp.elements[0].position = 0.0

    # 中间调
    elem_mid = ramp.color_ramp.elements.new(0.35)
    elem_mid.color = base_color

    # 亮部：略微提亮偏暖
    ramp.color_ramp.elements[1].color = (
        min(base_color[0] * 1.15, 1.0),
        min(base_color[1] * 1.1, 1.0),
        min(base_color[2] * 1.05, 1.0),
        1.0
    )
    ramp.color_ramp.elements[1].position = 1.0

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (200, 0)

    links.new(diffuse.outputs['BSDF'], shader_to_rgb.inputs['Shader'])
    links.new(shader_to_rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        setup_ghibli_material(obj)
```

## 步骤二：Freestyle 手绘描边

```python
import bpy

scene = bpy.context.scene
scene.render.use_freestyle = True
view_layer = bpy.context.view_layer
view_layer.use_freestyle = True

if not view_layer.freestyle_settings.linesets:
    view_layer.freestyle_settings.linesets.new("GhibliLine")

lineset = view_layer.freestyle_settings.linesets[0]
style = lineset.linestyle

# 基础线宽（会被粗细调节器覆盖）
style.thickness = 1.2
style.color = (0.2, 0.15, 0.1)  # 暖棕色

# 开启粗细变化（模拟手绘笔触）
style.use_thickness_modifiers = True
# Along Stroke 修改器让线条粗细沿长度变化
mod = style.thickness_modifiers.new("AlongStroke", "ALONG_STROKE")
mod.blend = 'MULTIPLY'
mod.mapping = 'CURVE'
# 线条中间粗、两端细
mod.value_min = 0.3
mod.value_max = 1.0
```

## 步骤三：合成节点（水彩纹理叠加）

```python
import bpy

scene = bpy.context.scene
scene.use_nodes = True
tree = scene.node_tree
nodes = tree.nodes
links = tree.links

# 清理默认连接
for link in links:
    links.remove(link)

# 渲染层
render_layers = nodes.get('Render Layers') or nodes.new('CompositorNodeRLayers')

# 水彩纸纹理
# 需要准备一张水彩纸纹理图片放在 assets/ 目录
# 如果没有，可以用程序生成噪波纹理代替
tex_image = nodes.new('CompositorNodeImage')
# tex_image.image = bpy.data.images.load("path/to/watercolor_paper.jpg")
# 如果没有纹理图片，跳过此步，用下面的噪波代替

# 替代方案：用噪波模拟纸张纹理
# 这里用 Blur + 亮度对比度 模拟
blur = nodes.new('CompositorNodeBlur')
blur.size_x = 2
blur.size_y = 2

# 混合模式：Overlay 叠加
mix = nodes.new('CompositorNodeMixRGB')
mix.blend_type = 'OVERLAY'
mix.inputs['Fac'].default_value = 0.15  # 纹理强度

# 整体调色：偏暖 + 降饱和
hue_sat = nodes.new('CompositorNodeHueSat')
hue_sat.inputs['Saturation'].default_value = 0.85  # 略降饱和
hue_sat.inputs['Value'].default_value = 1.05  # 略提亮

# 输出
composite = nodes.get('Composite') or nodes.new('CompositorNodeComposite')

# 连接
links.new(render_layers.outputs['Image'], blur.inputs['Image'])
links.new(render_layers.outputs['Image'], mix.inputs[1])
links.new(blur.outputs['Image'], mix.inputs[2])
links.new(mix.outputs['Image'], hue_sat.inputs['Image'])
links.new(hue_sat.outputs['Image'], composite.inputs['Image'])
```

## 色彩要点

吉卜力动画的色彩规律：
- **阴影永远不是纯黑**，而是偏紫、偏蓝、偏青
- **亮部偏暖**，暗部偏冷，形成冷暖对比
- **饱和度中等偏低**，不是浓烈的糖果色
- **天空和远景偏淡**，近景偏实，自然的空气透视
- **绿色系特别丰富**——翠绿、草绿、橄榄绿、苔绿都会同时出现
