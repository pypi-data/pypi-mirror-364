"""Colección de agentes disponibles en AGIX."""

from .genetic import GeneticAgent
from .neuromorphic import NeuromorphicAgent
from .universal import UniversalAgent
from .narrative import NarrativeAgent

__all__ = [
    "GeneticAgent",
    "NeuromorphicAgent",
    "UniversalAgent",
    "NarrativeAgent",
]
