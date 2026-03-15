#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "pillow>=10.0.0",
#     "python-dotenv>=1.0.0",
#     "requests>=2.31.0",
# ]
# ///
"""
Generate images using OpenRouter API with various image generation models.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--api-key KEY] [--model MODEL]
"""

import argparse
import os
import sys
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        env_path = Path.home() / ".openclaw" / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass
    
    return os.environ.get("OPENROUTER_API_KEY")




def main():
    parser = argparse.ArgumentParser(
        description="Generate images using OpenRouter API"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        help="Optional input image path for editing/modification (not supported by all models)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        default=None,
        help="Aspect ratio (optional): 1:1, 16:9, etc."
    )
    parser.add_argument(
        "--model", "-m",
        default="google/gemini-3.1-flash-image-preview",
        help="Model to use (default: google/gemini-3.1-flash-image-preview)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="OpenRouter API key (overrides OPENROUTER_API_KEY env var)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set OPENROUTER_API_KEY environment variable", file=sys.stderr)
        print("  3. Add OPENROUTER_API_KEY to ~/.openclaw/.env file", file=sys.stderr)
        sys.exit(1)

    # Import here after checking API key
    from openai import OpenAI
    from PIL import Image as PILImage
    import requests
    from io import BytesIO

    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check for input image (image-to-image editing)
    if args.input_image:
        print("Warning: Image editing (input-image) is not supported by most OpenRouter models.", file=sys.stderr)
        print("This feature requires models with image-to-image capabilities.", file=sys.stderr)
        # For now, we'll just generate based on the prompt
        # Future: implement image-to-image for supported models

    aspect_info = f" with aspect ratio {args.aspect_ratio}" if args.aspect_ratio else ""
    print(f"Generating image with model {args.model} at resolution {args.resolution}{aspect_info}...")

    try:
        # Generate image using OpenRouter's chat completions endpoint
        # Must include modalities parameter for image generation
        # Build image_config for resolution and aspect ratio control
        image_config = {
            "image_size": args.resolution  # 1K, 2K, or 4K
        }
        if args.aspect_ratio:
            image_config["aspect_ratio"] = args.aspect_ratio
        
        response = client.chat.completions.create(
            model=args.model,
            messages=[
                {
                    "role": "user",
                    "content": args.prompt
                }
            ],
            modalities=["image", "text"],  # Required for Gemini image models
            extra_body={
                "image_config": image_config
            }
        )

        # Extract image from response
        message = response.choices[0].message
        
        # Check if there are images in the response
        if hasattr(message, 'images') and message.images:
            # Get the first image (base64 data URL)
            # Handle both dict and object formats
            first_image = message.images[0]
            if isinstance(first_image, dict):
                image_data_url = first_image.get('image_url', {}).get('url', '')
            else:
                image_data_url = first_image.image_url.url
            
            # Parse base64 data URL (format: data:image/png;base64,...)
            if image_data_url and image_data_url.startswith('data:image'):
                import base64
                # Extract base64 data after the comma
                base64_data = image_data_url.split(',', 1)[1]
                image_bytes = base64.b64decode(base64_data)
                
                # Open and save as PNG
                image = PILImage.open(BytesIO(image_bytes))
                
                # Ensure RGB mode for PNG
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    rgb_image.save(str(output_path), 'PNG')
                elif image.mode == 'RGB':
                    image.save(str(output_path), 'PNG')
                else:
                    image.convert('RGB').save(str(output_path), 'PNG')
                
                full_path = output_path.resolve()
                print(f"\nImage saved: {full_path}")
            else:
                print(f"Error: Unexpected image data format: {image_data_url[:100]}...", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: No images found in response.", file=sys.stderr)
            if message.content:
                print(f"Response content: {message.content}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
