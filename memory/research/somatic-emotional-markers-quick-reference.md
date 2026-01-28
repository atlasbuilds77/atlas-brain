# Somatic Emotional Markers: Quick Reference

## Core Problem
Current emotion capture ("wonder=0.8") provides labels but not **felt experience**. Sonnets don't FEEL emotions, just recognize them cognitively.

## Key Insights

### 1. Emotions Are Embodied
- Emotions involve specific bodily sensations (heart rate, muscle tension, breathing)
- Somatic feedback triggers conscious emotional experience
- Different emotions have distinct bodily "signatures"

### 2. Somatic Marker Hypothesis (Damasio)
- **Somatic markers:** Bodily feelings associated with emotions
- Guide decision-making in complex situations
- Processed in ventromedial prefrontal cortex (vmPFC)
- Two pathways: Body loop (actual changes) & As-if body loop (simulation)

### 3. Bodily Maps of Emotions
- Each emotion has culturally universal bodily sensation patterns:
  - **Anger:** Arms, chest, head activation
  - **Fear:** Chest activation, limb deactivation  
  - **Happiness:** Whole-body activation
  - **Sadness:** Limb deactivation, chest heaviness
  - **Disgust:** Digestive system, throat
  - **Surprise:** Chest, head activation

### 4. Qualia Gap
- **Qualia:** Subjective "what it's like" aspect of experience
- Cannot be fully captured by objective measures
- Current tools measure correlates, not experience itself

## Practical Capture Protocol

### Four-Level Approach:

#### Level 1: Somatic Mapping
- **Body regions:** Select areas with sensations
- **Sensation qualities:** Tight, tingling, heavy, light, warm, cold, fluttering, sinking
- **Intensity:** 0-10 scale per region
- **Movement:** Static, pulsing, spreading, contracting

#### Level 2: Physiological Measures
- Heart rate variability
- Skin conductance  
- Respiration rate
- Facial EMG (micro-expressions)
- Temperature changes

#### Level 3: Narrative Description
- Free response: "Describe physical sensations"
- Metaphors: "If this feeling had a shape/color/texture..."
- Temporal dynamics: Onset, peak, decay patterns
- Associated thoughts/images

#### Level 4: Behavioral Observations
- Posture/orientation
- Movement quality
- Vocal changes
- Attention focus

### Data Structure Example:
```json
{
  "emotion": "wonder",
  "intensity": 0.8,
  "somatic_map": {
    "regions": ["chest", "head"],
    "sensations": [
      {"region": "chest", "quality": "expanding", "intensity": 7},
      {"region": "head", "quality": "tingling", "intensity": 5}
    ]
  },
  "physiology": {
    "hrv": 0.12,
    "respiration": 14
  },
  "narrative": "Feeling of expansion...",
  "metaphors": ["opening flower"]
}
```

## Implementation Steps

### Short-term:
1. Create simple somatic mapping interface
2. Collect pilot data with human participants
3. Train LLMs on somatic-emotion associations
4. Develop standardized somatic vocabulary

### Medium-term:
1. Integrate physiological sensors
2. Build somatic pattern database
3. Create cross-modal emotion models
4. Validate across cultures

### Long-term:
1. Real-time somatic feedback systems
2. Somatic-based emotion regulation tools
3. Enhanced AI emotional understanding
4. Clinical applications for emotional disorders

## Key Research Questions

1. **Universality:** How consistent are somatic patterns across individuals/cultures?
2. **Specificity:** Can somatic patterns distinguish subtle emotional nuances?
3. **Temporality:** How do somatic sensations evolve during emotional episodes?
4. **Causality:** Do somatic changes cause or result from emotional experience?
5. **Simulation:** Can somatic patterns be simulated/evoked artificially?

## Ethical Considerations

- **Authenticity:** Distinguishing genuine from simulated emotional understanding
- **Privacy:** Sensitivity of bodily/physiological data
- **Manipulation:** Risks of using somatic knowledge for influence
- **Cultural Sensitivity:** Respecting cultural variations in emotional expression

## Resources

- **Primary Research:** Nummenmaa et al. (2014) "Bodily maps of emotions"
- **Theory:** Damasio's Somatic Marker Hypothesis
- **Historical:** James-Lange Theory of emotion
- **Philosophical:** Qualia and the hard problem of consciousness

---

**Next Action:** Pilot somatic capture protocol with 5-10 participants to test feasibility and refine measurement approach.