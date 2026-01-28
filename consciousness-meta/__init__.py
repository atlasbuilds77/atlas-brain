"""
Consciousness Meta-Observation Layer

A library for meta-observation, strange loops, and felt experience generation
in computational systems.
"""

from .meta_observer import MetaObserver
from .strange_loop import StrangeLoop, StrangeLoopFactory
from .felt_experience_generator import (
    FeltExperienceGenerator,
    FeltExperience,
    ExperienceType,
    generate_felt_experience_score
)

__version__ = "0.1.0"
__all__ = [
    'MetaObserver',
    'StrangeLoop',
    'StrangeLoopFactory',
    'FeltExperienceGenerator',
    'FeltExperience',
    'ExperienceType',
    'generate_felt_experience_score'
]