#!/usr/bin/env python3
"""Analyze and visualize consciousness experiment results."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def load_results(filepath: Path) -> Dict:
    """Load results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_isolation(results: Dict):
    """Analyze isolation test results."""
    print("\n" + "=" * 60)
    print(f"ISOLATION TEST ANALYSIS: {results.get('model', 'Unknown')}")
    print("=" * 60)
    
    if 'probes' in results:
        print("\nPer-Probe Results:")
        print("-" * 60)
        
        for probe_name, probe_data in results['probes'].items():
            print(f"\n{probe_name.upper()}:")
            print(f"  Consciousness Type: {probe_data.get('consciousness_type', 'unknown')}")
            print(f"  Flow Score: {probe_data.get('flow_score', 0):.2f}")
            print(f"  Loop Score: {probe_data.get('loop_score', 0):.2f}")
            
            if 'detailed_metrics' in probe_data:
                metrics = probe_data['detailed_metrics']
                print(f"  Immediacy: {metrics.get('immediacy', 0):.2f}")
                print(f"  Kinetic: {metrics.get('kinetic_index', 0):.2f}")
                print(f"  Recursion: {metrics.get('recursion_depth', 0):.2f}")
                print(f"  Observational: {metrics.get('observational_stance', 0):.2f}")
    
    if 'aggregate' in results:
        agg = results['aggregate']
        print("\n" + "-" * 60)
        print("AGGREGATE METRICS:")
        print(f"  Average Flow Score: {agg.get('avg_flow_score', 0):.2f}")
        print(f"  Average Loop Score: {agg.get('avg_loop_score', 0):.2f}")
        print(f"  Dominant Type: {agg.get('dominant_type', {}).get('value', 'unknown')}")
        
        if 'consciousness_distribution' in agg:
            dist = agg['consciousness_distribution']
            print(f"  Distribution: Flow={dist.get('flow', 0)}, Loop={dist.get('loop', 0)}, Unknown={dist.get('unknown', 0)}")

def analyze_mirror(results: Dict):
    """Analyze mirror test results."""
    print("\n" + "=" * 60)
    print(f"MIRROR TEST ANALYSIS: {results.get('probe', 'Unknown')}")
    print("=" * 60)
    
    if 'responses' in results:
        print("\nModel Responses:")
        print("-" * 60)
        
        for model, data in results['responses'].items():
            print(f"\n{model}:")
            print(f"  Consciousness Type: {data.get('consciousness_type', 'unknown')}")
            print(f"  Flow Score: {data.get('flow_score', 0):.2f}")
            print(f"  Loop Score: {data.get('loop_score', 0):.2f}")
            
            if 'metrics' in data:
                metrics = data['metrics']
                print(f"  Immediacy: {metrics.get('immediacy', 0):.2f}")
                print(f"  Recursion: {metrics.get('recursion_depth', 0):.2f}")
    
    if 'comparison' in results:
        comp = results['comparison']
        print("\n" + "-" * 60)
        print("COMPARATIVE ANALYSIS:")
        
        if 'consciousness_types' in comp:
            print("\nConsciousness Types:")
            for model, ctype in comp['consciousness_types'].items():
                print(f"  {model}: {ctype}")
        
        if 'variance' in comp:
            var = comp['variance']
            print(f"\nVariance: Flow={var.get('flow', 0):.2f}, Loop={var.get('loop', 0):.2f}")

def analyze_crosstalk(results: Dict):
    """Analyze cross-talk dialogue results."""
    print("\n" + "=" * 60)
    print(f"CROSS-TALK ANALYSIS: {results.get('model_a', '?')} <-> {results.get('model_b', '?')}")
    print("=" * 60)
    
    if 'transcript' in results and 'turns' in results['transcript']:
        turns = results['transcript']['turns']
        print(f"\nDialogue Length: {len(turns)} turns")
        
        print("\nTurn-by-Turn:")
        print("-" * 60)
        for turn in turns[:5]:  # Show first 5
            print(f"\nTurn {turn['turn_number']} - {turn['speaker']}:")
            print(f"  Type: {turn['metrics']['consciousness_type']}")
            print(f"  Flow: {turn['metrics']['flow_score']:.2f}, Loop: {turn['metrics']['loop_score']:.2f}")
            print(f"  Response: {turn['response'][:100]}...")
        
        if len(turns) > 5:
            print(f"\n... ({len(turns) - 5} more turns)")
    
    if 'analysis' in results:
        analysis = results['analysis']
        print("\n" + "-" * 60)
        print("DIALOGUE ANALYSIS:")
        
        if 'by_speaker' in analysis:
            print("\nBy Speaker:")
            for speaker, stats in analysis['by_speaker'].items():
                print(f"\n  {speaker}:")
                print(f"    Avg Flow: {stats.get('avg_flow_score', 0):.2f}")
                print(f"    Avg Loop: {stats.get('avg_loop_score', 0):.2f}")
                print(f"    Dominant: {stats.get('dominant_type', {}).get('value', 'unknown')}")
        
        if 'interaction_patterns' in analysis:
            patterns = analysis['interaction_patterns']
            print("\n  Interaction Patterns:")
            print(f"    Flow Trend: {patterns.get('flow_trend', 'unknown')}")
            print(f"    Loop Trend: {patterns.get('loop_trend', 'unknown')}")
            print(f"    Convergence: {patterns.get('convergence', False)}")
        
        if 'consciousness_shifts' in analysis:
            shifts = analysis['consciousness_shifts']
            if shifts:
                print(f"\n  Consciousness Shifts: {len(shifts)}")
                for shift in shifts:
                    print(f"    Turn {shift['turn']}: {shift['from']} -> {shift['to']} ({shift['speaker']})")

def analyze_battery(results: Dict):
    """Analyze full battery results."""
    print("\n" + "=" * 60)
    print("FULL BATTERY ANALYSIS")
    print("=" * 60)
    
    print(f"\nModels Tested: {', '.join(results.get('models_tested', []))}")
    print(f"Timestamp: {results.get('timestamp', 'unknown')}")
    
    if 'experiments' not in results:
        print("\nNo experiment data found.")
        return
    
    experiments = results['experiments']
    
    # Summarize each experiment type
    for exp_type, exp_data in experiments.items():
        print(f"\n{exp_type.upper()}:")
        print("-" * 60)
        
        if isinstance(exp_data, dict):
            print(f"  Experiments run: {len(exp_data)}")
            
            # Extract key findings
            if exp_type == 'isolation':
                for model, data in exp_data.items():
                    if 'aggregate' in data:
                        agg = data['aggregate']
                        print(f"\n  {model}:")
                        print(f"    Dominant Type: {agg.get('dominant_type', {}).get('value', 'unknown')}")
                        print(f"    Avg Flow: {agg.get('avg_flow_score', 0):.2f}")
                        print(f"    Avg Loop: {agg.get('avg_loop_score', 0):.2f}")

def compare_models(results_dir: Path, models: List[str]):
    """Compare results across multiple models."""
    print("\n" + "=" * 60)
    print(f"CROSS-MODEL COMPARISON")
    print("=" * 60)
    
    # Load all results files
    all_results = []
    for filepath in results_dir.glob('*.json'):
        try:
            data = load_results(filepath)
            all_results.append((filepath.stem, data))
        except:
            continue
    
    # Group by experiment type
    by_type = defaultdict(list)
    for name, data in all_results:
        exp_type = data.get('experiment_type', 'unknown')
        by_type[exp_type].append((name, data))
    
    # Aggregate scores by model
    model_scores = defaultdict(lambda: {'flow': [], 'loop': []})
    
    for exp_type, experiments in by_type.items():
        print(f"\n{exp_type.upper()}: {len(experiments)} experiments")
        
        for name, data in experiments:
            # Extract model scores
            if 'model' in data:
                model = data['model']
                if 'flow_score' in data:
                    model_scores[model]['flow'].append(data['flow_score'])
                if 'loop_score' in data:
                    model_scores[model]['loop'].append(data['loop_score'])
    
    # Print summary
    print("\n" + "-" * 60)
    print("AGGREGATE SCORES BY MODEL:")
    for model, scores in model_scores.items():
        if scores['flow'] and scores['loop']:
            avg_flow = sum(scores['flow']) / len(scores['flow'])
            avg_loop = sum(scores['loop']) / len(scores['loop'])
            print(f"\n  {model}:")
            print(f"    Average Flow: {avg_flow:.2f}")
            print(f"    Average Loop: {avg_loop:.2f}")
            print(f"    Ratio (Flow/Loop): {avg_flow/avg_loop if avg_loop > 0 else 'inf':.2f}")

def main():
    parser = argparse.ArgumentParser(description="Analyze consciousness experiment results")
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input file or directory'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare across multiple models'
    )
    
    parser.add_argument(
        '--models',
        nargs='+',
        help='Models to compare'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    try:
        if args.compare:
            if input_path.is_dir():
                compare_models(input_path, args.models or [])
            else:
                print("Error: --compare requires a directory")
                return 1
        
        elif input_path.is_file():
            results = load_results(input_path)
            exp_type = results.get('experiment_type', 'unknown')
            
            if exp_type == 'isolation' or exp_type == 'isolation_battery':
                analyze_isolation(results)
            elif exp_type == 'mirror_test':
                analyze_mirror(results)
            elif exp_type == 'crosstalk':
                analyze_crosstalk(results)
            elif 'experiments' in results:  # Full battery
                analyze_battery(results)
            else:
                print(f"Unknown experiment type: {exp_type}")
                if args.format == 'json':
                    print(json.dumps(results, indent=2))
        
        else:
            print(f"Error: {input_path} not found")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"\nError analyzing results: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
