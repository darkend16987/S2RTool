"""api/upscale.py - Image Upscaling Endpoint
Upscales rendered images using Replicate Real-ESRGAN
"""

from core.logger import logger

import base64
import io
from flask import Blueprint, request, jsonify

from core.thread_local import get_image_processor
from core.upscale_client import UpscaleClient

upscale_bp = Blueprint('upscale', __name__)


@upscale_bp.route('/upscale', methods=['POST'])
def upscale_image():
    """
    Upscale an image using Real-ESRGAN

    Request:
    {
        "image_base64": "data:image/png;base64,...",
        "scale": 2  // 2 or 4
    }

    Response:
    {
        "upscaled_image_base64": "data:image/png;base64,...",
        "original_resolution": "2048x2048",
        "upscaled_resolution": "4096x4096",
        "scale": 2,
        "cost_estimate": 0.025
    }
    """
    try:
        # Get image processor
        processor = get_image_processor()

        data = request.json

        # Validate required fields
        if 'image_base64' not in data:
            return jsonify({"error": "Missing image_base64"}), 400

        # Get scale (default 2x)
        scale = data.get('scale', 2)
        if scale not in [2, 4]:
            return jsonify({"error": "Scale must be 2 or 4"}), 400

        # Process input image
        image_pil, _ = processor.process_base64_image(data['image_base64'])
        if not image_pil:
            return jsonify({"error": "Invalid image"}), 400

        original_width, original_height = image_pil.size

        logger.debug(f"🔍 Upscaling image...")
        logger.info(f"   Original: {original_width}x{original_height}")
        logger.info(f"   Scale: {scale}x")
        logger.info(f"   Target: {original_width * scale}x{original_height * scale}")

        # Initialize upscale client
        upscale_client = UpscaleClient()

        # Upscale image
        upscaled_pil = upscale_client.upscale(image_pil, scale=scale)

        # Convert to base64
        output_buffer = io.BytesIO()
        upscaled_pil.save(output_buffer, format='PNG', quality=95)
        output_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

        # Add data URI prefix
        output_base64_full = f"data:image/png;base64,{output_base64}"

        # Estimate cost
        cost_estimate = upscale_client.estimate_cost(scale)

        logger.info(f"✅ Upscale complete!")
        logger.info(f"   Output: {upscaled_pil.width}x{upscaled_pil.height}")
        logger.info(f"   Cost: ${cost_estimate:.3f}")

        return jsonify({
            "upscaled_image_base64": output_base64_full,
            "original_resolution": f"{original_width}x{original_height}",
            "upscaled_resolution": f"{upscaled_pil.width}x{upscaled_pil.height}",
            "scale": scale,
            "cost_estimate": cost_estimate,
            "mime_type": "image/png"
        })

    except ValueError as e:
        logger.error(f"❌ [UPSCALE_VALIDATION_ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"❌ [UPSCALE_ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({"error": str(e)}), 500


@upscale_bp.route('/upscale/estimate-cost', methods=['POST'])
def estimate_upscale_cost():
    """
    Estimate cost for upscaling

    Request:
    {
        "scale": 2  // 2 or 4
    }

    Response:
    {
        "scale": 2,
        "cost_estimate": 0.025,
        "processing_time_estimate": "10-30 seconds"
    }
    """
    try:
        data = request.json
        scale = data.get('scale', 2)

        if scale not in [2, 4]:
            return jsonify({"error": "Scale must be 2 or 4"}), 400

        upscale_client = UpscaleClient()
        cost_estimate = upscale_client.estimate_cost(scale)

        # Estimate processing time
        if scale == 2:
            time_estimate = "10-30 seconds"
        else:  # scale == 4
            time_estimate = "30-60 seconds"

        return jsonify({
            "scale": scale,
            "cost_estimate": cost_estimate,
            "processing_time_estimate": time_estimate
        })

    except Exception as e:
        logger.error(f"❌ [ESTIMATE_COST_ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500
