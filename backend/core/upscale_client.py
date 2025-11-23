"""
core/upscale_client.py - Image Upscaling with Replicate Real-ESRGAN
Handles upscaling of generated images using Replicate API
"""

import os
import io
from PIL import Image
import requests


class UpscaleClient:
    """
    Client for upscaling images using Replicate Real-ESRGAN

    Supports 2x and 4x upscaling:
    - 2x: 2048x2048 → 4096x4096
    - 4x: 2048x2048 → 8192x8192
    """

    def __init__(self, api_token=None):
        """
        Initialize upscale client

        Args:
            api_token: Replicate API token (optional, falls back to env var)
        """
        self.api_token = api_token or os.environ.get("REPLICATE_API_TOKEN")

        if not self.api_token:
            raise ValueError(
                "Missing REPLICATE_API_TOKEN!\n"
                "Please set it in .env file or Settings UI:\n"
                "REPLICATE_API_TOKEN=r8_..."
            )

        # Validate API token format
        if not self.api_token.startswith("r8_"):
            print(f"⚠️  WARNING: Replicate API token format looks suspicious!")
            print(f"   Token should start with 'r8_'")

    def upscale(self, image_pil, scale=2):
        """
        Upscale PIL Image using Real-ESRGAN via Replicate

        Args:
            image_pil: PIL Image object
            scale: Upscale factor (2 or 4)

        Returns:
            PIL Image (upscaled)

        Raises:
            ValueError: If scale is not 2 or 4
            Exception: If API call fails
        """
        if scale not in [2, 4]:
            raise ValueError(f"Scale must be 2 or 4, got {scale}")

        print(f"🔍 Starting upscale {scale}x...")
        print(f"   Input size: {image_pil.width}x{image_pil.height}")
        print(f"   Target size: {image_pil.width * scale}x{image_pil.height * scale}")

        try:
            # Import replicate here (lazy import)
            import replicate

            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image_pil.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Prepare input
            input_data = {
                "image": img_byte_arr,  # File-like object
                "scale": scale
            }

            print(f"   📤 Uploading to Replicate...")

            # Run Real-ESRGAN model
            output = replicate.run(
                "nightmareai/real-esrgan",
                input=input_data
            )

            print(f"   ⏳ Processing on Replicate...")

            # Download result
            # output is a FileOutput object with .read() method
            upscaled_bytes = output.read()

            # Convert to PIL Image
            upscaled_pil = Image.open(io.BytesIO(upscaled_bytes))

            print(f"   ✅ Upscale complete!")
            print(f"   Output size: {upscaled_pil.width}x{upscaled_pil.height}")

            return upscaled_pil

        except ImportError:
            raise Exception(
                "replicate library not installed!\n"
                "Install it with: pip install replicate"
            )
        except Exception as e:
            print(f"   ❌ Upscale failed: {str(e)}")
            raise Exception(f"Upscale failed: {str(e)}")

    def upscale_from_url(self, image_url, scale=2):
        """
        Upscale image from URL

        Args:
            image_url: URL to image
            scale: Upscale factor (2 or 4)

        Returns:
            PIL Image (upscaled)
        """
        if scale not in [2, 4]:
            raise ValueError(f"Scale must be 2 or 4, got {scale}")

        print(f"🔍 Starting upscale {scale}x from URL...")
        print(f"   URL: {image_url[:80]}...")

        try:
            import replicate

            # Prepare input with URL
            input_data = {
                "image": image_url,
                "scale": scale
            }

            print(f"   📤 Sending to Replicate...")

            # Run Real-ESRGAN model
            output = replicate.run(
                "nightmareai/real-esrgan",
                input=input_data
            )

            print(f"   ⏳ Processing on Replicate...")

            # Download result
            upscaled_bytes = output.read()
            upscaled_pil = Image.open(io.BytesIO(upscaled_bytes))

            print(f"   ✅ Upscale complete!")
            print(f"   Output size: {upscaled_pil.width}x{upscaled_pil.height}")

            return upscaled_pil

        except ImportError:
            raise Exception(
                "replicate library not installed!\n"
                "Install it with: pip install replicate"
            )
        except Exception as e:
            print(f"   ❌ Upscale failed: {str(e)}")
            raise Exception(f"Upscale failed: {str(e)}")

    def estimate_cost(self, scale=2):
        """
        Estimate cost for upscaling

        Args:
            scale: Upscale factor (2 or 4)

        Returns:
            float: Estimated cost in USD
        """
        # Real-ESRGAN on Replicate costs ~$0.02-0.03 for 2x, ~$0.04-0.05 for 4x
        if scale == 2:
            return 0.025  # $0.025
        elif scale == 4:
            return 0.045  # $0.045
        else:
            return 0.0
