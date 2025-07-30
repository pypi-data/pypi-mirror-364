"""
Test the add_unstructured functionality of KGMem.
This tests extracting structured knowledge from unstructured text.
"""

import pytest
from datetime import datetime
from kg_mem import KGMem, Ontology, EntityType, RelationType, QueryType


@pytest.fixture
def basic_ontology():
    """Create a basic ontology for testing."""
    # Entity types
    person_type = EntityType(name="Person")
    organization_type = EntityType(name="Organization")
    location_type = EntityType(name="Location")
    
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
    
    # Create ontology
    ontology = Ontology(
        entity_types=[person_type, organization_type, location_type],
        relation_types=[works_for, located_in],
        query_types=[]
    )
    
    return ontology


@pytest.fixture
def scientific_ontology():
    """Create a scientific ontology for testing."""
    # Entity types
    researcher_type = EntityType(name="Researcher")
    experiment_type = EntityType(name="Experiment")
    result_type = EntityType(name="Result")
    
    # Relation types
    conducts = RelationType(
        name="conducts",
        entity_type0=researcher_type,
        entity_type1=experiment_type,
        context="Researcher performs experiment"
    )
    
    produces = RelationType(
        name="produces",
        entity_type0=experiment_type,
        entity_type1=result_type,
        context="Experiment yields results"
    )
    
    # Create ontology
    ontology = Ontology(
        entity_types=[researcher_type, experiment_type, result_type],
        relation_types=[conducts, produces],
        query_types=[]
    )
    
    return ontology


def test_add_unstructured_basic(basic_ontology, monkeypatch, tmp_path):
    """Test adding unstructured text with basic ontology."""
    # Initialize KGMem with mock AI config
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(basic_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method to return empty list
    def mock_extract_relations(text_chunk):
        return []
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    # Test text
    text_chunk = "John Smith works for Google. Google is located in Mountain View."
    
    # Add unstructured text
    relations = kg.add_unstructured(text_chunk)
    
    # Verify return value
    assert isinstance(relations, list)
    assert len(relations) == 0  # Mock returns empty list


def test_add_unstructured_scientific(scientific_ontology, monkeypatch, tmp_path):
    """Test adding unstructured text with scientific ontology."""
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(scientific_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method
    def mock_extract_relations(text_chunk):
        return []
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    text_chunk = """
    Dr. Jane Smith conducted the quantum computing experiment.
    The quantum computing experiment produced significant speedup results.
    """
    
    relations = kg.add_unstructured(text_chunk)
    
    assert isinstance(relations, list)


def test_add_unstructured_empty_text(basic_ontology, monkeypatch, tmp_path):
    """Test adding empty text."""
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(basic_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method
    def mock_extract_relations(text_chunk):
        return []
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    relations = kg.add_unstructured("")
    
    assert isinstance(relations, list)
    # Empty text should return empty list


def test_add_unstructured_complex_text(basic_ontology, monkeypatch, tmp_path):
    """Test adding complex unstructured text."""
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(basic_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method
    def mock_extract_relations(text_chunk):
        return []
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    text_chunk = """
    Alice Johnson, the CEO of TechCorp, announced today that the company
    is expanding its operations to London. TechCorp, which is currently
    located in San Francisco, has hired Bob Smith as the new VP of Engineering.
    Bob previously worked at DataInc, which is located in New York.
    """
    
    relations = kg.add_unstructured(text_chunk)
    
    assert isinstance(relations, list)


def test_add_unstructured_no_matching_entities(basic_ontology, monkeypatch, tmp_path):
    """Test adding text that doesn't match ontology."""
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(basic_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method
    def mock_extract_relations(text_chunk):
        return []
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    # Text about topics not in the ontology
    text_chunk = "The weather is nice today. The sky is blue."
    
    relations = kg.add_unstructured(text_chunk)
    
    assert isinstance(relations, list)
    # Should return empty list if no entities match ontology


def test_add_unstructured_updates_kg_state(basic_ontology, monkeypatch, tmp_path):
    """Test that add_unstructured updates KG state."""
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(basic_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method
    def mock_extract_relations(text_chunk):
        return []
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    initial_relation_count = len(kg.relations)
    initial_entity_count = len(kg.entities)
    
    text_chunk = "Sarah works for Microsoft. Microsoft is located in Seattle."
    relations = kg.add_unstructured(text_chunk)
    
    # With mock returning empty list, no changes expected
    assert len(kg.relations) == initial_relation_count
    assert len(kg.entities) == initial_entity_count


def test_add_unstructured_with_mock_ai(basic_ontology, monkeypatch, tmp_path):
    """Test add_unstructured with mocked AI extraction."""
    storage_path = tmp_path / "test_kg.json"
    kg = KGMem(basic_ontology, ai_config={"model": "openai/gpt-4o"}, storage_path=str(storage_path))
    
    # Mock the AI extract_relations method
    mock_relations = []
    
    def mock_extract_relations(text_chunk):
        # Create mock entities and relations
        person = kg.entity(name="John Doe", type=basic_ontology.entity_types[0])  # Person
        org = kg.entity(name="Acme Corp", type=basic_ontology.entity_types[1])  # Organization
        relation = kg.relation(
            entity0=person,
            entity1=org,
            relation="works for",
            type=basic_ontology.relation_types[0]  # works_for
        )
        return [relation]
    
    monkeypatch.setattr(kg.ai, "extract_relations", mock_extract_relations)
    
    # Test
    text_chunk = "John Doe works for Acme Corp."
    relations = kg.add_unstructured(text_chunk)
    
    # Verify
    assert len(relations) == 1
    assert relations[0].entity0.name == "John Doe"
    assert relations[0].entity1.name == "Acme Corp"
    assert len(kg.relations) == 1
    assert len(kg.entities) == 2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 