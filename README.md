# nano-banana-pro-openrouter-版本
---
名称： nano banana Pro 
描述：使用 OpenRouter API 和 Google Gemini 3.1 Flash 图像预览模型生成图像。用于图像创建请求。支持1K/2K/4K分辨率的文本转图像。
---

# 通过 OpenRouter 生成图像

使用 OpenRouter API 和 Google 的 Gemini 3.1 Flash 图像预览模型 (google/gemini-3.1-flash-image-preview) 生成图像。

## 用法

使用绝对路径运行脚本（不要先 cd 到技能目录）：
**生成新图像：**
````bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "图像描述" --filename "output-name.png" [--resolution 1K|2K|4K] [--model MODEL] [--api-key KEY]
````

**重要提示：**始终从用户当前的工作目录运行，以便图像保存在用户工作的位置，而不是技能目录中。

## 可用型号
默认模型是 **google/gemini-3.1-flash-image-preview**-Google 的 Gemini 图像生成模型。

如果需要，您可以使用“--model”参数指定不同的模型。

## 默认工作流程（草案→迭代→最终）

目标：快速迭代，无需在 4K 上消耗时间，直到提示正确。

-草稿（1K）：快速反馈循环
  ````bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "<草稿提示>" --filename "yyyy-mm-dd-hh-mm-ss-draft.png" --resolution 1K
  ````
-迭代：在小差异中调整提示；每次运行时保持文件名是新的
-最终 (4K)：仅当提示被锁定时
  ````bash
  uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "<最终提示>" --filename "yyyy-mm-dd-hh-mm-ss-final.png" --resolution 4K
  ````

## 分辨率选项
该脚本使用 OpenRouter 的“image_config.image_size”参数支持三种分辨率预设：

-**1K**（默认） -标准分辨率（~1024×1024px）
-**2K**-更高分辨率（~2048×2048px 或类似）
-**4K**-最高分辨率（~4096×4096px 或类似）

**注意：**确切尺寸可能因型号而异。 OpenRouter 的图像生成模型使用这些尺寸提示来控制输出质量和分辨率。

将用户请求映射到解析参数：
-没有提及分辨率 → `1K`
-“低分辨率”、“1080”、“1080p”、“1K”、“小”、“标准”→ `1K`
-“2K”、“中等分辨率”、“更高质量”→ `2K`
-“高分辨率”、“高分辨率”、“高分辨率”、“4K”、“超”、“大”、“最高质量” → `4K`

## API 密钥

该脚本按以下顺序检查 API 密钥：
1. `--api-key` 参数（如果用户在聊天中提供了密钥则使用）
2.`OPENROUTER_API_KEY`环境变量
3. `~/.openclaw/.env` 文件，其中包含 `OPENROUTER_API_KEY=...`

如果没有可用的，脚本将退出并显示错误消息。
## 预检 + 常见故障（快速修复）

-飞行前：
  -`command -v uv`（必须存在）
  -检查 API 密钥是否可用（见上文）

-常见故障：
  -`Error: No API key provided.` → 在 env 中设置 `OPENROUTER_API_KEY` 或传入 `--api-key`
  -`Error generating image:` → 检查 API 密钥有效性、配额或模型可用性
  -网络错误→检查互联网连接
  -未找到型号 → 验证 OpenRouter 的型号名称是否正确

## 文件名生成
使用以下模式生成文件名：`yyyy-mm-dd-hh-mm-ss-name.png`

**格式：**`{时间戳}-{描述性名称}.png`
-时间戳：当前日期/时间，格式为“yyyy-mm-dd-hh-mm-ss”（24 小时格式）
-名称：带有连字符的描述性小写文本
-保持描述性部分简洁（通常1-5个字）
-使用用户提示或对话中的上下文
-如果不清楚，请使用随机标识符（例如“x9k2”、“a7b3”）

示例：
-提示“宁静的花园”→ `2026-03-15-16-23-05-garden.png`
-提示“山上日落”→ `2026-03-15-17-30-12-sunset-mountains.png`
-提示“创建机器人图像”→ `2026-03-15-18-45-33-robot.png`
-上下文不明确 → `2026-03-15-19-12-48-x9k2.png`

## 图像编辑

**注意：**大多数 OpenRouter 型号目前不支持图像到图像编辑（使用 `--input-image`）。该脚本将仅根据提示生成新图像。
对于模型可用时的未来支持：
-检查 OpenRouter 文档中的模型功能
-使用“--input-image”参数和图像路径
-提示应包含编辑说明

## 及时处理

**对于生成：**将用户的图像描述按原样传递给“--prompt”。仅在明显不足时才返工。

保留用户的创作意图。

## 提示模板（高命中率）

当用户模糊或需要指导时使用模板：

-生成模板：
-“创建以下图像：<主题>。风格：<风格>。构图：<相机/镜头>。灯光：<照明>。背景：<背景>。调色板：<调色板>。避免：<列表>。”

## 输出

-将 PNG 保存到当前目录（或指定路径，如果文件名包含目录）
-脚本输出生成图像的完整路径
-**不要读回图像**-只需告知用户保存的路径

## 示例

**使用默认模型生成（Gemini 3.1 Flash 图像预览）：**
````bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "宁静的花园" --filename "2026-03-15-16-23-05-garden.png" --resolution 4K
````

**用不同的模型生成：**
````bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "霓虹灯夜晚的赛博朋克城市" --filename "2026-03-15-16-25-30-cyberpunk-city.png" --resolution 2K --model google/gemini-2.5-flash-image-preview
````
**快速草稿：**
````bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "山景" --filename "2026-03-15-16-30-00-draft.png" --resolution 1K
````

## 技术细节

该脚本使用 OpenRouter 的聊天完成 API 以及以下关键参数：

-**端点：**`https://openrouter.ai/api/v1/chat/completions`
-**模态：**`["image", "text"]` -Gemini 图像生成模型所需
-**图像配置：**`{"image_size": "1K|2K|4K"}` -控制输出分辨率
-**响应格式：**图像在`message.images[].image_url.url`中作为base64编码的数据URL返回

脚本自动执行：
1. 使用正确的模式配置发送提示
2. 从响应中提取base64图像数据
3.解码并保存为PNG格式
4.正确处理RGB/RGBA颜色模式

## 依赖关系

该脚本通过 uv 自动安装所需的依赖项：
-`openai>=1.0.0` -OpenRouter API 客户端（OpenAI 兼容）
-`pillow>=10.0.0` -图像处理
-`python-dotenv>=1.0.0` -环境变量加载