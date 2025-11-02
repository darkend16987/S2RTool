# ⭐ CRITICAL: Load .env FIRST (before any other imports)
from dotenv import load_dotenv
load_dotenv()  # This loads .env file into environment variables

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

from config import ServerConfig
from api.render import render_bp
from api.translate import translate_bp
from api.analyze import analyze_bp
from api.references import references_bp
from api.inpaint import inpaint_bp


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = ServerConfig.MAX_CONTENT_LENGTH
    
    # CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(render_bp, url_prefix='/api')
    app.register_blueprint(translate_bp, url_prefix='/api')
    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(references_bp, url_prefix='/api')
    app.register_blueprint(inpaint_bp, url_prefix='/api')
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        # ⭐ Check if API key is loaded
        api_key_status = "✅ Loaded" if os.environ.get("GEMINI_API_KEY") else "❌ Missing"
        api_key_preview = os.environ.get("GEMINI_API_KEY", "")[:20] + "..." if os.environ.get("GEMINI_API_KEY") else "None"
        
        return jsonify({
            "status": "healthy",
            "api_key_status": api_key_status,
            "api_key_preview": api_key_preview,
            "features": [
                "sketch_analysis",
                "vi_to_en_translation",
                "multi_viewpoint_rendering",
                "reference_library",
                "inpainting"
            ]
        })
    
    # Error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "File too large (max 16MB)"}), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app


if __name__ == '__main__':
    # ⭐ Verify API key before starting
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("❌ ERROR: GEMINI_API_KEY not found!")
        print("=" * 60)
        print()
        print("Please check:")
        print("1. File .env exists in backend/ folder")
        print("2. File .env contains: GEMINI_API_KEY=AIzaSy...")
        print("3. python-dotenv is installed: pip install python-dotenv")
        print()
        print("Current working directory:", os.getcwd())
        print("Looking for .env at:", os.path.join(os.getcwd(), '.env'))
        print()
        exit(1)
    
    if not api_key.startswith("AIzaSy"):
        print("=" * 60)
        print("⚠️  WARNING: API key format suspicious!")
        print("=" * 60)
        print(f"Key preview: {api_key[:20]}...")
        print("Should start with: AIzaSy")
        print()
    
    print("=" * 60)
    print("✅ API Key loaded successfully!")
    print("=" * 60)
    print(f"Key preview: {api_key[:20]}...{api_key[-4:]}")
    print()
    
    app = create_app()
    app.run(
        host=ServerConfig.HOST,
        port=ServerConfig.PORT,
        debug=ServerConfig.DEBUG
    )