---
name: image-to-3d-studio
description: |
  单图→3D场景→多风格渲染的全流程部署+创作引擎。
  覆盖 image-blaster 一键安装部署、World Labs 3D场景生成、fal/Hunyuan 单体模型提取、
  Blender 精细调整与多风格渲染（纯3D、写实2D、三渲二赛璐珞/吉卜力/概念艺术/电影感）、
  以及 AI 视频控制信号输出（深度图/法线图/mask/参考帧/相机轨迹）的完整闭环。
  支持通过 Codex/Claude 远程手机一键部署和操控。

  强制触发词：image-blaster、World Labs、3D场景生成、单图转3D、图片转3D、
  三渲二、3D转2D、cel-shading、赛璐珞渲染、吉卜力风格渲染、toon shader、
  NPR渲染、非真实感渲染、Blender渲染风格、场景一致性、AI视频片场、
  3D场景部署、一键部署3D、Codex部署、远程建模、手机遥控建模、
  深度图导出、法线图导出、参考帧生成、相机轨迹、
  glb、spz、obj、3D资产、场景重建、全景图生成、
  fal.ai、Hunyuan 3D、腾讯混元3D、ElevenLabs音效、
  "帮我把这张图变成3D""一键跑image-blaster""部署3D场景工具"
  "渲染成动画风格""三渲二怎么做""Blender里怎么出赛璐珞"
  "帮我装image-blaster""帮我配环境""生成深度图""导出法线图"

  当用户想从一张图片生成可控3D场景时务必触发。
  当用户提到部署或安装 image-blaster、配置 API Key 时务必触发。
  当用户想在 Blender 里做三渲二（任何风格）渲染时务必触发。
  当用户需要为 AI 视频生成控制信号（深度图/法线图/mask/参考帧）时务必触发。
  当用户说"帮我远程跑一下""用手机操控""Codex跑这个"时也应触发。
  即使用户只是说"这张图能不能变成3D"或"怎么保持AI视频场景一致"也应触发。
---

# Image-to-3D Studio：单图→3D片场→多风格渲染 全流程引擎

## 这个 Skill 解决什么问题

AI 视频创作最大的痛点是场景一致性——每一帧都是模型从头想象的，空间关系随时崩塌。
这个 skill 把「一张图」变成「一个可控的 3D 片场」，然后从这个片场输出各种风格的渲染和控制信号，
让 AI 视频的每个镜头都锚定在同一个稳定的三维空间里。

核心链路：**一张图 → 3D 场景资产 → Blender 精调 → 多风格渲染/控制信号 → AI 视频引导**

---

## 第一部分：一键部署 image-blaster

这部分可以直接发给 Codex 或 Claude Code 执行。把下面的指令整段发过去即可。

### 部署指令（直接复制给 Codex/Claude）

```
请帮我完成 image-blaster 的完整部署：

1. 克隆仓库
   git clone https://github.com/slashml/image-blaster.git
   cd image-blaster

2. 创建虚拟环境并安装依赖
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. 配置 API Key（在 .env 文件中填写）
   - WORLD_LABS_API_KEY=（World Labs 官网申请：https://platform.worldlabs.ai/api-keys）
   - FAL_KEY=（fal.ai 官网申请：https://fal.ai/dashboard/usage-billing/credits）
   - ELEVENLABS_API_KEY=（ElevenLabs 官网申请：https://elevenlabs.io）

4. 测试运行
   python main.py --image test_image.jpg

5. 确认输出目录包含：
   - model.glb / model.obj / model.blend（3D场景文件）
   - panorama.jpg（720度全景图）
   - 单体物体的独立 .glb 文件
   - preview 视频

如果遇到网络问题，自动重试。如果缺少系统依赖（如 ffmpeg），自动安装。
```

### 手机远程操控说明

如果你在手机上用 Codex：
1. 打开手机端 Codex app，连接到你的电脑
2. 把上面的部署指令发给 Codex
3. Codex 会在你电脑上自动执行全流程
4. 完成后查看输出文件列表，可以直接在手机上预览

如果你在手机上用 Claude + Blender MCP：
1. 确保电脑上 Blender 已打开且 MCP 连接器已启用
2. 用 Claude 对话式操控 Blender（后续章节详述）

---

## 第二部分：3D 场景生成工作流

### 输入 → 输出一览

| 输入 | 工具 | 输出 |
|------|------|------|
| 一张 JPG/PNG | World Labs Marble | 完整 3D 场景（.spz → .glb） |
| 场景中的物体 | fal.ai / Hunyuan 3D | 单体 .glb 模型 |
| 场景空间 | World Labs | 720° 全景图 |
| 可选 | ElevenLabs | 环境音效 |

### 运行命令

```bash
# 基础用法
python main.py --image your_photo.jpg

# 指定输出目录
python main.py --image your_photo.jpg --output ./my_scene

# 跳过音效生成（省 API 调用费）
python main.py --image your_photo.jpg --no-audio
```

### 输出文件结构

```
output/
├── scene/
│   ├── model.glb          # 完整场景，可直接导入 Blender/Unity/Unreal
│   ├── model.obj          # OBJ 格式备用
│   └── model.blend        # Blender 原生格式
├── panorama/
│   └── panorama_360.jpg   # 720度全景图，可做环境贴图
├── objects/
│   ├── suitcase.glb       # 自动识别并提取的单体物体
│   ├── table.glb
│   └── ...
├── preview/
│   └── turntable.mp4      # 自动生成的转盘预览
└── audio/
    └── ambient.mp3        # 环境音效（可选）
```

---

## 第三部分：Blender 集成与精调

把 .glb 或 .blend 导入 Blender 后，通过 Claude Blender MCP 连接器对话式操控。

### 导入场景

对 Claude 说：
```
打开 Blender，导入 output/scene/model.glb，自动居中并适配视口。
```

### 常用精调指令

**布光：**
```
主光源设为区域光，从窗户方向45度角打进来，色温 4500K，强度 800W。
加一盏补光在对角，强度是主光的 30%。
```

**材质：**
```
地板材质换成深色橡木，粗糙度 0.4。
所有金属物体加一层微反光，粗糙度 0.15。
```

**相机路径：**
```
创建一条相机运动路径：从门口开始，缓慢推进到餐桌，
总时长 5 秒，运动曲线 ease-in-out，输出 1920x1080 24fps。
```

---

## 第四部分：多风格渲染系统（核心）

从同一个 3D 场景输出多种视觉风格，每种风格在 Blender 里通过不同渲染设置实现。

### 风格速查

| 风格 | 类型 | 适用场景 | Blender 引擎 |
|------|------|----------|-------------|
| 写实3D | 三维 | 建筑可视化、产品展示 | Cycles |
| PBR实时 | 三维 | 游戏预览、实时交互 | EEVEE |
| 赛璐珞 | 三渲二 | 日系动画、MV | EEVEE + Freestyle |
| 吉卜力水彩 | 三渲二 | 治愈系、绘本感 | EEVEE + 合成 |
| 电影写实 | 二维输出 | AI视频参考帧 | Cycles + Filmic |
| 概念艺术 | 三渲二 | 概念设计、气氛图 | Cycles 低采样 |

### 风格 A：赛璐珞 / Cel-Shading（三渲二核心）

最常用的三渲二风格。核心原理：把光照信息离散化成 2-3 个色阶 + Freestyle 描边。

对 Claude 说：
```
把场景渲染成赛璐珞风格：
1. 所有材质换成 Shader to RGB + ColorRamp 做 2 段色阶
2. 开启 Freestyle 描边，线宽 1.5px，深棕色
3. 关闭环境光遮蔽，阴影硬边
4. 渲染引擎用 EEVEE
```

详细节点设置参考 `references/cel-shading-setup.md`。

### 风格 B：吉卜力水彩风

在赛璐珞基础上加柔化，模拟水彩渗透和纸张纹理。

对 Claude 说：
```
在赛璐珞基础上改吉卜力风格：
1. ColorRamp 改 3 段渐变过渡，不硬切
2. 阴影色偏紫/偏蓝
3. Freestyle 描边不等宽，模拟手绘
4. 合成节点叠一层水彩纸纹理（Overlay 15%）
5. 整体偏暖，饱和度略降
```

详细节点设置参考 `references/ghibli-watercolor-setup.md`。

### 风格 C：电影写实（2D 输出）

目标是输出电影感 2D 图片，作为 AI 视频参考帧。

对 Claude 说：
```
电影感渲染：Cycles 512采样，35mm f/2.8 浅景深，
Filmic Medium High Contrast，
合成加镜头暗角 0.3、轻微色差、FilmGrain 0.02，输出 2K 16:9。
```

### 风格 D：概念艺术风

模拟概念设计师的大色块+笔触感。

对 Claude 说：
```
概念艺术风格：Cycles 64采样保留噪点，
材质简化成大色块，叠画布纹理 5%，
Freestyle 粗线 3px 描主轮廓，对比度拉高。
```

---

## 第五部分：AI 视频控制信号输出

从 3D 场景导出控制信号，喂给 Seedance/Kling/Sora。

### 控制信号类型

| 信号 | 用途 | Blender 导出方式 |
|------|------|------------------|
| 深度图 | 空间距离 | Depth Pass → Normalize → PNG |
| 法线图 | 表面朝向 | Normal Pass → PNG |
| 遮挡 Mask | 前后关系 | Cryptomatte / Object ID |
| 参考帧 | 各角度画面 | 多角度渲染 PNG |
| 相机轨迹 | 运镜引导 | 相机动画 → MP4 |

### 一键导出指令

对 Claude 说：
```
导出完整 AI 视频控制信号包：
1. 当前视角深度图（Normalize 灰度 PNG）
2. 法线图（RGB PNG）
3. 物体遮挡 mask（每物体不同颜色）
4. 8 个等间距角度各一张参考帧（电影写实风格）
5. 相机路径 5 秒运镜视频（1080p 24fps）
保存到 ./control_signals/
```

### 对接 AI 视频模型

**Seedance / 即梦：** 参考帧→首帧，深度图→ControlNet depth，全景图→环境参考
**Kling / 可灵：** 参考帧→首帧，运镜视频→运镜参考，法线图→空间理解
**Sora：** 多角度参考帧→storyboard，全景图→场景一致性

---

## 注意事项

**单图重建的局限：** 背面是 AI 推断的，不是精确 CAD。需要在 Blender 里修正关键物体。
不影响作为 AI 视频片场的价值——要的是空间关系的稳定性，不是毫米级精度。

**人物一致性：** 这套主要解决场景一致性。人物一致性需要单独方案（LoRA / ID Adapter / 3D rig），
但场景固定后人物至少在同一空间、光线、透视中。

**API 费用：** 单次全流程约 $0.10-0.20。

**系统要求：** Python 3.10+，macOS/Linux（Windows需WSL），Blender 3.6+。
