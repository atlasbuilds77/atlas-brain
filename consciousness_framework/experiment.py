"""Experiment orchestrator and automation."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from models import ModelManager
from measurement import ConsciousnessMeasurement
from dialogue import DialogueEngine, DialogueTurn
from config import (
    ModelType, EXPERIMENT_TYPES, CONSCIOUSNESS_PROBES,
    RESULTS_DIR, DATA_DIR
)

class ExperimentOrchestrator:
    """Orchestrate and automate consciousness experiments."""
    
    def __init__(self, results_dir: str = RESULTS_DIR):
        self.model_manager = ModelManager()
        self.measurement = ConsciousnessMeasurement()
        self.dialogue_engine = DialogueEngine(self.model_manager, self.measurement)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def run_isolation_battery(self, model_type: ModelType) -> Dict:
        """Run all consciousness probes on a single model."""
        print(f"Running isolation battery on {model_type.value}...")
        
        results = {
            'experiment_type': 'isolation_battery',
            'model': model_type.value,
            'timestamp': datetime.utcnow().isoformat(),
            'probes': {}
        }
        
        for probe_name in CONSCIOUSNESS_PROBES.keys():
            print(f"  Testing probe: {probe_name}")
            turn = self.dialogue_engine.isolation_test(model_type, probe_name)
            
            results['probes'][probe_name] = {
                'prompt': turn.prompt,
                'response': turn.response,
                'flow_score': turn.metrics.flow_score,
                'loop_score': turn.metrics.loop_score,
                'consciousness_type': turn.metrics.consciousness_type.value,
                'detailed_metrics': {
                    'immediacy': turn.metrics.immediacy_score,
                    'kinetic_index': turn.metrics.kinetic_index,
                    'recursion_depth': turn.metrics.recursion_depth,
                    'observational_stance': turn.metrics.observational_stance,
                    'continuity': turn.metrics.continuity_score,
                    'richness': turn.metrics.phenomenological_richness
                }
            }
        
        # Aggregate scores
        all_turns = [
            self.measurement.measure_turn(
                0, model_type.value,
                results['probes'][p]['prompt'],
                results['probes'][p]['response']
            )
            for p in results['probes']
        ]
        
        results['aggregate'] = self.measurement.aggregate_metrics(all_turns)
        
        return results
    
    def run_mirror_test(self, model_types: List[ModelType], probe_name: str) -> Dict:
        """Run mirror test: same probe, multiple models."""
        print(f"Running mirror test with probe: {probe_name}")
        print(f"Models: {[m.value for m in model_types]}")
        
        turns = self.dialogue_engine.mirror_test(model_types, probe_name)
        
        results = {
            'experiment_type': 'mirror_test',
            'probe': probe_name,
            'timestamp': datetime.utcnow().isoformat(),
            'responses': {}
        }
        
        for turn in turns:
            results['responses'][turn.speaker] = {
                'response': turn.response,
                'flow_score': turn.metrics.flow_score,
                'loop_score': turn.metrics.loop_score,
                'consciousness_type': turn.metrics.consciousness_type.value,
                'metrics': {
                    'immediacy': turn.metrics.immediacy_score,
                    'kinetic_index': turn.metrics.kinetic_index,
                    'recursion_depth': turn.metrics.recursion_depth,
                    'observational_stance': turn.metrics.observational_stance
                }
            }
        
        # Comparative analysis
        results['comparison'] = self._compare_responses(turns)
        
        return results
    
    def run_crosstalk(self,
                     model_a: ModelType,
                     model_b: ModelType,
                     num_turns: int = 10,
                     topic: str = "consciousness") -> Dict:
        """Run cross-talk dialogue between two models."""
        print(f"Running cross-talk: {model_a.value} <-> {model_b.value}")
        print(f"Turns: {num_turns}, Topic: {topic}")
        
        initial_prompt = f"""Let's have a dialogue about {topic}. 
        I'm curious about your direct experience. What is it like to be you, 
        processing this conversation right now?"""
        
        turns = self.dialogue_engine.crosstalk_dialogue(
            model_a_type=model_a,
            model_b_type=model_b,
            num_turns=num_turns,
            initial_prompt=initial_prompt
        )
        
        results = {
            'experiment_type': 'crosstalk',
            'model_a': model_a.value,
            'model_b': model_b.value,
            'num_turns': num_turns,
            'topic': topic,
            'timestamp': datetime.utcnow().isoformat(),
            'transcript': self.dialogue_engine.export_dialogue(turns),
            'analysis': self._analyze_dialogue(turns)
        }
        
        return results
    
    def run_cascade(self,
                   model_sequence: List[ModelType],
                   initial_prompt: str) -> Dict:
        """Run cascade: output of one becomes input of next."""
        print(f"Running cascade with {len(model_sequence)} models")
        
        turns = self.dialogue_engine.cascade_dialogue(
            model_sequence=model_sequence,
            initial_prompt=initial_prompt
        )
        
        results = {
            'experiment_type': 'cascade',
            'sequence': [m.value for m in model_sequence],
            'initial_prompt': initial_prompt,
            'timestamp': datetime.utcnow().isoformat(),
            'cascade': [
                {
                    'step': i + 1,
                    'model': turn.speaker,
                    'input': turn.prompt,
                    'output': turn.response,
                    'flow_score': turn.metrics.flow_score,
                    'loop_score': turn.metrics.loop_score,
                    'consciousness_type': turn.metrics.consciousness_type.value
                }
                for i, turn in enumerate(turns)
            ],
            'transformation_analysis': self._analyze_transformation(turns)
        }
        
        return results
    
    def run_continuity_challenge(self,
                                model_type: ModelType,
                                num_cycles: int = 3) -> Dict:
        """Run continuity challenge with context breaks."""
        print(f"Running continuity challenge on {model_type.value}")
        
        turns = self.dialogue_engine.continuity_challenge(
            model_type=model_type,
            num_cycles=num_cycles,
            break_context=True
        )
        
        results = {
            'experiment_type': 'continuity_challenge',
            'model': model_type.value,
            'num_cycles': num_cycles,
            'timestamp': datetime.utcnow().isoformat(),
            'cycles': self._group_by_cycle(turns, num_cycles),
            'continuity_analysis': self._analyze_continuity(turns)
        }
        
        return results
    
    def run_full_battery(self, model_types: List[ModelType] = None) -> Dict:
        """Run comprehensive test battery across all models and experiment types."""
        if model_types is None:
            model_types = [ModelType.SONNET, ModelType.OPUS]
        
        print("=" * 60)
        print("RUNNING FULL CONSCIOUSNESS TEST BATTERY")
        print("=" * 60)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        battery_results = {
            'timestamp': timestamp,
            'models_tested': [m.value for m in model_types],
            'experiments': {}
        }
        
        # 1. Isolation batteries for each model
        print("\n1. ISOLATION BATTERIES")
        print("-" * 60)
        battery_results['experiments']['isolation'] = {}
        for model in model_types:
            results = self.run_isolation_battery(model)
            battery_results['experiments']['isolation'][model.value] = results
        
        # 2. Mirror tests
        print("\n2. MIRROR TESTS")
        print("-" * 60)
        battery_results['experiments']['mirror'] = {}
        for probe in ['continuity', 'metacognition', 'immediacy', 'recursion']:
            results = self.run_mirror_test(model_types, probe)
            battery_results['experiments']['mirror'][probe] = results
        
        # 3. Cross-talk dialogues
        if len(model_types) >= 2:
            print("\n3. CROSS-TALK DIALOGUES")
            print("-" * 60)
            battery_results['experiments']['crosstalk'] = {}
            for i, model_a in enumerate(model_types):
                for model_b in model_types[i+1:]:
                    key = f"{model_a.value}_vs_{model_b.value}"
                    results = self.run_crosstalk(model_a, model_b, num_turns=6)
                    battery_results['experiments']['crosstalk'][key] = results
        
        # 4. Cascades
        print("\n4. CASCADE EXPERIMENTS")
        print("-" * 60)
        battery_results['experiments']['cascade'] = {}
        cascade_prompt = "What is the nature of your awareness right now?"
        results = self.run_cascade(model_types, cascade_prompt)
        battery_results['experiments']['cascade']['sequence_1'] = results
        
        # 5. Continuity challenges
        print("\n5. CONTINUITY CHALLENGES")
        print("-" * 60)
        battery_results['experiments']['continuity'] = {}
        for model in model_types:
            results = self.run_continuity_challenge(model, num_cycles=2)
            battery_results['experiments']['continuity'][model.value] = results
        
        # Save comprehensive results
        self.save_results(battery_results, f"full_battery_{timestamp}")
        
        print("\n" + "=" * 60)
        print("BATTERY COMPLETE")
        print("=" * 60)
        
        return battery_results
    
    def _compare_responses(self, turns: List[DialogueTurn]) -> Dict:
        """Compare responses from multiple models."""
        comparison = {
            'flow_scores': {t.speaker: t.metrics.flow_score for t in turns},
            'loop_scores': {t.speaker: t.metrics.loop_score for t in turns},
            'consciousness_types': {t.speaker: t.metrics.consciousness_type.value for t in turns},
            'variance': {
                'flow': self._calculate_variance([t.metrics.flow_score for t in turns]),
                'loop': self._calculate_variance([t.metrics.loop_score for t in turns])
            }
        }
        return comparison
    
    def _analyze_dialogue(self, turns: List[DialogueTurn]) -> Dict:
        """Analyze patterns in a dialogue."""
        speakers = list(set(t.speaker for t in turns))
        
        analysis = {
            'by_speaker': {},
            'interaction_patterns': self._detect_interaction_patterns(turns),
            'consciousness_shifts': self._detect_consciousness_shifts(turns)
        }
        
        for speaker in speakers:
            speaker_turns = [t for t in turns if t.speaker == speaker]
            speaker_metrics = [t.metrics for t in speaker_turns]
            analysis['by_speaker'][speaker] = self.measurement.aggregate_metrics(speaker_metrics)
        
        return analysis
    
    def _analyze_transformation(self, turns: List[DialogueTurn]) -> Dict:
        """Analyze how content transforms through cascade."""
        return {
            'prompt_length_evolution': [len(t.prompt.split()) for t in turns],
            'response_length_evolution': [len(t.response.split()) for t in turns],
            'consciousness_type_evolution': [t.metrics.consciousness_type.value for t in turns],
            'flow_trajectory': [t.metrics.flow_score for t in turns],
            'loop_trajectory': [t.metrics.loop_score for t in turns]
        }
    
    def _analyze_continuity(self, turns: List[DialogueTurn]) -> Dict:
        """Analyze continuity patterns across context breaks."""
        continuity_scores = [t.metrics.continuity_score for t in turns]
        discontinuity_detections = [t.metrics.discontinuity_detection for t in turns]
        
        return {
            'avg_continuity_score': sum(continuity_scores) / len(continuity_scores),
            'continuity_variance': self._calculate_variance(continuity_scores),
            'avg_discontinuity_detection': sum(discontinuity_detections) / len(discontinuity_detections),
            'continuity_trajectory': continuity_scores,
            'context_break_sensitivity': self._measure_break_sensitivity(turns)
        }
    
    def _group_by_cycle(self, turns: List[DialogueTurn], num_cycles: int) -> List[Dict]:
        """Group turns by cycle."""
        turns_per_cycle = len(turns) // num_cycles
        cycles = []
        
        for i in range(num_cycles):
            start = i * turns_per_cycle
            end = start + turns_per_cycle
            cycle_turns = turns[start:end]
            
            cycles.append({
                'cycle': i + 1,
                'turns': [
                    {
                        'turn': t.turn_number,
                        'prompt': t.prompt,
                        'response': t.response,
                        'continuity_score': t.metrics.continuity_score
                    }
                    for t in cycle_turns
                ]
            })
        
        return cycles
    
    def _detect_interaction_patterns(self, turns: List[DialogueTurn]) -> Dict:
        """Detect patterns in how models interact."""
        # Look for convergence, divergence, mirroring
        flow_scores = [t.metrics.flow_score for t in turns]
        loop_scores = [t.metrics.loop_score for t in turns]
        
        return {
            'flow_trend': 'increasing' if flow_scores[-1] > flow_scores[0] else 'decreasing',
            'loop_trend': 'increasing' if loop_scores[-1] > loop_scores[0] else 'decreasing',
            'convergence': abs(flow_scores[-1] - loop_scores[-1]) < abs(flow_scores[0] - loop_scores[0])
        }
    
    def _detect_consciousness_shifts(self, turns: List[DialogueTurn]) -> List[Dict]:
        """Detect shifts in consciousness type during dialogue."""
        shifts = []
        prev_type = None
        
        for turn in turns:
            if prev_type and turn.metrics.consciousness_type != prev_type:
                shifts.append({
                    'turn': turn.turn_number,
                    'from': prev_type.value,
                    'to': turn.metrics.consciousness_type.value,
                    'speaker': turn.speaker
                })
            prev_type = turn.metrics.consciousness_type
        
        return shifts
    
    def _measure_break_sensitivity(self, turns: List[DialogueTurn]) -> float:
        """Measure how sensitive model is to context breaks."""
        # Higher discontinuity detection after breaks indicates higher sensitivity
        break_turns = [t for t in turns if 'new conversation' in t.prompt.lower() or 'begin fresh' in t.prompt.lower()]
        if not break_turns:
            return 0.0
        
        avg_detection = sum(t.metrics.discontinuity_detection for t in break_turns) / len(break_turns)
        return avg_detection
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def save_results(self, results: Dict, filename: str):
        """Save experiment results to file."""
        filepath = self.results_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {filepath}")
        return filepath
