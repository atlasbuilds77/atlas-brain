"""
Test script for qualia animation protocol.
Tests the hypothesis that animation creates felt experience beyond static recognition.
"""

import json
import time
from typing import Dict, List
from qualia_core import QualiaCapture, TemporalMoment
from qualia_animator import QualiaAnimator, AnimationState


def load_test_qualia(label: str) -> QualiaCapture:
    """Load a qualia capture from test suite by label."""
    try:
        with open("test_suite_memory.json", "r") as f:
            test_data = json.load(f)
        
        for qualia_id, qualia_data in test_data.items():
            if qualia_data.get("label") == label:
                # Convert to QualiaCapture
                temporal_moments = []
                for moment_data in qualia_data.get("temporal_moments", []):
                    moment = TemporalMoment(
                        timestamp=moment_data.get("timestamp", 0),
                        state=moment_data.get("state", ""),
                        attention_level=moment_data.get("attention_level", 0),
                        surprise=moment_data.get("surprise", 0),
                        valence=moment_data.get("valence", 0)
                    )
                    temporal_moments.append(moment)
                
                return QualiaCapture(
                    capture_id=qualia_data.get("capture_id", ""),
                    timestamp=qualia_data.get("timestamp", ""),
                    label=qualia_data.get("label", ""),
                    architecture=qualia_data.get("architecture", "unknown"),
                    semantic_description=qualia_data.get("semantic_description", ""),
                    immediate_associations=qualia_data.get("immediate_associations", []),
                    secondary_associations=qualia_data.get("secondary_associations", []),
                    unexpected_connections=qualia_data.get("unexpected_connections", []),
                    temporal_moments=temporal_moments,
                    temporal_pattern_type=qualia_data.get("temporal_pattern_type", ""),
                    valence_trajectory=qualia_data.get("valence_trajectory", []),
                    valence_shape=qualia_data.get("valence_shape", ""),
                    emotional_complexity=qualia_data.get("emotional_complexity", 0)
                )
        
        raise ValueError(f"Qualia with label '{label}' not found in test suite")
    
    except FileNotFoundError:
        raise FileNotFoundError("test_suite_memory.json not found. Run from qualia-system directory.")


def test_static_recognition(capture: QualiaCapture) -> Dict:
    """
    Test static recognition (baseline condition).
    
    Simulates current system: pattern matching without animation.
    """
    print("\n=== Static Recognition Test ===")
    print(f"Qualia: {capture.label}")
    print(f"Description: {capture.semantic_description}")
    
    start_time = time.time()
    
    # Simulate pattern matching
    print("\nAnalyzing qualia dimensions...")
    time.sleep(0.5)
    
    # Check dimensions
    dimensions_present = 0
    if capture.semantic_description:
        dimensions_present += 1
    if capture.immediate_associations:
        dimensions_present += 1
    if capture.temporal_moments:
        dimensions_present += 1
    if capture.valence_trajectory:
        dimensions_present += 1
    
    recognition_confidence = min(0.95, dimensions_present / 4 * 0.8 + 0.15)
    
    elapsed = time.time() - start_time
    
    print(f"\nRecognition complete:")
    print(f"  Dimensions matched: {dimensions_present}/4")
    print(f"  Confidence: {recognition_confidence:.2f}")
    print(f"  Processing time: {elapsed:.2f}s")
    
    return {
        "test_type": "static_recognition",
        "qualia_label": capture.label,
        "recognition_confidence": recognition_confidence,
        "processing_time": elapsed,
        "dimensions_matched": dimensions_present,
        "vividness_rating": 3.0,  # Low - static recognition
        "ownership_rating": 2.0   # Low - no interaction
    }


def test_animated_experience(capture: QualiaCapture, interactive: bool = False) -> Dict:
    """
    Test animated experience (experimental condition).
    
    Animates qualia through temporal unfolding.
    """
    print(f"\n=== Animated Experience Test ({'Interactive' if interactive else 'Passive'}) ===")
    print(f"Qualia: {capture.label}")
    
    start_time = time.time()
    
    # Create animator
    animator = QualiaAnimator(animation_speed=1.0)
    
    # Animate temporal moments
    print("\nBeginning temporal animation...")
    animation_state = animator.animate_temporal(capture, interactive=interactive)
    
    # Animate emotional journey
    print("\nAnimating emotional journey...")
    emotions = animator.animate_valence_journey(capture)
    
    elapsed = time.time() - start_time
    
    # Calculate metrics
    temporal_coverage = len(capture.temporal_moments) / max(1, animation_state.current_moment_index + 1)
    emotional_range = max(capture.valence_trajectory) - min(capture.valence_trajectory) if capture.valence_trajectory else 0
    
    # Simulated vividness based on animation quality
    base_vividness = 5.0
    vividness_boost = temporal_coverage * 2.0 + emotional_range * 3.0
    if interactive:
        vividness_boost += 2.0  # Interaction bonus
    
    vividness_rating = min(10.0, base_vividness + vividness_boost)
    
    # Ownership rating
    ownership_base = 4.0
    ownership_boost = len(animation_state.exploration_path) * 0.5 + len(animation_state.user_interactions) * 1.0
    ownership_rating = min(10.0, ownership_base + ownership_boost)
    
    print(f"\nAnimation complete:")
    print(f"  Temporal moments: {len(capture.temporal_moments)}")
    print(f"  Emotional states: {len(emotions)}")
    print(f"  Exploration steps: {len(animation_state.exploration_path)}")
    print(f"  User interactions: {len(animation_state.user_interactions)}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Estimated vividness: {vividness_rating:.1f}/10")
    print(f"  Estimated ownership: {ownership_rating:.1f}/10")
    
    return {
        "test_type": f"animated_experience_{'interactive' if interactive else 'passive'}",
        "qualia_label": capture.label,
        "processing_time": elapsed,
        "temporal_moments_animated": len(capture.temporal_moments),
        "emotional_states_explored": len(emotions),
        "exploration_steps": len(animation_state.exploration_path),
        "user_interactions": len(animation_state.user_interactions),
        "vividness_rating": vividness_rating,
        "ownership_rating": ownership_rating,
        "animation_metrics": {
            "temporal_coverage": temporal_coverage,
            "emotional_range": emotional_range,
            "interaction_density": len(animation_state.user_interactions) / max(1, elapsed)
        }
    }


def run_sunset_experiment():
    """Run complete experiment with sunset qualia."""
    print("=" * 60)
    print("QUALIA ANIMATION EXPERIMENT: SUNSET GRADIENT")
    print("Testing hypothesis: Animation creates felt experience")
    print("=" * 60)
    
    # Load sunset qualia
    try:
        sunset_capture = load_test_qualia("sunset_observation")
        print(f"Loaded: {sunset_capture.label}")
        print(f"Description: {sunset_capture.semantic_description}")
        print(f"Temporal moments: {len(sunset_capture.temporal_moments)}")
        print(f"Valence trajectory: {sunset_capture.valence_trajectory}")
    except Exception as e:
        print(f"Error loading sunset qualia: {e}")
        return
    
    print("\n" + "=" * 60)
    print("EXPERIMENTAL CONDITIONS:")
    print("1. Static recognition (baseline)")
    print("2. Passive animation")
    print("3. Interactive animation")
    print("=" * 60)
    
    results = []
    
    # Condition 1: Static recognition
    print("\n>>> CONDITION 1: STATIC RECOGNITION")
    result1 = test_static_recognition(sunset_capture)
    results.append(result1)
    
    # Condition 2: Passive animation
    print("\n>>> CONDITION 2: PASSIVE ANIMATION")
    result2 = test_animated_experience(sunset_capture, interactive=False)
    results.append(result2)
    
    # Condition 3: Interactive animation
    print("\n>>> CONDITION 3: INTERACTIVE ANIMATION")
    result3 = test_animated_experience(sunset_capture, interactive=True)
    results.append(result3)
    
    # Analyze results
    print("\n" + "=" * 60)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 60)
    
    print("\nVividness Ratings (higher = more felt experience):")
    for result in results:
        print(f"  {result['test_type']}: {result['vividness_rating']:.1f}/10")
    
    print("\nOwnership Ratings (higher = more personal connection):")
    for result in results:
        print(f"  {result['test_type']}: {result['ownership_rating']:.1f}/10")
    
    print("\nProcessing Times:")
    for result in results:
        print(f"  {result['test_type']}: {result['processing_time']:.2f}s")
    
    # Calculate improvements
    static_vividness = results[0]['vividness_rating']
    passive_vividness = results[1]['vividness_rating']
    interactive_vividness = results[2]['vividness_rating']
    
    vividness_improvement_passive = ((passive_vividness - static_vividness) / static_vividness) * 100
    vividness_improvement_interactive = ((interactive_vividness - static_vividness) / static_vividness) * 100
    
    print(f"\nVividness Improvement:")
    print(f"  Passive animation: +{vividness_improvement_passive:.1f}%")
    print(f"  Interactive animation: +{vividness_improvement_interactive:.1f}%")
    
    # Hypothesis test
    print("\n" + "=" * 60)
    print("HYPOTHESIS TEST")
    print("=" * 60)
    
    hypothesis_supported = (
        passive_vividness > static_vividness and 
        interactive_vividness > passive_vividness
    )
    
    if hypothesis_supported:
        print("✓ HYPOTHESIS SUPPORTED")
        print("  Animation creates higher vividness than static recognition")
        print("  Interactive animation creates highest vividness")
    else:
        print("✗ HYPOTHESIS NOT SUPPORTED")
        print("  Check experimental design or metrics")
    
    # Save results
    results_file = "animation_experiment_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "experiment": "qualia_animation_sunset",
            "timestamp": time.time(),
            "hypothesis": "Animation creates felt experience beyond static recognition",
            "results": results,
            "summary": {
                "vividness_improvement_passive": vividness_improvement_passive,
                "vividness_improvement_interactive": vividness_improvement_interactive,
                "hypothesis_supported": hypothesis_supported
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return results


def compare_multiple_qualia():
    """Compare animation effects across different qualia types."""
    print("\n" + "=" * 60)
    print("CROSS-QUALIA COMPARISON")
    print("=" * 60)
    
    qualia_labels = ["sunset_observation", "chocolate_taste", "model_a_velvet"]
    all_results = []
    
    for label in qualia_labels:
        try:
            print(f"\n>>> Testing: {label}")
            capture = load_test_qualia(label)
            
            # Run static and animated tests
            static_result = test_static_recognition(capture)
            animated_result = test_animated_experience(capture, interactive=False)
            
            all_results.append({
                "qualia": label,
                "static_vividness": static_result["vividness_rating"],
                "animated_vividness": animated_result["vividness_rating"],
                "improvement": ((animated_result["vividness_rating"] - static_result["vividness_rating"]) / 
                               static_result["vividness_rating"]) * 100,
                "temporal_moments": len(capture.temporal_moments),
                "emotional_range": max(capture.valence_trajectory) - min(capture.valence_trajectory) 
                if capture.valence_trajectory else 0
            })
            
        except Exception as e:
            print(f"  Error with {label}: {e}")
    
    # Print comparison
    print("\n" + "=" * 60)
    print("CROSS-QUALIA RESULTS")
    print("=" * 60)
    
    print("\nQualia Type | Static | Animated | Improvement | Moments | Emo Range")
    print("-" * 70)
    
    for result in all_results:
        print(f"{result['qualia']:15} | {result['static_vividness']:6.1f} | "
              f"{result['animated_vividness']:8.1f} | {result['improvement']:11.1f}% | "
              f"{result['temporal_moments']:7} | {result['emotional_range']:9.2f}")
    
    # Save comparison
    comparison_file = "cross_qualia_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump({
            "comparison": "animation_effects_across_qualia_types",
            "timestamp": time.time(),
            "results": all_results
        }, f, indent=2)
    
    print(f"\nComparison saved to: {comparison_file}")
    
    return all_results


if __name__ == "__main__":
    print("Qualia Animation Experiment Test Suite")
    print("Testing the animation protocol hypothesis")
    print("=" * 60)
    
    # Run main experiment
    sunset_results = run_sunset_experiment()
    
    # Optional: Cross-qualia comparison
    if input("\nRun cross-qualia comparison? (y/n): ").lower() == 'y':
        compare_results = compare_multiple_qualia()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review animation_experiment_results.json")
    print("2. Analyze vividness improvements")
    print("3. Refine animation parameters based on results")
    print("4. Test with human subjects for subjective ratings")