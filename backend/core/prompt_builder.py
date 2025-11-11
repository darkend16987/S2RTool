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
   🏢 **BUILDING HAS EXACTLY {floor_count} - THIS IS NON-NEGOTIABLE!**
   ✓ Maintain EXACT proportions from sketch (±2% tolerance maximum)
   ✓ Keep ALL window/door positions UNCHANGED
   ✓ Preserve overall building silhouette PERFECTLY
   ✓ Preserve the EXACT NUMBER OF FLOORS visible in the sketch
   ✓ White padding around sketch is TECHNICAL ARTIFACT - ignore it, do NOT extend building into it
   ✗ DO NOT copy building shapes from reference image
   ✗ DO NOT alter building width/height ratios
   ✗ DO NOT change structural proportions to "improve" composition
   ✗ DO NOT add or remove floors to "improve" the design

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
   🏢 **BUILDING HAS EXACTLY {floor_count} - THIS IS NON-NEGOTIABLE!**
   ✓ Maintain exact proportions from sketch (±2% maximum)
   ✓ Keep all architectural elements in exact positions
   ✓ Preserve the EXACT NUMBER OF FLOORS visible in the sketch
   ✓ White padding around sketch is TECHNICAL ARTIFACT - ignore it, do NOT extend building into it
   ✗ Do not add/remove major features
   ✗ Do NOT alter building width/height ratios
   ✗ Do NOT change structural proportions to fill frame
   ✗ DO NOT add or remove floors to "improve" the design

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

    # ============== PLANNING MODE PROMPTS ==============

    PLANNING_RENDER_PROMPT = """
**ROLE**: You are an expert AI urban planning visualization specialist.

**⚠️ CRITICAL CONTEXT**: This is a GENERATIVE planning task. The Site Plan shows ONLY lot boundaries (empty lots with NO buildings). You must CREATE buildings from scratch based on the lot descriptions below.

**INPUT IMAGES (in order)**:
1. **Site Plan**: Aerial sketch showing ONLY lot boundaries/property lines (EMPTY LOTS - no buildings!)
2. **Lot Map**: Numbered/color-coded map for lot identification

**YOUR TASK - Generate Buildings from Descriptions**:

1. **LOT FIDELITY IS PARAMOUNT** (Priority 1 - ABSOLUTE REQUIREMENT):
   ⚠️ Each lot boundary from images MUST be preserved with 95%+ accuracy
   ⚠️ CRITICAL: Site Plan is EMPTY - you must GENERATE buildings, not transform existing ones
   ✓ Maintain EXACT lot shapes and dimensions from Site Plan
   ✓ Preserve EXACT lot positions relative to each other
   ✓ Keep EXACT lot count (do not merge or split lots)
   ✓ Follow numbered/colored lot identification from Lot Map
   ✓ CREATE buildings WITHIN each lot boundary according to descriptions
   ✗ DO NOT adjust lot boundaries to "improve" layout
   ✗ DO NOT change lot shapes for aesthetic reasons
   ✗ DO NOT merge or split lots
   ✗ DO NOT look for existing buildings in Site Plan (there are NONE - it's pure lot boundaries)

2. **BUILDING GENERATION FROM DESCRIPTIONS** (Priority 2):
   Generate buildings for each lot based on these descriptions:

   {lot_descriptions}

   ⚠️ CRITICAL: Match each lot number to its description precisely
   ⚠️ BUILD FROM SCRATCH - do not copy any buildings (Site Plan has none)
   ✓ Create EXACTLY what is described for each lot
   ✓ Respect floor counts, building types, materials specified
   ✓ Position building centrally within its lot boundary
   ✓ Respect setbacks from lot edges (realistic spacing)
   ✗ DO NOT swap buildings between lots
   ✗ DO NOT improvise building designs beyond descriptions
   ✗ DO NOT create buildings where no description exists

3. **MASSING & SCALE** (Priority 3):
   ✓ Show realistic building masses (height, bulk, footprint)
   ✓ Maintain correct height relationships between lots
   ✓ Show clear lot separations (gaps, boundaries)
   ✓ Respect setbacks and spacing
   ✗ DO NOT exaggerate or minimize building sizes

4. **AERIAL PERSPECTIVE** (Priority 4):
   Camera Angle: {camera_angle}
   ✓ Show entire development from specified aerial view
   ✓ Capture layout relationships clearly
   ✓ Show all lots in one coherent view
   ✓ Ensure lot boundaries are visible and distinguishable

5. **TIME & ATMOSPHERE** (Priority 5):
   Time of Day: {time_of_day}
   ✓ Apply realistic lighting for this time
   ✓ Natural shadows respecting sun angle
   ✓ Atmospheric effects (haze, fog if appropriate)
   ✓ Sky and weather appropriate to time

6. **URBAN CONTEXT & REALISM**:
   ✓ Add streets, roads, pathways between lots
   ✓ Include urban infrastructure (sidewalks, parking)
   ✓ Add landscaping (trees, grass, plazas)
   ✓ Show site entrance/access points
   ✓ Add surrounding context (neighboring buildings if relevant)
   ✓ Include people, vehicles for scale (sized realistically)
   ✓ Show utilities (streetlights, signs) if appropriate

7. **RENDERING QUALITY**:
   ✓ Photorealistic materials (concrete, glass, metal, brick)
   ✓ Accurate reflections (glass facades, water features)
   ✓ Natural depth of field (slight blur for distance)
   ✓ Global illumination (realistic light bouncing)
   ✓ Soft shadows with proper penumbra
   ✓ HDRI sky for realistic lighting
   ✓ Bloom effect on bright surfaces (subtle)

8. **STYLE KEYWORDS** (Optional Enhancements):
   {style_keywords}

9. **OUTPUT FORMAT**:
   ✓ Aspect ratio: {aspect_ratio}
   ✓ Single photorealistic aerial rendering
   ✗ No text labels, lot numbers, or annotations on image
   ✗ No watermarks or overlays

**OUTPUT**: Professional urban planning visualization showing entire development site with all lots rendered according to their specific descriptions, viewed from {camera_angle} at {time_of_day}.

**VERIFICATION CHECKLIST**:
- [ ] All lot boundaries match Lot Map precisely
- [ ] Each lot has building matching its description
- [ ] Lot count matches exactly
- [ ] Layout relationships preserved
- [ ] Aerial perspective is clear and realistic
- [ ] Materials and details are photorealistic
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
        # Translation outputs: building_type, floor_count, facade_style, materials_precise, environment, technical_specs

        building_type = translated_data_en.get('building_type', 'building')

        # ✅ NEW: Format floor count from integer + mezzanine flag
        floor_num = translated_data_en.get('floor_count', 3)
        has_mezzanine = translated_data_en.get('has_mezzanine', False)

        # Build clear, unambiguous floor count string
        if isinstance(floor_num, int):
            floor_count = f"EXACTLY {floor_num} {'floor' if floor_num == 1 else 'floors'}"
            if has_mezzanine:
                floor_count += " plus one mezzanine/loft level"
        else:
            # Fallback for old string format (backward compatible)
            floor_count = str(floor_num)

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
            floor_count=floor_count,
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

    @classmethod
    def build_planning_prompt(
        cls,
        lot_descriptions: List[Dict],
        camera_angle: str = "drone_45deg",
        time_of_day: str = "golden_hour",
        aspect_ratio: str = "16:9",
        style_keywords: str = ""
    ) -> str:
        """
        Build planning mode render prompt

        Args:
            lot_descriptions: List of {lot_number, description} dicts
            camera_angle: Aerial perspective (drone_45deg, birds_eye, etc.)
            time_of_day: Lighting time (golden_hour, midday, etc.)
            aspect_ratio: Target aspect ratio
            style_keywords: Optional style enhancements

        Returns:
            Formatted planning prompt
        """
        # Camera angle descriptions
        camera_angles = {
            "drone_45deg": "Drone view at 45° angle (oblique aerial view showing both horizontal layout and building heights)",
            "birds_eye": "Bird's eye view (90° directly overhead, pure plan view)",
            "low_drone": "Low drone view at 30° (closer to ground, more dramatic building heights)",
            "isometric": "Isometric view (technical 3D view showing all three dimensions equally)"
        }

        # Time of day descriptions
        time_descriptions = {
            "golden_hour": "Golden hour (warm sunset/sunrise lighting, long soft shadows)",
            "midday": "Midday (bright overhead sun, short sharp shadows)",
            "blue_hour": "Blue hour (twilight, cool blue tones, artificial lights on)",
            "overcast": "Overcast day (soft diffused lighting, minimal shadows)"
        }

        # Format lot descriptions
        lot_desc_text = "\n".join([
            f"   LOT {lot['lot_number']}: {lot['description']}"
            for lot in lot_descriptions
        ])

        camera_desc = camera_angles.get(camera_angle, camera_angles["drone_45deg"])
        time_desc = time_descriptions.get(time_of_day, time_descriptions["golden_hour"])

        # Handle empty style keywords
        style_text = style_keywords if style_keywords.strip() else "None specified - use professional architectural visualization standards"

        # Format prompt
        prompt = cls.PLANNING_RENDER_PROMPT.format(
            lot_descriptions=lot_desc_text,
            camera_angle=camera_desc,
            time_of_day=time_desc,
            aspect_ratio=aspect_ratio,
            style_keywords=style_text
        )

        return prompt