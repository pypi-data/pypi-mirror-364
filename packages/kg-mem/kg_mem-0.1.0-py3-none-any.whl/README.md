# Knowledge Graph MCP Server

A Model Context Protocol (MCP) server that implements a **heavily typed** knowledge graph-based memory system with AI-powered entity and relation extraction. Unlike other memory systems that rely on basic summarization or unstructured storage, our system uses **structured ontologies** to extract meaningful, typed relationships from unstructured text.

## Why Choose a Heavily Typed Approach?

Most AI memory systems treat information as unstructured blobs or simple key-value pairs. This system is different - we use **strongly typed ontologies** that define exactly what kinds of entities and relationships exist in your domain. This means:

- **Predictable structure** - You know exactly what types of information will be extracted
- **Domain-specific accuracy** - Tailored extraction for your specific use case
- **Relationship validation** - Only valid connections between entity types are allowed
- **Query precision** - Ask complex questions about specific relationship patterns

## Comparison with Other Memory Systems

We're the only system that combines **heavy typing** with **local storage** and **native MCP integration**, making us ideal for developers who want predictable, domain-specific memory extraction without external dependencies.

| Feature                | **kg\_mcp** (Ours)                     | Graphiti/Zep                                                   | Mem0                               | Letta                         | GraphRAG               |
| ---------------------- | -------------------------------------- | -------------------------------------------------------------- | ---------------------------------- | ----------------------------- | ---------------------- |
| **Type System**        | ✅ **Heavily typed ontologies**         | ⚡ Temporal knowledge graphs                                    | ❌ Unstructured memories            | ❌ Unstructured storage        | ❌ Community summaries  |
| **Structure**          | ✅ **Predefined entity/relation types** | ⚡ Dynamic graph evolution                                      | ❌ LLM‑generated summaries          | ❌ Simple key‑value            | ❌ Static hierarchical  |
| **Validation**         | ✅ **Schema‑enforced relationships**    | ❌ Dynamic, no validation                                       | ❌ No relationship rules            | ❌ No validation               | ❌ No validation        |
| **Domain Specificity** | ✅ **6 built‑in ontologies + custom**   | ⚡ Generic entities (custom ontologies supported) ([GitHub][1]) | ❌ Generic extraction               | ❌ Generic storage             | ❌ Generic clustering   |
| **Local Storage**      | ✅ **JSON files, full control**         | ⚡ Neo4j required (local or cloud) ([GitHub][1])                | ⚡ Multiple backends                | ✅ Local SQLite ([GitHub][2])  | ❌ Complex setup        |
| **MCP Integration**    | ✅ **Native MCP server**                | ⚡ Optional MCP wrapper ([GitHub][1])                           | ❌ No MCP support                   | ✅ MCP compatible ([Letta][3]) | ❌ No MCP support       |
| **Query Flexibility**  | ✅ **Ontology‑driven queries**          | ⚡ Graph traversal + semantic                                   | ⚡ Vector + graph search            | ❌ Basic retrieval             | ❌ Community‑based only |
| **Real‑time Updates**  | ✅ **Immediate JSON persistence**       | ✅ Real‑time graph updates                                      | ⚡ Real‑time with LLM consolidation | ✅ Instant updates             | ❌ Batch recomputation  |

[1]: https://github.com/getzep/graphiti "GitHub - getzep/graphiti: Build Real-Time Knowledge Graphs for AI Agents"
[2]: https://github.com/letta-ai/letta "GitHub - letta-ai/letta: Letta (formerly MemGPT) is the stateful agents framework with memory, reasoning, and context management."
[3]: https://docs.letta.com/guides/mcp/overview?utm_source=chatgpt.com "What is Model Context Protocol (MCP)? - Letta"


## Features

- **Ontology-driven extraction** - Uses predefined ontologies to structure knowledge extraction
- **AI-powered relation extraction** - Leverages LLMs to extract entities and relationships from text  
- **JSON persistence** - Automatic saving and loading from JSON files with configurable paths
- **MCP compatible** - Works with any MCP-enabled AI assistant
- **Multiple ontologies** - Ships with 6 predefined ontologies for different domains
- **Custom ontologies** - Support for user-defined ontologies
- **Local storage** - All data stored locally in JSON format

## Getting Started

### 1. Use an Existing Ontology

Start with one of our 6 built-in ontologies:

```bash
# Installation
git clone https://github.com/belindamo/kg_mcp
cd kg_mcp
uv pip install -e .

# Basic ontology (Person, Organization, Location, Concept)
ONTOLOGY=basic fastmcp run server.py
```

Add to your MCP configuration:
```json
{
  "mcps": {
    "kg-memory": {
      "command": "fastmcp", 
      "args": ["run", "server.py"],
      "env": {
        "ONTOLOGY": "basic",
        "KG_STORAGE_PATH": "./my_knowledge.json"
      }
    }
  }
}
```

### 2. Add Unstructured Memory

Let the AI extract structured knowledge from any text:

```python
# Through MCP tools
add_memories("John Smith works for Google. Google is located in Mountain View.")
# Returns: "Successfully extracted 2 memories:
# - John Smith (Person) works_for Google (Organization)  
# - Google (Organization) located_in Mountain View (Location)"

# Or directly via Python API
from kg_mem import KGMem
from ontologies import basic_ontology
kg = KGMem(basic_ontology)
relations = kg.add_unstructured("John Smith works for Google. Google is located in Mountain View.")

# Expected output:
# John Smith (Person) John Smith works for Google Google (Organization)
# Google (Organization) Google is located in Mountain View Mountain View (Location)
```

### 3. Add Typed Memory (Advanced)

For precise control, create entities and relations directly:

```python
# Create typed entities
alice = kg.entity(name="Alice Smith", type=person_type)
microsoft = kg.entity(name="Microsoft", type=organization_type)

# Create a typed relationship
employment = kg.relation(
    entity0=alice, 
    entity1=microsoft,
    relation="works for",
    type=works_for_relation_type
)

# Add to the knowledge graph
kg += [employment]
```

### 4. Visualize Your Knowledge Graph

Generate an interactive HTML visualization of all your memories:

```python
kg.visualize(output_path="./knowledge_graph.html")
# Opens a web page showing all entities and relationships as an interactive graph
```

### 5. Create Your Own Ontology

Define domain-specific entity and relationship types:

```python
from kg_mcp import EntityType, RelationType, Ontology

# Define your entities
patient_type = EntityType(name="Patient")
doctor_type = EntityType(name="Doctor") 
diagnosis_type = EntityType(name="Diagnosis")

# Define valid relationships
treats_relation = RelationType(
    name="treats",
    entity_type0=doctor_type,      # Doctor
    entity_type1=patient_type,     # treats Patient
    context="Medical treatment relationship"
)

diagnoses_relation = RelationType(
    name="diagnoses", 
    entity_type0=doctor_type,      # Doctor
    entity_type1=diagnosis_type,   # diagnoses Diagnosis
    context="Medical diagnosis relationship"
)

# Create your ontology
medical_ontology = Ontology(
    entity_types=[patient_type, doctor_type, diagnosis_type],
    relation_types=[treats_relation, diagnoses_relation],
    query_types=[]  # Optional: define query patterns
)

# Use your custom ontology
kg = KGMem(medical_ontology, storage_path="./medical_kg.json")
```

## Available Ontologies

- **basic** (default) - Person, Organization, Location, Concept
- **messaging** - Sessions, Messages, Semantic Entities  
- **github** - Developers, Repositories, PRs, Issues, Commits
- **scientific** - Researchers, Experiments, Results, Publications
- **simple_person_project** - Simple Person-Project relationships
- **employment** - Employment relationships

### Custom Ontologies

You can provide a path to a custom ontology file:

```json
{
  "env": {
    "ONTOLOGY": "/path/to/my_ontology.py"
  }
}
```

The file must define an `ontology` variable of type `Ontology`.

### Storage Configuration

Control where the knowledge graph is stored:

```json
{
  "env": {
    "KG_STORAGE_PATH": "/path/to/my_knowledge.json"
  }
}
```

Default storage path is `./kg_memory.json` in the current directory.

## MCP Tools

The server provides four MCP tools:

### `add_memories(text_chunk: str) -> str`

Extracts structured knowledge from unstructured text and stores it in the knowledge graph.


### `retrieve_relevant_context(query: str) -> str`

Retrieves relevant context from the knowledge graph based on a query.

### `save_knowledge_graph() -> str`

Manually saves the current knowledge graph to the JSON file.

### `get_knowledge_stats() -> str`

Returns statistics about the current knowledge graph including entity/relation counts and ontology information.

## Examples

### Example 1: Employment Tracking
```python
from kg_mem import KGMem
from ontologies import employment_ontology

kg = KGMem(employment_ontology)

# Add employment information
relations = kg.add_unstructured("""
Sarah Johnson is the new CTO at TechStart Inc. 
Bob Wilson also joined TechStart as a Senior Engineer.
TechStart Inc. was recently acquired by MegaCorp.
""")

# Expected extraction output:
# Sarah Johnson (Person) Sarah Johnson works at TechStart Inc. TechStart Inc. (Company)
# Bob Wilson (Person) Bob Wilson works at TechStart Inc. TechStart Inc. (Company)

# Query employment relationships
results = kg.retrieve_str("Who works at TechStart?")
# Expected query result:
# "Retrieved 2 relevant relations for query 'Who works at TechStart?'. 
#  Found relations involving: Bob Wilson-TechStart Inc., Sarah Johnson-TechStart Inc...."
```

### Example 2: GitHub Project Tracking
```python
from kg_mem import KGMem
from ontologies import github_ontology

kg = KGMem(github_ontology)

# Add development activity
relations = kg.add_unstructured("""
Alice opened a pull request to fix the authentication bug.
The PR targets the main branch and fixes issue #123.
Bob reviewed the pull request and approved it.
""")

# Note: GitHub ontology extraction can be complex and may require 
# more structured input or manual entity creation for best results

# Query development workflow
results = kg.retrieve_str("What pull requests are open?")
```

### Example 3: Scientific Research Workflow

The scientific ontology demonstrates the power of heavily typed knowledge graphs for complex domains. Let's walk through a complete research workflow:

```python
from kg_mcp import KGMem
from ontologies.scientific import scientific_ontology

# Initialize with the scientific ontology
kg = KGMem(scientific_ontology)

# The scientific ontology defines 7 entity types:
# - Researcher, Idea, Proposal, Experiment, Result, Publication, Insight
# And 10 relation types that model the research process:
# - conceives, develops_into, proposes, conducts, produces, publishes, 
#   collaborates_with, derives_insight, inspires, validates

# Create entities with proper typing
dr_smith = kg.entity(name="Dr. Smith", type=researcher_type)
quantum_idea = kg.entity(name="Quantum Computing Optimization", type=idea_type)
quantum_proposal = kg.entity(name="Quantum Algorithm Proposal", type=proposal_type)
quantum_exp = kg.entity(name="Quantum Circuit Test A", type=experiment_type)
quantum_result = kg.entity(name="30% Speed Improvement", type=result_type)
quantum_paper = kg.entity(name="Advances in Quantum Optimization", type=publication_type)

# Build the research workflow with typed relationships
kg += [
    kg.relation(entity0=dr_smith, entity1=quantum_idea, 
               relation="Dr. Smith conceives Quantum Computing Optimization", 
               type=conceives_type),
    kg.relation(entity0=quantum_idea, entity1=quantum_proposal,
               relation="Quantum Computing Optimization develops into Quantum Algorithm Proposal",
               type=develops_into_type),
    kg.relation(entity0=dr_smith, entity1=quantum_exp,
               relation="Dr. Smith conducts Quantum Circuit Test A",
               type=conducts_type),
    kg.relation(entity0=quantum_exp, entity1=quantum_result,
               relation="Quantum Circuit Test A produces 30% Speed Improvement", 
               type=produces_type),
    kg.relation(entity0=quantum_result, entity1=quantum_paper,
               relation="30% Speed Improvement leads to Advances in Quantum Optimization",
               type=publishes_type)
]

# Now query the research workflow
workflow_query = kg.query(
    name="What is the research workflow for quantum computing?",
    type=research_flow_query_type
)

result = kg.retrieve(workflow_query, limit=10)
print(f"Query: {workflow_query.name}")
print(f"Result: {result.result}")
```

**Try it yourself!** Run the complete example to see the typed extraction in action:

```bash
# Run the scientific research example
cd tests/examples
python test_scientific_experiments.py
```

This will show you:
- **Query 1:** Research workflow tracking (ideas → proposals → experiments → results → publications)
- **Query 2:** Individual researcher activities ("What is Dr. Smith working on?")
- **Query 3:** Experiment details and outcomes
- **Query 4:** Insight discovery and validation

You'll see output like:
```
Query: What is the research workflow for quantum computing?
Result summary: Retrieved 7 relevant relations for query 'What is the research workflow for quantum computing?'. Found relations involving: Quantum Algorithm Proposal-Quantum Circuit Test A, Dr. Smith-Quantum Computing Optimization...
Retrieved relations:
  - Dr. Smith conceives Quantum Computing Optimization
  - Quantum Computing Optimization develops into Quantum Algorithm Proposal
  - Quantum Algorithm Proposal proposes Quantum Circuit Test A
  - Quantum Circuit Test A produces 30% Speed Improvement
  - 30% Speed Improvement leads to Advances in Quantum Optimization
  - Quantum Algorithm Proposal proposes Quantum Circuit Test B
  - 30% Speed Improvement derives insight Superposition enables parallel computation

Query: What is Dr. Smith working on?
Result summary: Retrieved 3 relevant relations for query 'What is Dr. Smith working on?'. Found relations involving: Dr. Smith-Quantum Circuit Test B, Dr. Smith-Quantum Circuit Test A...
Retrieved relations:
  - Dr. Smith conceives Quantum Computing Optimization
  - Dr. Smith conducts Quantum Circuit Test A
  - Dr. Smith conducts Quantum Circuit Test B

Query: What experiments were proposed and what were their outcomes?
Result summary: Retrieved 8 relevant relations for query 'What experiments were proposed and what were their outcomes?'. Found relations involving: Quantum Algorithm Proposal-Quantum Circuit Test A...
Retrieved relations:
  - Quantum Algorithm Proposal proposes Quantum Circuit Test A
  - Quantum Algorithm Proposal proposes Quantum Circuit Test B
  - Quantum Circuit Test A produces 30% Speed Improvement
  - Quantum Circuit Test B validates Superposition enables parallel computation
  - Model Compression Study proposes Compression Benchmark
  - Compression Benchmark produces 50% Size Reduction

Query: What insights were discovered?
Result summary: Retrieved 3 relevant relations for query 'What insights were discovered?'. Found relations involving: Quantum Circuit Test B-Superposition enables parallel computation...
Retrieved relations:
  - 30% Speed Improvement derives insight Superposition enables parallel computation
  - Quantum Circuit Test B validates Superposition enables parallel computation
  - 50% Size Reduction derives insight Pruning preserves essential features
```

The beauty of the typed approach is that relationships are **validated** - you can't accidentally create invalid connections like "Experiment collaborates_with Result" because the ontology enforces that only Researchers can collaborate with other Researchers.

## Running the Server

Start the MCP server:

```bash
# With default basic ontology
fastmcp run server.py

# With specific ontology and custom storage
ONTOLOGY=github KG_STORAGE_PATH=./github_knowledge.json fastmcp run server.py

# With custom ontology
ONTOLOGY=/path/to/custom_ontology.py fastmcp run server.py
```

## Testing

Run the test suite:

```bash
cd tests
python run_all_tests.py
```

Individual test files:
- `test_mcp.py` - MCP server integration tests
- `test_add_unstructured.py` - Text extraction tests
- `test_retrieve.py` - Knowledge retrieval tests
- `test_*_ontology.py` - Ontology-specific tests

## Architecture

The system consists of:

1. **KGMem** - Core knowledge graph memory class
2. **AI** - DSPy-based extraction and retrieval engine
3. **Ontologies** - Structured type definitions
4. **MCP Server** - FastMCP-based server implementation

## Future Experiments

- **Interactive visualizations** - HTML graph visualization via `visualize.py`
- **Ontology discovery** - Automatically discover new ontologies from existing text chunks
- **Enhanced retrieval methods** - Cosine similarity over vector embeddings and BM-25 over text chunks
- **Original text preservation** - Store and retrieve original text chunks alongside structured data



## License

MIT
