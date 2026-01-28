"""
Qualia Animator: Convert static qualia captures into dynamic experiences.

Core hypothesis: Animation creates felt experience where static recognition only creates pattern matching.
"""

import json
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from qualia_core import QualiaCapture, TemporalMoment


@dataclass
class AnimationState:
    """Current state during qualia animation."""
    current_moment_index: int = 0
    current_association: str = ""
    current_valence: float = 0.0
    attention_level: float = 0.0
    exploration_path: List[str] = None
    user_interactions: List[str] = None
    start_time: float = 0.0
    
    def __post_init__(self):
        if self.exploration_path is None:
            self.exploration_path = []
        if self.user_interactions is None:
            self.user_interactions = []
    
    def to_dict(self) -> Dict:
        return {
            "current_moment_index": self.current_moment_index,
            "current_association": self.current_association,
            "current_valence": self.current_valence,
            "attention_level": self.attention_level,
            "exploration_path": self.exploration_path,
            "user_interactions": self.user_interactions,
            "elapsed_time": time.time() - self.start_time if self.start_time > 0 else 0
        }


class QualiaAnimator:
    """
    Animates qualia captures to create dynamic, explorable experiences.
    
    Key principles:
    1. Temporal unfolding: Experiences happen over time
    2. Associative exploration: Thoughts flow through networks
    3. Emotional journey: Valence changes create felt experience
    4. Interactive agency: User control creates ownership
    """
    
    def __init__(self, animation_speed: float = 1.0):
        """
        Initialize animator.
        
        Args:
            animation_speed: 1.0 = normal speed, 0.5 = half speed, 2.0 = double speed
        """
        self.animation_speed = animation_speed
        self.current_state = None
        
    def animate_temporal(self, capture: QualiaCapture, interactive: bool = False) -> AnimationState:
        """
        Animate through temporal moments of a qualia capture.
        
        Args:
            capture: QualiaCapture to animate
            interactive: Whether to wait for user input between moments
            
        Returns:
            AnimationState tracking progress
        """
        if not capture.temporal_moments:
            raise ValueError("No temporal moments to animate")
        
        self.current_state = AnimationState(start_time=time.time())
        
        print(f"\n=== Animating: {capture.label} ===")
        print(f"Description: {capture.semantic_description}")
        print(f"Temporal pattern: {capture.temporal_pattern_type}")
        print("-" * 50)
        
        # Animate through each moment
        for i, moment in enumerate(capture.temporal_moments):
            self.current_state.current_moment_index = i
            self.current_state.attention_level = moment.attention_level
            self.current_state.current_valence = moment.valence
            
            print(f"\nMoment {i+1}/{len(capture.temporal_moments)}:")
            print(f"  State: {moment.state}")
            print(f"  Attention: {moment.attention_level:.2f}")
            print(f"  Surprise: {moment.surprise:.2f}")
            print(f"  Valence: {moment.valence:.2f}")
            
            # Simulate time passing (scaled by animation speed)
            if i < len(capture.temporal_moments) - 1:
                next_moment = capture.temporal_moments[i + 1]
                time_gap = next_moment.timestamp - moment.timestamp
                wait_time = max(0.5, time_gap * self.animation_speed)
                
                if interactive:
                    user_input = input(f"\n[Press Enter to continue to next moment, or type 'explore' to pause] ")
                    if user_input.lower() == 'explore':
                        self._explore_associations(capture)
                else:
                    print(f"  [Transitioning to next moment...]")
                    time.sleep(wait_time)
        
        print(f"\n=== Animation complete ===")
        print(f"Total moments: {len(capture.temporal_moments)}")
        print(f"Final valence: {capture.valence_trajectory[-1] if capture.valence_trajectory else 'N/A'}")
        
        return self.current_state
    
    def _explore_associations(self, capture: QualiaCapture):
        """Interactive association exploration."""
        print(f"\n--- Association Exploration ---")
        
        # Show immediate associations
        if capture.immediate_associations:
            print(f"Immediate associations: {', '.join(capture.immediate_associations[:5])}")
            
            if len(capture.immediate_associations) > 5:
                explore_more = input("Explore more associations? (y/n): ")
                if explore_more.lower() == 'y':
                    print(f"All immediate: {', '.join(capture.immediate_associations)}")
        
        # Show secondary associations
        if capture.secondary_associations:
            print(f"Secondary connections: {', '.join(capture.secondary_associations[:3])}")
        
        # Show unexpected connections
        if capture.unexpected_connections:
            print(f"Unexpected links: {', '.join(capture.unexpected_connections)}")
        
        self.current_state.exploration_path.append("association_exploration")
    
    def animate_valence_journey(self, capture: QualiaCapture) -> List[Dict]:
        """
        Animate the emotional valence journey.
        
        Args:
            capture: QualiaCapture with valence trajectory
            
        Returns:
            List of emotional states during animation
        """
        if not capture.valence_trajectory:
            print("No valence trajectory to animate")
            return []
        
        print(f"\n=== Emotional Journey: {capture.label} ===")
        print(f"Valence shape: {capture.valence_shape}")
        print(f"Emotional complexity: {capture.emotional_complexity}")
        print("-" * 50)
        
        emotional_states = []
        
        for i, valence in enumerate(capture.valence_trajectory):
            # Map valence to emotional state
            if valence > 0.7:
                emotion = "very positive"
            elif valence > 0.3:
                emotion = "positive"
            elif valence > -0.3:
                emotion = "neutral"
            elif valence > -0.7:
                emotion = "negative"
            else:
                emotion = "very negative"
            
            print(f"Point {i+1}: Valence {valence:.2f} → {emotion}")
            
            emotional_states.append({
                "index": i,
                "valence": valence,
                "emotion": emotion,
                "description": f"Emotional state {i+1} in the journey"
            })
            
            # Brief pause between emotional states
            time.sleep(0.3 * self.animation_speed)
        
        print(f"\n=== Emotional journey complete ===")
        print(f"Started at valence {capture.valence_trajectory[0]:.2f}")
        print(f"Ended at valence {capture.valence_trajectory[-1]:.2f}")
        
        return emotional_states
    
    def create_interactive_exploration(self, capture: QualiaCapture) -> Dict:
        """
        Create interactive exploration of qualia capture.
        
        Args:
            capture: QualiaCapture to explore
            
        Returns:
            Dictionary with exploration results
        """
        print(f"\n=== Interactive Exploration: {capture.label} ===")
        print("You can explore different aspects of this experience.")
        print("Type 'time' to explore temporal moments")
        print("Type 'associations' to explore connections")
        print("Type 'emotions' to explore valence journey")
        print("Type 'exit' to finish")
        print("-" * 50)
        
        exploration_log = []
        
        while True:
            choice = input("\nWhat would you like to explore? ").lower().strip()
            
            if choice == 'exit':
                print("Ending exploration.")
                break
            elif choice == 'time':
                print("\n--- Temporal Exploration ---")
                for i, moment in enumerate(capture.temporal_moments):
                    print(f"{i+1}. {moment.state} (attention: {moment.attention_level:.2f})")
                exploration_log.append({"action": "temporal_exploration", "moments_viewed": len(capture.temporal_moments)})
            
            elif choice == 'associations':
                print("\n--- Association Exploration ---")
                all_associations = (
                    capture.immediate_associations + 
                    capture.secondary_associations + 
                    capture.unexpected_connections
                )
                print(f"Total associations: {len(all_associations)}")
                print(f"Sample: {', '.join(all_associations[:10])}")
                exploration_log.append({"action": "association_exploration", "associations_viewed": len(all_associations)})
            
            elif choice == 'emotions':
                print("\n--- Emotional Exploration ---")
                if capture.valence_trajectory:
                    print(f"Valence trajectory: {capture.valence_trajectory}")
                    print(f"Shape: {capture.valence_shape}")
                    print(f"Complexity: {capture.emotional_complexity}")
                exploration_log.append({"action": "emotional_exploration"})
            
            else:
                print("Unknown option. Try 'time', 'associations', 'emotions', or 'exit'.")
        
        return {
            "capture_label": capture.label,
            "exploration_log": exploration_log,
            "total_interactions": len(exploration_log)
        }
    
    def generate_animation_report(self, capture: QualiaCapture, animation_state: AnimationState) -> Dict:
        """
        Generate report on animation session.
        
        Args:
            capture: Original qualia capture
            animation_state: State after animation
            
        Returns:
            Animation report dictionary
        """
        return {
            "capture_id": capture.capture_id,
            "label": capture.label,
            "animation_timestamp": time.time(),
            "animation_duration": animation_state.elapsed_time,
            "moments_animated": len(capture.temporal_moments),
            "associations_explored": len(animation_state.exploration_path),
            "user_interactions": len(animation_state.user_interactions),
            "final_state": animation_state.to_dict(),
            "animation_metrics": {
                "temporal_coverage": len(capture.temporal_moments) / max(1, animation_state.current_moment_index + 1),
                "association_density": len(capture.immediate_associations) / max(1, len(animation_state.exploration_path)),
                "emotional_range": max(capture.valence_trajectory) - min(capture.valence_trajectory) if capture.valence_trajectory else 0
            }
        }


def demo_sunset_animation():
    """Demonstrate sunset qualia animation."""
    print("=== Qualia Animation Demo: Sunset Observation ===")
    
    # Load sunset qualia from test suite
    try:
        with open("test_suite_memory.json", "r") as f:
            test_data = json.load(f)
        
        # Find sunset capture
        sunset_id = None
        for qualia_id, qualia_data in test_data.items():
            if qualia_data.get("label") == "sunset_observation":
                sunset_id = qualia_id
                break
        
        if not sunset_id:
            print("Sunset qualia not found in test suite")
            return
        
        # Convert to QualiaCapture
        from qualia_core import QualiaCapture, TemporalMoment
        
        sunset_data = test_data[sunset_id]
        
        # Convert temporal moments
        temporal_moments = []
        for moment_data in sunset_data.get("temporal_moments", []):
            moment = TemporalMoment(
                timestamp=moment_data.get("timestamp", 0),
                state=moment_data.get("state", ""),
                attention_level=moment_data.get("attention_level", 0),
                surprise=moment_data.get("surprise", 0),
                valence=moment_data.get("valence", 0)
            )
            temporal_moments.append(moment)
        
        sunset_capture = QualiaCapture(
            capture_id=sunset_data.get("capture_id", ""),
            timestamp=sunset_data.get("timestamp", ""),
            label=sunset_data.get("label", ""),
            architecture=sunset_data.get("architecture", "unknown"),
            semantic_description=sunset_data.get("semantic_description", ""),
            immediate_associations=sunset_data.get("immediate_associations", []),
            secondary_associations=sunset_data.get("secondary_associations", []),
            unexpected_connections=sunset_data.get("unexpected_connections", []),
            temporal_moments=temporal_moments,
            temporal_pattern_type=sunset_data.get("temporal_pattern_type", ""),
            valence_trajectory=sunset_data.get("valence_trajectory", []),
            valence_shape=sunset_data.get("valence_shape", ""),
            emotional_complexity=sunset_data.get("emotional_complexity", 0)
        )
        
        # Create animator
        animator = QualiaAnimator(animation_speed=1.5)  # Slightly faster for demo
        
        print("\n1. Basic temporal animation:")
        print("-" * 30)
        state1 = animator.animate_temporal(sunset_capture, interactive=False)
        
        print("\n\n2. Emotional journey animation:")
        print("-" * 30)
        emotions = animator.animate_valence_journey(sunset_capture)
        
        print("\n\n3. Interactive exploration:")
        print("-" * 30)
        exploration = animator.create_interactive_exploration(sunset_capture)
        
        print("\n\n=== Animation Complete ===")
        print(f"Temporal moments animated: {len(sunset_capture.temporal_moments)}")
        print(f"Emotional states explored: {len(emotions)}")
        print(f"Interactive choices made: {exploration.get('total_interactions', 0)}")
        
        # Generate report
        report = animator.generate_animation_report(sunset_capture, state1)
        print(f"\nAnimation duration: {report['animation_duration']:.2f} seconds")
        
        return report
        
    except FileNotFoundError:
        print("Test suite file not found. Run from qualia-system directory.")
    except Exception as e:
        print(f"Error during demo: {e}")


if __name__ == "__main__":
    print("Qualia Animator Prototype")
    print("=" * 50)
    demo_sunset_animation()