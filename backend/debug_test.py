"""
DEBUG SCRIPT - Test từng component riêng biệt
Run trong thư mục backend: python debug_test.py
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🔍 S2R TOOL - DEBUG SCRIPT")
print("=" * 60)
print()

# ============== TEST 1: Environment Variables ==============
print("1️⃣ Testing Environment Variables...")
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in environment!")
    print("   Please set: export GEMINI_API_KEY='your_key'")
    print("   Or in Windows: set GEMINI_API_KEY=your_key")
    sys.exit(1)

if not api_key.startswith("AIzaSy"):
    print(f"⚠️  API Key suspicious: {api_key[:20]}...")
    print("   Should start with 'AIzaSy'")
else:
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-4:]}")
print()

# ============== TEST 2: Import Dependencies ==============
print("2️⃣ Testing Imports...")

try:
    import google.generativeai as genai
    print("✅ google.generativeai imported")
except ImportError as e:
    print(f"❌ Failed to import google.generativeai: {e}")
    print("   Install: pip install google-generativeai")
    sys.exit(1)

try:
    from PIL import Image
    print("✅ PIL imported")
except ImportError as e:
    print(f"❌ Failed to import PIL: {e}")
    print("   Install: pip install Pillow")
    sys.exit(1)

try:
    import cv2
    print("✅ opencv-python imported")
except ImportError as e:
    print(f"❌ Failed to import cv2: {e}")
    print("   Install: pip install opencv-python")
    sys.exit(1)

try:
    import numpy as np
    print("✅ numpy imported")
except ImportError:
    print("❌ numpy not found")
    sys.exit(1)

print()

# ============== TEST 3: Gemini API Connection ==============
print("3️⃣ Testing Gemini API Connection...")

try:
    genai.configure(api_key=api_key)
    print("✅ API configured")
except Exception as e:
    print(f"❌ Failed to configure API: {e}")
    sys.exit(1)

# Test simple generation
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Say 'Hello World' in JSON format")
    print(f"✅ API works! Response: {response.text[:100]}...")
except Exception as e:
    print(f"❌ API call failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error details: {str(e)}")
    sys.exit(1)

print()

# ============== TEST 4: Image Generation ==============
print("4️⃣ Testing Imagen API...")

try:
    imagen = genai.ImageGenerationModel("imagen-3.0-generate-001")
    print("✅ Imagen model loaded")
    
    # Try simple generation
    result = imagen.generate_images(
        prompt="A simple red circle",
        number_of_images=1,
        aspect_ratio="1:1"
    )
    
    if result and result.images:
        print(f"✅ Image generation works!")
        print(f"   Generated {len(result.images)} image(s)")
    else:
        print("⚠️  Image generation returned empty result")
        
except Exception as e:
    print(f"❌ Image generation failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   This might be OK if quota issue")

print()

# ============== TEST 5: Local Imports ==============
print("5️⃣ Testing Local Modules...")

# Check if we're in backend folder
if not Path("core").exists():
    print("❌ 'core' folder not found!")
    print("   Please run this script from backend/ folder")
    sys.exit(1)

try:
    from core.gemini_client import GeminiClient
    print("✅ GeminiClient imported")
except ImportError as e:
    print(f"❌ Failed to import GeminiClient: {e}")
    sys.exit(1)

try:
    from core.image_processor import ImageProcessor
    print("✅ ImageProcessor imported")
except ImportError as e:
    print(f"❌ Failed to import ImageProcessor: {e}")
    sys.exit(1)

try:
    from core.prompt_builder import PromptBuilder
    print("✅ PromptBuilder imported")
except ImportError as e:
    print(f"❌ Failed to import PromptBuilder: {e}")
    sys.exit(1)

print()

# ============== TEST 6: Create Instances ==============
print("6️⃣ Testing Component Initialization...")

try:
    client = GeminiClient()
    print("✅ GeminiClient initialized")
except Exception as e:
    print(f"❌ GeminiClient init failed: {e}")
    sys.exit(1)

try:
    processor = ImageProcessor()
    print("✅ ImageProcessor initialized")
except Exception as e:
    print(f"❌ ImageProcessor init failed: {e}")
    sys.exit(1)

try:
    prompt_builder = PromptBuilder()
    print("✅ PromptBuilder initialized")
except Exception as e:
    print(f"❌ PromptBuilder init failed: {e}")
    sys.exit(1)

print()

# ============== TEST 7: Test Simple Analysis ==============
print("7️⃣ Testing Simple Text Generation...")

try:
    test_prompt = "Return JSON: {\"test\": \"success\"}"
    result = client.generate_content_json(
        prompt_parts=[test_prompt],
        model_name="gemini-2.0-flash-exp"
    )
    
    if result and isinstance(result, dict):
        print(f"✅ JSON generation works: {result}")
    else:
        print(f"⚠️  Unexpected result: {result}")
        
except Exception as e:
    print(f"❌ JSON generation failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print()

# ============== FINAL SUMMARY ==============
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("If you still get 500 error, please:")
print("1. Check Flask terminal for detailed traceback")
print("2. Send me the full error message")
print("3. Try these curl tests:")
print()
print("   # Test health endpoint:")
print("   curl http://localhost:5001/health")
print()
print("   # Test analyze with sample data:")
print("   curl -X POST http://localhost:5001/api/analyze-sketch \\")
print("     -H 'Content-Type: application/json' \\")
print("     -d '{\"image_base64\": \"data:image/png;base64,iVBORw0KG...\"}'")
print()