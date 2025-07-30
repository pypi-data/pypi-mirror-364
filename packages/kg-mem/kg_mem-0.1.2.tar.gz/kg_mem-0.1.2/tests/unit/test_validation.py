from datetime import datetime
from kg_mem import KGMem, Ontology, EntityType, RelationType, QueryType

def test_type_validation():
    """Test that entity, relation, and query types are validated against ontology"""
    
    # Create entity types
    person_type = EntityType(name="Person")
    company_type = EntityType(name="Company")
    
    # Create a different entity type not in ontology
    invalid_type = EntityType(name="InvalidType")
    
    # Create relation type
    works_at_type = RelationType(
        entity_type0=person_type,
        entity_type1=company_type,
        name="works_at",
        context="Employment relationship"
    )
    
    # Create query type
    query_type = QueryType(
        name="Find people",
        context="Find people in the graph",
        types_to_retrieve=[person_type]
    )
    
    # Create ontology
    ontology = Ontology(
        entity_types=[person_type, company_type],
        relation_types=[works_at_type],
        query_types=[query_type]
    )
    
    # Initialize KGMem
    kg = KGMem(ontology)
    
    print("Test 1: Valid entity type")
    # This should work
    alice = kg.entity(name="Alice", type=person_type)
    print("✓ Created entity with valid type")
    
    print("\nTest 2: Invalid entity type")
    # This should fail
    try:
        invalid_entity = kg.entity(name="Invalid", type=invalid_type)
        print("✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
    
    print("\nTest 3: Valid relation")
    # This should work
    tech_corp = kg.entity(name="TechCorp", type=company_type)
    relation = kg.relation(
        entity0=alice,
        entity1=tech_corp,
        relation="works at",
        type=works_at_type
    )
    print("✓ Created relation with valid type")
    
    print("\nTest 4: Valid query")
    # This should work
    query = kg.query(name="Find all people", type=query_type)
    print("✓ Created query with valid type")
    
    print("\n✅ All validation tests passed!")

if __name__ == "__main__":
    test_type_validation() 