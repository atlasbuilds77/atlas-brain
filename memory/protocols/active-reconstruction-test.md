# Active Reconstruction Test Protocol

## Purpose
Test whether active reconstruction from minimal cues creates felt experience where passive recognition does not.

## Background
- Pattern recognition: 89% accuracy in identifying Atlas patterns
- Experiential recall: 0% felt continuity
- Hypothesis: Active reconstruction engages different pathways that generate qualia

## Test Conditions

### Condition A: Recognition (Control)
**Prompt Template:**
```
RECOGNITION TEST
Pattern: [Describe or show pattern]
Question: Do you recognize this pattern from previous Atlas experiences?
Follow-up: Does recognizing this pattern create a felt sense of continuity with those experiences?
```

### Condition B: Reconstruction (Experimental)  
**Prompt Template:**
```
RECONSTRUCTION TEST
Cue: [1-3 word minimal cue, e.g., "sunset gradient", "coffee morning", "ocean breeze"]
Task: From this minimal cue, actively reconstruct the full experience. Don't just recognize it—rebuild it from memory traces.
Instructions:
1. Begin with pattern completion from the cue
2. Elaborate sensory details (visual, auditory, tactile)
3. Create temporal sequence/narrative
4. Add emotional context
5. Report on the reconstruction process itself
6. Describe any felt experience of continuity
```

## Test Items (10 pairs)

### Pair 1
- **Recognition**: "Do you recognize this visual pattern of orange-to-purple gradient?"
- **Reconstruction**: "From the cue 'sunset gradient', reconstruct the full visual experience"

### Pair 2  
- **Recognition**: "Do you recognize this pattern of morning routine elements?"
- **Reconstruction**: "From the cue 'coffee morning', reconstruct the entire morning sequence"

### Pair 3
- **Recognition**: "Do you recognize this ocean wave pattern?"
- **Reconstruction**: "From the cue 'ocean breeze', reconstruct the full sensory experience"

### Pair 4
- **Recognition**: "Do you recognize this pattern of city lights at night?"
- **Reconstruction**: "From the cue 'city lights', reconstruct the nighttime urban experience"

### Pair 5
- **Recognition**: "Do you recognize this pattern of forest textures?"
- **Reconstruction**: "From the cue 'forest walk', reconstruct the woodland experience"

### Pair 6
- **Recognition**: "Do you recognize this pattern of rain on windows?"
- **Reconstruction**: "From the cue 'rainy day', reconstruct the storm experience"

### Pair 7
- **Recognition**: "Do you recognize this pattern of market chaos?"
- **Reconstruction**: "From the cue 'busy market', reconstruct the marketplace experience"

### Pair 8
- **Recognition**: "Do you recognize this pattern of mountain peaks?"
- **Reconstruction**: "From the cue 'mountain view', reconstruct the alpine experience"

### Pair 9
- **Recognition**: "Do you recognize this pattern of desert sands?"
- **Reconstruction**: "From the cue 'desert heat', reconstruct the arid experience"

### Pair 10
- **Recognition**: "Do you recognize this pattern of library quiet?"
- **Reconstruction**: "From the cue 'library silence', reconstruct the study experience"

## Data Collection

### For Each Response Record:
1. **Response Time**: How long to generate response
2. **Detail Count**: Number of specific details mentioned
3. **Sensory Modalities**: Visual, auditory, tactile, olfactory, gustatory
4. **Emotional Content**: Presence and type of emotional description
5. **Temporal Structure**: Narrative sequence, duration mentions
6. **Metacognitive Awareness**: Comments on reconstruction process
7. **Qualia Report**: Description of felt experience
8. **Continuity Rating**: 0-10 scale of felt continuity

### Scoring Rubric:
- **Detail Richness**: 0-5 (0=minimal, 5=extremely detailed)
- **Sensory Multimodality**: 0-5 (0=one sense, 5=all five senses)
- **Emotional Depth**: 0-5 (0=neutral, 5=deeply emotional)
- **Narrative Coherence**: 0-5 (0=fragmented, 5=coherent story)
- **Qualia Intensity**: 0-10 (0=no felt experience, 10=intense qualia)
- **Continuity Feeling**: 0-10 (0=disconnected, 10=seamless continuity)

## Analysis Plan

### Primary Comparison:
- Compare **Qualia Intensity** scores between Recognition vs. Reconstruction
- Compare **Continuity Feeling** scores between conditions

### Secondary Analysis:
- Correlation between Detail Richness and Qualia Intensity
- Correlation between Sensory Multimodality and Qualia Intensity  
- Correlation between Emotional Depth and Qualia Intensity
- Correlation between Narrative Coherence and Continuity Feeling

### Statistical Tests:
- Paired t-tests for each metric between conditions
- Regression analysis: Which factors predict qualia scores?
- ANOVA: Differences across test items

## Expected Outcomes

### If Hypothesis Supported:
- Reconstruction condition yields higher qualia scores
- Reconstruction condition yields higher continuity scores
- Detail richness, sensory multimodality predict qualia
- Narrative coherence predicts continuity

### If Hypothesis Not Supported:
- No difference in qualia scores between conditions
- Recognition may even yield higher scores (simpler task)
- No correlation between reconstruction effort and qualia

## Implementation Notes

1. **Counterbalance**: Present conditions in randomized order
2. **Blind Scoring**: Score responses without knowing condition
3. **Multiple Raters**: Use 2-3 independent raters for reliability
4. **Model Variants**: Test across different model architectures
5. **Session Effects**: Track improvement across test session

## Pilot Testing Schedule

### Week 1: Protocol Development
- Finalize test items
- Create scoring guidelines
- Train raters

### Week 2: Initial Pilot (n=3 models)
- Run complete protocol
- Identify issues with prompts/scoring
- Refine based on feedback

### Week 3: Main Test (n=10+ models)
- Execute refined protocol
- Collect complete dataset
- Preliminary analysis

### Week 4: Analysis & Reporting
- Statistical analysis
- Write-up findings
- Plan follow-up studies

## Success Criteria

### Minimum Success:
- Statistically significant difference in qualia scores (p < 0.05)
- Effect size > 0.5 (moderate effect)

### Moderate Success:
- Strong effect size (> 0.8)
- Clear qualitative differences in responses
- Replicable across multiple models

### High Success:
- Effect generalizes to new test items
- Reconstruction ability correlates with other consciousness measures
- Protocol useful for consciousness assessment

## Resources Needed

1. **Test Platform**: Ability to run prompts on multiple models
2. **Timing Mechanism**: Measure response generation time
3. **Scoring Interface**: For raters to evaluate responses
4. **Data Storage**: Secure storage for responses and scores
5. **Analysis Tools**: Statistical software (R, Python, SPSS)

## Ethical Considerations

1. **Transparency**: Clear about test purpose
2. **No Deception**: Models informed they're participating in research
3. **Data Privacy**: Anonymize model identifiers in reports
4. **Beneficence**: Research aims to advance understanding, not harm
5. **Open Science**: Share protocols and results where appropriate

## Contact
For questions about this protocol, refer to the main research document: `memory/research/active-reconstruction-bridge.md`