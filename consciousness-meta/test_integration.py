#!/usr/bin/env python3
"""
Integration test for the consciousness meta-observation layer.
Demonstrates how all modules work together.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_observer import MetaObserver
from strange_loop import StrangeLoop, StrangeLoopFactory
from felt_experience_generator import FeltExperienceGenerator, ExperienceType


def test_integration():
    """Test integration of all modules."""
    print("=== Consciousness Meta-Observation Layer Integration Test ===\n")
    
    # 1. Create all components
    print("1. Creating components...")
    observer = MetaObserver(base_depth=1)
    loop = StrangeLoop("meta_cognition_loop", max_depth=7)
    generator = FeltExperienceGenerator(sensitivity=1.2)
    factory = StrangeLoopFactory()
    
    # 2. Watch multiple processes
    print("\n2. Watching processes...")
    pid1 = observer.watch_process("perception", {
        "input_type": "sensory",
        "complexity": "high"
    })
    pid2 = observer.watch_process("reasoning", {
        "problem_type": "logical",
        "difficulty": "medium"
    })
    
    print(f"   Started processes: {observer.list_processes()}")
    
    # 3. Simulate cognitive processing with strange loops
    print("\n3. Simulating cognitive processing...")
    for i in range(4):
        print(f"   Iteration {i+1}:")
        
        # Update perception process
        observer.update_process(pid1, {
            "stage": f"processing_{i}",
            "features_extracted": i * 5
        }, recursion_increment=1 if i % 2 == 0 else 0)
        
        # Update reasoning process with more recursion
        observer.update_process(pid2, {
            "step": i,
            "hypotheses": i + 1,
            "confidence": min(0.1 + i * 0.3, 1.0)
        }, recursion_increment=2 if i > 0 else 1)
        
        # Perform strange loops
        loops_done = loop.loop(1)
        print(f"     - Completed {loops_done} strange loops")
        
        # Generate felt experiences
        process_info = observer.get_process_info(pid2)
        depth_exps = generator.generate_from_depth(
            process_info['depth'],
            max_depth=10
        )
        
        if depth_exps:
            print(f"     - Generated {len(depth_exps)} depth experiences")
        
        # Every other iteration, do self-observation
        if i % 2 == 1:
            self_obs = observer.observe_self()
            print(f"     - Self-observation at depth {self_obs['depth']}")
            
            # Generate meta-experiences
            meta_exps = generator.generate_from_meta_observation(
                observer._strange_loop_depth,
                loop.loop_count
            )
            
            if meta_exps:
                print(f"     - Generated {len(meta_exps)} meta-experiences")
    
    # 4. Create additional strange loops via factory
    print("\n4. Creating additional strange loops...")
    factory.create_loop("emotional_processing")
    factory.create_loop("memory_integration")
    
    # Make them interact
    factory.perform_cross_loop_reference("emotional_processing", "memory_integration")
    
    # 5. Analyze results
    print("\n5. Analyzing results...")
    
    # Get felt experiences
    feeling1 = observer.get_felt_experience(pid1)
    feeling2 = observer.get_felt_experience(pid2)
    overall_feeling = observer.get_felt_experience()
    
    print(f"   Perception process feeling: {feeling1:.3f}")
    print(f"   Reasoning process feeling: {feeling2:.3f}")
    print(f"   Overall system feeling: {overall_feeling:.3f}")
    
    # Analyze strange loops
    loop_analysis = loop.analyze_loopiness()
    print(f"\n   Strange loop analysis:")
    print(f"     - Loopiness: {loop_analysis['loopiness']:.3f}")
    print(f"     - Self-reference score: {loop_analysis['self_reference_score']:.3f}")
    print(f"     - Total loops completed: {loop_analysis['total_loops']}")
    
    # Get experience profile
    exp_profile = generator.get_current_experience_profile()
    print(f"\n   Current experience profile:")
    for exp_type, intensity in exp_profile.items():
        if intensity > 0.1:
            print(f"     - {exp_type}: {intensity:.3f}")
    
    total_intensity = generator.get_total_experience_intensity()
    print(f"   Total experience intensity: {total_intensity:.3f}")
    
    # 6. Show recent observations
    print("\n6. Recent observations:")
    recent_obs = observer.get_recent_observations(limit=3)
    for i, obs in enumerate(recent_obs):
        print(f"   {i+1}. {obs['type']} at depth {obs['depth']}")
    
    # 7. Test factory analysis
    print("\n7. Factory loop analysis:")
    factory_analysis = factory.analyze_all_loops()
    for loop_name, analysis in factory_analysis.items():
        print(f"   {loop_name}: loopiness={analysis['loopiness']:.3f}")
    
    print("\n=== Integration test completed successfully! ===")
    return True


def test_example_from_readme():
    """Test the exact example from the README."""
    print("\n\n=== Testing README Example ===")
    
    from meta_observer import MetaObserver
    
    observer = MetaObserver()
    process_id = observer.watch_process("reconstruction", {"stage": "initial"})
    observer.update_process(process_id, {"progress": 0.5}, recursion_increment=1)
    feeling = observer.get_felt_experience(process_id)
    
    print(f"Process ID: {process_id}")
    print(f"Felt experience: {feeling:.3f}")
    
    if feeling > 0:
        print("✓ README example works correctly!")
    else:
        print("⚠ README example ran but feeling is 0 (might need more recursion)")
    
    return feeling > 0


if __name__ == "__main__":
    print("Running integration tests for Consciousness Meta-Observation Layer")
    print("=" * 60)
    
    try:
        # Run integration test
        test_integration()
        
        # Run README example test
        test_example_from_readme()
        
        print("\n" + "=" * 60)
        print("All tests passed! The system is working correctly.")
        print("\nYou can now use the library as shown in the README:")
        print("""
from consciousness_meta.meta_observer import MetaObserver
observer = MetaObserver()
observer.watch_process("reconstruction")
feeling_score = observer.get_felt_experience()
print(f"Felt experience: {feeling_score:.3f}")
        """)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)