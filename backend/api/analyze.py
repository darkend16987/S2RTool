"""
api/analyze.py - Sketch Analysis Endpoint
✅ FIX: Thread-safe instances to prevent race conditions
"""

from flask import Blueprint, request, jsonify

from core.thread_local import get_image_processor, get_prompt_builder, get_gemini_client
from config import Models

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/analyze-sketch', methods=['POST'])
def analyze_sketch():
    """
    Analyze sketch and return Vietnamese description

    Request:
    {
        "image_base64": "..."
    }

    Response:
    {
        "building_type": "...",
        "facade_style": "...",
        "sketch_detail_level": "...",
        ...
    }
    """
    try:
        # ✅ FIX: Get thread-local instances (prevents race conditions)
        processor = get_image_processor()
        prompt_builder = get_prompt_builder()
        gemini = get_gemini_client()

        data = request.json

        if 'image_base64' not in data:
            return jsonify({"error": "Missing image_base64"}), 400

        # Process image
        pil_image, _ = processor.process_base64_image(data['image_base64'])
        if not pil_image:
            return jsonify({"error": "Invalid image"}), 400
        
        # Detect sketch type
        sketch_info = processor.detect_sketch_type(pil_image)
        
        # Resize if needed
        pil_image = processor.resize_image(pil_image, max_size=1024)
        
        # Analyze with Gemini
        analysis_prompt = prompt_builder.build_analysis_prompt()
        
        analysis_result = gemini.generate_content_json(
            prompt_parts=[analysis_prompt, pil_image],
            model_name=Models.PRO,
            temperature=0.3
        )
        
        # Add sketch detection info
        analysis_result['sketch_detail_level'] = sketch_info.detail_level
        analysis_result['is_colored'] = sketch_info.is_colored
        analysis_result['sketch_type'] = sketch_info.sketch_type
        
        return jsonify(analysis_result)
        
    except Exception as e:
        # SỬA LỖI: In lỗi thực sự ra console để debug
        # Chúng ta cần biết lý do API call thất bại (thường là do API key)
        print(f"❌ [ANALYZE_SKETCH_ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({"error": str(e)}), 500
