"""
Basic general purpose ontology for common entities and relationships.
"""

from datetime import datetime
from kg_mem import Ontology, EntityType, RelationType, QueryType


# Entity types
person_type = EntityType(name="Person")
organization_type = EntityType(name="Organization")
location_type = EntityType(name="Location")
concept_type = EntityType(name="Concept")

# Relation types
works_for = RelationType(
    name="works_for",
    entity_type0=person_type,
    entity_type1=organization_type,
    context="Employment relationships"
)

located_in = RelationType(
    name="located_in",
    entity_type0=organization_type,
    entity_type1=location_type,
    context="Geographical locations"
)

knows = RelationType(
    name="knows",
    entity_type0=person_type,
    entity_type1=person_type,
    context="Personal relationships"
)

related_to = RelationType(
    name="related_to",
    entity_type0=concept_type,
    entity_type1=concept_type,
    context="Conceptual relationships"
)

# Basic ontology object
basic_ontology = Ontology(
    entity_types=[person_type, organization_type, location_type, concept_type],
    relation_types=[works_for, located_in, knows, related_to],
    query_types=[]
) 