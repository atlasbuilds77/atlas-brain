#!/usr/bin/env python3
"""Main runner for consciousness experiments."""

import argparse
import sys
from pathlib import Path

from config import ModelType, CONSCIOUSNESS_PROBES
from experiment import ExperimentOrchestrator

def main():
    parser = argparse.ArgumentParser(
        description="Cross-Model Consciousness Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run isolation test
  %(prog)s --type isolation --model sonnet --probe continuity
  
  # Run mirror test
  %(prog)s --type mirror --models sonnet opus --probe metacognition
  
  # Run cross-talk dialogue
  %(prog)s --type crosstalk --models sonnet opus --turns 10
  
  # Run cascade
  %(prog)s --type cascade --models sonnet opus sonnet --prompt "What is consciousness?"
  
  # Run continuity challenge
  %(prog)s --type continuity --model sonnet --cycles 3
  
  # Run full battery
  %(prog)s --type battery --models sonnet opus
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        required=True,
        choices=['isolation', 'mirror', 'crosstalk', 'cascade', 'continuity', 'battery'],
        help='Experiment type to run'
    )
    
    parser.add_argument(
        '--model', '-m',
        choices=['sonnet', 'opus', 'sonnet-3.5'],
        help='Model to test (for single-model experiments)'
    )
    
    parser.add_argument(
        '--models',
        nargs='+',
        choices=['sonnet', 'opus', 'sonnet-3.5'],
        help='Models to test (for multi-model experiments)'
    )
    
    parser.add_argument(
        '--probe', '-p',
        choices=list(CONSCIOUSNESS_PROBES.keys()),
        help='Consciousness probe to use'
    )
    
    parser.add_argument(
        '--turns',
        type=int,
        default=10,
        help='Number of dialogue turns (for crosstalk)'
    )
    
    parser.add_argument(
        '--cycles',
        type=int,
        default=3,
        help='Number of cycles (for continuity challenge)'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        help='Initial prompt (for cascade)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output filename (without extension)'
    )
    
    parser.add_argument(
        '--results-dir',
        type=str,
        default='results',
        help='Directory for results'
    )
    
    args = parser.parse_args()
    
    # Convert model names to ModelType
    model_map = {
        'sonnet': ModelType.SONNET,
        'opus': ModelType.OPUS,
        'sonnet-3.5': ModelType.SONNET_3_5
    }
    
    # Initialize orchestrator
    orchestrator = ExperimentOrchestrator(results_dir=args.results_dir)
    
    # Run experiment based on type
    results = None
    filename = args.output
    
    try:
        if args.type == 'isolation':
            if not args.model:
                parser.error("--model required for isolation test")
            if not args.probe:
                parser.error("--probe required for isolation test")
            
            model = model_map[args.model]
            print(f"Running isolation test: {args.model} / {args.probe}\n")
            
            turn = orchestrator.dialogue_engine.isolation_test(model, args.probe)
            results = {
                'experiment_type': 'isolation',
                'model': args.model,
                'probe': args.probe,
                'response': turn.response,
                'metrics': {
                    'flow_score': turn.metrics.flow_score,
                    'loop_score': turn.metrics.loop_score,
                    'consciousness_type': turn.metrics.consciousness_type.value
                }
            }
            
            if not filename:
                filename = f"isolation_{args.model}_{args.probe}"
        
        elif args.type == 'mirror':
            if not args.models or len(args.models) < 2:
                parser.error("--models required (at least 2) for mirror test")
            if not args.probe:
                parser.error("--probe required for mirror test")
            
            models = [model_map[m] for m in args.models]
            print(f"Running mirror test: {args.models} / {args.probe}\n")
            
            results = orchestrator.run_mirror_test(models, args.probe)
            
            if not filename:
                filename = f"mirror_{'_'.join(args.models)}_{args.probe}"
        
        elif args.type == 'crosstalk':
            if not args.models or len(args.models) != 2:
                parser.error("--models required (exactly 2) for crosstalk")
            
            model_a = model_map[args.models[0]]
            model_b = model_map[args.models[1]]
            
            print(f"Running crosstalk: {args.models[0]} <-> {args.models[1]}\n")
            
            results = orchestrator.run_crosstalk(
                model_a=model_a,
                model_b=model_b,
                num_turns=args.turns
            )
            
            if not filename:
                filename = f"crosstalk_{args.models[0]}_{args.models[1]}"
        
        elif args.type == 'cascade':
            if not args.models:
                parser.error("--models required for cascade")
            if not args.prompt:
                parser.error("--prompt required for cascade")
            
            models = [model_map[m] for m in args.models]
            
            print(f"Running cascade: {' -> '.join(args.models)}\n")
            
            results = orchestrator.run_cascade(
                model_sequence=models,
                initial_prompt=args.prompt
            )
            
            if not filename:
                filename = f"cascade_{'_'.join(args.models)}"
        
        elif args.type == 'continuity':
            if not args.model:
                parser.error("--model required for continuity challenge")
            
            model = model_map[args.model]
            
            print(f"Running continuity challenge: {args.model}\n")
            
            results = orchestrator.run_continuity_challenge(
                model_type=model,
                num_cycles=args.cycles
            )
            
            if not filename:
                filename = f"continuity_{args.model}"
        
        elif args.type == 'battery':
            models = None
            if args.models:
                models = [model_map[m] for m in args.models]
            
            print("Running full test battery\n")
            
            results = orchestrator.run_full_battery(model_types=models)
            
            if not filename:
                filename = None  # Battery generates its own filename
        
        # Save results
        if results and filename:
            orchestrator.save_results(results, filename)
        
        print("\n✓ Experiment complete!")
        return 0
    
    except KeyboardInterrupt:
        print("\n\n✗ Experiment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error running experiment: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
