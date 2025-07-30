"""
Messaging system ontology for chat sessions and semantic entities.
"""

from datetime import datetime
from kg_mem import Ontology, EntityType, RelationType, QueryType


# Entity types
semantic_entity_type = EntityType(name="SemanticEntity", created_at=datetime.now())
session_type = EntityType(name="Session", created_at=datetime.now())
agent_message_type = EntityType(name="AgentMessage", created_at=datetime.now())
user_message_type = EntityType(name="UserMessage", created_at=datetime.now())

# Relation types
user_message_session_type = RelationType(
    entity_type0=user_message_type,
    entity_type1=session_type,
    name="user_message_in_session",
    context="User message belongs to a session",
    created_at=datetime.now()
)

agent_message_session_type = RelationType(
    entity_type0=agent_message_type,
    entity_type1=session_type,
    name="agent_message_in_session",
    context="Agent message belongs to a session",
    created_at=datetime.now()
)

semantic_entity_user_message_type = RelationType(
    entity_type0=semantic_entity_type,
    entity_type1=user_message_type,
    name="extracted_from_user_message",
    context="Semantic entity extracted from user message",
    created_at=datetime.now()
)

semantic_entity_agent_message_type = RelationType(
    entity_type0=semantic_entity_type,
    entity_type1=agent_message_type,
    name="mentioned_in_agent_message",
    context="Semantic entity mentioned in agent message",
    created_at=datetime.now()
)

semantic_entity_semantic_entity_type = RelationType(
    entity_type0=semantic_entity_type,
    entity_type1=semantic_entity_type,
    name="relates_to",
    context="Semantic entities are related",
    created_at=datetime.now()
)

# Query types
session_flow_query_type = QueryType(
    name="Session flow query",
    context="Understanding the flow of messages in a session",
    types_to_retrieve=[session_type, user_message_session_type, agent_message_session_type]
)

semantic_extraction_query_type = QueryType(
    name="Semantic extraction query",
    context="Finding semantic entities from messages",
    types_to_retrieve=[semantic_entity_type, semantic_entity_user_message_type, semantic_entity_agent_message_type]
)

entity_relationship_query_type = QueryType(
    name="Entity relationship query",
    context="Understanding relationships between semantic entities",
    types_to_retrieve=[semantic_entity_type, semantic_entity_semantic_entity_type]
)

user_message_analysis_query_type = QueryType(
    name="User message analysis query",
    context="Analyzing user messages and their entities",
    types_to_retrieve=[user_message_type, user_message_session_type, semantic_entity_user_message_type]
)

agent_response_query_type = QueryType(
    name="Agent response query",
    context="Analyzing agent responses and referenced entities",
    types_to_retrieve=[agent_message_type, agent_message_session_type, semantic_entity_agent_message_type]
)

# Messaging ontology object
messaging_ontology = Ontology(
    entity_types=[semantic_entity_type, session_type, agent_message_type, user_message_type],
    relation_types=[user_message_session_type, agent_message_session_type, semantic_entity_user_message_type,
                   semantic_entity_agent_message_type, semantic_entity_semantic_entity_type],
    query_types=[session_flow_query_type, semantic_extraction_query_type, entity_relationship_query_type,
                user_message_analysis_query_type, agent_response_query_type]
) 