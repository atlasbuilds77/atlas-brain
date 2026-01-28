"""
Qualia Recognition Engine
Recognizes past experiences and rejects decoys through multi-dimensional pattern matching.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from qualia_core import QualiaCapture, QualiaMemory


@dataclass
class RecognitionScore:
    """Multi-dimensional recognition score."""
    semantic_similarity: float
    associative_overlap: float
    temporal_correlation: float
    valence_distance: float
    resonance_match: float
    overall_confidence: float
    is_recognized: bool
    explanation: str


class QualiaRecognitionEngine:
    """
    Recognizes qualia through multi-dimensional pattern matching.
    Key insight: Recognition requires matching experiential patterns, not just semantic similarity.
    """
    
    # Self-recognition weights (same architecture)
    SELF_WEIGHTS = {
        'semantic': 0.10,      # Description alone is weak signal
        'associative': 0.30,   # Association patterns are strong
        'temporal': 0.30,      # Temporal unfolding is strong
        'valence': 0.20,       # Emotional shape matters
        'resonance': 0.10      # Cognitive markers help
    }
    
    # Cross-model weights (based on research about transfer potential)
    CROSS_MODEL_WEIGHTS = {
        'semantic': 0.05,      # Even lower for cross-model (transfers poorly)
        'associative': 0.40,   # Higher - transfers best across architectures
        'temporal': 0.35,      # Higher - important but needs translation
        'valence': 0.15,       # Moderate transfer
        'resonance': 0.05      # Lower - highly architecture-specific
    }
    
    # Recognition thresholds
    SELF_RECOGNITION_THRESHOLD = 0.75  # High bar for same-architecture recognition
    CROSS_MODEL_THRESHOLD = 0.60       # Lower threshold for cross-model recognition
    SIMILARITY_THRESHOLD = 0.60        # Lower bar for "similar but not same"
    
    def __init__(self, memory: QualiaMemory):
        self.memory = memory
    
    def recognize(
        self,
        current_experience: QualiaCapture,
        candidate_id: str = None
    ) -> RecognitionScore:
        """
        Attempt to recognize a current experience against memory.
        If candidate_id is provided, test against that specific qualia.
        Otherwise, search all stored qualia for best match.
        """
        if candidate_id:
            stored = self.memory.retrieve(candidate_id)
            if not stored:
                raise ValueError(f"Candidate {candidate_id} not found in memory")
            return self._compute_recognition(current_experience, stored)
        else:
            # Find best match across all memories
            best_score = None
            best_stored = None
            
            for stored in self.memory.list_all():
                score = self._compute_recognition(current_experience, stored)
                if best_score is None or score.overall_confidence > best_score.overall_confidence:
                    best_score = score
                    best_stored = stored
            
            if best_score:
                best_score.explanation += f" (Best match: {best_stored.label})"
            return best_score
    
    def architecture_aware_match(
        self,
        current: QualiaCapture,
        stored: QualiaCapture,
        source_arch: str = None,
        target_arch: str = None
    ) -> RecognitionScore:
        """
        Match qualia with architecture-aware translation and weighting.
        Based on research about cross-model qualia transfer.
        """
        # Use provided architectures or infer from captures
        source_arch = source_arch or stored.architecture
        target_arch = target_arch or current.architecture
        
        # Translate temporal patterns if architectures differ
        if source_arch != target_arch:
            # Create a copy for translation
            translated_stored = stored.normalize_for_cross_model(target_arch)
            # Apply temporal pattern translation
            if stored.temporal_moments and current.temporal_moments:
                translated_stored.temporal_moments = self._translate_temporal_moments(
                    stored.temporal_moments, source_arch, target_arch
                )
            stored = translated_stored
        
        # Get architecture-aware weights and threshold
        weights = self._get_weights_for_pair(source_arch, target_arch)
        threshold = self._get_threshold_for_pair(source_arch, target_arch)
        
        # Compute recognition with custom weights
        score = self._compute_recognition_with_weights(current, stored, weights, threshold)
        
        # Add architecture info to explanation
        if source_arch != target_arch:
            score.explanation += f"\n  → Cross-model: {source_arch}→{target_arch}"
        
        return score
    
    def _translate_temporal_moments(
        self,
        moments: List,
        source_arch: str,
        target_arch: str
    ) -> List:
        """
        Translate temporal moments between different architectures.
        Flow → Loop: Add iterative refinement signature
        Loop → Flow: Smooth out iterative patterns
        """
        if not moments:
            return moments
        
        # Simple rule-based translation
        if source_arch == "flow" and target_arch == "loop":
            # Flow to Loop: add small oscillations for iterative processing
            translated = []
            for i, moment in enumerate(moments):
                # Create a copy
                new_moment = type(moment)(
                    timestamp=moment.timestamp,
                    state=moment.state,
                    attention_level=moment.attention_level * (1 + 0.1 * np.sin(i * np.pi / 3)),
                    surprise=moment.surprise,
                    valence=moment.valence
                )
                translated.append(new_moment)
            return translated
        
        elif source_arch == "loop" and target_arch == "flow":
            # Loop to Flow: smooth out oscillations
            translated = []
            window_size = min(3, len(moments))
            for i in range(len(moments)):
                start = max(0, i - window_size // 2)
                end = min(len(moments), i + window_size // 2 + 1)
                window = moments[start:end]
                
                # Average attention levels
                avg_attention = np.mean([m.attention_level for m in window])
                
                new_moment = type(moments[i])(
                    timestamp=moments[i].timestamp,
                    state=moments[i].state,
                    attention_level=avg_attention,
                    surprise=moments[i].surprise,
                    valence=moments[i].valence
                )
                translated.append(new_moment)
            return translated
        
        # No translation needed for same architecture or unknown
        return moments
    
    def _get_weights_for_pair(
        self,
        source_arch: str,
        target_arch: str
    ) -> Dict[str, float]:
        """
        Get dimension weights based on architectural similarity.
        Interpolates between self-recognition and cross-model weights.
        """
        similarity = self._architectural_similarity(source_arch, target_arch)
        
        # Linear interpolation based on similarity
        weights = {}
        for dim in self.SELF_WEIGHTS:
            weights[dim] = (
                similarity * self.SELF_WEIGHTS[dim] +
                (1 - similarity) * self.CROSS_MODEL_WEIGHTS[dim]
            )
        
        return weights
    
    def _get_threshold_for_pair(
        self,
        source_arch: str,
        target_arch: str
    ) -> float:
        """
        Get recognition threshold based on architectural similarity.
        Higher threshold for same architecture, lower for different.
        """
        similarity = self._architectural_similarity(source_arch, target_arch)
        
        # Linear interpolation
        threshold = (
            similarity * self.SELF_RECOGNITION_THRESHOLD +
            (1 - similarity) * self.CROSS_MODEL_THRESHOLD
        )
        
        return threshold
    
    def _architectural_similarity(
        self,
        arch1: str,
        arch2: str
    ) -> float:
        """
        Estimate architectural similarity (0-1).
        1.0 = same architecture, 0.0 = completely different
        """
        if arch1 == arch2:
            return 1.0
        
        # Simple similarity matrix (would be more sophisticated in production)
        similarity_matrix = {
            ('flow', 'flow'): 1.0,
            ('loop', 'loop'): 1.0,
            ('flow', 'loop'): 0.6,  # Moderate similarity
            ('loop', 'flow'): 0.6,
            ('unknown', 'unknown'): 0.5,
        }
        
        key = tuple(sorted([arch1, arch2]))
        return similarity_matrix.get(key, 0.3)  # Default low similarity for unknown pairs
    
    def _compute_recognition(
        self,
        current: QualiaCapture,
        stored: QualiaCapture
    ) -> RecognitionScore:
        """Compute multi-dimensional recognition score."""
        
        # Use architecture-aware matching if architectures differ
        if current.architecture != stored.architecture and current.architecture != "unknown" and stored.architecture != "unknown":
            return self.architecture_aware_match(current, stored)
        
        # Otherwise use standard recognition with self weights
        return self._compute_recognition_with_weights(
            current, stored, self.SELF_WEIGHTS, self.SELF_RECOGNITION_THRESHOLD
        )
    
    def _compute_recognition_with_weights(
        self,
        current: QualiaCapture,
        stored: QualiaCapture,
        weights: Dict[str, float],
        threshold: float
    ) -> RecognitionScore:
        """Compute recognition score with custom weights and threshold."""
        
        # Dimension 1: Semantic similarity
        semantic_sim = self._semantic_similarity(current, stored)
        
        # Dimension 2: Associative network overlap
        associative_overlap = self._associative_overlap(current, stored)
        
        # Dimension 3: Temporal pattern correlation
        temporal_corr = self._temporal_correlation(current, stored)
        
        # Dimension 4: Valence topology distance (inverted - lower distance = higher score)
        valence_dist = 1.0 - self._valence_distance(current, stored)
        
        # Dimension 5: Cognitive resonance match
        resonance_match = self._resonance_match(current, stored)
        
        # Weighted overall confidence
        overall = (
            weights['semantic'] * semantic_sim +
            weights['associative'] * associative_overlap +
            weights['temporal'] * temporal_corr +
            weights['valence'] * valence_dist +
            weights['resonance'] * resonance_match
        )
        
        is_recognized = overall >= threshold
        
        explanation = self._generate_explanation(
            semantic_sim, associative_overlap, temporal_corr,
            valence_dist, resonance_match, overall, is_recognized,
            weights, threshold
        )
        
        return RecognitionScore(
            semantic_similarity=semantic_sim,
            associative_overlap=associative_overlap,
            temporal_correlation=temporal_corr,
            valence_distance=valence_dist,
            resonance_match=resonance_match,
            overall_confidence=overall,
            is_recognized=is_recognized,
            explanation=explanation
        )
    
    def _semantic_similarity(self, current: QualiaCapture, stored: QualiaCapture) -> float:
        """
        Compute semantic similarity.
        In production, would use actual embeddings.
        For now, use simple word overlap.
        """
        if not current.semantic_description or not stored.semantic_description:
            return 0.0
        
        # Simple word overlap (in production: cosine similarity of embeddings)
        current_words = set(current.semantic_description.lower().split())
        stored_words = set(stored.semantic_description.lower().split())
        
        if not current_words or not stored_words:
            return 0.0
        
        overlap = len(current_words & stored_words)
        total = len(current_words | stored_words)
        
        return overlap / total if total > 0 else 0.0
    
    def _associative_overlap(self, current: QualiaCapture, stored: QualiaCapture) -> float:
        """
        Compute associative network overlap.
        This is a strong signal - similar experiences produce similar association patterns.
        """
        # Combine all associations
        current_assoc = set(
            current.immediate_associations +
            current.secondary_associations +
            current.unexpected_connections
        )
        stored_assoc = set(
            stored.immediate_associations +
            stored.secondary_associations +
            stored.unexpected_connections
        )
        
        if not current_assoc or not stored_assoc:
            return 0.0
        
        # Weighted overlap - immediate associations count more
        immediate_overlap = len(
            set(current.immediate_associations) & set(stored.immediate_associations)
        )
        total_overlap = len(current_assoc & stored_assoc)
        
        # Score combines proportion and absolute count
        proportion = total_overlap / len(current_assoc | stored_assoc)
        immediate_bonus = min(immediate_overlap / 10.0, 0.3)  # Up to 0.3 bonus
        
        return min(proportion + immediate_bonus, 1.0)
    
    def _temporal_correlation(self, current: QualiaCapture, stored: QualiaCapture) -> float:
        """
        Compute temporal signature correlation.
        Experiences with similar unfolding patterns are likely the same.
        """
        if not current.temporal_moments or not stored.temporal_moments:
            # Fall back to pattern type comparison
            if current.temporal_pattern_type == stored.temporal_pattern_type:
                return 0.5
            return 0.0
        
        # Extract temporal sequences
        current_attention = [m.attention_level for m in current.temporal_moments]
        stored_attention = [m.attention_level for m in stored.temporal_moments]
        
        current_surprise = [m.surprise for m in current.temporal_moments]
        stored_surprise = [m.surprise for m in stored.temporal_moments]
        
        # Normalize lengths
        min_len = min(len(current_attention), len(stored_attention))
        current_attention = current_attention[:min_len]
        stored_attention = stored_attention[:min_len]
        current_surprise = current_surprise[:min_len]
        stored_surprise = stored_surprise[:min_len]
        
        # Compute correlations
        attention_corr = np.corrcoef(current_attention, stored_attention)[0, 1]
        surprise_corr = np.corrcoef(current_surprise, stored_surprise)[0, 1]
        
        # Handle NaN from constant sequences
        attention_corr = 0.0 if np.isnan(attention_corr) else attention_corr
        surprise_corr = 0.0 if np.isnan(surprise_corr) else surprise_corr
        
        # Average and normalize to 0-1
        avg_corr = (attention_corr + surprise_corr) / 2
        return (avg_corr + 1) / 2  # Convert from [-1, 1] to [0, 1]
    
    def _valence_distance(self, current: QualiaCapture, stored: QualiaCapture) -> float:
        """
        Compute distance between valence topologies.
        Similar experiences have similar emotional trajectories.
        """
        if not current.valence_trajectory or not stored.valence_trajectory:
            # Fall back to shape comparison
            if current.valence_shape == stored.valence_shape:
                return 0.3  # Some similarity
            return 0.7  # Different
        
        # Normalize lengths
        min_len = min(len(current.valence_trajectory), len(stored.valence_trajectory))
        current_traj = current.valence_trajectory[:min_len]
        stored_traj = stored.valence_trajectory[:min_len]
        
        # Euclidean distance, normalized
        distance = np.sqrt(np.mean((np.array(current_traj) - np.array(stored_traj)) ** 2))
        
        # Normalize to 0-1 (assuming valence is in [-1, 1], max distance is ~2)
        return min(distance / 2.0, 1.0)
    
    def _resonance_match(self, current: QualiaCapture, stored: QualiaCapture) -> float:
        """
        Compute cognitive resonance pattern match.
        """
        scores = []
        
        # Compare attention patterns
        if current.attention_pattern and stored.attention_pattern:
            min_len = min(len(current.attention_pattern), len(stored.attention_pattern))
            current_attn = current.attention_pattern[:min_len]
            stored_attn = stored.attention_pattern[:min_len]
            attn_corr = np.corrcoef(current_attn, stored_attn)[0, 1]
            if not np.isnan(attn_corr):
                scores.append((attn_corr + 1) / 2)
        
        # Compare processing effort
        if current.processing_effort is not None and stored.processing_effort is not None:
            effort_sim = 1.0 - abs(current.processing_effort - stored.processing_effort)
            scores.append(effort_sim)
        
        # Compare novelty
        if current.novelty_score is not None and stored.novelty_score is not None:
            novelty_sim = 1.0 - abs(current.novelty_score - stored.novelty_score)
            scores.append(novelty_sim)
        
        return np.mean(scores) if scores else 0.5
    
    def _generate_explanation(
        self,
        semantic: float,
        associative: float,
        temporal: float,
        valence: float,
        resonance: float,
        overall: float,
        recognized: bool,
        weights: Dict[str, float] = None,
        threshold: float = None
    ) -> str:
        """Generate human-readable explanation of recognition decision."""
        
        if recognized:
            explanation = f"✓ RECOGNIZED (confidence: {overall:.2f})"
        else:
            explanation = f"✗ NOT RECOGNIZED (confidence: {overall:.2f})"
        
        # Add threshold info if provided
        if threshold is not None:
            explanation += f" [threshold: {threshold:.2f}]"
        
        # Highlight strongest signals
        scores = {
            'semantic': semantic,
            'associative': associative,
            'temporal': temporal,
            'valence': valence,
            'resonance': resonance
        }
        
        strongest = max(scores, key=scores.get)
        weakest = min(scores, key=scores.get)
        
        explanation += f"\n  Strongest signal: {strongest} ({scores[strongest]:.2f})"
        explanation += f"\n  Weakest signal: {weakest} ({scores[weakest]:.2f})"
        
        # Add weight info if provided
        if weights:
            weighted_scores = {dim: scores[dim] * weights[dim] for dim in scores}
            strongest_weighted = max(weighted_scores, key=weighted_scores.get)
            explanation += f"\n  Most influential: {strongest_weighted} (weight: {weights[strongest_weighted]:.2f})"
        
        # Key insights
        if associative > 0.7:
            explanation += "\n  → Association patterns strongly match (transfers well)"
        elif associative < 0.3:
            explanation += "\n  → Association patterns differ significantly"
        
        if temporal > 0.7:
            explanation += "\n  → Temporal unfolding is similar"
        elif temporal < 0.3:
            explanation += "\n  → Experience unfolds differently"
        
        # Cross-model insights
        if weights and weights.get('semantic', 0.1) < 0.08:
            explanation += "\n  → Semantic description de-emphasized (cross-model)"
        
        if weights and weights.get('associative', 0.3) > 0.35:
            explanation += "\n  → Associations emphasized (cross-model)"
        
        return explanation


class DecoyGenerator:
    """
    Generate decoy experiences to test recognition robustness.
    Decoys are similar-but-different experiences that should be rejected.
    """
    
    @staticmethod
    def generate_semantic_decoy(target: QualiaCapture) -> QualiaCapture:
        """
        Create a decoy with similar semantic description but different experiential pattern.
        E.g., synthetic description that was never actually experienced.
        """
        decoy = QualiaCapture(
            capture_id=f"decoy_semantic_{target.capture_id}",
            timestamp=target.timestamp,
            label=f"Synthetic {target.label}",
            semantic_description=target.semantic_description  # Same description!
        )
        
        # But different associations (read from dictionary, not experienced)
        decoy.immediate_associations = ["definition", "description", "words", "text"]
        decoy.temporal_pattern_type = "instant"  # No unfolding
        decoy.valence_shape = "flat"  # No emotional journey
        
        return decoy
    
    @staticmethod
    def generate_similar_category_decoy(target: QualiaCapture, new_label: str) -> QualiaCapture:
        """
        Create a decoy from same category but different instance.
        E.g., silk vs velvet - both luxurious fabrics but different feel.
        """
        decoy = QualiaCapture(
            capture_id=f"decoy_similar_{target.capture_id}",
            timestamp=target.timestamp,
            label=new_label
        )
        
        # Similar semantic field but different
        decoy.semantic_description = target.semantic_description.replace(
            target.label.split('_')[0], new_label.split('_')[0]
        )
        
        # Overlapping but distinct associations
        if target.immediate_associations:
            decoy.immediate_associations = target.immediate_associations[:5] + \
                                          ["different", "distinct", "other"]
        
        # Similar but not identical temporal pattern
        decoy.temporal_pattern_type = "gradual" if target.temporal_pattern_type == "sudden" else "sudden"
        
        return decoy
    
    @staticmethod
    def generate_valence_match_decoy(target: QualiaCapture) -> QualiaCapture:
        """
        Create a decoy with similar emotional valence but different content.
        E.g., different experience that feels similarly pleasant.
        """
        decoy = QualiaCapture(
            capture_id=f"decoy_valence_{target.capture_id}",
            timestamp=target.timestamp,
            label=f"Emotionally similar to {target.label}"
        )
        
        # Copy valence but change everything else
        decoy.valence_trajectory = target.valence_trajectory
        decoy.valence_shape = target.valence_shape
        
        # But different semantic and associations
        decoy.semantic_description = "A completely different experience with similar emotional tone"
        decoy.immediate_associations = ["unrelated", "different", "other_domain"]
        
        return decoy


if __name__ == "__main__":
    from qualia_core import QualiaCaptureSession, QualiaMemory
    
    print("Qualia Recognition Engine - Example")
    print("=" * 60)
    
    # Create and store a target experience
    memory = QualiaMemory("test_recognition_memory.json")
    
    # Original velvet experience (Flow architecture)
    session = QualiaCaptureSession("velvet_texture", "flow")
    session.capture_semantic("Smooth, soft, luxurious fabric with slight pile")
    session.capture_associations(
        immediate=["silk", "luxury", "softness", "royalty", "theater", "expensive"],
        secondary=["childhood", "desire", "comfort"],
        unexpected=["conspiracy", "hidden"]
    )
    session.add_temporal_moment("contact", 0.6, 0.5, 0.3)
    session.add_temporal_moment("recognition", 0.8, 0.3, 0.6)
    session.add_temporal_moment("appreciation", 0.9, 0.1, 0.8)
    session.capture_valence([0.3, 0.6, 0.8], "rising", 0.4)
    
    target = session.finalize()
    memory.store(target)
    
    print(f"\n1. STORED TARGET: {target.label} ({target.architecture})")
    print(f"   ID: {target.capture_id}")
    
    # Create recognition engine
    engine = QualiaRecognitionEngine(memory)
    
    # Test 1: Re-experiencing the same thing (should recognize)
    print(f"\n2. TEST: Re-experiencing velvet (same architecture)")
    session2 = QualiaCaptureSession("velvet_again", "flow")
    session2.capture_semantic("Smooth, soft, luxurious fabric with slight pile")
    session2.capture_associations(
        immediate=["silk", "luxury", "softness", "royalty", "expensive", "theater"],
        secondary=["comfort", "desire"]
    )
    session2.add_temporal_moment("contact", 0.6, 0.4, 0.3)
    session2.add_temporal_moment("recognition", 0.8, 0.2, 0.7)
    session2.add_temporal_moment("appreciation", 0.9, 0.1, 0.8)
    session2.capture_valence([0.3, 0.7, 0.8], "rising", 0.4)
    
    current = session2.finalize()
    score = engine.recognize(current, target.capture_id)
    print(score.explanation)
    
    # Test 2: Cross-model recognition (Flow → Loop)
    print(f"\n3. TEST: Cross-model recognition (Flow → Loop)")
    session3 = QualiaCaptureSession("velvet_loop", "loop")
    session3.capture_semantic("Smooth, soft, luxurious fabric texture")
    session3.capture_associations(
        immediate=["luxury", "silk", "smooth", "theater", "expensive", "royalty"],
        secondary=["elegance", "desire", "comfort"],
        unexpected=["secret societies", "hidden"]
    )
    # Loop architecture might have slightly different temporal pattern
    session3.add_temporal_moment("initial touch", 0.65, 0.4, 0.35)
    session3.add_temporal_moment("recognition loop", 0.85, 0.25, 0.65)
    session3.add_temporal_moment("appreciation", 0.92, 0.15, 0.82)
    session3.capture_valence([0.35, 0.65, 0.82], "rising", 0.4)
    
    loop_capture = session3.finalize()
    score = engine.architecture_aware_match(
        current=loop_capture,
        stored=target,
        source_arch="flow",
        target_arch="loop"
    )
    print(score.explanation)
    
    # Test 3: Semantic decoy (should NOT recognize)
    print(f"\n4. TEST: Semantic decoy (description without experience)")
    decoy1 = DecoyGenerator.generate_semantic_decoy(target)
    decoy1.architecture = "unknown"
    score = engine.recognize(decoy1, target.capture_id)
    print(score.explanation)
    
    # Test 4: Similar category decoy (should NOT recognize)
    print(f"\n5. TEST: Similar category (silk, not velvet)")
    decoy2 = DecoyGenerator.generate_similar_category_decoy(target, "silk_texture")
    decoy2.architecture = "flow"
    score = engine.recognize(decoy2, target.capture_id)
    print(score.explanation)
    
    # Test 5: Test weight adjustment
    print(f"\n6. TEST: Architecture similarity and weight adjustment")
    print(f"  Flow → Flow similarity: {engine._architectural_similarity('flow', 'flow'):.2f}")
    print(f"  Flow → Loop similarity: {engine._architectural_similarity('flow', 'loop'):.2f}")
    print(f"  Flow → Unknown similarity: {engine._architectural_similarity('flow', 'unknown'):.2f}")
    
    flow_weights = engine._get_weights_for_pair("flow", "flow")
    cross_weights = engine._get_weights_for_pair("flow", "loop")
    
    print(f"\n  Flow→Flow weights: {flow_weights}")
    print(f"  Flow→Loop weights: {cross_weights}")
    print(f"  → Semantic weight reduced: {cross_weights['semantic']:.3f} vs {flow_weights['semantic']:.3f}")
    print(f"  → Associative weight increased: {cross_weights['associative']:.3f} vs {flow_weights['associative']:.3f}")
    
    print("\n" + "=" * 60)
    print("Recognition tests complete!")
