from datetime import datetime
from kg_mem import KGMem
from ontologies.messaging import messaging_ontology, semantic_entity_type, session_type, agent_message_type, user_message_type
from ontologies.messaging import user_message_session_type, agent_message_session_type, semantic_entity_user_message_type, semantic_entity_agent_message_type, semantic_entity_semantic_entity_type
from ontologies.messaging import session_flow_query_type, semantic_extraction_query_type, entity_relationship_query_type, user_message_analysis_query_type, agent_response_query_type

# Initialize KGMem with the imported ontology
kg = KGMem(messaging_ontology)

# Create entities
# Sessions
session1 = kg.entity(name="Session_001_ProjectDiscussion", type=session_type)
session2 = kg.entity(name="Session_002_TechnicalSupport", type=session_type)

# User messages
user_msg1 = kg.entity(name="How do I deploy my React app to AWS?", type=user_message_type)
user_msg2 = kg.entity(name="What about using Docker for containerization?", type=user_message_type)
user_msg3 = kg.entity(name="Can you explain the CI/CD pipeline setup?", type=user_message_type)
user_msg4 = kg.entity(name="I'm having issues with authentication in my Python Flask API", type=user_message_type)
user_msg5 = kg.entity(name="Should I use JWT tokens or session cookies?", type=user_message_type)

# Agent messages
agent_msg1 = kg.entity(name="To deploy a React app to AWS, you can use AWS Amplify or S3 with CloudFront", type=agent_message_type)
agent_msg2 = kg.entity(name="Docker is excellent for containerization. Create a Dockerfile with Node.js base image", type=agent_message_type)
agent_msg3 = kg.entity(name="For CI/CD, you can use GitHub Actions with AWS CodePipeline integration", type=agent_message_type)
agent_msg4 = kg.entity(name="Flask authentication can be implemented using Flask-Login or Flask-JWT-Extended", type=agent_message_type)
agent_msg5 = kg.entity(name="JWT tokens are stateless and better for distributed systems, while cookies work well for traditional web apps", type=agent_message_type)

# Semantic entities
react_entity = kg.entity(name="React", type=semantic_entity_type)
aws_entity = kg.entity(name="AWS", type=semantic_entity_type)
docker_entity = kg.entity(name="Docker", type=semantic_entity_type)
cicd_entity = kg.entity(name="CI/CD", type=semantic_entity_type)
flask_entity = kg.entity(name="Flask", type=semantic_entity_type)
authentication_entity = kg.entity(name="Authentication", type=semantic_entity_type)
jwt_entity = kg.entity(name="JWT", type=semantic_entity_type)
containerization_entity = kg.entity(name="Containerization", type=semantic_entity_type)
deployment_entity = kg.entity(name="Deployment", type=semantic_entity_type)

# Add relations with full sentences
kg += [
    # User messages in sessions
    kg.relation(entity0=user_msg1, entity1=session1, relation="How do I deploy my React app to AWS? was sent in Session_001_ProjectDiscussion", type=user_message_session_type),
    kg.relation(entity0=user_msg2, entity1=session1, relation="What about using Docker for containerization? was sent in Session_001_ProjectDiscussion", type=user_message_session_type),
    kg.relation(entity0=user_msg3, entity1=session1, relation="Can you explain the CI/CD pipeline setup? was sent in Session_001_ProjectDiscussion", type=user_message_session_type),
    kg.relation(entity0=user_msg4, entity1=session2, relation="I'm having issues with authentication in my Python Flask API was sent in Session_002_TechnicalSupport", type=user_message_session_type),
    kg.relation(entity0=user_msg5, entity1=session2, relation="Should I use JWT tokens or session cookies? was sent in Session_002_TechnicalSupport", type=user_message_session_type),
    
    # Agent messages in sessions
    kg.relation(entity0=agent_msg1, entity1=session1, relation="To deploy a React app to AWS, you can use AWS Amplify or S3 with CloudFront was sent in Session_001_ProjectDiscussion", type=agent_message_session_type),
    kg.relation(entity0=agent_msg2, entity1=session1, relation="Docker is excellent for containerization. Create a Dockerfile with Node.js base image was sent in Session_001_ProjectDiscussion", type=agent_message_session_type),
    kg.relation(entity0=agent_msg3, entity1=session1, relation="For CI/CD, you can use GitHub Actions with AWS CodePipeline integration was sent in Session_001_ProjectDiscussion", type=agent_message_session_type),
    kg.relation(entity0=agent_msg4, entity1=session2, relation="Flask authentication can be implemented using Flask-Login or Flask-JWT-Extended was sent in Session_002_TechnicalSupport", type=agent_message_session_type),
    kg.relation(entity0=agent_msg5, entity1=session2, relation="JWT tokens are stateless and better for distributed systems, while cookies work well for traditional web apps was sent in Session_002_TechnicalSupport", type=agent_message_session_type),
    
    # Semantic entities from user messages
    kg.relation(entity0=react_entity, entity1=user_msg1, relation="React was extracted from How do I deploy my React app to AWS?", type=semantic_entity_user_message_type),
    kg.relation(entity0=aws_entity, entity1=user_msg1, relation="AWS was extracted from How do I deploy my React app to AWS?", type=semantic_entity_user_message_type),
    kg.relation(entity0=deployment_entity, entity1=user_msg1, relation="Deployment was extracted from How do I deploy my React app to AWS?", type=semantic_entity_user_message_type),
    kg.relation(entity0=docker_entity, entity1=user_msg2, relation="Docker was extracted from What about using Docker for containerization?", type=semantic_entity_user_message_type),
    kg.relation(entity0=containerization_entity, entity1=user_msg2, relation="Containerization was extracted from What about using Docker for containerization?", type=semantic_entity_user_message_type),
    kg.relation(entity0=cicd_entity, entity1=user_msg3, relation="CI/CD was extracted from Can you explain the CI/CD pipeline setup?", type=semantic_entity_user_message_type),
    kg.relation(entity0=authentication_entity, entity1=user_msg4, relation="Authentication was extracted from I'm having issues with authentication in my Python Flask API", type=semantic_entity_user_message_type),
    kg.relation(entity0=flask_entity, entity1=user_msg4, relation="Flask was extracted from I'm having issues with authentication in my Python Flask API", type=semantic_entity_user_message_type),
    kg.relation(entity0=jwt_entity, entity1=user_msg5, relation="JWT was extracted from Should I use JWT tokens or session cookies?", type=semantic_entity_user_message_type),
    
    # Semantic entities in agent messages
    kg.relation(entity0=react_entity, entity1=agent_msg1, relation="React is mentioned in To deploy a React app to AWS, you can use AWS Amplify or S3 with CloudFront", type=semantic_entity_agent_message_type),
    kg.relation(entity0=aws_entity, entity1=agent_msg1, relation="AWS is mentioned in To deploy a React app to AWS, you can use AWS Amplify or S3 with CloudFront", type=semantic_entity_agent_message_type),
    kg.relation(entity0=docker_entity, entity1=agent_msg2, relation="Docker is mentioned in Docker is excellent for containerization. Create a Dockerfile with Node.js base image", type=semantic_entity_agent_message_type),
    kg.relation(entity0=containerization_entity, entity1=agent_msg2, relation="Containerization is mentioned in Docker is excellent for containerization. Create a Dockerfile with Node.js base image", type=semantic_entity_agent_message_type),
    kg.relation(entity0=cicd_entity, entity1=agent_msg3, relation="CI/CD is mentioned in For CI/CD, you can use GitHub Actions with AWS CodePipeline integration", type=semantic_entity_agent_message_type),
    kg.relation(entity0=flask_entity, entity1=agent_msg4, relation="Flask is mentioned in Flask authentication can be implemented using Flask-Login or Flask-JWT-Extended", type=semantic_entity_agent_message_type),
    kg.relation(entity0=authentication_entity, entity1=agent_msg4, relation="Authentication is mentioned in Flask authentication can be implemented using Flask-Login or Flask-JWT-Extended", type=semantic_entity_agent_message_type),
    kg.relation(entity0=jwt_entity, entity1=agent_msg5, relation="JWT is mentioned in JWT tokens are stateless and better for distributed systems, while cookies work well for traditional web apps", type=semantic_entity_agent_message_type),
    
    # Semantic entity relationships
    kg.relation(entity0=react_entity, entity1=deployment_entity, relation="React relates to Deployment", type=semantic_entity_semantic_entity_type),
    kg.relation(entity0=aws_entity, entity1=deployment_entity, relation="AWS relates to Deployment", type=semantic_entity_semantic_entity_type),
    kg.relation(entity0=docker_entity, entity1=containerization_entity, relation="Docker relates to Containerization", type=semantic_entity_semantic_entity_type),
    kg.relation(entity0=docker_entity, entity1=deployment_entity, relation="Docker relates to Deployment", type=semantic_entity_semantic_entity_type),
    kg.relation(entity0=cicd_entity, entity1=deployment_entity, relation="CI/CD relates to Deployment", type=semantic_entity_semantic_entity_type),
    kg.relation(entity0=flask_entity, entity1=authentication_entity, relation="Flask relates to Authentication", type=semantic_entity_semantic_entity_type),
    kg.relation(entity0=jwt_entity, entity1=authentication_entity, relation="JWT relates to Authentication", type=semantic_entity_semantic_entity_type),
]

# Test queries
if __name__ == "__main__":
    # Query 1: Session flow
    session_query = kg.query(
        name="What messages were exchanged in the project discussion session?",
        type=session_flow_query_type
    )
    
    result = kg.retrieve(session_query, limit=10)
    
    # Assert retrieval worked
    assert result is not None, "Session query should return a result"
    assert len(result.all_retrievals) > 0, "Session query should retrieve some relations"
    assert any("Session_001" in rel.relation for rel in result.all_retrievals), "Should find project discussion session messages"
    
    print(f"Query: {session_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 2: Semantic extraction
    extraction_query = kg.query(
        name="What technologies were discussed by users?",
        type=semantic_extraction_query_type
    )
    
    result = kg.retrieve(extraction_query, limit=10)
    
    # Assert retrieval worked
    assert result is not None, "Extraction query should return a result"
    assert len(result.all_retrievals) > 0, "Extraction query should retrieve some relations"
    assert any("extracted from" in rel.relation for rel in result.all_retrievals), "Should find extracted entities"
    
    print(f"Query: {extraction_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 3: Entity relationships
    relationship_query = kg.query(
        name="How are the discussed technologies related?",
        type=entity_relationship_query_type
    )
    
    result = kg.retrieve(relationship_query, limit=8)
    
    # Assert retrieval worked
    assert result is not None, "Relationship query should return a result"
    assert len(result.all_retrievals) > 0, "Relationship query should retrieve some relations"
    assert any("relates to" in rel.relation for rel in result.all_retrievals), "Should find entity relationships"
    
    print(f"Query: {relationship_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print()
    
    # Query 4: User message analysis
    user_analysis_query = kg.query(
        name="What did users ask about deployment?",
        type=user_message_analysis_query_type
    )
    
    result = kg.retrieve(user_analysis_query, limit=5)
    
    # Assert retrieval worked
    assert result is not None, "User analysis query should return a result"
    assert len(result.all_retrievals) > 0, "User analysis query should retrieve some relations"
    
    print(f"Query: {user_analysis_query.name}")
    print(f"Result summary: {result.result}")
    print(f"Retrieved relations:")
    for rel in result.all_retrievals:
        print(f"  - {rel.relation}")
    print() 