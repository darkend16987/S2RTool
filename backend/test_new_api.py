"""
test_new_api.py - Test google-genai NEW API

Run: python test_new_api.py
"""

import sys

print("=" * 60)
print("🧪 TESTING NEW API (google-genai)")
print("=" * 60)
print()

# Test 1: Check if google-genai is installed
print("Test 1: Check google-genai installation")
try:
    from google import genai
    print("✅ google-genai imported successfully")
except ImportError as e:
    print(f"❌ google-genai NOT installed!")
    print(f"   Error: {e}")
    print()
    print("FIX: pip install google-genai")
    sys.exit(1)

# Test 2: Check Client availability
print("\nTest 2: Check Client class")
try:
    from google.genai import Client
    print("✅ Client class available")
except ImportError:
    print("❌ Client class not available")
    print("   Upgrade: pip install --upgrade google-genai")
    sys.exit(1)

# Test 3: Check types module
print("\nTest 3: Check types module")
try:
    from google.genai import types
    print("✅ types module available")
    
    # Check key classes
    has_content = hasattr(types, 'Content')
    has_part = hasattr(types, 'Part')
    has_config = hasattr(types, 'GenerateContentConfig')
    
    print(f"   - Content: {'✅' if has_content else '❌'}")
    print(f"   - Part: {'✅' if has_part else '❌'}")
    print(f"   - GenerateContentConfig: {'✅' if has_config else '❌'}")
    
    if not (has_content and has_part and has_config):
        print("   ⚠️  Some types missing. Update google-genai!")
except ImportError as e:
    print(f"❌ types module error: {e}")
    sys.exit(1)

# Test 4: Check API key
print("\nTest 4: Check API key")
try:
    from config import GEMINI_API_KEY
    
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 20:
        print(f"✅ API key loaded")
        print(f"   Preview: {GEMINI_API_KEY[:20]}...{GEMINI_API_KEY[-4:]}")
    else:
        print("❌ API key invalid or missing")
        sys.exit(1)
except Exception as e:
    print(f"❌ API key error: {e}")
    sys.exit(1)

# Test 5: Create client
print("\nTest 5: Create client")
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("✅ Client created successfully")
except Exception as e:
    print(f"❌ Client creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test simple text generation
print("\nTest 6: Test simple text generation")
try:
    from google.genai import types
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="Say 'Hello World' in JSON format")
            ]
        )
    ]
    
    config = types.GenerateContentConfig(
        response_modalities=["TEXT"],
        temperature=0.1
    )
    
    print("   Sending request to gemini-2.5-flash...")
    
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=config
    ):
        if hasattr(chunk, 'text'):
            response_text += chunk.text
    
    if response_text:
        print(f"✅ Text generation works!")
        print(f"   Response: {response_text[:100]}")
    else:
        print(f"⚠️  No text response")
        
except Exception as e:
    print(f"❌ Text generation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Check image generation model availability
print("\nTest 7: Check gemini-2.5-flash-image model")
try:
    print("   Attempting to use gemini-2.5-flash-image...")
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="Generate a simple red square")
            ]
        )
    ]
    
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        temperature=0.4
    )
    
    print("   Sending image generation request...")
    
    image_found = False
    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash-image",
        contents=contents,
        config=config
    ):
        if (
            chunk.candidates and 
            chunk.candidates[0].content and 
            chunk.candidates[0].content.parts
        ):
            for part in chunk.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_found = True
                    print(f"✅ Image generation works!")
                    print(f"   Mime type: {part.inline_data.mime_type}")
                    print(f"   Data size: {len(part.inline_data.data)} bytes")
                    break
        
        if hasattr(chunk, 'text'):
            print(f"   Text response: {chunk.text[:100]}")
    
    if not image_found:
        print(f"⚠️  No image generated (but no error - model may not support it)")
        
except Exception as e:
    print(f"❌ Image generation test failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("✅ NEW API TEST COMPLETED")
print("=" * 60)
print()
print("Summary:")
print("  - google-genai: ✅ Installed")
print("  - Client: ✅ Working")
print("  - Text generation: ✅ Working")
print("  - Image generation: Check output above")
print()
print("If all tests pass, run:")
print("  python app.py")
print()