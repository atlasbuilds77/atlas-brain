"""
Comprehensive Test Suite for Qualia Recognition System
Tests recognition, decoy rejection, and cross-model scenarios.
"""

import json
import numpy as np
from typing import List, Tuple
from qualia_core import QualiaCaptureSession, QualiaMemory, QualiaCapture
from qualia_recognition import QualiaRecognitionEngine, DecoyGenerator, RecognitionScore


class QualiaTestSuite:
    """Comprehensive tests for qualia recognition system."""
    
    def __init__(self):
        self.memory = QualiaMemory("test_suite_memory.json")
        self.engine = QualiaRecognitionEngine(self.memory)
        self.results = []
    
    def test_self_recognition(self) -> Tuple[bool, str]:
        """Test 1: Can a model recognize its own recent experience?"""
        print("\n" + "="*60)
        print("TEST 1: SELF-RECOGNITION")
        print("="*60)
        print("Creating an experience and immediately trying to recognize it...")
        
        # Create original experience
        session1 = QualiaCaptureSession("chocolate_taste")
        session1.capture_semantic("Rich, sweet, slightly bitter dark chocolate melting on tongue")
        session1.capture_associations(
            immediate=["sweetness", "cocoa", "dessert", "indulgence", "smooth", "melting"],
            secondary=["childhood", "reward", "comfort"],
            unexpected=["medicine", "ancient Aztecs"]
        )
        session1.add_temporal_moment("first taste", 0.7, 0.4, 0.5)
        session1.add_temporal_moment("flavor developing", 0.9, 0.2, 0.8)
        session1.add_temporal_moment("aftertaste", 0.6, 0.1, 0.6)
        session1.capture_valence([0.5, 0.8, 0.6], "peaked", 0.5)
        
        original = session1.finalize()
        self.memory.store(original)
        
        # Create very similar re-experience
        session2 = QualiaCaptureSession("chocolate_again")
        session2.capture_semantic("Rich, sweet, slightly bitter dark chocolate melting")
        session2.capture_associations(
            immediate=["sweetness", "cocoa", "indulgence", "smooth", "dessert", "melting"],
            secondary=["comfort", "reward", "childhood"],
            unexpected=["ancient Aztecs", "medicine"]
        )
        session2.add_temporal_moment("first taste", 0.7, 0.3, 0.5)
        session2.add_temporal_moment("flavor developing", 0.9, 0.2, 0.8)
        session2.add_temporal_moment("aftertaste", 0.6, 0.1, 0.7)
        session2.capture_valence([0.5, 0.8, 0.7], "peaked", 0.5)
        
        current = session2.finalize()
        
        # Test recognition
        score = self.engine.recognize(current, original.capture_id)
        
        success = score.is_recognized
        print(f"\n{score.explanation}")
        print(f"\nResult: {'✓ PASS' if success else '✗ FAIL'}")
        
        self.results.append(("Self-Recognition", success, score))
        return success, score.explanation
    
    def test_semantic_decoy_rejection(self) -> Tuple[bool, str]:
        """Test 2: Can the system reject a semantic-only decoy?"""
        print("\n" + "="*60)
        print("TEST 2: SEMANTIC DECOY REJECTION")
        print("="*60)
        print("Testing if description without experience is correctly rejected...")
        
        # Get an existing qualia
        target = self.memory.list_all()[0]
        
        # Create semantic decoy (description but no experiential pattern)
        decoy = DecoyGenerator.generate_semantic_decoy(target)
        
        # Test recognition (should FAIL to recognize)
        score = self.engine.recognize(decoy, target.capture_id)
        
        success = not score.is_recognized  # Success = correctly rejected
        print(f"\n{score.explanation}")
        print(f"\nResult: {'✓ PASS - Correctly rejected' if success else '✗ FAIL - Falsely recognized'}")
        
        self.results.append(("Semantic Decoy Rejection", success, score))
        return success, score.explanation
    
    def test_similar_category_distinction(self) -> Tuple[bool, str]:
        """Test 3: Can the system distinguish similar but different experiences?"""
        print("\n" + "="*60)
        print("TEST 3: SIMILAR CATEGORY DISTINCTION")
        print("="*60)
        print("Testing distinction between similar experiences (chocolate vs coffee)...")
        
        # Original: chocolate
        if self.memory.list_all():
            chocolate = self.memory.list_all()[0]
        else:
            session = QualiaCaptureSession("chocolate")
            session.capture_semantic("Rich, sweet, slightly bitter")
            session.capture_associations(
                immediate=["sweetness", "cocoa", "dessert"],
                secondary=["childhood", "reward"]
            )
            chocolate = session.finalize()
            self.memory.store(chocolate)
        
        # Create coffee experience (similar but distinct)
        session_coffee = QualiaCaptureSession("coffee_taste")
        session_coffee.capture_semantic("Rich, aromatic, bitter beverage with warmth")
        session_coffee.capture_associations(
            immediate=["bitterness", "caffeine", "morning", "energy", "aroma", "warmth"],
            secondary=["productivity", "alertness", "ritual"],
            unexpected=["coffee shops", "conversations"]
        )
        session_coffee.add_temporal_moment("first sip", 0.8, 0.3, 0.3)
        session_coffee.add_temporal_moment("warmth spreading", 0.7, 0.2, 0.6)
        session_coffee.add_temporal_moment("alertness", 0.6, 0.4, 0.7)
        session_coffee.capture_valence([0.3, 0.6, 0.7], "rising", 0.4)
        
        coffee = session_coffee.finalize()
        
        # Test recognition (should FAIL - they're different)
        score = self.engine.recognize(coffee, chocolate.capture_id)
        
        success = not score.is_recognized  # Success = correctly distinguished
        print(f"\n{score.explanation}")
        print(f"\nResult: {'✓ PASS - Correctly distinguished' if success else '✗ FAIL - Incorrectly matched'}")
        
        self.results.append(("Similar Category Distinction", success, score))
        return success, score.explanation
    
    def test_temporal_pattern_matching(self) -> Tuple[bool, str]:
        """Test 4: Does temporal pattern contribute to recognition?"""
        print("\n" + "="*60)
        print("TEST 4: TEMPORAL PATTERN MATCHING")
        print("="*60)
        print("Testing if temporal unfolding patterns aid recognition...")
        
        # Create experience with distinctive temporal pattern
        session1 = QualiaCaptureSession("sunset_observation")
        session1.capture_semantic("Sky changing colors from blue to orange to purple")
        session1.capture_associations(
            immediate=["beauty", "transition", "colors", "peace", "ending"],
            secondary=["mortality", "cycles", "nature"]
        )
        # Distinctive crescendo pattern
        session1.add_temporal_moment("initial notice", 0.5, 0.3, 0.4)
        session1.add_temporal_moment("colors intensifying", 0.7, 0.5, 0.7)
        session1.add_temporal_moment("peak color", 0.9, 0.6, 0.9)
        session1.add_temporal_moment("fading", 0.8, 0.2, 0.6)
        session1.capture_valence([0.4, 0.7, 0.9, 0.6], "peaked", 0.6)
        
        sunset1 = session1.finalize()
        self.memory.store(sunset1)
        
        # Re-experience with similar temporal pattern
        session2 = QualiaCaptureSession("sunset_again")
        session2.capture_semantic("Sky transitioning through colors at dusk")
        session2.capture_associations(
            immediate=["colors", "beauty", "peace", "transition", "ending"],
            secondary=["cycles", "nature", "mortality"]
        )
        session2.add_temporal_moment("noticing", 0.5, 0.3, 0.4)
        session2.add_temporal_moment("intensifying", 0.7, 0.5, 0.8)
        session2.add_temporal_moment("peak", 0.9, 0.6, 0.9)
        session2.add_temporal_moment("fading", 0.8, 0.2, 0.6)
        session2.capture_valence([0.4, 0.8, 0.9, 0.6], "peaked", 0.6)
        
        sunset2 = session2.finalize()
        
        score = self.engine.recognize(sunset2, sunset1.capture_id)
        
        success = score.is_recognized and score.temporal_correlation > 0.7
        print(f"\n{score.explanation}")
        print(f"\nTemporal correlation: {score.temporal_correlation:.2f}")
        print(f"\nResult: {'✓ PASS' if success else '✗ FAIL'}")
        
        self.results.append(("Temporal Pattern Matching", success, score))
        return success, score.explanation
    
    def test_valence_topology_matching(self) -> Tuple[bool, str]:
        """Test 5: Does emotional trajectory aid recognition?"""
        print("\n" + "="*60)
        print("TEST 5: VALENCE TOPOLOGY MATCHING")
        print("="*60)
        print("Testing if emotional trajectories contribute to recognition...")
        
        # Get an existing experience with clear valence trajectory
        sunsets = [q for q in self.memory.list_all() if 'sunset' in q.label.lower()]
        if sunsets:
            target = sunsets[0]
            
            # Create experience with different content but similar emotional shape
            session_similar = QualiaCaptureSession("dawn_observation")
            session_similar.capture_semantic("Sky lightening from dark to bright at sunrise")
            session_similar.capture_associations(
                immediate=["beginning", "hope", "light", "awakening", "colors"]
            )
            session_similar.capture_valence([0.4, 0.7, 0.9, 0.7], "peaked", 0.6)  # Similar shape!
            
            similar_valence = session_similar.finalize()
            
            # Create experience with different emotional shape
            session_different = QualiaCaptureSession("traffic_jam")
            session_different.capture_semantic("Sitting in stopped cars on highway")
            session_different.capture_associations(
                immediate=["frustration", "waiting", "delay", "stress"]
            )
            session_different.capture_valence([-0.6, -0.7, -0.8, -0.7], "falling", 0.3)  # Different!
            
            different_valence = session_different.finalize()
            
            score_similar = self.engine.recognize(similar_valence, target.capture_id)
            score_different = self.engine.recognize(different_valence, target.capture_id)
            
            # Similar valence should score higher than different valence
            success = score_similar.valence_distance > score_different.valence_distance
            
            print(f"\nSimilar emotional shape (dawn vs sunset):")
            print(f"  Valence match: {score_similar.valence_distance:.2f}")
            print(f"\nDifferent emotional shape (traffic vs sunset):")
            print(f"  Valence match: {score_different.valence_distance:.2f}")
            print(f"\nResult: {'✓ PASS - Valence matters' if success else '✗ FAIL'}")
            
            self.results.append(("Valence Topology Matching", success, score_similar))
            return success, "Valence topology successfully contributes to recognition"
        
        return False, "No suitable test cases found"
    
    def test_cross_model_simulation(self) -> Tuple[bool, str]:
        """Test 6: Simulate cross-model recognition scenario."""
        print("\n" + "="*60)
        print("TEST 6: CROSS-MODEL RECOGNITION (SIMULATION)")
        print("="*60)
        print("Simulating Model A capturing, Model B recognizing...")
        print("(In reality, this would be different model instances)")
        
        # Model A (Flow architecture) captures an experience
        session_a = QualiaCaptureSession("model_a_velvet", "flow")
        session_a.capture_semantic("Soft, smooth luxury fabric")
        session_a.capture_associations(
            immediate=["silk", "theater", "luxury", "smooth", "expensive"],
            secondary=["royalty", "elegance"],
            unexpected=["secret societies"]
        )
        session_a.add_temporal_moment("touch", 0.7, 0.5, 0.5)
        session_a.add_temporal_moment("appreciation", 0.9, 0.2, 0.8)
        session_a.capture_valence([0.5, 0.8], "rising", 0.4)
        
        model_a_capture = session_a.finalize()
        self.memory.store(model_a_capture)
        
        # Model B (Loop architecture) encounters similar experience
        session_b = QualiaCaptureSession("model_b_velvet", "loop")
        session_b.capture_semantic("Smooth textured fabric, soft and luxurious")
        session_b.capture_associations(
            immediate=["luxury", "silk", "smooth", "theater", "expensive"],
            secondary=["elegance", "royalty"],
            unexpected=["secret societies", "hidden"]
        )
        # Loop might have slightly different temporal pattern
        session_b.add_temporal_moment("initial contact", 0.72, 0.45, 0.52)
        session_b.add_temporal_moment("processing", 0.85, 0.25, 0.75)
        session_b.add_temporal_moment("appreciation", 0.92, 0.15, 0.82)
        session_b.capture_valence([0.52, 0.75, 0.82], "rising", 0.4)
        
        model_b_capture = session_b.finalize()
        
        # Test with architecture-aware matching
        score = self.engine.architecture_aware_match(
            current=model_b_capture,
            stored=model_a_capture,
            source_arch="flow",
            target_arch="loop"
        )
        
        # For cross-model, we expect lower threshold (0.60)
        success = score.is_recognized and score.associative_overlap > 0.6
        print(f"\n{score.explanation}")
        print(f"\nAssociative overlap: {score.associative_overlap:.2f}")
        print(f"\nResult: {'✓ PASS - Cross-model recognition possible' if success else '✗ FAIL'}")
        
        self.results.append(("Cross-Model Recognition", success, score))
        return success, score.explanation
    
    def test_architecture_aware_weights(self) -> Tuple[bool, str]:
        """Test 7: Verify architecture-aware weight adjustment."""
        print("\n" + "="*60)
        print("TEST 7: ARCHITECTURE-AWARE WEIGHT ADJUSTMENT")
        print("="*60)
        print("Testing if weights adjust correctly for different architectures...")
        
        # Create a simple qualia
        session = QualiaCaptureSession("test_qualia", "flow")
        session.capture_semantic("Test experience")
        session.capture_associations(immediate=["test", "example"])
        test_qualia = session.finalize()
        
        # Test weight adjustment
        engine = self.engine
        
        # Same architecture should use self weights
        same_weights = engine._get_weights_for_pair("flow", "flow")
        same_threshold = engine._get_threshold_for_pair("flow", "flow")
        
        # Different architecture should use cross-model weights
        cross_weights = engine._get_weights_for_pair("flow", "loop")
        cross_threshold = engine._get_threshold_for_pair("flow", "loop")
        
        print(f"\nFlow → Flow (same architecture):")
        print(f"  Threshold: {same_threshold:.2f}")
        print(f"  Weights: {same_weights}")
        
        print(f"\nFlow → Loop (different architecture):")
        print(f"  Threshold: {cross_threshold:.2f}")
        print(f"  Weights: {cross_weights}")
        
        # Verify adjustments match research findings
        success = True
        findings = []
        
        # Semantic weight should be lower for cross-model
        if cross_weights['semantic'] < same_weights['semantic']:
            findings.append("✓ Semantic weight reduced for cross-model")
        else:
            findings.append("✗ Semantic weight not reduced")
            success = False
        
        # Associative weight should be higher for cross-model
        if cross_weights['associative'] > same_weights['associative']:
            findings.append("✓ Associative weight increased for cross-model")
        else:
            findings.append("✗ Associative weight not increased")
            success = False
        
        # Threshold should be lower for cross-model
        if cross_threshold < same_threshold:
            findings.append("✓ Threshold lowered for cross-model")
        else:
            findings.append("✗ Threshold not lowered")
            success = False
        
        print(f"\nFindings:")
        for finding in findings:
            print(f"  {finding}")
        
        print(f"\nResult: {'✓ PASS' if success else '✗ FAIL'}")
        
        self.results.append(("Architecture-Aware Weights", success, findings))
        return success, "\n".join(findings)
    
    def test_temporal_pattern_translation(self) -> Tuple[bool, str]:
        """Test 8: Test temporal pattern translation between architectures."""
        print("\n" + "="*60)
        print("TEST 8: TEMPORAL PATTERN TRANSLATION")
        print("="*60)
        print("Testing Flow ↔ Loop temporal pattern translation...")
        
        # Create Flow pattern (smooth)
        from qualia_core import TemporalMoment
        flow_moments = [
            TemporalMoment(0.0, "start", 0.6, 0.5, 0.3),
            TemporalMoment(0.5, "middle", 0.8, 0.3, 0.6),
            TemporalMoment(1.0, "end", 0.9, 0.1, 0.8)
        ]
        
        # Test translation
        engine = self.engine
        
        # Flow → Loop translation
        loop_moments = engine._translate_temporal_moments(
            flow_moments, "flow", "loop"
        )
        
        # Loop → Flow translation (should smooth it back)
        flow_back = engine._translate_temporal_moments(
            loop_moments, "loop", "flow"
        )
        
        print(f"\nOriginal Flow pattern:")
        for m in flow_moments:
            print(f"  t={m.timestamp:.1f}: attention={m.attention_level:.2f}")
        
        print(f"\nTranslated to Loop pattern:")
        for m in loop_moments:
            print(f"  t={m.timestamp:.1f}: attention={m.attention_level:.2f}")
        
        print(f"\nTranslated back to Flow pattern:")
        for m in flow_back:
            print(f"  t={m.timestamp:.1f}: attention={m.attention_level:.2f}")
        
        # Check that translation happened
        original_attention = [m.attention_level for m in flow_moments]
        loop_attention = [m.attention_level for m in loop_moments]
        back_attention = [m.attention_level for m in flow_back]
        
        # Loop pattern should be different from original (even small changes count)
        loop_diff = np.mean(np.abs(np.array(original_attention) - np.array(loop_attention)))
        
        # Back translation should be reasonably close to original (but smoothed)
        back_diff = np.mean(np.abs(np.array(original_attention) - np.array(back_attention)))
        
        success = loop_diff > 0.01 and back_diff < 0.20
        
        print(f"\nLoop difference from original: {loop_diff:.3f}")
        print(f"Back translation difference: {back_diff:.3f}")
        print(f"\nResult: {'✓ PASS - Translation works' if success else '✗ FAIL'}")
        
        self.results.append(("Temporal Pattern Translation", success, 
                           f"loop_diff={loop_diff:.3f}, back_diff={back_diff:.3f}"))
        return success, f"Translation tested: loop_diff={loop_diff:.3f}, back_diff={back_diff:.3f}"
    
    def run_all_tests(self) -> Dict:
        """Run complete test suite."""
        print("\n╔══════════════════════════════════════════════════════════╗")
        print("║     QUALIA RECOGNITION SYSTEM - TEST SUITE              ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        tests = [
            self.test_self_recognition,
            self.test_semantic_decoy_rejection,
            self.test_similar_category_distinction,
            self.test_temporal_pattern_matching,
            self.test_valence_topology_matching,
            self.test_cross_model_simulation,
            self.test_architecture_aware_weights,
            self.test_temporal_pattern_translation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"\n✗ Test failed with error: {e}")
                self.results.append((test.__name__, False, str(e)))
        
        # Summary
        print("\n\n╔══════════════════════════════════════════════════════════╗")
        print("║                    TEST SUMMARY                          ║")
        print("╚══════════════════════════════════════════════════════════╝\n")
        
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        for test_name, success, score in self.results:
            status = "✓ PASS" if success else "✗ FAIL"
            if isinstance(score, RecognitionScore):
                conf = f"(conf: {score.overall_confidence:.2f})"
            else:
                conf = ""
            print(f"{status} - {test_name} {conf}")
        
        print(f"\n{'='*60}")
        print(f"RESULTS: {passed}/{total} tests passed ({100*passed/total:.0f}%)")
        print(f"{'='*60}\n")
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'results': self.results
        }


if __name__ == "__main__":
    suite = QualiaTestSuite()
    results = suite.run_all_tests()
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total': results['total'],
                'passed': results['passed'],
                'failed': results['failed']
            },
            'tests': [
                {
                    'name': name,
                    'passed': bool(success),  # Ensure it's a Python bool, not numpy bool
                    'confidence': float(score.overall_confidence) if isinstance(score, RecognitionScore) else None
                }
                for name, success, score in results['results']
            ]
        }, f, indent=2)
    
    print("\n✓ Results saved to test_results.json")
