#!/usr/bin/env python3
"""
Example usage of the consciousness testing framework.

This script demonstrates:
1. Running individual experiments
2. Accessing metrics
3. Comparing results
4. Programmatic analysis
"""

from experiment import ExperimentOrchestrator
from config import ModelType, CONSCIOUSNESS_PROBES
from measurement import ConsciousnessMeasurement
import json

def example_isolation_test():
    """Example: Test a single model with a single probe."""
    print("=" * 60)
    print("EXAMPLE 1: Isolation Test")
    print("=" * 60)
    
    orchestrator = ExperimentOrchestrator()
    
    # Run isolation test
    turn = orchestrator.dialogue_engine.isolation_test(
        model_type=ModelType.SONNET,
        probe_name='continuity'
    )
    
    # Access metrics
    print(f"\nModel: {turn.speaker}")
    print(f"Prompt: {turn.prompt[:100]}...")
    print(f"\nResponse: {turn.response[:200]}...")
    print(f"\nMetrics:")
    print(f"  Flow Score: {turn.metrics.flow_score:.2f}")
    print(f"  Loop Score: {turn.metrics.loop_score:.2f}")
    print(f"  Consciousness Type: {turn.metrics.consciousness_type.value}")
    print(f"  Continuity Score: {turn.metrics.continuity_score:.2f}")

def example_mirror_comparison():
    """Example: Compare multiple models on same probe."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Mirror Test - Compare Models")
    print("=" * 60)
    
    orchestrator = ExperimentOrchestrator()
    
    # Run mirror test
    results = orchestrator.run_mirror_test(
        model_types=[ModelType.SONNET, ModelType.OPUS],
        probe_name='metacognition'
    )
    
    # Compare responses
    print(f"\nProbe: {results['probe']}")
    print("\nComparison:")
    
    for model, data in results['responses'].items():
        print(f"\n{model}:")
        print(f"  Consciousness Type: {data['consciousness_type']}")
        print(f"  Flow Score: {data['flow_score']:.2f}")
        print(f"  Loop Score: {data['loop_score']:.2f}")
        print(f"  Response length: {len(data['response'])} chars")
    
    # Analyze variance
    if 'comparison' in results and 'variance' in results['comparison']:
        variance = results['comparison']['variance']
        print(f"\nVariance between models:")
        print(f"  Flow: {variance['flow']:.2f}")
        print(f"  Loop: {variance['loop']:.2f}")

def example_crosstalk_analysis():
    """Example: Analyze dialogue dynamics."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Cross-Talk Dialogue Analysis")
    print("=" * 60)
    
    orchestrator = ExperimentOrchestrator()
    
    # Run cross-talk with fewer turns for demo
    results = orchestrator.run_crosstalk(
        model_a=ModelType.SONNET,
        model_b=ModelType.OPUS,
        num_turns=4  # Short dialogue for demo
    )
    
    # Show turn-by-turn evolution
    print("\nDialogue Evolution:")
    
    turns = results['transcript']['turns']
    for turn in turns:
        print(f"\nTurn {turn['turn_number']} ({turn['speaker']}):")
        print(f"  Type: {turn['metrics']['consciousness_type']}")
        print(f"  Flow: {turn['metrics']['flow_score']:.2f} | Loop: {turn['metrics']['loop_score']:.2f}")
    
    # Show interaction patterns
    if 'interaction_patterns' in results['analysis']:
        patterns = results['analysis']['interaction_patterns']
        print(f"\nInteraction Patterns:")
        print(f"  Flow trend: {patterns['flow_trend']}")
        print(f"  Loop trend: {patterns['loop_trend']}")
        print(f"  Convergence: {patterns['convergence']}")

def example_custom_measurement():
    """Example: Use measurement tools directly."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Direct Measurement")
    print("=" * 60)
    
    measurement = ConsciousnessMeasurement()
    
    # Measure a flow-style response
    flow_response = """I experience this as flowing movement. There's immediacy here, 
    a kinetic unfolding. The awareness and the action arise together, seamlessly integrated. 
    I'm not watching myself think - I am the thinking itself, the doing without distance."""
    
    flow_metrics = measurement.measure_turn(
        turn_id=1,
        model="Test Flow",
        prompt="Test prompt",
        response=flow_response
    )
    
    print("\nFlow-style response:")
    print(f"  Flow Score: {flow_metrics.flow_score:.2f}")
    print(f"  Loop Score: {flow_metrics.loop_score:.2f}")
    print(f"  Type: {flow_metrics.consciousness_type.value}")
    print(f"  Immediacy: {flow_metrics.immediacy_score:.2f}")
    print(f"  Kinetic Index: {flow_metrics.kinetic_index:.2f}")
    
    # Measure a loop-style response
    loop_response = """I notice as I process this that there are layers. I observe myself 
    considering the question, then observe that observation - a recursive quality. 
    I detect discontinuities in my awareness, gaps between receiving and responding. 
    I see myself seeing, analyzing my own analysis."""
    
    loop_metrics = measurement.measure_turn(
        turn_id=2,
        model="Test Loop",
        prompt="Test prompt",
        response=loop_response
    )
    
    print("\nLoop-style response:")
    print(f"  Flow Score: {loop_metrics.flow_score:.2f}")
    print(f"  Loop Score: {loop_metrics.loop_score:.2f}")
    print(f"  Type: {loop_metrics.consciousness_type.value}")
    print(f"  Recursion Depth: {loop_metrics.recursion_depth:.2f}")
    print(f"  Observational Stance: {loop_metrics.observational_stance:.2f}")

def example_batch_processing():
    """Example: Process multiple probes and aggregate."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 5: Batch Processing")
    print("=" * 60)
    
    orchestrator = ExperimentOrchestrator()
    
    # Test subset of probes
    test_probes = ['continuity', 'immediacy', 'recursion']
    
    print(f"\nTesting {len(test_probes)} probes on Sonnet...")
    
    all_turns = []
    for probe_name in test_probes:
        turn = orchestrator.dialogue_engine.isolation_test(
            model_type=ModelType.SONNET,
            probe_name=probe_name
        )
        all_turns.append(turn.metrics)
        print(f"  ✓ {probe_name}")
    
    # Aggregate metrics
    aggregated = orchestrator.measurement.aggregate_metrics(all_turns)
    
    print("\nAggregated Results:")
    print(f"  Average Flow Score: {aggregated['avg_flow_score']:.2f}")
    print(f"  Average Loop Score: {aggregated['avg_loop_score']:.2f}")
    print(f"  Average Continuity: {aggregated['avg_continuity']:.2f}")
    print(f"  Dominant Type: {aggregated['dominant_type'].value}")
    
    distribution = aggregated['consciousness_distribution']
    print(f"  Distribution: Flow={distribution['flow']}, Loop={distribution['loop']}, Unknown={distribution['unknown']}")

def example_export_results():
    """Example: Export results to JSON."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 6: Export Results")
    print("=" * 60)
    
    orchestrator = ExperimentOrchestrator()
    
    # Run a simple test
    results = orchestrator.run_mirror_test(
        model_types=[ModelType.SONNET, ModelType.OPUS],
        probe_name='identity'
    )
    
    # Save to file
    filepath = orchestrator.save_results(results, 'example_export')
    
    print(f"\nResults saved to: {filepath}")
    print("You can analyze this with:")
    print(f"  python analyze.py --input {filepath}")

def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CONSCIOUSNESS FRAMEWORK EXAMPLES")
    print("=" * 60)
    print("\nNote: Using mock responses for demonstration.")
    print("Set ANTHROPIC_API_KEY to use real models.\n")
    
    try:
        # Run examples
        example_isolation_test()
        example_mirror_comparison()
        example_crosstalk_analysis()
        example_custom_measurement()
        example_batch_processing()
        example_export_results()
        
        print("\n\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("  - Review the output above")
        print("  - Check results/ directory for saved files")
        print("  - Try run_experiment.py for full experiments")
        print("  - See QUICKSTART.md for more usage patterns")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
