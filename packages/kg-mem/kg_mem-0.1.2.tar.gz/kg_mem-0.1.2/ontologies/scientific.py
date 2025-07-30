"""
Scientific experiments ontology for research workflows.
"""

from datetime import datetime
from kg_mem import Ontology, EntityType, RelationType, QueryType


# Entity types
researcher_type = EntityType(name="Researcher", created_at=datetime.now())
idea_type = EntityType(name="Idea", created_at=datetime.now())
proposal_type = EntityType(name="Proposal", created_at=datetime.now())
experiment_type = EntityType(name="Experiment", created_at=datetime.now())
result_type = EntityType(name="Result", created_at=datetime.now())
publication_type = EntityType(name="Publication", created_at=datetime.now())
insight_type = EntityType(name="Insight", created_at=datetime.now())

# Relation types
conceives_type = RelationType(
    entity_type0=researcher_type,
    entity_type1=idea_type,
    name="conceives",
    context="Researcher comes up with a new idea",
    created_at=datetime.now()
)

develops_into_type = RelationType(
    entity_type0=idea_type,
    entity_type1=proposal_type,
    name="develops_into",
    context="An idea is developed into a formal proposal",
    created_at=datetime.now()
)

proposes_type = RelationType(
    entity_type0=proposal_type,
    entity_type1=experiment_type,
    name="proposes",
    context="A proposal suggests specific experiments",
    created_at=datetime.now()
)

conducts_type = RelationType(
    entity_type0=researcher_type,
    entity_type1=experiment_type,
    name="conducts",
    context="Researcher performs the experiment",
    created_at=datetime.now()
)

produces_type = RelationType(
    entity_type0=experiment_type,
    entity_type1=result_type,
    name="produces",
    context="Experiment yields results",
    created_at=datetime.now()
)

publishes_type = RelationType(
    entity_type0=result_type,
    entity_type1=publication_type,
    name="leads_to",
    context="Results lead to publication",
    created_at=datetime.now()
)

collaborates_with_type = RelationType(
    entity_type0=researcher_type,
    entity_type1=researcher_type,
    name="collaborates_with",
    context="Researchers work together",
    created_at=datetime.now(),
    directed=False  # Bidirectional relationship
)

derives_insight_type = RelationType(
    entity_type0=result_type,
    entity_type1=insight_type,
    name="derives_insight",
    context="Results lead to new insights",
    created_at=datetime.now()
)

inspires_idea_type = RelationType(
    entity_type0=insight_type,
    entity_type1=idea_type,
    name="inspires",
    context="Insights inspire new ideas",
    created_at=datetime.now()
)

validates_insight_type = RelationType(
    entity_type0=experiment_type,
    entity_type1=insight_type,
    name="validates",
    context="Experiment validates an insight",
    created_at=datetime.now()
)

# Query types
research_flow_query_type = QueryType(
    name="Research workflow query",
    context="Tracking the flow from ideas to publications",
    types_to_retrieve=[conceives_type, develops_into_type, proposes_type, produces_type, 
                      publishes_type, derives_insight_type]
)

researcher_activity_query_type = QueryType(
    name="Researcher activity query",
    context="Finding what a researcher is working on",
    types_to_retrieve=[researcher_type, conceives_type, conducts_type, collaborates_with_type]
)

experiment_details_query_type = QueryType(
    name="Experiment details query",
    context="Understanding experiment context and outcomes",
    types_to_retrieve=[experiment_type, proposes_type, conducts_type, produces_type, validates_insight_type]
)

insight_discovery_query_type = QueryType(
    name="Insight discovery query",
    context="Tracking insights and their impact",
    types_to_retrieve=[insight_type, derives_insight_type, inspires_idea_type, validates_insight_type]
)

# Scientific experiments ontology object
scientific_ontology = Ontology(
    entity_types=[researcher_type, idea_type, proposal_type, experiment_type, result_type, 
                  publication_type, insight_type],
    relation_types=[conceives_type, develops_into_type, proposes_type, conducts_type, produces_type, 
                   publishes_type, collaborates_with_type, derives_insight_type, inspires_idea_type, 
                   validates_insight_type],
    query_types=[research_flow_query_type, researcher_activity_query_type, experiment_details_query_type, 
                insight_discovery_query_type]
) 