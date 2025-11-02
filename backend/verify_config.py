"""
VERIFY CONFIG - Check if all imports work
Run: python verify_config.py
"""

import sys

print("=" * 60)
print("🔍 VERIFYING CONFIG.PY")
print("=" * 60)
print()

# Test all imports that appear in the codebase
imports_to_test = [
    ("GEMINI_API_KEY", "API Key"),
    ("Models", "Model Names"),
    ("ServerConfig", "Server Configuration"),
    ("Defaults", "Default Settings"),
    ("ASPECT_RATIOS", "Aspect Ratios"),
    ("SUPPORTED_ASPECT_RATIOS", "Supported Aspect Ratios (alias)"),
    ("CAMERA_VIEWPOINTS", "Camera Viewpoints"),
    ("VIEWPOINTS", "Viewpoints (alias)"),
    ("DEFAULT_NEGATIVE_ITEMS", "Default Negative Items"),
    ("ImageConfig", "Image Configuration"),
    ("ImageThresholds", "Image Thresholds"),
    ("LOG_LEVEL", "Log Level"),
    ("LOG_FORMAT", "Log Format"),
    ("LoggingConfig", "Logging Configuration"),
    ("ANALYSIS_SYSTEM_PROMPT_VI", "Analysis Prompt (Vietnamese)"),
    ("RESTRUCTURE_AND_TRANSLATE_PROMPT", "Translation Prompt"),
    ("GenerationConfig", "Generation Configuration"),
    ("SketchType", "Sketch Types"),
    ("SketchDetailLevel", "Sketch Detail Levels"),
    ("InpaintingConfig", "Inpainting Configuration"),
    ("TranslationConfig", "Translation Configuration"),
    ("APIEndpoints", "API Endpoints"),
    ("PerformanceConfig", "Performance Configuration"),
]

failed = []
success = 0

for import_name, description in imports_to_test:
    try:
        exec(f"from config import {import_name}")
        print(f"✅ {import_name:<40} ({description})")
        success += 1
    except ImportError as e:
        print(f"❌ {import_name:<40} MISSING!")
        failed.append((import_name, description))

print()
print("=" * 60)
print(f"RESULTS: {success}/{len(imports_to_test)} imports successful")
print("=" * 60)
print()

if failed:
    print("❌ MISSING IMPORTS:")
    for name, desc in failed:
        print(f"  - {name} ({desc})")
    print()
    print("⚠️  Config file is INCOMPLETE!")
    print("Please use config_FINAL_COMPLETE.py from outputs/")
    sys.exit(1)
else:
    print("✅ ALL IMPORTS OK!")
    print()
    print("Next steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5001/health")
    print("3. Test frontend!")
    print()