# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **specification project** for building an ArchGuide MCP Server - a Model Context Protocol server that provides architecture guidelines and design patterns to AI development workflows. The project currently contains only implementation specifications, not actual code.

## Project Status

**Current State**: Documentation/Specification Phase
- Contains comprehensive implementation guide (`archguide-mcp-implementation.md`)
- No actual code implementation exists yet
- Ready to begin development phase

## Planned Architecture (From Specification)

When implemented, this will be a **TypeScript Node.js MCP server** with:

### Core Components
- **MCP Server**: Uses `@modelcontextprotocol/sdk` for Claude Code integration  
- **Storage Layer**: File-based guideline storage with markdown parsing
- **Search Engine**: Full-text search using `@orama/orama`
- **Content Parser**: Extracts patterns, examples, and anti-patterns from markdown
- **Handlers**: Separate handlers for guidelines and search operations

### Directory Structure (Planned)
```
src/
├── server/ArchGuideServer.ts        # Main MCP server
├── storage/GuidelineStore.ts        # Storage abstraction  
├── indexing/SearchIndex.ts          # Search implementation
└── handlers/                        # Request handlers

guidelines/                          # Architecture content
├── microservices/
├── cloud-native/ 
├── security/
└── data-patterns/
```

## Development Commands (When Implemented)

```bash
# Development
npm run dev                 # Start development server with tsx
npm run build              # Compile TypeScript
npm run start              # Run production server
npm run test               # Run Jest tests
npm run lint               # ESLint code quality check

# Setup
npm install                # Install dependencies
npm link                   # Link for global development use
```

## MCP Tools (Planned Implementation)

The server will expose these tools to Claude Code:

1. **get-architecture-guideline** - Fetch guidelines for specific topics with context filtering
2. **search-patterns** - Search for patterns and best practices  
3. **list-categories** - List available guideline categories
4. **check-compliance** - Validate designs against architectural standards

## Integration with Claude Code

When implemented, add to Claude Code configuration:
```json
{
  "mcpServers": {
    "archguide": {
      "command": "npx",
      "args": ["-y", "archguide-mcp"]
    }
  }
}
```

## Guidelines Content Format

Architecture guidelines will be stored as Markdown files with YAML frontmatter:
```yaml
---
id: unique-id
title: Guideline Title  
category: microservices
tags: [distributed-systems, data-patterns]
version: 1.0.0
techStack: [java, spring-boot, kafka]
applicability: [enterprise, cloud-native]
---
```

## Next Steps for Implementation

1. Initialize Node.js project structure as specified
2. Install dependencies: `@modelcontextprotocol/sdk`, `@orama/orama`, `gray-matter`, `marked`, `zod`
3. Implement core TypeScript classes following the detailed specifications
4. Create sample guidelines content in the guidelines/ directory  
5. Set up testing with Jest
6. Package for NPM distribution

## Key Design Principles

- **Service Autonomy**: Each guideline category is independently searchable
- **Context-Aware**: Filter guidelines by tech stack, scale, and domain
- **Version Control**: Support multiple versions of guidelines
- **Fast Search**: In-memory indexing with caching for performance
- **Extensible**: Easy to add new guideline categories and patterns