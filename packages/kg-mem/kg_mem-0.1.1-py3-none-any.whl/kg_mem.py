from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Union, TYPE_CHECKING, Any
import dspy
from ai import AI
from storage import JSONStorage

if TYPE_CHECKING:
  # These are for type hints only
  Entity = Any
  Relation = Any
  Query = Any

class EntityType(BaseModel):
  name: str
  created_at: datetime = Field(default_factory=datetime.now)

class RelationType(BaseModel):
  entity_type0: EntityType
  entity_type1: EntityType
  name: str
  context: str = Field(description="In what context does this relationship type appear, and why is it important?", default="")
  created_at: datetime = Field(default_factory=datetime.now)
  directed: bool = True
  required: bool = True

class QueryType(BaseModel):
  name: str
  context: str = Field(description="In what context is this query type created, and why is it important?", default="")
  types_to_retrieve: list[Union[EntityType, RelationType]]

class QueryResult(BaseModel):
  result: str
  init_retrievals: list[Any] # Should be Union['Relation', 'Entity']
  all_retrievals: list[Any] # Should be Union['Relation', 'Entity']
  init_limit: int
  total_limit: int
  depth: int

class Ontology(BaseModel):
  entity_types: list[EntityType]
  relation_types: list[RelationType]
  query_types: list[QueryType]

class KGMem:
  entity = None
  relation = None
  query = None

  def __init__(self, ontology, ai_config: dict = {}, storage_path: str = None):
    self.ontology = ontology
    self.relations = []
    self.entities = []
    self.storage = JSONStorage(storage_path)

    class Entity(BaseModel):
      name: str
      type: EntityType
      created_at: datetime = Field(default_factory=datetime.now)
      
      @field_validator('type')
      def validate_type(cls, v):
        if v not in ontology.entity_types:
          valid_types = [t.name for t in ontology.entity_types]
          raise ValueError(f"Entity type must be one of {valid_types}, got {v.name}")
        return v

    class Relation(BaseModel):
      entity0: Entity
      entity1: Entity
      relation: str
      type: RelationType
      created_at: datetime = Field(default_factory=datetime.now)
      
      @field_validator('type')
      def validate_type(cls, v):
        if v not in ontology.relation_types:
          valid_types = [t.name for t in ontology.relation_types]
          raise ValueError(f"Relation type must be one of {valid_types}, got {v.name}")
        return v

    class Query(BaseModel):
      name: str
      type: QueryType
      created_at: datetime = Field(default_factory=datetime.now)
      
      @field_validator('type')
      def validate_type(cls, v):
        # Allow dynamically created QueryTypes for string queries
        if hasattr(v, 'types_to_retrieve'):
          return v
        if v not in ontology.query_types:
          valid_types = [t.name for t in ontology.query_types]
          raise ValueError(f"Query type must be one of {valid_types}, got {v.name}")
        return v

    self.entity = Entity
    self.relation = Relation
    self.query = Query
    
    # Pass the types to AI
    ai_config_with_types = {
      **ai_config,
      'entity_type': Entity,
      'relation_type': Relation,
      'query_type': Query,
      'ontology': ontology
    }
    self.ai = AI(**ai_config_with_types)
    
    # Load existing data
    self.storage.load(self)

  def save_to_json(self):
    """Save the knowledge graph to JSON."""
    return self.storage.save(self.entities, self.relations, self.ontology)

  def add(self, relations: Union['Relation', list['Relation']]):
    """Add relation(s) to the knowledge graph."""
    if isinstance(relations, list):
      self.relations.extend(relations)
      self.entities.extend(relation.entity0 for relation in relations)
      self.entities.extend(relation.entity1 for relation in relations)
    else:
      self.relations.append(relations)
      self.entities.append(relations.entity0)
      self.entities.append(relations.entity1)
    
    # Auto-save
    self.save_to_json()
    return self
  
  def add_unstructured(self, text_chunk: str):
    """Add unstructured text chunk to the knowledge graph."""
    relations = self.ai.extract_relations(text_chunk)
    if relations:
      self.add(relations)
    
    return relations

  def __iadd__(self, relations: Union['Relation', list['Relation']]):
    """Support += operator for adding relations."""
    return self.add(relations)
  
  def retrieve(self, query: 'Query', depth: int = 1, limit: int = 20, init_limit: int = 10) -> QueryResult:
    """Retrieve relations from the knowledge graph."""
    
    # Filter relations based on types_to_retrieve
    filtered_relations = []
    types_to_retrieve = query.type.types_to_retrieve
    
    for relation in self.relations:
      for type_to_retrieve in types_to_retrieve:
        if isinstance(type_to_retrieve, EntityType):
          # Check if either entity in the relation matches the entity type
          if (relation.entity0.type.name == type_to_retrieve.name or 
              relation.entity1.type.name == type_to_retrieve.name):
            filtered_relations.append(relation)
            break
        elif isinstance(type_to_retrieve, RelationType):
          # Check if the relation type matches
          if relation.type.name == type_to_retrieve.name:
            filtered_relations.append(relation)
            break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_relations = []
    for rel in filtered_relations:
      rel_key = (rel.entity0.name, rel.entity1.name, rel.relation)
      if rel_key not in seen:
        seen.add(rel_key)
        unique_relations.append(rel)
    
    # Get initial retrievals using AI
    init_retrievals = []
    if unique_relations:
      init_retrievals = self.ai.retrieve_relations(
        query_name=query.name,
        query_context=query.type.context,
        all_relations=unique_relations,
        types_to_retrieve=types_to_retrieve,
        limit=init_limit
      )
    
    # For now, we'll implement basic depth expansion later
    # Just use initial retrievals as all retrievals for depth=1
    all_retrievals = init_retrievals.copy()
    
    # If we need more results and haven't reached limit, get more
    if len(all_retrievals) < limit and len(unique_relations) > len(all_retrievals):
      # Get relations not already retrieved
      remaining_relations = [r for r in unique_relations if r not in all_retrievals]
      if remaining_relations:
        additional_retrievals = self.ai.retrieve_relations(
          query_name=query.name,
          query_context=query.type.context,
          all_relations=remaining_relations,
          types_to_retrieve=types_to_retrieve,
          limit=limit - len(all_retrievals)
        )
        all_retrievals.extend(additional_retrievals)
    
    # Create a summary of the results
    result_summary = f"Retrieved {len(all_retrievals)} relevant relations for query '{query.name}'"
    if all_retrievals:
      result_summary += f". Found relations involving: {', '.join(set(r.entity0.name + '-' + r.entity1.name for r in all_retrievals[:3]))}..."
    
    return QueryResult(
      result=result_summary,
      init_retrievals=init_retrievals,
      all_retrievals=all_retrievals,
      init_limit=init_limit,
      total_limit=limit,
      depth=depth
    )

  def retrieve_str(self, query: str, depth: int = 1, limit: int = 20, init_limit: int = 10) -> str:
    """Retrieve relations from the knowledge graph."""
    # Create a flexible query type that includes all entity and relation types
    all_types = self.ontology.entity_types + self.ontology.relation_types
    query_type = QueryType(name=query, context="", types_to_retrieve=all_types)
    query_obj = self.query(name=query, type=query_type)
    return self.retrieve(query_obj, depth, limit, init_limit).result