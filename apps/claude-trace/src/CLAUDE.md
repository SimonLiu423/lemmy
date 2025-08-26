# Claude Trace - Source Directory

## Overview

The `src/` directory contains the core implementation of Claude Trace, a TypeScript-based tool for intercepting, logging, and analyzing Claude API interactions. This directory provides the complete toolkit for monitoring Claude conversations, extracting OAuth tokens, generating HTML reports, and creating conversation summaries.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **CLI Interface** (`cli.ts`) - Main entry point handling command-line arguments and orchestrating different modes
- **Traffic Interception** (`interceptor.ts`, `interceptor-loader.js`) - Core networking interception for Claude API calls
- **Token Extraction** (`token-extractor.js`) - OAuth token capture from Claude API requests
- **Report Generation** (`html-generator.ts`) - Converts JSONL logs to interactive HTML reports
- **Data Processing** (`shared-conversation-processor.ts`) - Shared conversation parsing and analysis logic
- **Index Generation** (`index-generator.ts`) - Creates conversation summaries and index pages
- **Type Definitions** (`types.ts`) - Complete TypeScript type definitions
- **Module Exports** (`index.ts`) - Main package entry point and exports

## Key Components

### CLI Interface (`cli.ts`)

The main command-line interface providing four operational modes:

1. **Interactive Logging**: Spawns Claude with traffic interception enabled
2. **Token Extraction**: Captures OAuth tokens for SDK usage
3. **HTML Generation**: Converts JSONL logs to interactive HTML reports
4. **Index Generation**: Creates conversation summaries and directory indexes

**Key Functions:**

- `runClaudeWithInterception()` - Launches Claude with network interception
- `extractToken()` - Extracts OAuth tokens using token interceptor
- `generateHTMLFromCLI()` - Processes JSONL files into HTML reports
- `generateIndex()` - Creates conversation index with summaries

**Important Features:**

- Automatic Claude binary resolution with symlink and wrapper support
- Environment variable configuration for logging behavior
- Signal handling for graceful shutdown
- Cross-platform compatibility

### Traffic Interceptor (`interceptor.ts`)

Core networking interception system that captures Claude API traffic in real-time.

**ClaudeTrafficLogger Class:**

- `instrumentFetch()` - Intercepts global fetch calls
- `instrumentNodeHTTP()` - Intercepts Node.js http/https modules
- `isClaudeAPI()` - Filters requests to Claude endpoints (Anthropic & Bedrock)
- `generateHTML()` - Real-time HTML generation during logging

**Security Features:**

- `redactSensitiveHeaders()` - Automatic redaction of authentication tokens
- Configurable request filtering (all vs. message-only requests)
- Safe error handling to prevent interference with Claude operations

**Supported APIs:**

- Anthropic API (`api.anthropic.com/v1/messages`)
- AWS Bedrock Claude API (`bedrock-runtime.*.amazonaws.com`)
- Custom `ANTHROPIC_BASE_URL` support

### HTML Generator (`html-generator.ts`)

Converts JSONL logs into interactive HTML reports with embedded JavaScript viewer.

**HTMLGenerator Class:**

- `generateHTML()` - Creates HTML from raw pairs with embedded frontend
- `generateHTMLFromJSONL()` - Batch processes JSONL files
- `prepareDataForInjection()` - Base64-encodes data for safe HTML embedding

**Template System:**

- Uses placeholder replacement with unique markers
- Embeds pre-built frontend bundle (`frontend/dist/index.global.js`)
- Handles data injection via base64 encoding to avoid escaping issues

### Shared Conversation Processor (`shared-conversation-processor.ts`)

Advanced conversation parsing and analysis shared between frontend and backend.

**SharedConversationProcessor Class:**

- `processRawPairs()` - Converts raw JSONL pairs to structured conversations
- `parseStreamingResponse()` - Handles both standard and Bedrock streaming formats
- `mergeConversations()` - Groups related requests into conversation threads
- `detectAndMergeCompactConversations()` - Identifies and merges continuation sessions

**Streaming Support:**

- Standard Anthropic SSE format parsing
- AWS Bedrock binary EventStream format support
- Automatic stream format detection
- Token usage extraction from both formats

**Conversation Intelligence:**

- Tool use/result pairing and analysis
- Message deduplication and normalization
- Temporal conversation grouping
- Compact conversation detection (session continuations)

### Index Generator (`index-generator.ts`)

Creates conversation summaries and directory indexes using Claude API for summarization.

**IndexGenerator Class:**

- `generateIndex()` - Main entry point for index generation
- `processLogFile()` - Processes individual JSONL files
- `summarizeConversation()` - Uses Claude CLI to generate summaries
- `generateIndexHTML()` - Creates static HTML index pages

**Intelligent Processing:**

- Automatic detection of outdated summaries
- Conversation filtering (excludes short/tool-only conversations)
- Caching of generated summaries in JSON format
- HTML index generation with navigation

### Type Definitions (`types.ts`)

Comprehensive TypeScript types ensuring type safety throughout the codebase.

**Core Types:**

- `RawPair` - Raw HTTP request/response pairs from interception
- `ClaudeData` - Structured conversation data for frontend
- `ProcessedConversation` - Enhanced conversation with metadata
- `ProcessedMessage` - Individual messages with tool call information
- `BedrockBinaryEvent` & `BedrockInvocationMetrics` - Bedrock-specific types

**Template & Processing Types:**

- `HTMLGenerationData` - Data structure for HTML generation
- `TemplateReplacements` - HTML template placeholder mappings
- `SSEEvent` - Server-sent event structure
- `ToolCall` - Tool usage tracking

### Support Files

**Interceptor Loader (`interceptor-loader.js`)**

- CommonJS loader for TypeScript interceptor files
- Handles both compiled JavaScript and TypeScript execution via `tsx`
- Fallback loading strategy for different build scenarios

**Token Extractor (`token-extractor.js`)**

- Lightweight OAuth token capture utility
- Intercepts Authorization headers from Claude API requests
- Temporary file-based token communication
- Silent operation to avoid interfering with main Claude process

## Dependencies and Relationships

### Internal Dependencies

```
cli.ts
├── html-generator.ts
├── interceptor.ts (via interceptor-loader.js)
└── index-generator.ts
    ├── shared-conversation-processor.ts
    └── html-generator.ts

interceptor.ts
├── html-generator.ts
└── types.ts

html-generator.ts
├── types.ts
└── shared-conversation-processor.ts

shared-conversation-processor.ts
└── types.ts
```

### External Dependencies

- `@anthropic-ai/sdk` - Type definitions for Claude API structures
- `child_process` - Process spawning and management
- `fs`/`path` - File system operations
- `tsx` - TypeScript execution support

## Configuration and Environment

### Environment Variables

- `CLAUDE_TRACE_INCLUDE_ALL_REQUESTS` - Include all API requests vs. message-only
- `CLAUDE_TRACE_OPEN_BROWSER` - Auto-open HTML reports in browser
- `CLAUDE_TRACE_LOG_NAME` - Custom log file base name
- `CLAUDE_TRACE_TOKEN_FILE` - Token extraction output file
- `ANTHROPIC_BASE_URL` - Custom API endpoint support

### File Structure

```
.claude-trace/
├── log-YYYY-MM-DD-HH-MM-SS.jsonl    # Raw traffic logs
├── log-YYYY-MM-DD-HH-MM-SS.html     # Generated HTML reports
├── summary-YYYY-MM-DD-HH-MM-SS.json # Conversation summaries
├── index.html                        # Master index page
└── token.txt                         # Temporary token file
```

## Usage Patterns and Entry Points

### Command Line Interface

```bash
# Interactive logging
claude-trace                          # Start Claude with logging
claude-trace --log my-session         # Custom log name
claude-trace --run-with chat          # Pass arguments to Claude

# Token extraction
claude-trace --extract-token          # Extract OAuth token

# HTML generation
claude-trace --generate-html file.jsonl  # Convert logs to HTML
claude-trace --generate-html file.jsonl --no-open  # Skip browser opening

# Index generation
claude-trace --index                  # Generate conversation summaries
```

### Programmatic Usage

```typescript
import { ClaudeTrafficLogger, HTMLGenerator } from "claude-trace";

// Initialize interceptor
const logger = new ClaudeTrafficLogger({
	logDirectory: ".custom-trace",
	logBaseName: "my-session",
	enableRealTimeHTML: true,
});

// Generate HTML from existing logs
const htmlGen = new HTMLGenerator();
await htmlGen.generateHTMLFromJSONL("logs/session.jsonl", "reports/session.html");
```

## Type Safety and Best Practices

This codebase adheres to strict TypeScript practices:

- **No `any` types** - All data structures use proper TypeScript types
- **Comprehensive interfaces** - Every API response and data structure is typed
- **Error handling** - Graceful degradation with proper error boundaries
- **Null safety** - Explicit handling of optional and nullable values
- **Generic type constraints** - Proper use of TypeScript generics where applicable

## Performance Considerations

### Network Interception

- Minimal overhead through selective URL filtering
- Asynchronous processing to avoid blocking Claude operations
- Efficient memory management with streaming response handling

### File Operations

- Incremental JSONL writing for large sessions
- Lazy loading of conversation data
- Intelligent caching of generated summaries

### HTML Generation

- Single-file output with embedded assets for portability
- Base64 data encoding for injection safety
- Optimized frontend bundle inclusion

## Error Handling and Reliability

### Graceful Degradation

- Silent error handling during runtime to avoid disrupting Claude
- Fallback strategies for missing dependencies or files
- Comprehensive cleanup on process termination

### Data Integrity

- Orphaned request detection and logging
- JSON parsing error recovery
- File corruption detection and reporting

### Process Management

- Signal handling for clean shutdown
- Child process monitoring and cleanup
- Resource management during long-running sessions

This source directory represents a production-ready TypeScript application with enterprise-grade error handling, type safety, and extensibility. The modular design allows for easy maintenance and feature additions while maintaining backward compatibility with existing log formats.
