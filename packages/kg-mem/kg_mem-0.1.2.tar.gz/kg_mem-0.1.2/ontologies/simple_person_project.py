"""
Simple person-project ontology for basic project tracking.
"""

from kg_mem import Ontology, EntityType, RelationType


# Entity types
person_type = EntityType(name="Person")
project_type = EntityType(name="Project")

# Relation types
works_on_type = RelationType(
    entity_type0=person_type,
    entity_type1=project_type,
    name="works_on",
    context="Represents which person works on which project",
    directed=True
)

# Simple person-project ontology object
simple_person_project_ontology = Ontology(
    entity_types=[person_type, project_type],
    relation_types=[works_on_type],
    query_types=[]
) 