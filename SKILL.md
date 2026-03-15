---
name: nano-banana-pro
description: Generate images using OpenRouter API with Google Gemini 3.1 Flash Image Preview model. Use for image creation requests. Supports text-to-image with 1K/2K/4K resolutions.
---

# Image Generation via OpenRouter

Generate images using OpenRouter API with Google's Gemini 3.1 Flash Image Preview model (google/gemini-3.1-flash-image-preview).

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--resolution 1K|2K|4K] [--model MODEL] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Available Models

The default model is **google/gemini-3.1-flash-image-preview** - Google's Gemini image generation model.

You can specify a different model with the `--model` parameter if needed.

## Default Workflow (draft → iterate → final)

Goal: fast iteration without burning time on 4K until the prompt is correct.

- Draft (1K): quick feedback loop
  ```bash
  uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "<draft prompt>" --filename "yyyy-mm-dd-hh-mm-ss-draft.png" --resolution 1K
  ```
- Iterate: adjust prompt in small diffs; keep filename new per run
- Final (4K): only when prompt is locked
  ```bash
  uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "<final prompt>" --filename "yyyy-mm-dd-hh-mm-ss-final.png" --resolution 4K
  ```

## Resolution Options

The script supports three resolution presets using OpenRouter's `image_config.image_size` parameter:

- **1K** (default) - Standard resolution (~1024×1024px)
- **2K** - Higher resolution (~2048×2048px or similar)
- **4K** - Highest resolution (~4096×4096px or similar)

**Note:** The exact dimensions may vary by model. OpenRouter's image generation models use these size hints to control output quality and resolution.

Map user requests to resolution parameters:
- No mention of resolution → `1K`
- "low resolution", "1080", "1080p", "1K", "small", "standard" → `1K`
- "2K", "medium resolution", "higher quality" → `2K`
- "high resolution", "high-res", "hi-res", "4K", "ultra", "large", "highest quality" → `4K`

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `OPENROUTER_API_KEY` environment variable
3. `~/.openclaw/.env` file with `OPENROUTER_API_KEY=...`

If none is available, the script exits with an error message.

## Preflight + Common Failures (fast fixes)

- Preflight:
  - `command -v uv` (must exist)
  - Check API key is available (see above)

- Common failures:
  - `Error: No API key provided.` → set `OPENROUTER_API_KEY` in env or pass `--api-key`
  - `Error generating image:` → check API key validity, quota, or model availability
  - Network errors → check internet connection
  - Model not found → verify model name is correct for OpenRouter

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.png`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" → `2026-03-15-16-23-05-japanese-garden.png`
- Prompt "sunset over mountains" → `2026-03-15-17-30-12-sunset-mountains.png`
- Prompt "create an image of a robot" → `2026-03-15-18-45-33-robot.png`
- Unclear context → `2026-03-15-19-12-48-x9k2.png`

## Image Editing

**Note:** Image-to-image editing (using `--input-image`) is not currently supported by most OpenRouter models. The script will generate a new image based on the prompt only.

For future support when models become available:
- Check model capabilities on OpenRouter documentation
- Use `--input-image` parameter with the path to the image
- The prompt should contain editing instructions

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

Preserve user's creative intent.

## Prompt Templates (high hit-rate)

Use templates when the user is vague or needs guidance:

- Generation template:
  - "Create an image of: <subject>. Style: <style>. Composition: <camera/shot>. Lighting: <lighting>. Background: <background>. Color palette: <palette>. Avoid: <list>."

## Output

- Saves PNG to current directory (or specified path if filename includes directory)
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform the user of the saved path

## Examples

**Generate with default model (Gemini 3.1 Flash Image Preview):**
```bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2026-03-15-16-23-05-japanese-garden.png" --resolution 4K
```

**Generate with different model:**
```bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "Cyberpunk city at night with neon lights" --filename "2026-03-15-16-25-30-cyberpunk-city.png" --resolution 2K --model google/gemini-2.5-flash-image-preview
```

**Quick draft:**
```bash
uv run ~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py --prompt "Mountain landscape" --filename "2026-03-15-16-30-00-draft.png" --resolution 1K
```

## Technical Details

The script uses OpenRouter's chat completions API with the following key parameters:

- **Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
- **Modalities:** `["image", "text"]` - Required for Gemini image generation models
- **Image Config:** `{"image_size": "1K|2K|4K"}` - Controls output resolution
- **Response Format:** Images are returned as base64-encoded data URLs in `message.images[].image_url.url`

The script automatically:
1. Sends the prompt with proper modalities configuration
2. Extracts base64 image data from the response
3. Decodes and saves as PNG format
4. Handles RGB/RGBA color modes correctly

## Dependencies

The script automatically installs required dependencies via uv:
- `openai>=1.0.0` - OpenRouter API client (OpenAI-compatible)
- `pillow>=10.0.0` - Image processing
- `python-dotenv>=1.0.0` - Environment variable loading
