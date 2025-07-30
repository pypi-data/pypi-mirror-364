import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class JSONStorage:
    """Simple JSON storage for knowledge graph data."""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.environ.get("KG_STORAGE_PATH", "./kg_memory.json")
        self.storage_path = Path(storage_path)
    
    def save(self, entities: List[Any], relations: List[Any], ontology: Any) -> bool:
        """Save entities and relations to JSON file."""
        try:
            # Create directory if it doesn't exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "entities": [
                    {
                        "name": e.name,
                        "type": e.type.name,
                        "created_at": e.created_at.isoformat()
                    } for e in entities
                ],
                "relations": [
                    {
                        "entity0": {"name": r.entity0.name, "type": r.entity0.type.name},
                        "entity1": {"name": r.entity1.name, "type": r.entity1.type.name},
                        "relation": r.relation,
                        "type": r.type.name,
                        "created_at": r.created_at.isoformat()
                    } for r in relations
                ],
                "metadata": {
                    "total_entities": len(entities),
                    "total_relations": len(relations),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def load(self, kg_mem_instance) -> bool:
        """Load entities and relations from JSON file."""
        if not self.storage_path.exists():
            return False
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing data
            kg_mem_instance.entities = []
            kg_mem_instance.relations = []
            
            # Load entities
            entities_by_key = {}
            for entity_data in data.get("entities", []):
                entity_type = next((et for et in kg_mem_instance.ontology.entity_types 
                                  if et.name == entity_data["type"]), None)
                if entity_type:
                    entity = kg_mem_instance.entity(
                        name=entity_data["name"],
                        type=entity_type,
                        created_at=datetime.fromisoformat(entity_data["created_at"])
                    )
                    kg_mem_instance.entities.append(entity)
                    entities_by_key[(entity_data["name"], entity_data["type"])] = entity
            
            # Load relations
            for relation_data in data.get("relations", []):
                entity0_key = (relation_data["entity0"]["name"], relation_data["entity0"]["type"])
                entity1_key = (relation_data["entity1"]["name"], relation_data["entity1"]["type"])
                
                entity0 = entities_by_key.get(entity0_key)
                entity1 = entities_by_key.get(entity1_key)
                
                relation_type = next((rt for rt in kg_mem_instance.ontology.relation_types 
                                    if rt.name == relation_data["type"]), None)
                
                if entity0 and entity1 and relation_type:
                    relation = kg_mem_instance.relation(
                        entity0=entity0,
                        entity1=entity1,
                        relation=relation_data["relation"],
                        type=relation_type,
                        created_at=datetime.fromisoformat(relation_data["created_at"])
                    )
                    kg_mem_instance.relations.append(relation)
            
            if not self.storage_path.exists():
                print(f"No storage file found at {self.storage_path}. Starting from scratch.")
            else:
                print(f"Loaded {len(kg_mem_instance.entities)} entities and {len(kg_mem_instance.relations)} relations from {self.storage_path}")
            return True
            
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False 