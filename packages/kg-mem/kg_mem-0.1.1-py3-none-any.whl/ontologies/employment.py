"""
Employment ontology for tracking work relationships.
"""

from datetime import datetime
from kg_mem import Ontology, EntityType, RelationType, QueryType


# Entity types
person_type = EntityType(name="Person", created_at=datetime.now())
company_type = EntityType(name="Company", created_at=datetime.now())

# Relation types
works_at_type = RelationType(
    entity_type0=person_type,
    entity_type1=company_type,
    name="works_at",
    context="Employment relationship between person and company",
    created_at=datetime.now()
)

# Query types
employment_query_type = QueryType(
    name="Find employment relationships",
    context="Looking for who works where",
    types_to_retrieve=[works_at_type, person_type]
)

# Employment ontology object
employment_ontology = Ontology(
    entity_types=[person_type, company_type],
    relation_types=[works_at_type],
    query_types=[employment_query_type]
) 