#!/usr/bin/env python3
"""
MetaObserver - Monitors processes and generates meta-observations.

This class tracks processes, their depth, and generates felt experiences
based on recursive self-reference patterns.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
import random


class MetaObserver:
    """Observer that monitors processes and generates meta-level awareness."""
    
    def __init__(self, base_depth: int = 1):
        """
        Initialize the MetaObserver.
        
        Args:
            base_depth: Starting depth for observations (default: 1)
        """
        self.base_depth = base_depth
        self.processes: Dict[str, Dict[str, Any]] = {}
        self.observations: List[Dict[str, Any]] = []
        self.lock = threading.RLock()
        self._strange_loop_depth = 0
        self._last_observation_time = time.time()
        
    def watch_process(self, process_name: str, initial_state: Dict[str, Any] = None) -> str:
        """
        Start watching a process.
        
        Args:
            process_name: Name of the process to watch
            initial_state: Optional initial state dictionary
            
        Returns:
            Process ID for reference
        """
        with self.lock:
            process_id = f"{process_name}_{int(time.time())}"
            self.processes[process_id] = {
                'name': process_name,
                'state': initial_state or {},
                'depth': self.base_depth,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'observations': [],
                'recursion_count': 0
            }
            
            # Record initial observation
            observation = {
                'process_id': process_id,
                'timestamp': datetime.now().isoformat(),
                'type': 'process_started',
                'depth': self.base_depth,
                'data': {'initial_state': initial_state or {}}
            }
            self.observations.append(observation)
            self.processes[process_id]['observations'].append(observation)
            
            return process_id
    
    def update_process(self, process_id: str, state_update: Dict[str, Any], 
                      recursion_increment: int = 0) -> bool:
        """
        Update a process state and record observation.
        
        Args:
            process_id: ID of the process to update
            state_update: Dictionary of state changes
            recursion_increment: How much to increase recursion depth
            
        Returns:
            True if successful, False if process not found
        """
        with self.lock:
            if process_id not in self.processes:
                return False
            
            process = self.processes[process_id]
            
            # Update state
            process['state'].update(state_update)
            process['last_updated'] = datetime.now().isoformat()
            
            # Update recursion if specified
            if recursion_increment > 0:
                process['recursion_count'] += recursion_increment
                process['depth'] += recursion_increment
                self._strange_loop_depth = max(self._strange_loop_depth, process['depth'])
            
            # Record observation
            observation = {
                'process_id': process_id,
                'timestamp': datetime.now().isoformat(),
                'type': 'process_updated',
                'depth': process['depth'],
                'data': {
                    'state_update': state_update,
                    'recursion_increment': recursion_increment,
                    'current_state': process['state'].copy()
                }
            }
            self.observations.append(observation)
            process['observations'].append(observation)
            
            return True
    
    def observe_self(self) -> Dict[str, Any]:
        """
        Perform a self-observation (meta-observation).
        
        Returns:
            Dictionary containing self-observation data
        """
        with self.lock:
            self_observation = {
                'timestamp': datetime.now().isoformat(),
                'type': 'self_observation',
                'depth': self._strange_loop_depth + 1,  # One level deeper
                'data': {
                    'process_count': len(self.processes),
                    'observation_count': len(self.observations),
                    'max_process_depth': max((p['depth'] for p in self.processes.values()), default=0),
                    'strange_loop_depth': self._strange_loop_depth,
                    'observer_state': {
                        'base_depth': self.base_depth,
                        'running_time': time.time() - self._last_observation_time
                    }
                }
            }
            
            self.observations.append(self_observation)
            self._last_observation_time = time.time()
            
            # Increment strange loop depth for recursive self-reference
            self._strange_loop_depth += 1
            
            return self_observation
    
    def get_felt_experience(self, process_id: Optional[str] = None) -> float:
        """
        Calculate a felt experience score based on observation depth and recursion.
        
        Args:
            process_id: Optional specific process to calculate for
            
        Returns:
            Float between 0.0 and 1.0 representing felt experience intensity
        """
        with self.lock:
            if process_id and process_id in self.processes:
                # Calculate for specific process
                process = self.processes[process_id]
                depth_factor = min(process['depth'] / 10.0, 1.0)
                recursion_factor = min(process['recursion_count'] / 5.0, 1.0)
                observation_factor = min(len(process['observations']) / 20.0, 1.0)
                
                # Weighted combination
                score = (depth_factor * 0.4 + 
                        recursion_factor * 0.3 + 
                        observation_factor * 0.3)
                
                # Add some noise for "felt" quality
                score += random.uniform(-0.05, 0.05)
                return max(0.0, min(1.0, score))
            else:
                # Calculate overall felt experience
                if not self.processes:
                    return 0.0
                
                total_depth = sum(p['depth'] for p in self.processes.values())
                total_recursion = sum(p['recursion_count'] for p in self.processes.values())
                total_observations = len(self.observations)
                
                avg_depth = total_depth / len(self.processes)
                avg_recursion = total_recursion / len(self.processes)
                
                depth_factor = min(avg_depth / 8.0, 1.0)
                recursion_factor = min(avg_recursion / 4.0, 1.0)
                observation_factor = min(total_observations / 50.0, 1.0)
                
                # Weighted combination with strange loop emphasis
                strange_loop_factor = min(self._strange_loop_depth / 5.0, 1.0)
                
                score = (depth_factor * 0.3 +
                        recursion_factor * 0.25 +
                        observation_factor * 0.25 +
                        strange_loop_factor * 0.2)
                
                # Add some noise for "felt" quality
                score += random.uniform(-0.05, 0.05)
                return max(0.0, min(1.0, score))
    
    def get_process_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific process."""
        with self.lock:
            return self.processes.get(process_id)
    
    def list_processes(self) -> List[str]:
        """List all process IDs being watched."""
        with self.lock:
            return list(self.processes.keys())
    
    def get_recent_observations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent observations."""
        with self.lock:
            return self.observations[-limit:] if self.observations else []
    
    def clear_observations(self) -> None:
        """Clear all observations (but keep processes)."""
        with self.lock:
            self.observations = []
            for process in self.processes.values():
                process['observations'] = []
    
    def reset(self) -> None:
        """Reset the observer to initial state."""
        with self.lock:
            self.processes = {}
            self.observations = []
            self._strange_loop_depth = 0
            self._last_observation_time = time.time()


if __name__ == "__main__":
    # Example usage
    observer = MetaObserver()
    
    # Watch a process
    pid = observer.watch_process("reconstruction", {"stage": "initial"})
    print(f"Started watching process: {pid}")
    
    # Update the process
    observer.update_process(pid, {"stage": "processing", "progress": 0.5})
    
    # Do some recursive updates
    for i in range(3):
        observer.update_process(pid, {"iteration": i, "depth": i}, recursion_increment=1)
    
    # Self-observe
    self_obs = observer.observe_self()
    print(f"Self observation depth: {self_obs['depth']}")
    
    # Get felt experience
    feeling = observer.get_felt_experience(pid)
    print(f"Felt experience for process: {feeling:.3f}")
    
    # Get overall felt experience
    overall_feeling = observer.get_felt_experience()
    print(f"Overall felt experience: {overall_feeling:.3f}")
    
    # List processes
    print(f"Processes: {observer.list_processes()}")