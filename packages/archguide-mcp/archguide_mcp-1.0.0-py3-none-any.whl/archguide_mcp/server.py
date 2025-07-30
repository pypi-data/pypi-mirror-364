"""ArchGuide MCP Server implementation."""

import asyncio
import json
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

# Create the MCP server instance
server = Server("archguide-mcp")

# Store guidelines in memory for now
GUIDELINES = {
    "microservices": {
        "title": "Microservices Architecture Guidelines",
        "content": """## Microservices Best Practices

1. **Service Autonomy**: Each service should be independently deployable
2. **Database per Service**: Avoid shared databases
3. **API First**: Design APIs before implementation
4. **Event-Driven Communication**: Use events for loose coupling
5. **Circuit Breaker Pattern**: Handle failures gracefully""",
        "patterns": ["Database per Service", "API Gateway", "Service Mesh"],
        "tags": ["distributed-systems", "scalability", "cloud-native"]
    },
    "security": {
        "title": "Security Architecture Guidelines",
        "content": """## Security Best Practices

1. **Zero Trust Architecture**: Never trust, always verify
2. **Defense in Depth**: Multiple layers of security
3. **Principle of Least Privilege**: Minimal access rights
4. **Encryption**: Data at rest and in transit
5. **Security by Design**: Build security in from the start""",
        "patterns": ["OAuth2/OIDC", "API Keys", "JWT Tokens"],
        "tags": ["security", "authentication", "authorization"]
    }
}

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get-architecture-guideline",
            description="Get architecture guidelines for a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The architecture topic (e.g., 'microservices', 'security')"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="list-categories",
            description="List all available guideline categories",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution."""
    
    if name == "get-architecture-guideline":
        topic = arguments.get("topic", "").lower()
        
        if topic in GUIDELINES:
            guideline = GUIDELINES[topic]
            response = f"""# {guideline['title']}

{guideline['content']}

## Related Patterns
{', '.join(guideline['patterns'])}

## Tags
{', '.join(guideline['tags'])}"""
            
            return [types.TextContent(type="text", text=response)]
        else:
            return [types.TextContent(
                type="text", 
                text=f"No guidelines found for topic: {topic}. Available topics: {', '.join(GUIDELINES.keys())}"
            )]
    
    elif name == "list-categories":
        categories = "\n".join([f"- {k}: {v['title']}" for k, v in GUIDELINES.items()])
        return [types.TextContent(
            type="text",
            text=f"Available Architecture Guidelines:\n\n{categories}"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def run_server():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="archguide-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

def main():
    """Main entry point."""
    asyncio.run(run_server())

class ArchGuideServer:
    """Compatibility class."""
    def run(self):
        main()