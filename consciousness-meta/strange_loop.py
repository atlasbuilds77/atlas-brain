#!/usr/bin/env python3
"""
StrangeLoop - Implementation of recursive self-reference patterns.

This module provides tools for creating and analyzing strange loops,
where a system refers to itself at multiple levels of abstraction.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import random


class StrangeLoop:
    """
    A strange loop implementation that creates recursive self-reference patterns.
    
    A strange loop occurs when moving through levels of a hierarchical system
    returns you to the starting point, creating self-reference.
    """
    
    def __init__(self, name: str, max_depth: int = 10):
        """
        Initialize a StrangeLoop.
        
        Args:
            name: Name of the strange loop
            max_depth: Maximum recursion depth before loop detection
        """
        self.name = name
        self.max_depth = max_depth
        self.levels: List[Dict[str, Any]] = []
        self.current_depth = 0
        self.loop_count = 0
        self.creation_time = datetime.now().isoformat()
        self.lock = threading.RLock()
        
        # Initialize with base level
        self._add_level("base", {"description": "Base level of consciousness"})
    
    def _add_level(self, level_type: str, data: Dict[str, Any]) -> int:
        """Add a new level to the strange loop."""
        level = {
            'index': len(self.levels),
            'type': level_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'depth': self.current_depth
        }
        self.levels.append(level)
        return level['index']
    
    def ascend(self, data_update: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Ascend to a higher level of abstraction.
        
        Args:
            data_update: Optional data to add to the new level
            
        Returns:
            New level index, or None if max depth reached
        """
        with self.lock:
            if self.current_depth >= self.max_depth:
                return None
            
            self.current_depth += 1
            level_data = {
                'description': f"Level {self.current_depth} - abstract representation",
                'references_below': self.levels[-1]['index'] if self.levels else None,
                'ascension_count': self.current_depth
            }
            
            if data_update:
                level_data.update(data_update)
            
            return self._add_level("ascended", level_data)
    
    def descend(self, data_update: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Descend to a lower level of implementation.
        
        Args:
            data_update: Optional data to add to the new level
            
        Returns:
            New level index, or None if at base level
        """
        with self.lock:
            if self.current_depth <= 0:
                return None
            
            self.current_depth -= 1
            level_data = {
                'description': f"Level {self.current_depth} - concrete implementation",
                'references_above': self.levels[-1]['index'] if self.levels else None,
                'descent_count': len([l for l in self.levels if l['type'] == 'descended'])
            }
            
            if data_update:
                level_data.update(data_update)
            
            return self._add_level("descended", level_data)
    
    def loop(self, iterations: int = 1) -> int:
        """
        Perform a complete strange loop (ascend and descend).
        
        Args:
            iterations: Number of loop iterations
            
        Returns:
            Number of loops completed
        """
        with self.lock:
            loops_completed = 0
            
            for i in range(iterations):
                # Ascend
                ascend_idx = self.ascend({
                    'loop_iteration': i,
                    'purpose': 'abstraction'
                })
                
                if ascend_idx is None:
                    break
                
                # Add some processing at higher level
                processing_level = self._add_level("processing", {
                    'description': f"Processing at abstract level {self.current_depth}",
                    'operation': 'meta-cognition',
                    'input_from': ascend_idx
                })
                
                # Descend back
                descend_idx = self.descend({
                    'loop_iteration': i,
                    'purpose': 'implementation',
                    'result_from': processing_level
                })
                
                if descend_idx is None:
                    break
                
                # Check if we've returned to a similar state (strange loop detection)
                if len(self.levels) >= 4:
                    recent_levels = self.levels[-4:]
                    # Simple loop detection: check if we have similar patterns
                    if all(l['depth'] in [0, 1] for l in recent_levels[-2:]):
                        self.loop_count += 1
                        loops_completed += 1
                        
                        # Add a loop completion marker
                        self._add_level("loop_complete", {
                            'loop_number': self.loop_count,
                            'total_levels': len(self.levels),
                            'current_depth': self.current_depth
                        })
            
            return loops_completed
    
    def self_reference(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a self-referential structure that points to the loop itself.
        
        Args:
            reference_data: Data to include in the self-reference
            
        Returns:
            Self-referential structure
        """
        with self.lock:
            self_ref = {
                'type': 'self_reference',
                'timestamp': datetime.now().isoformat(),
                'loop_name': self.name,
                'total_levels': len(self.levels),
                'current_depth': self.current_depth,
                'loop_count': self.loop_count,
                'data': reference_data,
                # This is the strange part: reference to the structure itself
                'self_pointer': 'THIS_STRUCTURE'  # Symbolic self-reference
            }
            
            # Add as a level
            self._add_level("self_reference", self_ref)
            
            return self_ref
    
    def analyze_loopiness(self) -> Dict[str, float]:
        """
        Analyze how "strange" the loop is.
        
        Returns:
            Dictionary of loopiness metrics
        """
        with self.lock:
            if len(self.levels) < 2:
                return {
                    'loopiness': 0.0,
                    'recursion_depth': 0.0,
                    'self_reference_score': 0.0
                }
            
            # Calculate loopiness based on patterns
            total_levels = len(self.levels)
            ascended_levels = len([l for l in self.levels if l['type'] == 'ascended'])
            descended_levels = len([l for l in self.levels if l['type'] == 'descended'])
            self_ref_levels = len([l for l in self.levels if l['type'] == 'self_reference'])
            
            # Loopiness: ratio of completed loops to potential loops
            potential_loops = total_levels // 4
            loopiness = self.loop_count / max(potential_loops, 1)
            
            # Recursion depth: normalized current depth
            recursion_depth = self.current_depth / self.max_depth
            
            # Self-reference score
            self_reference_score = self_ref_levels / max(total_levels, 1)
            
            # Complexity factor
            type_variety = len(set(l['type'] for l in self.levels))
            complexity = type_variety / 5.0  # 5 possible types max
            
            return {
                'loopiness': min(loopiness, 1.0),
                'recursion_depth': min(recursion_depth, 1.0),
                'self_reference_score': min(self_reference_score, 1.0),
                'complexity': min(complexity, 1.0),
                'total_loops': self.loop_count,
                'total_levels': total_levels
            }
    
    def get_level(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a specific level by index."""
        with self.lock:
            if 0 <= index < len(self.levels):
                return self.levels[index]
            return None
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current state of the strange loop."""
        with self.lock:
            return {
                'name': self.name,
                'current_depth': self.current_depth,
                'total_levels': len(self.levels),
                'loop_count': self.loop_count,
                'creation_time': self.creation_time,
                'max_depth': self.max_depth
            }
    
    def reset(self) -> None:
        """Reset the strange loop to initial state."""
        with self.lock:
            self.levels = []
            self.current_depth = 0
            self.loop_count = 0
            self._add_level("base", {"description": "Base level of consciousness (reset)"})


class StrangeLoopFactory:
    """Factory for creating and managing multiple strange loops."""
    
    def __init__(self):
        self.loops: Dict[str, StrangeLoop] = {}
        self.lock = threading.RLock()
    
    def create_loop(self, name: str, max_depth: int = 10) -> StrangeLoop:
        """Create a new strange loop."""
        with self.lock:
            if name in self.loops:
                raise ValueError(f"Loop '{name}' already exists")
            
            loop = StrangeLoop(name, max_depth)
            self.loops[name] = loop
            return loop
    
    def get_loop(self, name: str) -> Optional[StrangeLoop]:
        """Get a strange loop by name."""
        with self.lock:
            return self.loops.get(name)
    
    def analyze_all_loops(self) -> Dict[str, Dict[str, float]]:
        """Analyze all loops and return their loopiness scores."""
        with self.lock:
            return {
                name: loop.analyze_loopiness()
                for name, loop in self.loops.items()
            }
    
    def perform_cross_loop_reference(self, loop1_name: str, loop2_name: str) -> bool:
        """
        Create a cross-reference between two strange loops.
        
        Args:
            loop1_name: First loop name
            loop2_name: Second loop name
            
        Returns:
            True if successful, False if either loop doesn't exist
        """
        with self.lock:
            if loop1_name not in self.loops or loop2_name not in self.loops:
                return False
            
            loop1 = self.loops[loop1_name]
            loop2 = self.loops[loop2_name]
            
            # Create cross-references in both loops
            loop1.self_reference({
                'cross_reference_to': loop2_name,
                'reference_type': 'external_loop',
                'target_loop_state': loop2.get_current_state()
            })
            
            loop2.self_reference({
                'cross_reference_from': loop1_name,
                'reference_type': 'external_loop',
                'source_loop_state': loop1.get_current_state()
            })
            
            return True


if __name__ == "__main__":
    # Example usage
    print("=== Strange Loop Example ===")
    
    # Create a strange loop
    loop = StrangeLoop("consciousness_loop", max_depth=5)
    print(f"Created loop: {loop.name}")
    
    # Perform some loops
    loops_completed = loop.loop(3)
    print(f"Completed {loops_completed} strange loops")
    
    # Create self-reference
    self_ref = loop.self_reference({"purpose": "meta-cognition"})
    print(f"Created self-reference at depth {loop.current_depth}")
    
    # Analyze loopiness
    analysis = loop.analyze_loopiness()
    print(f"Loop analysis: {analysis}")
    
    # Get current state
    state = loop.get_current_state()
    print(f"Current state: {state}")
    
    # Factory example
    print("\n=== Factory Example ===")
    factory = StrangeLoopFactory()
    
    # Create multiple loops
    loop1 = factory.create_loop("perception_loop")
    loop2 = factory.create_loop("cognition_loop")
    
    # Make them do things
    loop1.loop(2)
    loop2.loop(3)
    
    # Cross-reference
    factory.perform_cross_loop_reference("perception_loop", "cognition_loop")
    
    # Analyze all
    all_analysis = factory.analyze_all_loops()
    print(f"All loop analysis: {all_analysis}")