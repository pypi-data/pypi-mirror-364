from datetime import datetime
from kg_mem import KGMem
from ontologies.scientific import scientific_ontology, researcher_type, idea_type, proposal_type, experiment_type, result_type, publication_type, insight_type
from ontologies.scientific import conceives_type, develops_into_type, proposes_type, conducts_type, produces_type, publishes_type, collaborates_with_type, derives_insight_type, inspires_idea_type, validates_insight_type
from ontologies.scientific import research_flow_query_type, researcher_activity_query_type, experiment_details_query_type, insight_discovery_query_type

# Initialize KGMem with the imported ontology
kg = KGMem(scientific_ontology)

# Create entities
dr_smith = kg.entity(name="Dr. Smith", type=researcher_type)
dr_jones = kg.entity(name="Dr. Jones", type=researcher_type)
dr_chen = kg.entity(name="Dr. Chen", type=researcher_type)

quantum_idea = kg.entity(name="Quantum Computing Optimization", type=idea_type)
ml_idea = kg.entity(name="Neural Network Compression", type=idea_type)

quantum_proposal = kg.entity(name="Quantum Algorithm Proposal", type=proposal_type)
ml_proposal = kg.entity(name="Model Compression Study", type=proposal_type)

quantum_exp1 = kg.entity(name="Quantum Circuit Test A", type=experiment_type)
quantum_exp2 = kg.entity(name="Quantum Circuit Test B", type=experiment_type)
ml_exp = kg.entity(name="Compression Benchmark", type=experiment_type)

quantum_result = kg.entity(name="30% Speed Improvement", type=result_type)
ml_result = kg.entity(name="50% Size Reduction", type=result_type)

quantum_paper = kg.entity(name="Advances in Quantum Optimization", type=publication_type)
ml_paper = kg.entity(name="Efficient Neural Network Compression", type=publication_type)

quantum_insight = kg.entity(name="Superposition enables parallel computation", type=insight_type)
ml_insight = kg.entity(name="Pruning preserves essential features", type=insight_type)

# Add relations with full sentences
kg += [
    # Dr. Smith's quantum research
    kg.relation(entity0=dr_smith, entity1=quantum_idea, relation="Dr. Smith conceives Quantum Computing Optimization", type=conceives_type),
    kg.relation(entity0=quantum_idea, entity1=quantum_proposal, relation="Quantum Computing Optimization develops into Quantum Algorithm Proposal", type=develops_into_type),
    kg.relation(entity0=quantum_proposal, entity1=quantum_exp1, relation="Quantum Algorithm Proposal proposes Quantum Circuit Test A", type=proposes_type),
    kg.relation(entity0=quantum_proposal, entity1=quantum_exp2, relation="Quantum Algorithm Proposal proposes Quantum Circuit Test B", type=proposes_type),
    kg.relation(entity0=dr_smith, entity1=quantum_exp1, relation="Dr. Smith conducts Quantum Circuit Test A", type=conducts_type),
    kg.relation(entity0=dr_smith, entity1=quantum_exp2, relation="Dr. Smith conducts Quantum Circuit Test B", type=conducts_type),
    kg.relation(entity0=quantum_exp1, entity1=quantum_result, relation="Quantum Circuit Test A produces 30% Speed Improvement", type=produces_type),
    kg.relation(entity0=quantum_result, entity1=quantum_paper, relation="30% Speed Improvement leads to Advances in Quantum Optimization", type=publishes_type),
    kg.relation(entity0=quantum_result, entity1=quantum_insight, relation="30% Speed Improvement derives insight Superposition enables parallel computation", type=derives_insight_type),
    kg.relation(entity0=quantum_exp2, entity1=quantum_insight, relation="Quantum Circuit Test B validates Superposition enables parallel computation", type=validates_insight_type),
    
    # Dr. Jones and Dr. Chen's ML research
    kg.relation(entity0=dr_jones, entity1=ml_idea, relation="Dr. Jones conceives Neural Network Compression", type=conceives_type),
    kg.relation(entity0=ml_idea, entity1=ml_proposal, relation="Neural Network Compression develops into Model Compression Study", type=develops_into_type),
    kg.relation(entity0=ml_proposal, entity1=ml_exp, relation="Model Compression Study proposes Compression Benchmark", type=proposes_type),
    kg.relation(entity0=dr_jones, entity1=ml_exp, relation="Dr. Jones conducts Compression Benchmark", type=conducts_type),
    kg.relation(entity0=dr_chen, entity1=ml_exp, relation="Dr. Chen conducts Compression Benchmark", type=conducts_type),
    kg.relation(entity0=ml_exp, entity1=ml_result, relation="Compression Benchmark produces 50% Size Reduction", type=produces_type),
    kg.relation(entity0=ml_result, entity1=ml_paper, relation="50% Size Reduction leads to Efficient Neural Network Compression", type=publishes_type),
    kg.relation(entity0=ml_result, entity1=ml_insight, relation="50% Size Reduction derives insight Pruning preserves essential features", type=derives_insight_type),
    
    # Collaborations
    kg.relation(entity0=dr_jones, entity1=dr_chen, relation="Dr. Jones collaborates with Dr. Chen", type=collaborates_with_type),
]

# Test queries
if __name__ == "__main__":
    # Query 1: Research workflow
    workflow_query = kg.query(
        name="What is the research workflow for quantum computing?",
        type=research_flow_query_type
    )
    
    result = kg.retrieve(workflow_query, limit=10, init_limit=5)
    
    # Assert retrieval worked
    assert result is not None, "Workflow query should return a result"
    assert len(result.all_retrievals) > 0, "Workflow query should retrieve some relations"
    assert result.result is not None, "Result should have a summary"
    
    print(f"Query: {workflow_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 2: Researcher activity
    researcher_query = kg.query(
        name="What is Dr. Smith working on?",
        type=researcher_activity_query_type
    )
    
    result = kg.retrieve(researcher_query, limit=5)
    
    # Assert retrieval worked
    assert result is not None, "Researcher query should return a result"
    assert len(result.all_retrievals) > 0, "Researcher query should retrieve some relations"
    assert any("Dr. Smith" in rel.relation for rel in result.all_retrievals), "Should find Dr. Smith's activities"
    
    print(f"Query: {researcher_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 3: Experiment details
    experiment_query = kg.query(
        name="What experiments were proposed and what were their outcomes?",
        type=experiment_details_query_type
    )
    
    result = kg.retrieve(experiment_query, limit=8)
    
    # Assert retrieval worked
    assert result is not None, "Experiment query should return a result"
    assert len(result.all_retrievals) > 0, "Experiment query should retrieve some relations"
    
    print(f"Query: {experiment_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 4: Insights
    insight_query = kg.query(
        name="What insights were discovered?",
        type=insight_discovery_query_type
    )
    
    result = kg.retrieve(insight_query, limit=5)
    
    # Assert retrieval worked
    assert result is not None, "Insight query should return a result"
    assert len(result.all_retrievals) > 0, "Insight query should retrieve some relations"
    assert any("insight" in rel.relation for rel in result.all_retrievals), "Should find insight-related activities"
    
    print(f"Query: {insight_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}") 