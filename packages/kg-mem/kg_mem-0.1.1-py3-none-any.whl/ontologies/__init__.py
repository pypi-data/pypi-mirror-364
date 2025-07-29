"""
Knowledge graph ontologies for different domains.

This package contains predefined ontologies that can be used with the KGMem system.
Each ontology defines entity types, relation types, and query types for a specific domain.
"""

from .basic import basic_ontology
from .employment import employment_ontology
from .simple_person_project import simple_person_project_ontology
from .messaging import messaging_ontology
from .github import github_ontology
from .scientific import scientific_ontology

# Map of ontology names to ontology objects
ONTOLOGY_MAP = {
    "basic": basic_ontology,
    "employment": employment_ontology,
    "simple_person_project": simple_person_project_ontology,
    "messaging": messaging_ontology,
    "github": github_ontology,
    "scientific": scientific_ontology,
}

__all__ = [
    "basic_ontology",
    "employment_ontology", 
    "simple_person_project_ontology",
    "messaging_ontology",
    "github_ontology", 
    "scientific_ontology",
    "ONTOLOGY_MAP"
] 