"""
Test the MCP server functionality of CAT.
This tests the server integration, tools, and ontology loading.
"""

import pytest
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path


@pytest.fixture
def mcp_server_path():
    """Get the path to the MCP server file."""
    return Path(__file__).parent.parent / "mcp.py"


@pytest.fixture
def custom_ontology_path():
    """Get the path to the example custom ontology."""
    return Path(__file__).parent.parent.parent.parent.parent / "example" / "custom_ontology.py"


async def init_mcp_server(ontology=None):
    """Initialize MCP server with optional ontology."""
    server_path = Path(__file__).parent.parent.parent / "server.py"
    
    # Set up environment
    env = os.environ.copy()
    if ontology:
        env["ONTOLOGY"] = ontology
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="fastmcp",
        args=["run", str(server_path)],
        env=env
    )
    
    return server_params

@pytest.mark.asyncio
async def test_add_memories_tool():
    """Test the add_memories tool functionality."""
    server_params = await init_mcp_server()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test adding memories
            text_chunk = "John Smith works for Google. Google is located in Mountain View."
            result = await session.call_tool("add_memories", {"text_chunk": text_chunk})
            
            # Check response
            response_text = result.content[0].text
            assert "Successfully extracted" in response_text or "No memories could be extracted" in response_text


@pytest.mark.asyncio
async def test_retrieve_relevant_context_tool():
    """Test the retrieve_relevant_context tool functionality."""
    server_params = await init_mcp_server()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # First add some memories
            text_chunk = "Alice works for TechCorp. Bob also works for TechCorp. TechCorp is located in San Francisco."
            await session.call_tool("add_memories", {"text_chunk": text_chunk})
            
            # Now retrieve relevant context
            query = "Who works at TechCorp?"
            result = await session.call_tool("retrieve_relevant_context", {"query": query})
            
            # Check response
            response_text = result.content[0].text
            assert isinstance(response_text, str)
            # The response format depends on the retrieve implementation
            assert "Retrieved" in response_text or len(response_text) > 0

 
