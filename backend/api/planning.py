"""
api/planning.py - Planning Mode Render Endpoint
Urban planning visualization with multiple lots
"""

from flask import Blueprint, request, jsonify

from core.thread_local import (
    get_image_processor,
    get_prompt_builder,
    get_gemini_client
)
from config import Models

planning_bp = Blueprint('planning', __name__)


@planning_bp.route('/planning/render', methods=['POST'])
def planning_render():
    """
    Generate planning mode render from site plan and lot descriptions

    Request:
    {
        "site_plan_base64": "data:image/png;base64,...",
        "lot_map_base64": "data:image/png;base64,...",
        "lot_descriptions": [
            {
                "lot_number": "1",
                "description": "3-story residential building, modern style..."
            },
            ...
        ],
        "camera_angle": "drone_45deg",  // optional
        "time_of_day": "golden_hour",   // optional
        "aspect_ratio": "16:9",         // optional
        "style_keywords": "..."         // optional
    }

    Response:
    {
        "generated_image_base64": "...",
        "mime_type": "image/png"
    }
    """
    try:
        # Get thread-local instances
        processor = get_image_processor()
        prompt_builder = get_prompt_builder()
        gemini = get_gemini_client()

        data = request.json

        # Validate required fields
        required = ['site_plan_base64', 'lot_map_base64', 'lot_descriptions']
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing required fields: {required}"}), 400

        # Validate lot descriptions
        lot_descriptions = data['lot_descriptions']
        if not isinstance(lot_descriptions, list) or len(lot_descriptions) == 0:
            return jsonify({"error": "lot_descriptions must be a non-empty array"}), 400

        for lot in lot_descriptions:
            if not isinstance(lot, dict) or 'lot_number' not in lot or 'description' not in lot:
                return jsonify({"error": "Each lot must have lot_number and description"}), 400

        # Process images
        site_plan_pil, _ = processor.process_base64_image(data['site_plan_base64'])
        lot_map_pil, _ = processor.process_base64_image(data['lot_map_base64'])

        if not site_plan_pil or not lot_map_pil:
            return jsonify({"error": "Invalid images"}), 400

        # Resize if needed
        site_plan_pil = processor.resize_image(site_plan_pil, max_size=1024)
        lot_map_pil = processor.resize_image(lot_map_pil, max_size=1024)

        # Extract parameters
        camera_angle = data.get('camera_angle', 'drone_45deg')
        time_of_day = data.get('time_of_day', 'golden_hour')
        aspect_ratio = data.get('aspect_ratio', '16:9')
        style_keywords = data.get('style_keywords', '')

        # Build planning prompt
        planning_prompt = prompt_builder.build_planning_prompt(
            lot_descriptions=lot_descriptions,
            camera_angle=camera_angle,
            time_of_day=time_of_day,
            aspect_ratio=aspect_ratio,
            style_keywords=style_keywords
        )

        print(f"🏙️  Generating planning render...")
        print(f"   Lots: {len(lot_descriptions)}")
        print(f"   Camera: {camera_angle}")
        print(f"   Time: {time_of_day}")
        print(f"   Aspect ratio: {aspect_ratio}")

        # Generate with Gemini
        # Send: 1) Site Plan, 2) Lot Map (in that order as prompt specifies)
        result = gemini.generate_content_image(
            prompt_parts=[planning_prompt, site_plan_pil, lot_map_pil],
            model_name=Models.FLASH,  # Use FLASH for faster generation
            temperature=0.4  # Slightly higher for creative planning visualization
        )

        print("✅ Planning render complete")

        return jsonify({
            "generated_image_base64": result,
            "mime_type": "image/png"
        })

    except Exception as e:
        print(f"❌ [PLANNING_RENDER_ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({"error": str(e)}), 500
