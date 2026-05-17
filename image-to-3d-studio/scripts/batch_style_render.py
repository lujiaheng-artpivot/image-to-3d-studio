"""
多风格批量渲染脚本
在 Blender 中运行，从当前场景一次性输出所有风格的渲染
"""
import bpy
import os

def render_all_styles(output_dir="./styled_renders"):
    """批量渲染全部风格"""
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    
    styles = {
        "realistic_3d": render_realistic,
        "cel_shading": render_cel,
        "ghibli": render_ghibli,
        "cinematic": render_cinematic,
        "concept_art": render_concept,
    }
    
    for name, func in styles.items():
        print(f"\n>>> 渲染风格: {name}")
        style_dir = os.path.join(output_dir, name)
        os.makedirs(style_dir, exist_ok=True)
        scene.render.filepath = os.path.join(style_dir, f"{name}.png")
        func(scene)
        bpy.ops.render.render(write_still=True)
        print(f"    保存到 {scene.render.filepath}")
    
    print(f"\n全部完成！{len(styles)} 种风格已渲染到 {output_dir}/")


def render_realistic(scene):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'


def render_cel(scene):
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.use_freestyle = True
    scene.eevee.use_gtao = False
    bpy.context.view_layer.use_freestyle = True
    # 材质需要预先设置好 Shader to RGB 节点
    # 参考 references/cel-shading-setup.md


def render_ghibli(scene):
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.use_freestyle = True
    scene.eevee.use_gtao = False
    bpy.context.view_layer.use_freestyle = True
    scene.view_settings.look = 'Medium Low Contrast'
    # 材质和合成节点需要预先设置
    # 参考 references/ghibli-watercolor-setup.md


def render_cinematic(scene):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 512
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    
    # 浅景深
    cam = scene.camera
    if cam and cam.data:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = 2.8
        cam.data.lens = 35


def render_concept(scene):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64  # 低采样保留噪点当纹理
    scene.cycles.use_denoising = False
    scene.render.use_freestyle = True
    bpy.context.view_layer.use_freestyle = True
    scene.view_settings.view_transform = 'Standard'


if __name__ == "__main__":
    render_all_styles()
