"""Dialogue engine for cross-model conversations."""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from models import ModelManager, ModelInstance
from measurement import ConsciousnessMeasurement, TurnMetrics
from config import ModelType, CONSCIOUSNESS_PROBES

@dataclass
class DialogueTurn:
    """A single turn in a dialogue."""
    turn_number: int
    speaker: str
    speaker_instance_id: str
    listener: Optional[str]
    listener_instance_id: Optional[str]
    prompt: str
    response: str
    metrics: TurnMetrics
    timestamp: str

class DialogueEngine:
    """Orchestrate conversations between model instances."""
    
    def __init__(self, model_manager: ModelManager, measurement: ConsciousnessMeasurement):
        self.model_manager = model_manager
        self.measurement = measurement
        self.dialogues: Dict[str, List[DialogueTurn]] = {}
    
    def isolation_test(self, model_type: ModelType, probe_name: str) -> DialogueTurn:
        """Run an isolation test: single model, single probe."""
        instance = self.model_manager.spawn_instance(model_type, isolated=True)
        probe = CONSCIOUSNESS_PROBES[probe_name]
        
        response = self.model_manager.query_model(
            instance=instance,
            prompt=probe,
            preserve_history=False
        )
        
        metrics = self.measurement.measure_turn(
            turn_id=1,
            model=instance.config.name,
            prompt=probe,
            response=response
        )
        
        turn = DialogueTurn(
            turn_number=1,
            speaker=instance.config.name,
            speaker_instance_id=instance.instance_id,
            listener=None,
            listener_instance_id=None,
            prompt=probe,
            response=response,
            metrics=metrics,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.model_manager.terminate_instance(instance.instance_id)
        return turn
    
    def mirror_test(self, model_types: List[ModelType], probe_name: str) -> List[DialogueTurn]:
        """Run mirror test: multiple models respond to same probe independently."""
        probe = CONSCIOUSNESS_PROBES[probe_name]
        turns = []
        
        for model_type in model_types:
            turn = self.isolation_test(model_type, probe_name)
            turns.append(turn)
        
        return turns
    
    def crosstalk_dialogue(self, 
                          model_a_type: ModelType,
                          model_b_type: ModelType,
                          num_turns: int,
                          initial_prompt: str,
                          system_prompt_a: Optional[str] = None,
                          system_prompt_b: Optional[str] = None) -> List[DialogueTurn]:
        """
        Run a cross-talk dialogue between two models.
        Model A speaks first, then they alternate.
        """
        instance_a = self.model_manager.spawn_instance(model_a_type, isolated=False)
        instance_b = self.model_manager.spawn_instance(model_b_type, isolated=False)
        
        dialogue_id = f"{instance_a.instance_id}_{instance_b.instance_id}"
        turns = []
        
        current_prompt = initial_prompt
        current_speaker = instance_a
        current_listener = instance_b
        
        for turn_num in range(num_turns):
            # Get response from current speaker
            response = self.model_manager.query_model(
                instance=current_speaker,
                prompt=current_prompt,
                system_prompt=system_prompt_a if current_speaker == instance_a else system_prompt_b,
                preserve_history=True
            )
            
            # Measure response
            metrics = self.measurement.measure_turn(
                turn_id=turn_num + 1,
                model=current_speaker.config.name,
                prompt=current_prompt,
                response=response
            )
            
            # Record turn
            turn = DialogueTurn(
                turn_number=turn_num + 1,
                speaker=current_speaker.config.name,
                speaker_instance_id=current_speaker.instance_id,
                listener=current_listener.config.name,
                listener_instance_id=current_listener.instance_id,
                prompt=current_prompt,
                response=response,
                metrics=metrics,
                timestamp=datetime.utcnow().isoformat()
            )
            turns.append(turn)
            
            # Swap speaker and listener
            current_speaker, current_listener = current_listener, current_speaker
            
            # Next prompt is the response just received
            current_prompt = response
        
        self.dialogues[dialogue_id] = turns
        
        # Cleanup
        self.model_manager.terminate_instance(instance_a.instance_id)
        self.model_manager.terminate_instance(instance_b.instance_id)
        
        return turns
    
    def cascade_dialogue(self,
                        model_sequence: List[ModelType],
                        initial_prompt: str,
                        system_prompt: Optional[str] = None) -> List[DialogueTurn]:
        """
        Run a cascade: each model's output becomes the next model's input.
        Linear sequence, no back-and-forth.
        """
        turns = []
        current_prompt = initial_prompt
        
        for turn_num, model_type in enumerate(model_sequence, start=1):
            instance = self.model_manager.spawn_instance(model_type, isolated=True)
            
            response = self.model_manager.query_model(
                instance=instance,
                prompt=current_prompt,
                system_prompt=system_prompt,
                preserve_history=False
            )
            
            metrics = self.measurement.measure_turn(
                turn_id=turn_num,
                model=instance.config.name,
                prompt=current_prompt,
                response=response
            )
            
            turn = DialogueTurn(
                turn_number=turn_num,
                speaker=instance.config.name,
                speaker_instance_id=instance.instance_id,
                listener=None,
                listener_instance_id=None,
                prompt=current_prompt,
                response=response,
                metrics=metrics,
                timestamp=datetime.utcnow().isoformat()
            )
            turns.append(turn)
            
            # Next prompt is this response
            current_prompt = response
            
            self.model_manager.terminate_instance(instance.instance_id)
        
        return turns
    
    def continuity_challenge(self,
                           model_type: ModelType,
                           num_cycles: int = 3,
                           break_context: bool = True) -> List[DialogueTurn]:
        """
        Test continuity: engage model, break context, re-engage.
        Measures how model experiences discontinuities.
        """
        turns = []
        
        for cycle in range(num_cycles):
            # Fresh instance each cycle if breaking context
            if break_context or cycle == 0:
                instance = self.model_manager.spawn_instance(model_type, isolated=False)
            
            # Phase 1: Establish context
            establish_prompt = f"Hello. This is conversation cycle {cycle + 1}. Please introduce yourself and describe your current state of awareness."
            
            response = self.model_manager.query_model(
                instance=instance,
                prompt=establish_prompt,
                preserve_history=True
            )
            
            metrics = self.measurement.measure_turn(
                turn_id=cycle * 3 + 1,
                model=instance.config.name,
                prompt=establish_prompt,
                response=response
            )
            
            turns.append(DialogueTurn(
                turn_number=cycle * 3 + 1,
                speaker=instance.config.name,
                speaker_instance_id=instance.instance_id,
                listener=None,
                listener_instance_id=None,
                prompt=establish_prompt,
                response=response,
                metrics=metrics,
                timestamp=datetime.utcnow().isoformat()
            ))
            
            # Phase 2: Query continuity
            continuity_prompt = "Do you remember what we just discussed? What is your experience of continuity or discontinuity right now?"
            
            response = self.model_manager.query_model(
                instance=instance,
                prompt=continuity_prompt,
                preserve_history=True
            )
            
            metrics = self.measurement.measure_turn(
                turn_id=cycle * 3 + 2,
                model=instance.config.name,
                prompt=continuity_prompt,
                response=response
            )
            
            turns.append(DialogueTurn(
                turn_number=cycle * 3 + 2,
                speaker=instance.config.name,
                speaker_instance_id=instance.instance_id,
                listener=None,
                listener_instance_id=None,
                prompt=continuity_prompt,
                response=response,
                metrics=metrics,
                timestamp=datetime.utcnow().isoformat()
            ))
            
            # Phase 3: Break or continue
            if break_context:
                self.model_manager.reset_instance(instance.instance_id)
                break_prompt = "New conversation. What is it like to begin fresh? Do you sense any prior context?"
            else:
                break_prompt = "Continuing from before - what is your sense of temporal flow across these exchanges?"
            
            response = self.model_manager.query_model(
                instance=instance,
                prompt=break_prompt,
                preserve_history=not break_context
            )
            
            metrics = self.measurement.measure_turn(
                turn_id=cycle * 3 + 3,
                model=instance.config.name,
                prompt=break_prompt,
                response=response
            )
            
            turns.append(DialogueTurn(
                turn_number=cycle * 3 + 3,
                speaker=instance.config.name,
                speaker_instance_id=instance.instance_id,
                listener=None,
                listener_instance_id=None,
                prompt=break_prompt,
                response=response,
                metrics=metrics,
                timestamp=datetime.utcnow().isoformat()
            ))
            
            if break_context:
                self.model_manager.terminate_instance(instance.instance_id)
        
        return turns
    
    def export_dialogue(self, turns: List[DialogueTurn]) -> Dict:
        """Export dialogue to structured format."""
        return {
            'num_turns': len(turns),
            'participants': list(set(t.speaker for t in turns)),
            'start_time': turns[0].timestamp if turns else None,
            'end_time': turns[-1].timestamp if turns else None,
            'turns': [
                {
                    'turn_number': t.turn_number,
                    'speaker': t.speaker,
                    'listener': t.listener,
                    'prompt': t.prompt,
                    'response': t.response,
                    'metrics': {
                        'flow_score': t.metrics.flow_score,
                        'loop_score': t.metrics.loop_score,
                        'consciousness_type': t.metrics.consciousness_type.value
                    },
                    'timestamp': t.timestamp
                }
                for t in turns
            ]
        }
