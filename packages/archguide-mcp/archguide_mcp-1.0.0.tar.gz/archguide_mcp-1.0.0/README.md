# ArchGuide MCP Server

Architecture Guidelines MCP Server - Inject architectural best practices and design patterns directly into your AI development workflow.

## Features

- 🏗️ **Architecture Guidelines**: Comprehensive guidelines for microservices, cloud-native, security patterns
- 🔍 **Smart Search**: Full-text search across all guidelines and patterns
- 🎯 **Context-Aware**: Filter by tech stack, scale, and domain
- ✅ **Compliance Checking**: Validate designs against standards
- 📚 **Version Control**: Support multiple versions of guidelines

## Installation

### Using pipx (Recommended)

```bash
pipx install archguide-mcp
```

### Using pip

```bash
pip install archguide-mcp
```

### Using uvx (no installation)

```bash
# Run directly without installing
uvx archguide-mcp
```

## Configuration with Claude Code

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "archguide": {
      "command": "archguide-mcp"
    }
  }
}
```

Or with uvx:

```json
{
  "mcpServers": {
    "archguide": {
      "command": "uvx",
      "args": ["archguide-mcp"]
    }
  }
}
```

## Usage

Once configured, you can use the architecture guidelines in your Claude Code conversations:

```
"Design a microservices architecture for an e-commerce platform"

"Show me the event sourcing pattern with examples"

"Check if this API design follows REST best practices"

"What are the security patterns for API authentication?"
```

## Available Tools

### `get-architecture-guideline`
Fetch guidelines for specific topics with context filtering:
- Filter by tech stack (Java, Python, Node.js, etc.)
- Filter by scale (startup, growth, enterprise)
- Filter by domain (e-commerce, fintech, healthcare)

### `search-patterns`
Search across all patterns and best practices

### `list-categories`
Browse available guideline categories

### `check-compliance`
Validate designs against architectural standards

## Environment Variables

- `GUIDELINES_PATH`: Custom path to guidelines directory
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Contributing

Guidelines are written in Markdown with YAML frontmatter:

```markdown
---
id: microservices-data-patterns
title: Data Management in Microservices
category: microservices
tags: [data, distributed-systems, patterns]
version: 1.0.0
techStack: [java, spring-boot, kafka]
applicability: [enterprise, cloud-native]
---

# Your guideline content here...
```

## License

MIT License - see LICENSE file for details

## Author

Ioan Salau (ioan.salau@gmail.com)