"""
This is the MCP server.
Run the server locally with: `fastmcp run mcp.py`

You can specify an ontology via the ONTOLOGY environment variable:

Pre-defined ontologies:
- basic (default)
- messaging
- github
- scientific
- simple_person_project
- employment

Example: ONTOLOGY=github fastmcp run mcp.py

Custom ontology file:
You can also provide a path to a Python file containing a custom ontology.
The file must define an 'ontology' variable of type Ontology.

Example: ONTOLOGY=/path/to/my_ontology.py fastmcp run mcp.py

```
"""

import os
from fastmcp import FastMCP
from kg_mem import KGMem
from ontologies import ONTOLOGY_MAP, basic_ontology



# ONTOLOGY_MAP is now imported from ontologies package


# Global variable to store kgmem instance
kgmem_instance = None

def initialize_kgmem():
  """Initialize KGMem with the selected ontology."""
  global kgmem_instance
  
  # Get ontology name from environment variable, default to "basic"
  ontology_spec = os.environ.get("ONTOLOGY", "basic")
  
  # Check if it's a file path
  if os.path.exists(ontology_spec) and ontology_spec.endswith('.py'):
    print(f"Loading custom ontology from {ontology_spec}")
    # Import the custom ontology module
    import importlib.util
    spec = importlib.util.spec_from_file_location("custom_ontology", ontology_spec)
    custom_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(custom_module)
    
    # Look for an 'ontology' variable in the module
    if hasattr(custom_module, 'ontology'):
      ontology = custom_module.ontology
    else:
      print(f"Error: No 'ontology' variable found in {ontology_spec}, using 'basic' instead")
      ontology = basic_ontology
  else:
    # Use predefined ontology
    ontology_name = ontology_spec.lower()
    
    # Get the corresponding ontology object
    if ontology_name not in ONTOLOGY_MAP:
      print(f"Warning: Unknown ontology '{ontology_name}', using 'basic' instead")
      ontology_name = "basic"
    
    ontology = ONTOLOGY_MAP[ontology_name]
    print(f"Using {ontology_name} ontology")
  
  # Get storage path from environment variable
  storage_path = os.environ.get("KG_STORAGE_PATH", "./kg_memory.json")
  print(f"Using storage path: {storage_path}")
  
  # Initialize KGMem with the selected ontology and storage path
  kgmem_instance = KGMem(ontology, storage_path=storage_path)
  return kgmem_instance

# Initialize on module load
initialize_kgmem()

mcp = FastMCP(name="KG Memory")

@mcp.tool
def add_memories(text_chunk: str) -> str:
  """
  Add long term memories.
  """
  global kgmem_instance
  if kgmem_instance is None:
    initialize_kgmem()
  
  relations = kgmem_instance.add_unstructured(text_chunk)
  
  if not relations:
    return "No memories could be extracted from the text."
  
  # Format the extracted relations for display
  memories_str = f"Successfully extracted {len(relations)} memories:\n"
  for rel in relations:
    memories_str += f"- {rel.entity0.name} ({rel.entity0.type.name}) {rel.relation} {rel.entity1.name} ({rel.entity1.type.name})\n"
  
  return memories_str

@mcp.tool
def retrieve_relevant_context(query: str) -> str:
  """
  Retrieve relevant context from long term memory.
  """
  global kgmem_instance
  if kgmem_instance is None:
    initialize_kgmem()
  
  return kgmem_instance.retrieve_str(query)

@mcp.tool
def save_knowledge_graph() -> str:
  """
  Manually save the knowledge graph to JSON file. This is primarily for debugging purposes.
  """
  global kgmem_instance
  if kgmem_instance is None:
    initialize_kgmem()
  
  success = kgmem_instance.save_to_json()
  if success:
    return f"Knowledge graph saved successfully to {kgmem_instance.storage.storage_path}. Contains {len(kgmem_instance.entities)} entities and {len(kgmem_instance.relations)} relations."
  else:
    return "Failed to save knowledge graph."

@mcp.tool
def get_knowledge_stats() -> str:
  """
  Get statistics about the current knowledge graph. This is primarily for debugging purposes.
  """
  global kgmem_instance
  if kgmem_instance is None:
    initialize_kgmem()
  
  stats = {
    "total_entities": len(kgmem_instance.entities),
    "total_relations": len(kgmem_instance.relations),
    "storage_path": str(kgmem_instance.storage.storage_path),
    "ontology_entity_types": [et.name for et in kgmem_instance.ontology.entity_types],
    "ontology_relation_types": [rt.name for rt in kgmem_instance.ontology.relation_types]
  }
  
  return f"""Knowledge Graph Statistics:
- Total Entities: {stats['total_entities']}
- Total Relations: {stats['total_relations']}
- Storage Path: {stats['storage_path']}
- Entity Types: {', '.join(stats['ontology_entity_types'])}
- Relation Types: {', '.join(stats['ontology_relation_types'])}"""

if __name__ == "__main__":
  mcp.run()


