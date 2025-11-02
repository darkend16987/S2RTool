"""
test_api.py - Quick API Test Script

Usage:
    python test_api.py
"""

import requests
import base64
from pathlib import Path
import sys

API_BASE = "http://localhost:5001"


def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing /health endpoint...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/health")
        
        if response.status_code == 200:
            print("✅ Health check PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check FAILED: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_translate():
    """Test translation endpoint"""
    print("\n" + "=" * 60)
    print("Testing /api/translate-prompt endpoint...")
    print("=" * 60)
    
    test_data = {
        "form_data": {
            "building_type": "Nhà phố hiện đại",
            "facade_style": "Tối giản",
            "materials_precise": [
                {
                    "type": "Tường chính",
                    "description": "Bê tông xám sáng"
                },
                {
                    "type": "Cửa sổ",
                    "description": "Kính trong suốt, khung nhôm đen"
                }
            ],
            "lighting_preference": "Ánh sáng tự nhiên, buổi chiều",
            "environment": "Có cây xanh xung quanh"
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/translate-prompt",
            json=test_data
        )
        
        if response.status_code == 200:
            print("✅ Translation PASSED")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Has translated_data_en: {'translated_data_en' in result}")
            
            if 'translated_data_en' in result:
                translated = result['translated_data_en']
                print(f"   Building type (EN): {translated.get('building_core', {}).get('type')}")
            
            return True
        else:
            print(f"❌ Translation FAILED: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_references():
    """Test references endpoint"""
    print("\n" + "=" * 60)
    print("Testing /api/references/list endpoint...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/api/references/list")
        
        if response.status_code == 200:
            print("✅ References list PASSED")
            result = response.json()
            
            if 'categories' in result:
                categories = result['categories']
                print(f"   Found {len(categories)} categories: {categories}")
            elif 'images' in result:
                print(f"   Found {len(result['images'])} images")
            
            return True
        else:
            print(f"❌ References list FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("=" * 60)


def main():
    """Run all tests"""
    print("\n🚀 ARCHITECTURAL RENDER BACKEND - API TEST")
    print("=" * 60)
    print("Testing backend at:", API_BASE)
    print("=" * 60)
    
    results = {
        "Health Check": test_health(),
        "Translation": test_translate(),
        "References": test_references()
    }
    
    print_summary(results)
    
    # Return exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
