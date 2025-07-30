import sys
sys.path.append('../..')

from datetime import datetime
from kg_mem import KGMem, Ontology, EntityType, RelationType, QueryType

def test_kg_mem_add():
    """Test the add functionality of KGMem"""

    # Create entity types
    person_type = EntityType(
        name="Person",
    )

    project_type = EntityType(
        name="Project", 
    )

    # Create relation types
    works_on_type = RelationType(
        entity_type0=person_type,
        entity_type1=project_type,
        name="works_on",
        context="Represents which person works on which project",
        directed=True
    )

    # Create ontology
    ontology = Ontology(
        entity_types=[person_type, project_type],
        relation_types=[works_on_type],
        query_types=[]
    )

    # Initialize KGMem
    kg = KGMem(ontology)

    # Create entities
    alice = kg.entity(
        name="Alice",
        type=person_type,
    )

    bob = kg.entity(
        name="Bob", 
        type=person_type,
    )

    project_x = kg.entity(
        name="Project X",
        type=project_type,
    )

    # Create relations
    relation1 = kg.relation(
        entity0=alice,
        entity1=project_x,
        relation="Alice is working on Project X",
        type=works_on_type,
    )

    relation2 = kg.relation(
        entity0=bob,
        entity1=project_x,
        relation="Bob is working on Project X", 
        type=works_on_type,
    )

    # Test 1: Add single relation
    print("Test 1: Adding single relation")
    kg.add(relation1)
    print(f"Relations count: {len(kg.relations)}")
    assert len(kg.relations) == 1, "Should have 1 relation after adding one"
    assert kg.relations[0] == relation1, "First relation should be relation1"

    # Test 2: Add multiple relations at once
    print("\nTest 2: Adding list of relations")
    kg.add([relation2])
    print(f"Relations count: {len(kg.relations)}")
    assert len(kg.relations) == 2, "Should have 2 relations after adding another"
    assert kg.relations[1] == relation2, "Second relation should be relation2"

    # Test 3: Using += operator
    print("\nTest 3: Using += operator")
    relation3 = kg.relation(
        entity0=alice,
        entity1=project_x,
        relation="works_on",
        type=works_on_type,
    )
    kg += relation3
    print(f"Relations count: {len(kg.relations)}")
    assert len(kg.relations) == 3, "Should have 3 relations after using += operator"
    assert kg.relations[2] == relation3, "Third relation should be relation3"

    # Test 4: Method chaining
    print("\nTest 4: Method chaining")
    relation4 = kg.relation(
        entity0=bob,
        entity1=project_x,
        relation="works_on",
        type=works_on_type,
    )
    relation5 = kg.relation(
        entity0=alice,
        entity1=project_x,
        relation="works_on",
        type=works_on_type,
    )
    result = kg.add(relation4).add(relation5)
    print(f"Relations count: {len(kg.relations)}")
    assert len(kg.relations) == 5, "Should have 5 relations after method chaining"
    assert kg.relations[3] == relation4, "Fourth relation should be relation4"
    assert kg.relations[4] == relation5, "Fifth relation should be relation5"
    assert result == kg, "Method chaining should return self"

    # Print all relations
    print("\nAll relations:")
    for i, rel in enumerate(kg.relations):
        print(f"{i+1}. {rel.entity0.name} {rel.relation} {rel.entity1.name}")

    # Additional assertions to verify relation structure
    assert all(hasattr(rel, 'entity0') for rel in kg.relations), "All relations should have entity0"
    assert all(hasattr(rel, 'entity1') for rel in kg.relations), "All relations should have entity1"
    assert all(hasattr(rel, 'relation') for rel in kg.relations), "All relations should have relation attribute"

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    # Run the test directly
    test_kg_mem_add()
