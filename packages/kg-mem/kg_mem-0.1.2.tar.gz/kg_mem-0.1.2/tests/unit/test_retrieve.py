from datetime import datetime
from kg_mem import KGMem, Ontology, EntityType, RelationType, QueryType

# Create entity types
person_type = EntityType(name="Person", created_at=datetime.now())
company_type = EntityType(name="Company", created_at=datetime.now())

# Create relation types
works_at_type = RelationType(
    entity_type0=person_type,
    entity_type1=company_type,
    name="works_at",
    context="Employment relationship between person and company",
    created_at=datetime.now()
)

# Create query type
employment_query_type = QueryType(
    name="Find employment relationships",
    context="Looking for who works where",
    types_to_retrieve=[works_at_type, person_type]
)

# Create ontology
ontology = Ontology(
    entity_types=[person_type, company_type],
    relation_types=[works_at_type],
    query_types=[employment_query_type]
)

# Initialize KGMem
kg = KGMem(ontology)

# Add some sample data
alice = kg.entity(name="Alice", type=person_type)
bob = kg.entity(name="Bob", type=person_type)
charlie = kg.entity(name="Charlie", type=person_type)

tech_corp = kg.entity(name="TechCorp", type=company_type)
data_inc = kg.entity(name="DataInc", type=company_type)

# Add relations
kg += [
    kg.relation(entity0=alice, entity1=tech_corp, relation="works at", type=works_at_type),
    kg.relation(entity0=bob, entity1=tech_corp, relation="works at", type=works_at_type),
    kg.relation(entity0=charlie, entity1=data_inc, relation="works at", type=works_at_type),
]

# Create a query
employment_query = kg.query(
    name="Who works at TechCorp?",
    type=employment_query_type
)

# Retrieve relevant relations
result = kg.retrieve(employment_query, limit=5, init_limit=2)

print(f"Query: {employment_query.name}")
print(f"Result summary: {result.result}")
print(f"Initial retrievals ({len(result.init_retrievals)}): ")
for rel in result.init_retrievals:
    print(f"  - {rel.entity0.name} {rel.relation} {rel.entity1.name}")
print(f"All retrievals ({len(result.all_retrievals)}): ")
for rel in result.all_retrievals:
    print(f"  - {rel.entity0.name} {rel.relation} {rel.entity1.name}") 