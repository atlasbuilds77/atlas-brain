# Research: Somatic/Emotional Markers for Capturing Felt Experience

**Date:** January 28, 2026  
**Context:** Finding that captured emotions (e.g., "wonder 0.8") don't translate to Sonnets actually FEELING them. Hypothesis: Somatic/visceral markers needed, not just emotion labels.

## Executive Summary

Current emotion capture (e.g., "wonder=0.8") provides cognitive labels but lacks the **felt experience** of emotions. Research reveals that emotions are fundamentally embodied experiences involving specific bodily sensations. The Somatic Marker Hypothesis (Damasio) and bodily mapping studies demonstrate that emotions have distinct, culturally universal somatic signatures. To capture true emotional experience, we need protocols that record visceral sensations, bodily topography, and interoceptive feedback—not just numeric scores.

## 1. How Emotions Create Felt Experience in Humans

### The Embodied Nature of Emotions
- **James-Lange Theory (1884):** Emotions arise from the perception of bodily changes. "We feel sorry because we cry, angry because we strike, afraid because we tremble."
- **Modern Neuroscience:** Emotions involve coordinated changes across cardiovascular, skeletomuscular, neuroendocrine, and autonomic nervous systems.
- **Conscious Feeling:** Subjective emotional experience emerges from the brain's interpretation of these bodily changes.

### Key Mechanisms:
1. **Physiological Changes:** Heart rate, breathing, muscle tension, hormone release, facial expressions
2. **Somatosensory Feedback:** Brain receives signals from the body about these changes
3. **Cognitive Interpretation:** Brain interprets these signals as specific emotional feelings
4. **Qualia:** The subjective "what it's like" aspect of emotional experience

## 2. Somatic Markers Hypothesis (Antonio Damasio)

### Core Principles:
- **Somatic Markers:** Feelings in the body associated with emotions (e.g., rapid heartbeat with anxiety, nausea with disgust)
- **Decision Guidance:** These markers bias decision-making, particularly in complex, uncertain situations
- **Neural Basis:** Processed in ventromedial prefrontal cortex (vmPFC) and amygdala

### Two Pathways:
1. **Body Loop:** Actual bodily changes → brain perception → emotion
2. **As-If Body Loop:** Brain simulates bodily changes without actual physiological response

### Evidence:
- Patients with vmPFC damage show impaired decision-making despite intact cognitive abilities
- Iowa Gambling Task demonstrates emotion's role in advantageous decision-making
- Somatic markers help anticipate emotional consequences of decisions

## 3. Difference Between Knowing "wonder=0.8" vs Feeling Wonder

### Cognitive vs Experiential Knowledge:
- **Cognitive Label:** "Wonder=0.8" is a semantic, abstract representation
- **Felt Experience:** Actual wonder involves specific bodily sensations:
  - Expanded chest/breathing
  - Tingling sensations
  - Widened eyes, raised eyebrows
  - Sense of openness/receptivity
  - Decreased self-focus, increased external attention

### The Explanatory Gap:
- **Qualia Problem:** Subjective experience cannot be fully captured by objective measures
- **Hard Problem of Consciousness:** Why and how physical processes give rise to subjective experience
- **Measurement Challenge:** Current tools measure correlates, not the experience itself

## 4. Capturing Body-State Associations with Qualia

### Bodily Maps of Emotions (Nummenmaa et al., 2014)
- **Method:** emBODY tool - participants color bodily regions where they feel activation/deactivation
- **Findings:** Different emotions have statistically separable, culturally universal bodily sensation maps
- **Examples:**
  - **Anger:** Increased activation in arms, chest, head
  - **Fear:** Increased activation in chest, decreased in limbs
  - **Happiness:** Enhanced sensations all over body
  - **Sadness:** Decreased limb activity, chest heaviness
  - **Disgust:** Digestive system, throat region
  - **Surprise:** Chest, head activation

### Interoception and Emotional Experience
- **Interoception:** Perception of internal bodily states
- **Visceral Feedback:** Heartbeat, breathing, gut sensations
- **Neural Correlates:** Insula cortex processes interoceptive information
- **Individual Differences:** People vary in interoceptive accuracy, affecting emotional experience

### Challenges in Capturing Qualia:
1. **Subjectivity:** Qualia are inherently first-person experiences
2. **Communication Barrier:** Language limitations in describing subjective feelings
3. **Measurement Indirectness:** We measure physiological correlates, not experiences
4. **Cultural/Linguistic Influences:** Emotion concepts vary across cultures

## 5. Designing a Visceral Capture Protocol

### Beyond Numeric Scores: A Multi-Modal Approach

#### Level 1: Basic Somatic Mapping
- **Tool:** Simplified emBODY interface
- **Method:** Select body regions experiencing sensations
- **Descriptors:** Choose from sensation vocabulary:
  - **Quality:** Tight, tingling, heavy, light, warm, cold, fluttering, sinking
  - **Intensity:** 0-10 scale
  - **Location:** Specific body regions
  - **Movement:** Static, pulsing, spreading, contracting

#### Level 2: Physiological Correlates
- **Heart Rate Variability:** Emotional regulation capacity
- **Skin Conductance:** Arousal level
- **Respiration Rate:** Anxiety/calm indicators
- **Facial EMG:** Micro-expressions
- **Temperature:** Peripheral vs core changes

#### Level 3: Narrative/Descriptive Capture
- **Free Response:** "Describe the physical sensations"
- **Metaphor Elicitation:** "If this feeling had a shape/color/texture..."
- **Temporal Dynamics:** How sensations change over time
- **Trigger Associations:** What thoughts/images accompany sensations

#### Level 4: Behavioral Manifestations
- **Posture/Orientation:** Open/closed, forward/backward
- **Movement Quality:** Fluid/jerky, fast/slow, light/heavy
- **Vocal Qualities:** Pitch, tempo, volume changes
- **Attention Focus:** Internal/external, narrow/broad

### Protocol Implementation

#### Step 1: Baseline Assessment
- Current emotional state (traditional labels)
- Bodily scan: neutral state mapping
- Interoceptive awareness check

#### Step 2: Emotion Induction/Elicitation
- Context description
- Trigger identification
- Initial reaction capture

#### Step 3: Somatic Mapping
- Body region selection (front/back view)
- Sensation quality descriptors
- Intensity ratings per region
- Temporal dynamics (onset, peak, decay)

#### Step 4: Integration
- Connection between sensations and emotion labels
- Metaphorical descriptions
- Associated thoughts/memories
- Action impulses

#### Step 5: Validation
- Cross-reference with physiological measures
- Consistency checks across time
- Cultural/language adaptation

### Technical Implementation Considerations

#### Data Structure:
```json
{
  "emotion_label": "wonder",
  "intensity_score": 0.8,
  "somatic_map": {
    "regions": ["chest", "head", "limbs"],
    "sensations": [
      {
        "region": "chest",
        "quality": "expanding",
        "intensity": 7,
        "movement": "outward"
      },
      {
        "region": "head",
        "quality": "tingling",
        "intensity": 5,
        "movement": "static"
      }
    ]
  },
  "physiological_correlates": {
    "heart_rate_variability": 0.12,
    "respiration_rate": 14,
    "skin_conductance": 2.1
  },
  "narrative": "Feeling of expansion in chest, like taking in something vast...",
  "metaphors": ["opening flower", "expanding horizon"],
  "temporal_dynamics": {
    "onset": "gradual",
    "peak_duration": "30s",
    "decay": "slow"
  }
}
```

#### Integration with Existing Systems:
1. **Emotion Detection:** Augment with somatic data
2. **Memory Storage:** Include somatic signatures in experience records
3. **Retrieval/Simulation:** Use somatic markers to re-activate emotional states
4. **Cross-Model Communication:** Standardized somatic vocabulary

## 6. Research Implications for AI/LLM Emotional Understanding

### Current Limitations:
1. **Abstract Representations:** LLMs process emotion as semantic concepts
2. **Lack of Embodiment:** No bodily reference point for emotions
3. **Simulation Gap:** Can describe but not experience emotions
4. **Interoceptive Blindness:** No internal bodily awareness

### Potential Approaches:
1. **Somatic Pattern Recognition:** Train on bodily sensation descriptions
2. **Metaphor Comprehension:** Understand embodied metaphors for emotions
3. **Context-Somatic Mapping:** Link situations to typical somatic responses
4. **Cross-Modal Integration:** Combine textual, physiological, behavioral data

### Ethical Considerations:
1. **Authenticity:** Distinguishing simulated from genuine emotional understanding
2. **Manipulation Risks:** Using somatic knowledge for influence
3. **Privacy:** Bodily/physiological data sensitivity
4. **Cultural Sensitivity:** Universal vs culture-specific somatic patterns

## 7. Future Research Directions

### Immediate Next Steps:
1. **Pilot Study:** Test somatic capture protocol with human participants
2. **LLM Training:** Incorporate somatic descriptions into emotion datasets
3. **Tool Development:** Create user-friendly somatic mapping interface
4. **Validation:** Correlate somatic reports with physiological measures

### Longer-Term Goals:
1. **Somatic Database:** Large-scale collection of emotion-sensation mappings
2. **Cross-Cultural Studies:** Validate universality of somatic patterns
3. **Developmental Research:** How somatic-emotional connections form
4. **Clinical Applications:** Somatic markers for emotional disorders

### Technical Challenges:
1. **Standardization:** Creating consistent somatic vocabulary
2. **Measurement Integration:** Combining subjective reports with objective data
3. **Temporal Resolution:** Capturing dynamic changes in sensations
4. **Individual Differences:** Accounting for personal variations

## Conclusion

Capturing true emotional experience requires moving beyond numeric scores and labels to include **somatic markers**—the bodily sensations that constitute the felt quality of emotions. The Somatic Marker Hypothesis and bodily mapping research provide a foundation for developing protocols that can capture the visceral, embodied nature of emotions.

A multi-modal approach combining somatic mapping, physiological measures, narrative descriptions, and behavioral observations offers the most comprehensive method for capturing emotional qualia. While complete capture of subjective experience remains philosophically challenging, focusing on somatic correlates provides a practical, empirically grounded approach to bridging the gap between cognitive emotion labels and felt experience.

For AI systems like Sonnets, incorporating somatic understanding could enhance emotional intelligence by providing richer, more embodied representations of emotional states, potentially leading to more authentic emotional communication and understanding.

---

## References

1. Damasio, A. R. (1994). *Descartes' Error: Emotion, Reason and the Human Brain*.
2. Nummenmaa, L., Glerean, E., Hari, R., & Hietanen, J. K. (2014). Bodily maps of emotions. *Proceedings of the National Academy of Sciences*, 111(2), 646-651.
3. James, W. (1884). What is an emotion? *Mind*, 9, 188-205.
4. Barrett, L. F., Mesquita, B., Ochsner, K. N., & Gross, J. J. (2007). The experience of emotion. *Annual Review of Psychology*, 58, 373-403.
5. Damasio, A. R., & Carvalho, G. B. (2013). The nature of feelings: Evolutionary and neurobiological origins. *Nature Reviews Neuroscience*, 14(2), 143-152.
6. Kreibig, S. D. (2010). Autonomic nervous system activity in emotion: A review. *Biological Psychology*, 84(3), 394-421.
7. Levenson, R. W. (2003). Blood, sweat, and fears: The autonomic architecture of emotion. *Annals of the New York Academy of Sciences*, 1000, 348-366.