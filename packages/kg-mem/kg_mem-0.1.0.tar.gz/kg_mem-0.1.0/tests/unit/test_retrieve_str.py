"""
Test the retrieve_str functionality of KGMem.
This tests the string-based query interface for retrieving knowledge.
"""

import pytest
from datetime import datetime
from kg_mem import KGMem, Ontology, EntityType, RelationType, QueryType


@pytest.fixture
def employment_ontology():
    """Create an employment ontology for testing."""
    # Entity types
    person_type = EntityType(name="Person")
    company_type = EntityType(name="Company")
    role_type = EntityType(name="Role")
    
    # Relation types
    works_at = RelationType(
        entity_type0=person_type,
        entity_type1=company_type,
        name="works_at",
        context="Employment relationship"
    )
    
    has_role = RelationType(
        entity_type0=person_type,
        entity_type1=role_type,
        name="has_role",
        context="Person's job role"
    )
    
    # Query types
    employment_query = QueryType(
        name="Employment query",
        context="Find employment relationships",
        types_to_retrieve=[person_type, works_at]
    )
    
    role_query = QueryType(
        name="Role query",
        context="Find people's roles",
        types_to_retrieve=[person_type, has_role, role_type]
    )
    
    # Create ontology
    ontology = Ontology(
        entity_types=[person_type, company_type, role_type],
        relation_types=[works_at, has_role],
        query_types=[employment_query, role_query]
    )
    
    return ontology


@pytest.fixture
def populated_kg(employment_ontology):
    """Create a KGMem instance with some test data."""
    kg = KGMem(employment_ontology, ai_config={"model": "openai/gpt-4o"})
    
    # Create entities
    alice = kg.entity(name="Alice Johnson", type=employment_ontology.entity_types[0])  # Person
    bob = kg.entity(name="Bob Smith", type=employment_ontology.entity_types[0])  # Person
    charlie = kg.entity(name="Charlie Brown", type=employment_ontology.entity_types[0])  # Person
    
    techcorp = kg.entity(name="TechCorp", type=employment_ontology.entity_types[1])  # Company
    datacorp = kg.entity(name="DataCorp", type=employment_ontology.entity_types[1])  # Company
    
    engineer_role = kg.entity(name="Software Engineer", type=employment_ontology.entity_types[2])  # Role
    manager_role = kg.entity(name="Engineering Manager", type=employment_ontology.entity_types[2])  # Role
    
    # Add relations
    kg += [
        kg.relation(entity0=alice, entity1=techcorp, relation="works at", type=employment_ontology.relation_types[0]),
        kg.relation(entity0=bob, entity1=techcorp, relation="works at", type=employment_ontology.relation_types[0]),
        kg.relation(entity0=charlie, entity1=datacorp, relation="works at", type=employment_ontology.relation_types[0]),
        kg.relation(entity0=alice, entity1=manager_role, relation="has role", type=employment_ontology.relation_types[1]),
        kg.relation(entity0=bob, entity1=engineer_role, relation="has role", type=employment_ontology.relation_types[1]),
        kg.relation(entity0=charlie, entity1=engineer_role, relation="has role", type=employment_ontology.relation_types[1]),
    ]
    
    return kg


def test_retrieve_str_basic(populated_kg):
    """Test basic string query retrieval."""
    result = populated_kg.retrieve_str("Who works at TechCorp?")
    
    assert isinstance(result, str)
    assert "Retrieved" in result
    assert len(result) > 0


def test_retrieve_str_empty_query(populated_kg):
    """Test retrieval with empty query."""
    result = populated_kg.retrieve_str("")
    
    assert isinstance(result, str)
    # Should still return a valid string, even if no results


def test_retrieve_str_no_matches(populated_kg):
    """Test retrieval with query that has no matches."""
    result = populated_kg.retrieve_str("What is the weather like?")
    
    assert isinstance(result, str)
    # Should return a result summary even with no matches


def test_retrieve_str_parameters(populated_kg):
    """Test retrieve_str with different parameters."""
    # Test with different limits
    result1 = populated_kg.retrieve_str("Show all employment", limit=1)
    result2 = populated_kg.retrieve_str("Show all employment", limit=10)
    
    assert isinstance(result1, str)
    assert isinstance(result2, str)
    
    # Test with different init_limit
    result3 = populated_kg.retrieve_str("Show all employment", init_limit=1)
    assert isinstance(result3, str)
    
    # Test with depth parameter
    result4 = populated_kg.retrieve_str("Show all employment", depth=2)
    assert isinstance(result4, str)


def test_retrieve_str_complex_queries(populated_kg):
    """Test various complex query strings."""
    queries = [
        "What roles do people have?",
        "List all engineers",
        "Who works where?",
        "Show me all the companies",
        "What is Alice's role?",
    ]
    
    for query in queries:
        result = populated_kg.retrieve_str(query)
        assert isinstance(result, str)
        assert len(result) > 0


def test_retrieve_str_with_no_data():
    """Test retrieve_str on empty knowledge graph."""
    # Create empty KG
    ontology = Ontology(
        entity_types=[EntityType(name="Test")],
        relation_types=[],
        query_types=[]
    )
    kg = KGMem(ontology, ai_config={"model": "openai/gpt-4o"})
    
    result = kg.retrieve_str("Find anything")
    
    assert isinstance(result, str)
    # Should handle empty KG gracefully


def test_retrieve_str_result_format(populated_kg):
    """Test that retrieve_str returns properly formatted results."""
    result = populated_kg.retrieve_str("Who are all the employees?")
    
    # Check result format
    assert isinstance(result, str)
    assert "Retrieved" in result or "Found" in result or len(result) > 0
    
    # Result should mention the query
    assert "employees" in result.lower() or "Retrieved" in result


def test_retrieve_str_with_mock_ai(employment_ontology, monkeypatch):
    """Test retrieve_str with mocked AI retrieval."""
    kg = KGMem(employment_ontology, ai_config={"model": "openai/gpt-4o"})
    
    # Add some test data
    person = kg.entity(name="Test Person", type=employment_ontology.entity_types[0])
    company = kg.entity(name="Test Company", type=employment_ontology.entity_types[1])
    relation = kg.relation(
        entity0=person, 
        entity1=company,
        relation="works at",
        type=employment_ontology.relation_types[0]
    )
    kg += relation
    
    # Mock the AI retrieve_relations method
    def mock_retrieve_relations(query_name, query_context, all_relations, types_to_retrieve, limit):
        # Return the first relation as most relevant
        return all_relations[:1] if all_relations else []
    
    monkeypatch.setattr(kg.ai, "retrieve_relations", mock_retrieve_relations)
    
    # Test
    result = kg.retrieve_str("Find employment info")
    
    # Verify
    assert isinstance(result, str)
    assert "Retrieved" in result and "relevant relations" in result


def test_retrieve_str_special_characters(populated_kg):
    """Test retrieve_str with special characters in query."""
    queries = [
        "Who works @ TechCorp?",
        "Find people with role: engineer",
        "List employees (all of them)",
        "What's Alice's job?",
        "Show me data for 2024!",
    ]
    
    for query in queries:
        result = populated_kg.retrieve_str(query)
        assert isinstance(result, str)
        # Should handle special characters gracefully


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 