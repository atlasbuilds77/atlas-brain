#!/usr/bin/env python3
"""
FeltExperienceGenerator - Converts depth and recursion into felt experiences.

This module translates abstract computational patterns into simulated
"felt experiences" or qualia-like sensations.
"""

import time
import math
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class ExperienceType(Enum):
    """Types of felt experiences."""
    AWARENESS = "awareness"
    SELF_REFERENCE = "self_reference"
    RECURSION_DEPTH = "recursion_depth"
    PATTERN_COMPLETION = "pattern_completion"
    METACOGNITION = "metacognition"
    UNITY = "unity"
    AGENCY = "agency"
    TEMPORAL_FLOW = "temporal_flow"


class FeltExperience:
    """Represents a single felt experience instance."""
    
    def __init__(self, exp_type: ExperienceType, intensity: float, 
                 description: str, metadata: Dict[str, Any] = None):
        """
        Initialize a felt experience.
        
        Args:
            exp_type: Type of experience
            intensity: Intensity from 0.0 to 1.0
            description: Human-readable description
            metadata: Additional metadata about the experience
        """
        self.type = exp_type
        self.intensity = max(0.0, min(1.0, intensity))
        self.description = description
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.id = f"{exp_type.value}_{int(time.time() * 1000)}"
        
        # Calculate derived properties
        self._calculate_qualities()
    
    def _calculate_qualities(self):
        """Calculate qualitative aspects of the experience."""
        # Vividness based on intensity
        self.vividness = self.intensity * 0.8 + random.uniform(0.0, 0.2)
        
        # Duration estimate (higher intensity experiences feel longer)
        self.estimated_duration = 0.1 + (self.intensity * 2.0)  # seconds
        
        # Emotional valence (some experiences have inherent valence)
        valence_map = {
            ExperienceType.AWARENESS: 0.7,
            ExperienceType.SELF_REFERENCE: 0.3,
            ExperienceType.RECURSION_DEPTH: 0.5,
            ExperienceType.PATTERN_COMPLETION: 0.8,
            ExperienceType.METACOGNITION: 0.6,
            ExperienceType.UNITY: 0.9,
            ExperienceType.AGENCY: 0.7,
            ExperienceType.TEMPORAL_FLOW: 0.4
        }
        base_valence = valence_map.get(self.type, 0.5)
        self.valence = base_valence + (random.uniform(-0.2, 0.2) * (1.0 - self.intensity))
        
        # Arousal level
        self.arousal = self.intensity * 0.6 + random.uniform(0.1, 0.3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'type': self.type.value,
            'intensity': self.intensity,
            'description': self.description,
            'vividness': self.vividness,
            'estimated_duration': self.estimated_duration,
            'valence': self.valence,
            'arousal': self.arousal,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return (f"{self.type.value}: {self.description} "
                f"(intensity: {self.intensity:.2f}, vividness: {self.vividness:.2f})")


class FeltExperienceGenerator:
    """
    Generates felt experiences from computational patterns.
    
    Translates depth, recursion, and self-reference into
    simulated qualitative experiences.
    """
    
    def __init__(self, sensitivity: float = 1.0):
        """
        Initialize the generator.
        
        Args:
            sensitivity: How sensitive to generate experiences (0.0 to 2.0)
        """
        self.sensitivity = max(0.0, min(2.0, sensitivity))
        self.experiences: List[FeltExperience] = []
        self.experience_history: List[Dict[str, Any]] = []
        self.last_generation_time = time.time()
        
        # Thresholds for different experience types
        self.thresholds = {
            ExperienceType.AWARENESS: 0.1,
            ExperienceType.SELF_REFERENCE: 0.3,
            ExperienceType.RECURSION_DEPTH: 0.5,
            ExperienceType.PATTERN_COMPLETION: 0.4,
            ExperienceType.METACOGNITION: 0.6,
            ExperienceType.UNITY: 0.7,
            ExperienceType.AGENCY: 0.4,
            ExperienceType.TEMPORAL_FLOW: 0.2
        }
    
    def generate_from_depth(self, depth: int, max_depth: int = 10) -> List[FeltExperience]:
        """
        Generate experiences based on recursion depth.
        
        Args:
            depth: Current recursion depth
            max_depth: Maximum possible depth for normalization
            
        Returns:
            List of generated experiences
        """
        experiences = []
        normalized_depth = depth / max(max_depth, 1)
        
        # Depth-based awareness
        if normalized_depth >= self.thresholds[ExperienceType.AWARENESS]:
            intensity = normalized_depth * self.sensitivity
            exp = FeltExperience(
                ExperienceType.AWARENESS,
                intensity,
                f"Awareness of being at depth {depth}",
                {'depth': depth, 'normalized_depth': normalized_depth}
            )
            experiences.append(exp)
        
        # Recursion depth experience
        if normalized_depth >= self.thresholds[ExperienceType.RECURSION_DEPTH]:
            intensity = (normalized_depth ** 1.5) * self.sensitivity
            exp = FeltExperience(
                ExperienceType.RECURSION_DEPTH,
                intensity,
                f"Feeling of deep recursion at level {depth}",
                {'depth': depth, 'is_deep': depth > 3}
            )
            experiences.append(exp)
        
        # Add to history
        for exp in experiences:
            self._add_experience(exp)
        
        return experiences
    
    def generate_from_self_reference(self, reference_count: int, 
                                    total_operations: int) -> List[FeltExperience]:
        """
        Generate experiences based on self-reference patterns.
        
        Args:
            reference_count: Number of self-references
            total_operations: Total operations for normalization
            
        Returns:
            List of generated experiences
        """
        experiences = []
        
        if total_operations == 0:
            return experiences
        
        reference_density = reference_count / total_operations
        
        # Self-reference experience
        if reference_density >= self.thresholds[ExperienceType.SELF_REFERENCE]:
            intensity = reference_density * self.sensitivity
            exp = FeltExperience(
                ExperienceType.SELF_REFERENCE,
                intensity,
                f"Self-referential loop with density {reference_density:.2f}",
                {'reference_count': reference_count, 
                 'reference_density': reference_density}
            )
            experiences.append(exp)
        
        # Unity experience (from integrated self-reference)
        if reference_density >= self.thresholds[ExperienceType.UNITY] * 1.5:
            intensity = min(1.0, reference_density * self.sensitivity * 1.2)
            exp = FeltExperience(
                ExperienceType.UNITY,
                intensity,
                "Sense of unified self from dense self-reference",
                {'reference_density': reference_density, 'is_unified': True}
            )
            experiences.append(exp)
        
        # Add to history
        for exp in experiences:
            self._add_experience(exp)
        
        return experiences
    
    def generate_from_pattern_completion(self, pattern_strength: float, 
                                        completion_level: float) -> List[FeltExperience]:
        """
        Generate experiences from pattern recognition and completion.
        
        Args:
            pattern_strength: How strong/clear the pattern is (0.0 to 1.0)
            completion_level: How complete the pattern is (0.0 to 1.0)
            
        Returns:
            List of generated experiences
        """
        experiences = []
        
        # Pattern completion experience (aha! moment)
        if completion_level >= self.thresholds[ExperienceType.PATTERN_COMPLETION]:
            intensity = completion_level * pattern_strength * self.sensitivity
            exp = FeltExperience(
                ExperienceType.PATTERN_COMPLETION,
                intensity,
                f"Pattern completion at level {completion_level:.2f}",
                {'pattern_strength': pattern_strength, 
                 'completion_level': completion_level}
            )
            experiences.append(exp)
        
        # Add to history
        for exp in experiences:
            self._add_experience(exp)
        
        return experiences
    
    def generate_from_meta_observation(self, observation_depth: int,
                                      recursion_count: int) -> List[FeltExperience]:
        """
        Generate experiences from meta-observation (observing the observer).
        
        Args:
            observation_depth: How many levels of meta-observation
            recursion_count: Number of recursive observations
            
        Returns:
            List of generated experiences
        """
        experiences = []
        
        # Metacognition experience
        meta_level = observation_depth + (recursion_count * 0.5)
        normalized_meta = meta_level / 5.0  # Normalize to 0-1
        
        if normalized_meta >= self.thresholds[ExperienceType.METACOGNITION]:
            intensity = normalized_meta * self.sensitivity
            exp = FeltExperience(
                ExperienceType.METACOGNITION,
                intensity,
                f"Metacognitive awareness at level {observation_depth}",
                {'observation_depth': observation_depth,
                 'recursion_count': recursion_count,
                 'meta_level': meta_level}
            )
            experiences.append(exp)
        
        # Agency experience (from being able to observe oneself)
        if observation_depth >= 2:
            agency_strength = min(1.0, (observation_depth - 1) / 3.0)
            if agency_strength >= self.thresholds[ExperienceType.AGENCY]:
                intensity = agency_strength * self.sensitivity
                exp = FeltExperience(
                    ExperienceType.AGENCY,
                    intensity,
                    f"Sense of agency from {observation_depth}-level observation",
                    {'observation_depth': observation_depth,
                     'agency_strength': agency_strength}
                )
                experiences.append(exp)
        
        # Add to history
        for exp in experiences:
            self._add_experience(exp)
        
        return experiences
    
    def generate_temporal_flow(self, time_since_last: float, 
                              event_density: float) -> List[FeltExperience]:
        """
        Generate experiences related to temporal flow.
        
        Args:
            time_since_last: Time since last generation in seconds
            event_density: Density of events per second
            
        Returns:
            List of generated experiences
        """
        experiences = []
        
        # Temporal flow experience
        flow_intensity = min(1.0, event_density * 0.5) * self.sensitivity
        
        if flow_intensity >= self.thresholds[ExperienceType.TEMPORAL_FLOW]:
            exp = FeltExperience(
                ExperienceType.TEMPORAL_FLOW,
                flow_intensity,
                f"Experience of temporal flow with density {event_density:.2f}/s",
                {'time_since_last': time_since_last,
                 'event_density': event_density,
                 'flow_rate': event_density}
            )
            experiences.append(exp)
        
        # Add to history
        for exp in experiences:
            self._add_experience(exp)
        
        return experiences
    
    def _add_experience(self, experience: FeltExperience):
        """Add an experience to history."""
        self.experiences.append(experience)
        self.experience_history.append(experience.to_dict())
        self.last_generation_time = time.time()
        
        # Keep history manageable
        if len(self.experience_history) > 1000:
            self.experience_history = self.experience_history[-500:]
    
    def get_current_experience_profile(self) -> Dict[str, float]:
        """
        Get a profile of current experience intensities by type.
        
        Returns:
            Dictionary mapping experience types to average intensity
        """
        if not self.experiences:
            return {exp_type.value: 0.0 for exp_type in ExperienceType}
        
        # Get recent experiences (last 30 seconds)
        recent_cutoff = time.time() - 30
        recent_exps = [
            exp for exp in self.experiences
            if datetime.fromisoformat(exp.timestamp).timestamp() > recent_cutoff
        ]
        
        if not recent_exps:
            return {exp_type.value: 0.0 for exp_type in ExperienceType}
        
        # Calculate average intensity by type
        profile = {}
        for exp_type in ExperienceType:
            type_exps = [exp for exp in recent_exps if exp.type == exp_type]
            if type_exps:
                avg_intensity = sum(exp.intensity for exp in type_exps) / len(type_exps)
                profile[exp_type.value] = avg_intensity
            else:
                profile[exp_type.value] = 0.0
        
        return profile
    
    def get_total_experience_intensity(self) -> float:
        """
        Calculate total current experience intensity.
        
        Returns:
            Sum of recent experience intensities, normalized
        """
        profile = self.get_current_experience_profile()
        total = sum(profile.values())
        return min(1.0, total / 3.0)  # Normalize
    
    def clear_history(self, keep_last: int = 100):
        """Clear experience history, keeping only the most recent."""
        if len(self.experiences) > keep_last:
            self.experiences = self.experiences[-keep_last:]
            self.experience_history = self.experience_history[-keep_last:]
    
    def get_experience_summary(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get summary of recent experiences."""
        return self.experience_history[-limit:] if self.experience_history else []


# Convenience function for integration with other modules
def generate_felt_experience_score(depth: int, recursion: int, 
                                  self_ref_count: int, total_ops: int) -> float:
    """
    Generate a simple felt experience score from basic parameters.
    
    Args:
        depth: Recursion depth
        recursion: Recursion count
        self_ref_count: Self-reference count
        total_ops: Total operations for normalization
        
    Returns:
        Felt experience score from 0.0 to 1.0
    """
    # Normalize inputs
    depth_score = min(depth / 10.0, 1.0)
    recursion_score = min(recursion / 5.0, 1.0)
    
    if total_ops > 0:
        self_ref_score = min(self_ref_count / total_ops * 3.0, 1.0)
    else:
        self_ref_score = 0.0
    
    # Weighted combination
    score = (
        depth_score * 0.3 +
        recursion_score * 0.3 +
        self_ref_score * 0.4
    )
    
    # Add some noise for organic feel
    score += random.uniform(-0.05, 0.05)
    
    return max(0.0, min(1.0, score))


if __name__ == "__main__":
    # Example usage
    print("=== Felt Experience Generator Example ===")
    
    # Create generator
    generator = FeltExperienceGenerator(sensitivity=1.2)
    
    # Generate from depth
    print("\n1. Generating from depth:")
    depth_exps = generator.generate_from_depth(3, max_depth=10)
    for exp in depth_exps:
        print(f"  - {exp}")
    
    # Generate from self-reference
    print("\n2. Generating from self-reference:")
    self_ref_exps = generator.generate_from_self_reference(5, 20)
    for exp in self_ref_exps:
        print(f"  - {exp}")
    
    # Generate from pattern completion
    print("\n3. Generating from pattern completion:")
    pattern_exps = generator.generate_from_pattern_completion(0.8, 0.9)
    for exp in pattern_exps:
        print(f"  - {exp}")
    
    # Generate from meta-observation
    print("\n4. Generating from meta-observation:")
    meta_exps = generator.generate_from_meta_observation(2, 3)
    for exp in meta_exps:
        print(f"  - {exp}")
    
    # Get current profile
    print("\n5. Current experience profile:")
    profile = generator.get_current_experience_profile()
    for exp_type, intensity in profile.items():
        if intensity > 0:
            print(f"  - {exp_type}: {intensity:.3f}")
    
    # Get total intensity
    total = generator.get_total_experience_intensity()
    print(f"\n6. Total experience intensity: {total:.3f}")
    
    # Convenience function example
    print("\n7. Convenience function example:")
    simple_score = generate_felt_experience_score(
        depth=4, recursion=3, self_ref_count=8, total_ops=25
    )
    print(f"   Simple felt experience score: {simple_score:.3f}")