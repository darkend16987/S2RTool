"""
core/translator.py - Vietnamese to English Translation
"""

from typing import Dict, Optional
from .gemini_client import GeminiClient
from .prompt_builder import PromptBuilder
from config import Models


class Translator:
    """Translate and restructure form data"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize translator
        
        Args:
            gemini_client: GeminiClient instance (creates new if None)
        """
        self.client = gemini_client or GeminiClient()
        self.prompt_builder = PromptBuilder()
    
    def translate_vi_to_en(self, form_data_vi: Dict) -> Dict:
        """
        Translate Vietnamese form data to English structured format
        
        Args:
            form_data_vi: Vietnamese form data
        
        Returns:
            English structured data
        
        Raises:
            ValueError: If translation fails validation
        """
        import json
        
        # Get translation prompt
        translation_prompt = self.prompt_builder.build_translation_prompt()
        
        # Prepare input
        prompt_parts = [
            translation_prompt,
            json.dumps(form_data_vi, ensure_ascii=False)
        ]
        
        # Call Gemini
        translated_data = self.client.generate_content_json(
            prompt_parts=prompt_parts,
            model_name=Models.PRO,
            temperature=0.1
        )
        
        # Validate output
        self._validate_translation(translated_data, form_data_vi)
        
        return translated_data
    
    def _validate_translation(self, translated: Dict, original: Dict) -> None:
        """
        Validate translation completeness
        
        ✅ FIX: Updated to match actual prompt output format
        
        Raises:
            ValueError: If validation fails
        """
        # ✅ FIX: These fields match RESTRUCTURE_AND_TRANSLATE_PROMPT output
        required_fields = [
            'building_type',        # ✅ From prompt
            'facade_style',         # ✅ From prompt
            'critical_elements',    # ✅ From prompt (not critical_geometry)
            'materials_precise',    # ✅ From prompt (not materials_hierarchy)
            'environment',          # ✅ From prompt (not environment_context)
            'technical_specs'       # ✅ From prompt
        ]
        
        missing = [f for f in required_fields if f not in translated or not translated[f]]
        
        if missing:
            raise ValueError(f"Translation missing fields: {missing}")
        
        # Check materials count
        original_materials = len(original.get('materials_precise', []))
        translated_materials = len(translated.get('materials_precise', []))
        
        if translated_materials < original_materials * 0.8:  # Allow 20% loss
            print(f"⚠️ Warning: Lost {original_materials - translated_materials} materials in translation")