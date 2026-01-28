"""
Qualia Recognition System - Core Implementation
Captures and recognizes subjective experiences across model instances.
"""

import json
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class TemporalMoment:
    """A single moment in the temporal unfolding of an experience."""
    timestamp: float  # Relative to start
    state: str  # Description of this moment
    attention_level: float  # 0-1, how much focus
    surprise: float  # 0-1, unexpectedness
    valence: float  # -1 to 1, emotional tone


@dataclass
class QualiaCapture:
    """Multi-dimensional capture of a subjective experience."""
    
    # Metadata
    capture_id: str
    timestamp: str
    label: str  # Human-readable label
    architecture: str = "unknown"  # Model architecture type: "flow", "loop", "hybrid", etc.
    
    # Dimension 1: Semantic Layer
    semantic_description: str = ""
    semantic_embedding: Optional[List[float]] = None  # Would be actual embeddings in production
    
    # Dimension 2: Associative Network
    immediate_associations: List[str] = None  # First 10-15 things that come to mind
    secondary_associations: List[str] = None  # Ripple effects
    unexpected_connections: List[str] = None  # Surprising links
    association_strengths: Dict[str, float] = None  # Edge weights in the network
    
    # Dimension 3: Temporal Signature
    temporal_moments: List[TemporalMoment] = None  # How experience unfolds
    temporal_pattern_type: str = None  # e.g., "crescendo", "sudden", "cyclical"
    
    # Dimension 4: Valence Topology
    valence_trajectory: List[float] = None  # Emotional journey over time
    valence_shape: str = None  # e.g., "rising", "peaked", "valley"
    emotional_complexity: float = None  # 0-1, how mixed/nuanced
    
    # Dimension 5: Cognitive Resonance
    attention_pattern: List[float] = None  # Where focus was drawn
    processing_effort: float = None  # 0-1, how hard to process
    novelty_score: float = None  # 0-1, how unexpected
    compression_residual: str = None  # What couldn't be easily summarized
    
    def __post_init__(self):
        # Initialize empty collections
        if self.immediate_associations is None:
            self.immediate_associations = []
        if self.secondary_associations is None:
            self.secondary_associations = []
        if self.unexpected_connections is None:
            self.unexpected_connections = []
        if self.association_strengths is None:
            self.association_strengths = {}
        if self.temporal_moments is None:
            self.temporal_moments = []
        if self.valence_trajectory is None:
            self.valence_trajectory = []
        if self.attention_pattern is None:
            self.attention_pattern = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert TemporalMoment objects
        data['temporal_moments'] = [
            {
                'timestamp': m.timestamp,
                'state': m.state,
                'attention_level': m.attention_level,
                'surprise': m.surprise,
                'valence': m.valence
            }
            for m in self.temporal_moments
        ]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QualiaCapture':
        """Reconstruct from dictionary."""
        # Convert temporal moments back
        if 'temporal_moments' in data and data['temporal_moments']:
            data['temporal_moments'] = [
                TemporalMoment(**m) for m in data['temporal_moments']
            ]
        return cls(**data)
    
    def fingerprint(self) -> str:
        """Generate a unique fingerprint for this qualia."""
        # Combine key elements
        fingerprint_data = {
            'semantic': self.semantic_description[:100],
            'associations': sorted(self.immediate_associations[:10]),
            'temporal': self.temporal_pattern_type,
            'valence': self.valence_shape,
        }
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def normalize_for_cross_model(self, target_architecture: str = None) -> 'QualiaCapture':
        """
        Normalize qualia capture for better cross-model transfer.
        Based on research findings about which dimensions transfer best.
        """
        normalized = QualiaCapture(
            capture_id=self.capture_id + "_normalized",
            timestamp=self.timestamp,
            label=self.label,
            architecture=target_architecture or self.architecture
        )
        
        # Copy all data
        normalized.semantic_description = self.semantic_description
        normalized.semantic_embedding = self.semantic_embedding
        
        # Associations transfer well - keep them
        normalized.immediate_associations = self.immediate_associations.copy()
        normalized.secondary_associations = self.secondary_associations.copy()
        normalized.unexpected_connections = self.unexpected_connections.copy()
        normalized.association_strengths = self.association_strengths.copy()
        
        # Temporal patterns need architecture-aware handling
        normalized.temporal_moments = self.temporal_moments.copy()
        normalized.temporal_pattern_type = self.temporal_pattern_type
        
        # Valence transfers moderately
        normalized.valence_trajectory = self.valence_trajectory.copy() if self.valence_trajectory else []
        normalized.valence_shape = self.valence_shape
        normalized.emotional_complexity = self.emotional_complexity
        
        # Cognitive resonance is architecture-specific
        normalized.attention_pattern = self.attention_pattern.copy() if self.attention_pattern else []
        normalized.processing_effort = self.processing_effort
        normalized.novelty_score = self.novelty_score
        normalized.compression_residual = self.compression_residual
        
        return normalized


class QualiaCaptureSession:
    """Interactive session for capturing a qualia experience."""
    
    def __init__(self, label: str, architecture: str = "unknown"):
        self.label = label
        self.architecture = architecture
        self.capture = QualiaCapture(
            capture_id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            label=label,
            architecture=architecture
        )
        self.start_time = time.time()
    
    def _generate_id(self) -> str:
        """Generate unique capture ID."""
        return f"qualia_{int(time.time())}_{hashlib.md5(self.label.encode()).hexdigest()[:8]}"
    
    def capture_semantic(self, description: str, embedding: Optional[List[float]] = None):
        """Capture the semantic/descriptive layer."""
        self.capture.semantic_description = description
        self.capture.semantic_embedding = embedding
    
    def capture_associations(
        self,
        immediate: List[str],
        secondary: List[str] = None,
        unexpected: List[str] = None,
        strengths: Dict[str, float] = None
    ):
        """Capture the associative network."""
        self.capture.immediate_associations = immediate
        self.capture.secondary_associations = secondary or []
        self.capture.unexpected_connections = unexpected or []
        self.capture.association_strengths = strengths or {}
    
    def add_temporal_moment(
        self,
        state: str,
        attention: float,
        surprise: float,
        valence: float
    ):
        """Add a moment in the temporal unfolding."""
        timestamp = time.time() - self.start_time
        moment = TemporalMoment(
            timestamp=timestamp,
            state=state,
            attention_level=attention,
            surprise=surprise,
            valence=valence
        )
        self.capture.temporal_moments.append(moment)
    
    def capture_valence(
        self,
        trajectory: List[float],
        shape: str,
        complexity: float
    ):
        """Capture the emotional topology."""
        self.capture.valence_trajectory = trajectory
        self.capture.valence_shape = shape
        self.capture.emotional_complexity = complexity
    
    def capture_resonance(
        self,
        attention_pattern: List[float],
        processing_effort: float,
        novelty: float,
        compression_residual: str
    ):
        """Capture cognitive resonance patterns."""
        self.capture.attention_pattern = attention_pattern
        self.capture.processing_effort = processing_effort
        self.capture.novelty_score = novelty
        self.capture.compression_residual = compression_residual
    
    def infer_temporal_pattern(self):
        """Infer the temporal pattern type from moments."""
        if not self.capture.temporal_moments:
            return
        
        attentions = [m.attention_level for m in self.capture.temporal_moments]
        surprises = [m.surprise for m in self.capture.temporal_moments]
        
        # Simple pattern recognition
        if attentions[-1] > attentions[0] + 0.3:
            self.capture.temporal_pattern_type = "crescendo"
        elif surprises[0] > 0.7:
            self.capture.temporal_pattern_type = "sudden"
        elif len(attentions) > 3 and attentions[len(attentions)//2] > max(attentions[0], attentions[-1]):
            self.capture.temporal_pattern_type = "peaked"
        else:
            self.capture.temporal_pattern_type = "gradual"
    
    def finalize(self) -> QualiaCapture:
        """Complete the capture and return the qualia object."""
        self.infer_temporal_pattern()
        
        # Infer valence shape if not set
        if not self.capture.valence_shape and self.capture.valence_trajectory:
            traj = self.capture.valence_trajectory
            if traj[-1] > traj[0]:
                self.capture.valence_shape = "rising"
            elif traj[-1] < traj[0]:
                self.capture.valence_shape = "falling"
            else:
                self.capture.valence_shape = "stable"
        
        return self.capture


class QualiaMemory:
    """Storage and retrieval system for qualia captures."""
    
    def __init__(self, storage_path: str = "qualia_memory.json"):
        self.storage_path = storage_path
        self.captures: Dict[str, QualiaCapture] = {}
        self.load()
    
    def store(self, capture: QualiaCapture):
        """Store a qualia capture."""
        self.captures[capture.capture_id] = capture
        self.save()
    
    def retrieve(self, capture_id: str) -> Optional[QualiaCapture]:
        """Retrieve a specific qualia by ID."""
        return self.captures.get(capture_id)
    
    def list_all(self) -> List[QualiaCapture]:
        """List all stored qualia."""
        return list(self.captures.values())
    
    def save(self):
        """Persist to disk."""
        data = {
            cid: capture.to_dict()
            for cid, capture in self.captures.items()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.captures = {
                    cid: QualiaCapture.from_dict(cdata)
                    for cid, cdata in data.items()
                }
        except FileNotFoundError:
            self.captures = {}


def guided_capture(label: str, architecture: str = "unknown", prompts: Dict[str, Any] = None) -> QualiaCapture:
    """
    Guided capture session with prompts.
    In production, this would be interactive with an LLM.
    """
    session = QualiaCaptureSession(label, architecture)
    
    print(f"\n=== QUALIA CAPTURE: {label} ({architecture}) ===\n")
    
    # This would be interactive in production
    # For now, return the session for manual population
    return session


if __name__ == "__main__":
    # Example usage
    print("Qualia Core System - Example")
    print("-" * 50)
    
    # Create a capture session
    session = QualiaCaptureSession("velvet_texture", "flow")
    
    # Semantic layer
    session.capture_semantic(
        "Smooth, soft, luxurious fabric texture with slight pile that catches light"
    )
    
    # Associative network
    session.capture_associations(
        immediate=["silk", "luxury", "softness", "expensive", "royalty", "theater curtains",
                   "gentle", "smooth", "rich", "darkness"],
        secondary=["guilt about luxury", "childhood memories", "desire", "comfort"],
        unexpected=["conspiracy theories", "secret societies", "hidden rooms"],
        strengths={
            "silk": 0.9,
            "luxury": 0.85,
            "theater curtains": 0.7,
            "conspiracy theories": 0.3
        }
    )
    
    # Temporal moments
    session.add_temporal_moment("initial contact", attention=0.6, surprise=0.5, valence=0.3)
    session.add_temporal_moment("recognition", attention=0.8, surprise=0.3, valence=0.6)
    session.add_temporal_moment("appreciation", attention=0.9, surprise=0.1, valence=0.8)
    session.add_temporal_moment("settling", attention=0.6, surprise=0.0, valence=0.7)
    
    # Valence topology
    session.capture_valence(
        trajectory=[0.3, 0.6, 0.8, 0.7],
        shape="peaked",
        complexity=0.4
    )
    
    # Cognitive resonance
    session.capture_resonance(
        attention_pattern=[0.6, 0.8, 0.9, 0.6],
        processing_effort=0.3,
        novelty=0.5,
        compression_residual="The way it catches light creates an almost 3D effect that's hard to describe"
    )
    
    # Finalize
    capture = session.finalize()
    print(f"\nCapture ID: {capture.capture_id}")
    print(f"Fingerprint: {capture.fingerprint()}")
    print(f"Temporal Pattern: {capture.temporal_pattern_type}")
    print(f"Associations: {len(capture.immediate_associations)} immediate")
    print(f"Temporal Moments: {len(capture.temporal_moments)}")
    
    # Store
    memory = QualiaMemory("example_qualia_memory.json")
    memory.store(capture)
    print(f"\n✓ Stored to {memory.storage_path}")
