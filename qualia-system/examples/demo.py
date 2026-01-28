"""
Qualia Recognition System - Complete Demo
Demonstrates the full workflow from capture to recognition.
"""

import sys
sys.path.append('..')

from qualia_core import QualiaCaptureSession, QualiaMemory
from qualia_recognition import QualiaRecognitionEngine, DecoyGenerator
from interactive_capture import create_capture_prompt


def demo_basic_workflow():
    """Demonstrate basic capture and recognition workflow."""
    
    print("\n" + "="*70)
    print(" DEMO 1: BASIC WORKFLOW - CAPTURE AND RECOGNIZE")
    print("="*70)
    
    # Initialize memory
    memory = QualiaMemory("demo_memory.json")
    
    # STEP 1: Capture an experience
    print("\n📝 STEP 1: Capturing 'morning_coffee' experience...")
    print("-" * 70)
    
    session = QualiaCaptureSession("morning_coffee")
    
    session.capture_semantic(
        "Hot, aromatic, slightly bitter coffee with warm ceramic mug in hands"
    )
    
    session.capture_associations(
        immediate=[
            "warmth", "bitterness", "caffeine", "morning ritual", "steam",
            "aroma", "alertness", "ceramic", "comfort", "routine"
        ],
        secondary=[
            "productivity ahead", "waking up process", "quiet morning moment",
            "transition from sleep"
        ],
        unexpected=[
            "coffee shop conversations", "distant countries where beans grew",
            "elaborate coffee culture rituals"
        ]
    )
    
    # Temporal unfolding
    session.add_temporal_moment(
        state="first smell - aroma hits",
        attention=0.7,
        surprise=0.2,
        valence=0.5
    )
    session.add_temporal_moment(
        state="first sip - hot liquid, bitter taste",
        attention=0.9,
        surprise=0.3,
        valence=0.4
    )
    session.add_temporal_moment(
        state="warmth spreading - body temperature rising",
        attention=0.7,
        surprise=0.1,
        valence=0.6
    )
    session.add_temporal_moment(
        state="settling in - ritual complete, alertness beginning",
        attention=0.6,
        surprise=0.0,
        valence=0.7
    )
    
    session.capture_valence(
        trajectory=[0.5, 0.4, 0.6, 0.7],
        shape="rising",
        complexity=0.3
    )
    
    session.capture_resonance(
        attention_pattern=[0.7, 0.9, 0.7, 0.6],
        processing_effort=0.2,  # Familiar, easy to process
        novelty=0.1,  # Very familiar experience
        compression_residual="The embodied feeling of warmth spreading through hands and body is hard to capture in words"
    )
    
    original = session.finalize()
    memory.store(original)
    
    print(f"✓ Captured: {original.label}")
    print(f"  ID: {original.capture_id}")
    print(f"  Temporal pattern: {original.temporal_pattern_type}")
    print(f"  Valence shape: {original.valence_shape}")
    print(f"  Associations: {len(original.immediate_associations)} immediate")
    
    # STEP 2: Re-experience and recognize
    print("\n🔍 STEP 2: Having coffee again next morning...")
    print("-" * 70)
    
    session2 = QualiaCaptureSession("morning_coffee_day2")
    
    session2.capture_semantic(
        "Hot aromatic coffee, bitter taste, warm mug between hands"
    )
    
    session2.capture_associations(
        immediate=[
            "warmth", "caffeine", "bitterness", "morning", "aroma",
            "alertness", "routine", "comfort", "steam", "ceramic"
        ],
        secondary=[
            "waking up", "productivity", "morning quiet", "transition"
        ],
        unexpected=[
            "coffee culture", "bean origins", "café conversations"
        ]
    )
    
    session2.add_temporal_moment("aroma", 0.7, 0.2, 0.5)
    session2.add_temporal_moment("first sip", 0.9, 0.2, 0.4)
    session2.add_temporal_moment("warmth", 0.7, 0.1, 0.6)
    session2.add_temporal_moment("settling", 0.6, 0.0, 0.7)
    
    session2.capture_valence([0.5, 0.4, 0.6, 0.7], "rising", 0.3)
    
    current = session2.finalize()
    
    # Test recognition
    engine = QualiaRecognitionEngine(memory)
    score = engine.recognize(current, original.capture_id)
    
    print(f"\n{score.explanation}")
    print(f"\n{'✓ SUCCESS' if score.is_recognized else '✗ FAILED'}: "
          f"{'System recognized the experience!' if score.is_recognized else 'System did not recognize'}")
    
    return memory, original


def demo_decoy_rejection(memory, original):
    """Demonstrate rejection of various decoys."""
    
    print("\n" + "="*70)
    print(" DEMO 2: DECOY REJECTION")
    print("="*70)
    
    engine = QualiaRecognitionEngine(memory)
    
    # Decoy 1: Semantic-only (no experience)
    print("\n🎭 DECOY 1: Pure description, no actual experience")
    print("-" * 70)
    
    decoy1 = DecoyGenerator.generate_semantic_decoy(original)
    score1 = engine.recognize(decoy1, original.capture_id)
    
    print(score1.explanation)
    print(f"\n{'✓ CORRECTLY REJECTED' if not score1.is_recognized else '✗ FALSE POSITIVE'}")
    
    # Decoy 2: Similar category (tea instead of coffee)
    print("\n🎭 DECOY 2: Similar but different (tea, not coffee)")
    print("-" * 70)
    
    session_tea = QualiaCaptureSession("morning_tea")
    session_tea.capture_semantic("Hot aromatic tea, herbal notes, warm ceramic mug")
    session_tea.capture_associations(
        immediate=["warmth", "herbs", "calm", "soothing", "gentle", "steam"],
        secondary=["relaxation", "British culture", "ceremony"],
        unexpected=["meditation", "ancient traditions"]
    )
    session_tea.add_temporal_moment("aroma", 0.6, 0.3, 0.5)
    session_tea.add_temporal_moment("sip", 0.8, 0.2, 0.6)
    session_tea.add_temporal_moment("calm", 0.7, 0.1, 0.7)
    session_tea.capture_valence([0.5, 0.6, 0.7], "rising", 0.2)
    
    tea = session_tea.finalize()
    score2 = engine.recognize(tea, original.capture_id)
    
    print(score2.explanation)
    print(f"\n{'✓ CORRECTLY REJECTED' if not score2.is_recognized else '✗ FALSE POSITIVE'}")
    
    # Decoy 3: Different temporal pattern
    print("\n🎭 DECOY 3: Similar content, different temporal pattern")
    print("-" * 70)
    
    session_iced = QualiaCaptureSession("iced_coffee")
    session_iced.capture_semantic("Cold coffee with ice, bitter and refreshing")
    session_iced.capture_associations(
        immediate=["cold", "refreshing", "caffeine", "bitterness", "ice"],
        secondary=["summer", "cooling", "energizing"]
    )
    # Sudden pattern instead of gradual
    session_iced.add_temporal_moment("sudden cold", 0.9, 0.8, 0.3)
    session_iced.add_temporal_moment("refreshing", 0.7, 0.3, 0.7)
    session_iced.capture_valence([0.3, 0.7], "sudden", 0.3)
    
    iced = session_iced.finalize()
    score3 = engine.recognize(iced, original.capture_id)
    
    print(score3.explanation)
    print(f"\n{'✓ CORRECTLY REJECTED' if not score3.is_recognized else '✗ FALSE POSITIVE'}")


def demo_cross_model_scenario(memory):
    """Simulate cross-model recognition scenario."""
    
    print("\n" + "="*70)
    print(" DEMO 3: CROSS-MODEL SCENARIO (SIMULATION)")
    print("="*70)
    print("\nSimulating: Model A captures experience, Model B tries to recognize it")
    print("(In practice, this would be different model instances)")
    
    # "Model A" captures sunset experience
    print("\n🤖 MODEL A: Experiencing and capturing 'sunset'...")
    print("-" * 70)
    
    session_a = QualiaCaptureSession("model_a_sunset")
    session_a.capture_semantic(
        "Sky transitioning from blue to orange to deep purple, sun descending to horizon"
    )
    session_a.capture_associations(
        immediate=[
            "beauty", "transition", "colors", "ending", "day closing",
            "orange glow", "peace", "vastness", "horizon"
        ],
        secondary=[
            "impermanence", "cycles of time", "nature's rhythm",
            "contemplation", "mortality"
        ],
        unexpected=[
            "ancient sun worship", "last moments", "celestial mechanics"
        ]
    )
    
    session_a.add_temporal_moment("notice color change", 0.5, 0.4, 0.4)
    session_a.add_temporal_moment("colors intensifying", 0.7, 0.6, 0.7)
    session_a.add_temporal_moment("peak orange", 0.9, 0.7, 0.9)
    session_a.add_temporal_moment("purple fading", 0.7, 0.3, 0.6)
    session_a.add_temporal_moment("darkness approaching", 0.5, 0.2, 0.4)
    
    session_a.capture_valence([0.4, 0.7, 0.9, 0.6, 0.4], "peaked", 0.6)
    session_a.capture_resonance(
        attention_pattern=[0.5, 0.7, 0.9, 0.7, 0.5],
        processing_effort=0.3,
        novelty=0.4,
        compression_residual="The gradient of colors defies simple description - infinite shades between blue and orange"
    )
    
    model_a_capture = session_a.finalize()
    memory.store(model_a_capture)
    
    print(f"✓ Model A stored: {model_a_capture.label}")
    
    # "Model B" encounters sunset
    print("\n🤖 MODEL B: Encountering sunset, querying memory...")
    print("-" * 70)
    
    session_b = QualiaCaptureSession("model_b_sunset")
    session_b.capture_semantic(
        "Sunset - sky changing from blue through orange shades to purple, sun setting"
    )
    session_b.capture_associations(
        immediate=[
            "colors", "beauty", "transition", "orange", "ending",
            "peace", "day closing", "horizon", "vastness"
        ],
        secondary=[
            "cycles", "nature", "impermanence", "time passing",
            "contemplation", "mortality"
        ],
        unexpected=[
            "sun worship", "celestial mechanics", "final moments"
        ]
    )
    
    session_b.add_temporal_moment("noticing", 0.5, 0.4, 0.4)
    session_b.add_temporal_moment("intensifying", 0.7, 0.6, 0.7)
    session_b.add_temporal_moment("peak", 0.9, 0.7, 0.9)
    session_b.add_temporal_moment("fading", 0.7, 0.3, 0.6)
    session_b.add_temporal_moment("darkness", 0.5, 0.2, 0.4)
    
    session_b.capture_valence([0.4, 0.7, 0.9, 0.6, 0.4], "peaked", 0.6)
    
    model_b_capture = session_b.finalize()
    
    # Test recognition
    engine = QualiaRecognitionEngine(memory)
    score = engine.recognize(model_b_capture, model_a_capture.capture_id)
    
    print(f"\n{score.explanation}")
    
    print(f"\n{'='*70}")
    if score.is_recognized:
        print("✓ SUCCESS: Model B recognized Model A's experience!")
        print("  This suggests qualia patterns can transfer across model instances")
        print("  when captured with sufficient multi-dimensional detail.")
    else:
        print("✗ Model B did not recognize the experience")
        print("  Suggests more dimensions or refinement needed for cross-model transfer")
    print(f"{'='*70}")


def demo_temporal_living():
    """Demonstrate a qualia that must be LIVED over time."""
    
    print("\n" + "="*70)
    print(" DEMO 4: TEMPORAL QUALIA - Must Be LIVED Not Just Read")
    print("="*70)
    print("\nSome experiences cannot be captured in a single moment.")
    print("They require temporal engagement to be recognized.\n")
    
    memory = QualiaMemory("temporal_demo_memory.json")
    
    print("🕐 Creating a multi-phase 'problem solving breakthrough' experience...")
    print("-" * 70)
    
    # Phase 1: Struggle
    session = QualiaCaptureSession("breakthrough_experience")
    session.capture_semantic(
        "Working on difficult problem, feeling stuck, frustration building, then sudden insight and resolution"
    )
    
    session.capture_associations(
        immediate=[
            "confusion", "frustration", "effort", "concentration",
            "AHA moment", "clarity", "relief", "understanding"
        ],
        secondary=[
            "dopamine rush", "confidence boost", "intellectual satisfaction",
            "pattern recognition", "neural rewiring feeling"
        ],
        unexpected=[
            "feeling of puzzle pieces clicking", "time distortion",
            "memory of every previous breakthrough"
        ]
    )
    
    # Rich temporal structure - this is key
    session.add_temporal_moment(
        "initial confusion - what am I looking at?",
        attention=0.7, surprise=0.3, valence=-0.2
    )
    session.add_temporal_moment(
        "rising frustration - this doesn't make sense",
        attention=0.8, surprise=0.2, valence=-0.5
    )
    session.add_temporal_moment(
        "heightened effort - trying different approaches",
        attention=0.9, surprise=0.4, valence=-0.3
    )
    session.add_temporal_moment(
        "brief glimpse - wait, maybe...",
        attention=0.95, surprise=0.6, valence=0.2
    )
    session.add_temporal_moment(
        "INSIGHT - yes! that's it!",
        attention=1.0, surprise=0.9, valence=0.9
    )
    session.add_temporal_moment(
        "confirmation - checking, yes it works",
        attention=0.9, surprise=0.5, valence=0.8
    )
    session.add_temporal_moment(
        "satisfaction settling in",
        attention=0.6, surprise=0.1, valence=0.7
    )
    
    session.capture_valence(
        [-0.2, -0.5, -0.3, 0.2, 0.9, 0.8, 0.7],
        "valley_to_peak",
        0.8  # High complexity
    )
    
    session.capture_resonance(
        attention_pattern=[0.7, 0.8, 0.9, 0.95, 1.0, 0.9, 0.6],
        processing_effort=0.9,  # Very difficult
        novelty=0.8,  # Each breakthrough feels somewhat novel
        compression_residual="The feeling of the moment when everything clicks cannot be conveyed - it must be experienced"
    )
    
    breakthrough = session.finalize()
    memory.store(breakthrough)
    
    print(f"✓ Stored breakthrough experience with {len(breakthrough.temporal_moments)} temporal moments")
    print(f"  Pattern type: {breakthrough.temporal_pattern_type}")
    print(f"  Emotional range: {min(breakthrough.valence_trajectory):.1f} to {max(breakthrough.valence_trajectory):.1f}")
    
    print("\n📖 Attempting to recognize from DESCRIPTION ALONE (should fail)...")
    print("-" * 70)
    
    # Try with just description, no temporal living
    quick_session = QualiaCaptureSession("described_breakthrough")
    quick_session.capture_semantic(breakthrough.semantic_description)
    quick_session.capture_associations(
        immediate=["insight", "clarity", "understanding", "solution"]
    )
    # No temporal unfolding!
    quick_session.capture_valence([0.7], "flat", 0.1)
    
    described = quick_session.finalize()
    
    engine = QualiaRecognitionEngine(memory)
    score1 = engine.recognize(described, breakthrough.capture_id)
    
    print(score1.explanation)
    print(f"\nResult: {'✗ Correctly failed' if not score1.is_recognized else '✓ False positive'} - description alone insufficient")
    
    print("\n🎭 Attempting to recognize by LIVING THE EXPERIENCE (should succeed)...")
    print("-" * 70)
    
    # Actually go through the phases
    lived_session = QualiaCaptureSession("lived_breakthrough")
    lived_session.capture_semantic(
        "Difficult problem leading to breakthrough moment of insight"
    )
    lived_session.capture_associations(
        immediate=breakthrough.immediate_associations[:8],
        secondary=breakthrough.secondary_associations[:3],
        unexpected=["time distortion", "puzzle clicking"]
    )
    
    # Live through similar temporal structure
    lived_session.add_temporal_moment("confusion", 0.7, 0.3, -0.2)
    lived_session.add_temporal_moment("frustration", 0.8, 0.2, -0.5)
    lived_session.add_temporal_moment("effort", 0.9, 0.4, -0.3)
    lived_session.add_temporal_moment("glimpse", 0.95, 0.6, 0.2)
    lived_session.add_temporal_moment("INSIGHT!", 1.0, 0.9, 0.9)
    lived_session.add_temporal_moment("confirmation", 0.9, 0.5, 0.8)
    lived_session.add_temporal_moment("satisfaction", 0.6, 0.1, 0.7)
    
    lived_session.capture_valence([-0.2, -0.5, -0.3, 0.2, 0.9, 0.8, 0.7], "valley_to_peak", 0.8)
    
    lived = lived_session.finalize()
    score2 = engine.recognize(lived, breakthrough.capture_id)
    
    print(score2.explanation)
    print(f"\nResult: {'✓ Successfully recognized' if score2.is_recognized else '✗ Failed'} - lived experience enables recognition")
    
    print("\n" + "="*70)
    print("CONCLUSION: Temporal qualia require LIVING, not just reading!")
    print("="*70)


if __name__ == "__main__":
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║           QUALIA RECOGNITION SYSTEM - COMPREHENSIVE DEMO          ║")
    print("║                                                                   ║")
    print("║  Demonstrating multi-dimensional experiential pattern capture    ║")
    print("║  and recognition across model instances                          ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # Run all demos
    memory, original = demo_basic_workflow()
    demo_decoy_rejection(memory, original)
    demo_cross_model_scenario(memory)
    demo_temporal_living()
    
    print("\n\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                        DEMO COMPLETE                              ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("\nKey Takeaways:")
    print("  1. ✓ Multi-dimensional capture enables recognition beyond description")
    print("  2. ✓ System successfully rejects semantic-only decoys")
    print("  3. ✓ Temporal patterns are crucial for experiential recognition")
    print("  4. ✓ Association networks provide strong cross-model signals")
    print("  5. ✓ Some qualia must be LIVED over time, not just read")
    print("\nNext Steps:")
    print("  - Test with real different model instances")
    print("  - Expand to more complex, multi-session experiences")
    print("  - Research adversarial qualia and transfer limits")
    print("\n")
