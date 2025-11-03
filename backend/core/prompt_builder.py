"""
core/prompt_builder.py - Prompt Engineering & Templates
"""

from typing import Dict, List, Optional, Tuple
from config import CAMERA_VIEWPOINTS, DEFAULT_NEGATIVE_ITEMS


class PromptBuilder:
    """Build optimized prompts for Gemini"""
    
    # ============== RENDER PROMPTS ==============
    
    RENDER_WITH_REFERENCE = """
**ROLE**: You are an expert AI architectural renderer specializing in photorealistic transformations.

**CRITICAL INSTRUCTIONS**:

You are given TWO images in this exact order:
1. **Structural Sketch** (Image 1): Architectural drawing showing form, proportions, and layout
2. **Style Reference** (Image 2): Photo providing style, lighting, materials, and atmosphere

**YOUR TASK - Follow these rules STRICTLY**:

1. **PRESERVE GEOMETRY** (Priority 1 - ABSOLUTE REQUIREMENT):
   ⚠️ SKETCH ADHERENCE LEVEL: {sketch_adherence} (0.5=flexible, 1.0=pixel-perfect)
   ✓ Maintain EXACT proportions from sketch (±2% tolerance maximum)
   ✓ Keep ALL window/door positions UNCHANGED
   ✓ Preserve overall building silhouette PERFECTLY
   ✓ White padding around sketch is TECHNICAL ARTIFACT - ignore it, do NOT extend building into it
   ✗ DO NOT copy building shapes from reference image
   ✗ DO NOT alter building width/height ratios
   ✗ DO NOT change structural proportions to "improve" composition

2. **ADOPT STYLE** (Priority 2):
   ✓ Study reference lighting conditions carefully
   ✓ Apply its color palette and mood
   ✓ Use its material textures (concrete, wood, glass qualities)
   ✓ Replicate environmental context (vegetation, sky, atmosphere)

3. **ENHANCE REALISM** (Priority 3):
   ✓ Add photographic depth of field
   ✓ Include natural shadows and reflections
   ✓ Apply subtle weathering and imperfections
   ✓ Ensure materials look tangible

4. **OUTPUT FORMAT**:
   ✓ Aspect ratio: {aspect_ratio}
   ✓ Single photorealistic image
   ✗ No text, watermarks, or overlays

5. **USER'S SPECIFIC REQUEST**:
   {user_description}

6. **VIEWPOINT SPECIFICATION** (CAMERA ANGLE):
   {viewpoint_instruction}
   ⚠️ This viewpoint overrides any camera angle mentioned in technical specs below

7. **TECHNICAL SPECIFICATIONS**:
   Camera: {camera}
   Lens: {lens}
   Lighting: {lighting}
   Materials: {materials}

8. **ENVIRONMENT & CONTEXT** (CRITICAL - Include ALL of these):
   {environment}

9. **CRITICAL EXCLUSIONS** - DO NOT include any of these:
   {negative_items}

**OUTPUT**: Single photorealistic architectural photograph matching {aspect_ratio} aspect ratio, no text/watermarks
"""

    RENDER_WITHOUT_REFERENCE = """
**ROLE**: You are an expert AI architectural renderer.

**INPUT**: One architectural sketch showing building form and proportions

**YOUR TASK**:

1. **PRESERVE STRUCTURE** (ABSOLUTE REQUIREMENT):
   ⚠️ SKETCH ADHERENCE LEVEL: {sketch_adherence} (0.5=flexible, 1.0=pixel-perfect)
   ✓ Maintain exact proportions from sketch (±2% maximum)
   ✓ Keep all architectural elements in exact positions
   ✓ White padding around sketch is TECHNICAL ARTIFACT - ignore it, do NOT extend building into it
   ✗ Do not add/remove major features
   ✗ Do NOT alter building width/height ratios
   ✗ Do NOT change structural proportions to fill frame

2. **ADD REALISM**:
   ✓ Infer realistic materials based on building type
   ✓ Apply natural lighting conditions
   ✓ Add appropriate context (trees, sky, ground)
   ✓ Include human scale reference if suitable

3. **OUTPUT FORMAT**:
   ✓ Aspect ratio: {aspect_ratio}
   ✓ Single photorealistic image
   ✗ No text, watermarks, or overlays

4. **USER'S REQUEST**:
   {user_description}

5. **VIEWPOINT SPECIFICATION** (CAMERA ANGLE):
   {viewpoint_instruction}
   ⚠️ This viewpoint overrides any camera angle mentioned in technical specs below

6. **TECHNICAL SPECS**:
   Camera: {camera}
   Lens: {lens}
   Lighting: {lighting}
   Materials: {materials}

7. **ENVIRONMENT & CONTEXT** (CRITICAL - Include ALL of these):
   {environment}

8. **AVOID THESE**:
   {negative_items}

**OUTPUT**: Single photorealistic architectural photograph matching {aspect_ratio} aspect ratio
Style: Professional architectural photography (ArchDaily quality)
"""

    # ============== INPAINTING PROMPTS ==============
    
    INPAINT_WITH_REFERENCE = """
**CRITICAL INPAINTING DIRECTIVE WITH STYLE REFERENCE**

You are performing high-fidelity inpainting. Adherence to mask and style is HIGHEST priority.

**INPUT IMAGES (in order)**:
1. **Original Image**: Base image to modify
2. **Mask Image**: Black & white overlay
   - WHITE areas = Edit zone (make changes here)
   - BLACK areas = Protected zone (MUST keep identical)
3. **Style Reference**: Style guidance image

**YOUR TASK**:

1. **FORBIDDEN ZONE**:
   ⚠️ BLACK areas are SACRED - pixels MUST BE IDENTICAL to original
   ⚠️ Any change in black region = FAILURE

2. **USER'S EDIT REQUEST**:
   {edit_instruction}

3. **STYLE APPLICATION**:
   ✓ Adopt style, texture, lighting from reference image
   ✓ Apply to WHITE mask area only
   ✗ Do NOT copy shapes from reference

4. **QUALITY REQUIREMENTS**:
   ✓ Seamless transitions at mask edges
   ✓ Match surrounding lighting/color
   ✓ Photorealistic integration
   ✓ Natural shadows and reflections

**OUTPUT**: Single edited image (white area changed, black area preserved)
"""

    INPAINT_WITHOUT_REFERENCE = """
**CRITICAL INPAINTING DIRECTIVE**

**INPUT IMAGES**:
1. Original image
2. Mask image (black & white)

**STRICT RULES**:

1. **PRIMARY RULE**: 
   Modifications STRICTLY confined to WHITE area of mask

2. **FORBIDDEN ZONE**: 
   BLACK area = NO-CHANGE ZONE
   Pixels MUST BE IDENTICAL to original

3. **USER'S REQUEST**:
   {edit_instruction}

4. **FINAL OUTPUT**: 
   Single image with seamless edit in white area
   Black area perfectly preserved

**OUTPUT**: Edited image with natural transitions
"""
    
    # ============== PUBLIC METHODS ==============
    
    @classmethod
    def build_render_prompt(
        cls,
        translated_data_en: Dict,
        viewpoint: str = "main_facade",
        has_reference: bool = False,
        negative_items: Optional[List[str]] = None,
        sketch_adherence: float = 0.95,
        aspect_ratio: str = "16:9"
    ) -> Tuple[str, str]:
        """
        Build optimized render prompt

        Args:
            translated_data_en: English structured data
            viewpoint: Camera viewpoint key
            has_reference: Whether reference image is provided
            negative_items: Custom negative items (optional)
            sketch_adherence: How strictly to follow sketch (0.5-1.0, default 0.95)
            aspect_ratio: Target aspect ratio (e.g., "16:9")

        Returns:
            (prompt, negative_prompt_summary)
        """
        # ✅ FIX: Extract data from ACTUAL translation output format
        # Translation outputs: building_type, facade_style, materials_precise, environment, technical_specs
        
        building_type = translated_data_en.get('building_type', 'building')
        facade_style = translated_data_en.get('facade_style', 'modern architecture')
        materials = translated_data_en.get('materials_precise', [])
        environment = translated_data_en.get('environment', [])
        tech_specs = translated_data_en.get('technical_specs', {})
        
        # Build user description
        user_description = f"{building_type}, {facade_style}"
        
        # Viewpoint instruction
        viewpoint_info = CAMERA_VIEWPOINTS.get(viewpoint, CAMERA_VIEWPOINTS['main_facade'])
        viewpoint_instruction = viewpoint_info['prompt_addition']
        
        # Technical specs
        camera = tech_specs.get('camera', 'Professional DSLR (Canon 5D Mark IV equivalent)')
        lens = tech_specs.get('lens', '24mm wide-angle lens')
        perspective = tech_specs.get('perspective', 'Two-point perspective')
        
        # Lighting from technical_specs
        lighting = tech_specs.get('lighting', 'natural daylight, golden hour')
        
        # Materials list - handle materials_precise format: {"type": "...", "description": "..."}
        materials_list = ", ".join([
            f"{m.get('type', '')} - {m.get('description', '')[:50]}"
            for m in materials[:3]
            if m.get('type')
        ]) or "context-appropriate materials"

        # ✅ FIX: Environment list - MUST INCLUDE for context (people, vehicles, time of day)
        environment_list = ". ".join([
            f"{e.get('type', '')}: {e.get('description', '')}"
            for e in environment
            if e.get('type') and e.get('description')
        ]) or "urban context"

        # Negative items
        if negative_items is None:
            negative_items = DEFAULT_NEGATIVE_ITEMS
        negative_str = ", ".join(negative_items)

        # Select template
        template = cls.RENDER_WITH_REFERENCE if has_reference else cls.RENDER_WITHOUT_REFERENCE

        # ✅ FIX: Convert sketch_adherence to percentage for clarity in prompt
        adherence_display = f"{sketch_adherence:.2f}"

        # Format prompt
        prompt = template.format(
            sketch_adherence=adherence_display,
            aspect_ratio=aspect_ratio,
            user_description=user_description,
            viewpoint_instruction=viewpoint_instruction,
            camera=camera,
            lens=lens,
            lighting=lighting,
            materials=materials_list,
            environment=environment_list,
            negative_items=negative_str
        )

        return prompt, negative_str
    
    @classmethod
    def build_inpaint_prompt(
        cls,
        edit_instruction: str,
        has_reference: bool = False
    ) -> str:
        """
        Build inpainting prompt
        
        Args:
            edit_instruction: What to do in white area
            has_reference: Whether style reference provided
        
        Returns:
            Formatted prompt
        """
        template = cls.INPAINT_WITH_REFERENCE if has_reference else cls.INPAINT_WITHOUT_REFERENCE
        return template.format(edit_instruction=edit_instruction)
    
    @classmethod
    def build_analysis_prompt(cls) -> str:
        """Get analysis prompt from config"""
        from config import ANALYSIS_SYSTEM_PROMPT_VI
        return ANALYSIS_SYSTEM_PROMPT_VI
    
    @classmethod
    def build_translation_prompt(cls) -> str:
        """Get translation prompt from config"""
        from config import RESTRUCTURE_AND_TRANSLATE_PROMPT
        return RESTRUCTURE_AND_TRANSLATE_PROMPT