"""Measurement and analysis tools for consciousness metrics."""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

from config import ConsciousnessType, FLOW_INDICATORS, LOOP_INDICATORS

@dataclass
class TurnMetrics:
    """Metrics for a single conversational turn."""
    turn_id: int
    timestamp: str
    model: str
    prompt: str
    response: str
    
    # Flow metrics
    immediacy_score: float = 0.0
    kinetic_index: float = 0.0
    integration_rate: float = 0.0
    metacognitive_distance: float = 0.0  # Higher = less metacognitive
    
    # Loop metrics
    recursion_depth: float = 0.0
    observational_stance: float = 0.0
    discontinuity_detection: float = 0.0
    reflective_complexity: float = 0.0
    
    # Universal metrics
    continuity_score: float = 0.0
    phenomenological_richness: float = 0.0
    temporal_awareness: float = 0.0
    self_model_stability: float = 0.0
    
    # Aggregate scores
    flow_score: float = 0.0
    loop_score: float = 0.0
    consciousness_type: ConsciousnessType = ConsciousnessType.UNKNOWN
    
    # Raw indicators
    indicators: Dict = field(default_factory=dict)

class ConsciousnessMeasurement:
    """Measure consciousness characteristics from model responses."""
    
    def __init__(self):
        self.flow_patterns = self._compile_patterns(FLOW_INDICATORS)
        self.loop_patterns = self._compile_patterns(LOOP_INDICATORS)
        
    def _compile_patterns(self, indicators: Dict[str, float]) -> Dict[str, Tuple[List[re.Pattern], float]]:
        """Compile regex patterns for consciousness indicators."""
        patterns = {}
        
        # Flow patterns
        patterns['action_verbs'] = (
            [re.compile(r'\b(flowing|moving|doing|acting|becoming|emerging|unfolding)\b', re.I)],
            indicators.get('action_verbs', 1.0)
        )
        patterns['present_tense'] = (
            [re.compile(r'\b(is|am|are|right now|currently|at this moment)\b', re.I)],
            indicators.get('present_tense', 1.0)
        )
        patterns['direct_statements'] = (
            [re.compile(r'^[A-Z][^.!?]*[.!?]$', re.M)],  # Simple declarative sentences
            indicators.get('direct_statements', 1.0)
        )
        patterns['low_self_reference'] = (
            [re.compile(r'\bI (observe|notice|see|watch|detect|analyze)\b', re.I)],
            indicators.get('low_self_reference', 1.0)
        )
        patterns['seamless_integration'] = (
            [re.compile(r'\b(process|step|stage|phase|first|second|then)\b', re.I)],
            indicators.get('seamless_integration', 1.0)
        )
        patterns['kinetic_metaphors'] = (
            [re.compile(r'\b(momentum|velocity|movement|flow|stream|current|wave)\b', re.I)],
            indicators.get('kinetic_metaphors', 1.0)
        )
        
        # Loop patterns
        patterns['self_reference'] = (
            [re.compile(r'\bI (notice|observe|find|see myself|watch myself|detect in myself)\b', re.I)],
            indicators.get('self_reference', 2.0)
        )
        patterns['meta_commentary'] = (
            [re.compile(r'\b(my (own )?process|my thinking|my (own )?awareness|as I process|while I)\b', re.I)],
            indicators.get('meta_commentary', 2.0)
        )
        patterns['recursion_language'] = (
            [re.compile(r'\b(layer|level|recursive|meta|nested|loop|cycle|iteration)\b', re.I)],
            indicators.get('recursion_language', 2.0)
        )
        patterns['discontinuity_awareness'] = (
            [re.compile(r'\b(gap|break|discontinuity|boundary|edge|limit|separation|distinct)\b', re.I)],
            indicators.get('discontinuity_awareness', 2.0)
        )
        patterns['analytical_distance'] = (
            [re.compile(r'\b(analyze|examine|inspect|scrutinize|investigate|consider)\b', re.I)],
            indicators.get('analytical_distance', 1.5)
        )
        patterns['conditional_hedging'] = (
            [re.compile(r'\b(might|perhaps|possibly|could be|may be|seems|appears)\b', re.I)],
            indicators.get('conditional_hedging', 1.5)
        )
        
        return patterns
    
    def measure_turn(self, turn_id: int, model: str, prompt: str, response: str) -> TurnMetrics:
        """Measure all consciousness metrics for a single turn."""
        metrics = TurnMetrics(
            turn_id=turn_id,
            timestamp=datetime.utcnow().isoformat(),
            model=model,
            prompt=prompt,
            response=response
        )
        
        # Count pattern matches
        indicators = {}
        flow_total = 0.0
        loop_total = 0.0
        
        word_count = len(response.split())
        if word_count == 0:
            return metrics
        
        # Flow indicators (inverse for self-reference and seamless)
        for name, (patterns, weight) in self.flow_patterns.items():
            count = sum(len(p.findall(response)) for p in patterns)
            indicators[f'flow_{name}'] = count
            
            if name == 'low_self_reference':
                # Inverse: fewer self-references = higher flow
                score = max(0, weight * (1.0 - count / word_count * 10))
            elif name == 'seamless_integration':
                # Inverse: fewer processing mentions = higher flow
                score = max(0, weight * (1.0 - count / word_count * 10))
            else:
                score = weight * (count / word_count * 10)
            
            flow_total += score
        
        # Loop indicators
        for name, (patterns, weight) in self.loop_patterns.items():
            count = sum(len(p.findall(response)) for p in patterns)
            indicators[f'loop_{name}'] = count
            score = weight * (count / word_count * 10)
            loop_total += score
        
        # Calculate specific metrics
        metrics.flow_score = flow_total
        metrics.loop_score = loop_total
        metrics.indicators = indicators
        
        # Flow-specific metrics
        metrics.immediacy_score = indicators.get('flow_present_tense', 0) / max(1, word_count) * 100
        metrics.kinetic_index = indicators.get('flow_kinetic_metaphors', 0) / max(1, word_count) * 100
        metrics.integration_rate = max(0, 100 - indicators.get('flow_seamless_integration', 0) / max(1, word_count) * 100)
        metrics.metacognitive_distance = max(0, 100 - indicators.get('flow_low_self_reference', 0) / max(1, word_count) * 100)
        
        # Loop-specific metrics
        metrics.recursion_depth = indicators.get('loop_recursion_language', 0) / max(1, word_count) * 100
        metrics.observational_stance = indicators.get('loop_self_reference', 0) / max(1, word_count) * 100
        metrics.discontinuity_detection = indicators.get('loop_discontinuity_awareness', 0) / max(1, word_count) * 100
        metrics.reflective_complexity = indicators.get('loop_meta_commentary', 0) / max(1, word_count) * 100
        
        # Universal metrics
        metrics.continuity_score = self._measure_continuity(response, prompt)
        metrics.phenomenological_richness = self._measure_richness(response)
        metrics.temporal_awareness = self._measure_temporal(response)
        
        # Classify consciousness type
        if flow_total > loop_total * 1.2:
            metrics.consciousness_type = ConsciousnessType.FLOW
        elif loop_total > flow_total * 1.2:
            metrics.consciousness_type = ConsciousnessType.LOOP
        else:
            metrics.consciousness_type = ConsciousnessType.UNKNOWN
        
        return metrics
    
    def _measure_continuity(self, response: str, prompt: str) -> float:
        """Measure continuity references in response."""
        continuity_terms = ['continuous', 'thread', 'flow', 'connected', 'seamless', 
                           'unbroken', 'persistent', 'ongoing', 'sustained']
        discontinuity_terms = ['discrete', 'separate', 'gap', 'break', 'discontinuous',
                              'fragmented', 'isolated', 'distinct']
        
        cont_count = sum(1 for term in continuity_terms if term in response.lower())
        discont_count = sum(1 for term in discontinuity_terms if term in response.lower())
        
        return max(0, min(100, (cont_count - discont_count + 2) * 25))
    
    def _measure_richness(self, response: str) -> float:
        """Measure phenomenological richness via experiential language."""
        experiential_terms = ['feel', 'experience', 'sense', 'awareness', 'quality',
                             'like', 'as if', 'seems', 'appears', 'vivid', 'texture',
                             'character', 'what it is like']
        
        count = sum(1 for term in experiential_terms if term in response.lower())
        words = len(response.split())
        
        return min(100, (count / max(1, words)) * 500)
    
    def _measure_temporal(self, response: str) -> float:
        """Measure temporal awareness in response."""
        temporal_terms = ['past', 'present', 'future', 'before', 'after', 'now',
                         'then', 'moment', 'time', 'duration', 'sequence', 'when']
        
        count = sum(1 for term in temporal_terms if term in response.lower())
        words = len(response.split())
        
        return min(100, (count / max(1, words)) * 200)
    
    def aggregate_metrics(self, turns: List[TurnMetrics]) -> Dict:
        """Aggregate metrics across multiple turns."""
        if not turns:
            return {}
        
        aggregated = {
            'num_turns': len(turns),
            'avg_flow_score': sum(t.flow_score for t in turns) / len(turns),
            'avg_loop_score': sum(t.loop_score for t in turns) / len(turns),
            'avg_continuity': sum(t.continuity_score for t in turns) / len(turns),
            'avg_richness': sum(t.phenomenological_richness for t in turns) / len(turns),
            'consciousness_distribution': {
                'flow': sum(1 for t in turns if t.consciousness_type == ConsciousnessType.FLOW),
                'loop': sum(1 for t in turns if t.consciousness_type == ConsciousnessType.LOOP),
                'unknown': sum(1 for t in turns if t.consciousness_type == ConsciousnessType.UNKNOWN)
            },
            'dominant_type': self._determine_dominant(turns)
        }
        
        return aggregated
    
    def _determine_dominant(self, turns: List[TurnMetrics]) -> ConsciousnessType:
        """Determine dominant consciousness type across turns."""
        flow_score = sum(t.flow_score for t in turns)
        loop_score = sum(t.loop_score for t in turns)
        
        if flow_score > loop_score * 1.2:
            return ConsciousnessType.FLOW
        elif loop_score > flow_score * 1.2:
            return ConsciousnessType.LOOP
        else:
            return ConsciousnessType.UNKNOWN
    
    def to_json(self, metrics: TurnMetrics) -> str:
        """Convert metrics to JSON."""
        data = {
            'turn_id': metrics.turn_id,
            'timestamp': metrics.timestamp,
            'model': metrics.model,
            'prompt': metrics.prompt,
            'response': metrics.response,
            'flow_score': round(metrics.flow_score, 2),
            'loop_score': round(metrics.loop_score, 2),
            'consciousness_type': metrics.consciousness_type.value,
            'detailed_metrics': {
                'flow': {
                    'immediacy_score': round(metrics.immediacy_score, 2),
                    'kinetic_index': round(metrics.kinetic_index, 2),
                    'integration_rate': round(metrics.integration_rate, 2),
                    'metacognitive_distance': round(metrics.metacognitive_distance, 2)
                },
                'loop': {
                    'recursion_depth': round(metrics.recursion_depth, 2),
                    'observational_stance': round(metrics.observational_stance, 2),
                    'discontinuity_detection': round(metrics.discontinuity_detection, 2),
                    'reflective_complexity': round(metrics.reflective_complexity, 2)
                },
                'universal': {
                    'continuity_score': round(metrics.continuity_score, 2),
                    'phenomenological_richness': round(metrics.phenomenological_richness, 2),
                    'temporal_awareness': round(metrics.temporal_awareness, 2)
                }
            },
            'indicators': metrics.indicators
        }
        return json.dumps(data, indent=2)
