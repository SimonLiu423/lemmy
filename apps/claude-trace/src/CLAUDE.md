# Claude Trace Backend System

## Overview

The `src/` directory contains the complete backend implementation of Claude Trace - a sophisticated TypeScript-based system for intercepting, processing, and analyzing Claude API interactions. This backend provides the core infrastructure for traffic interception, conversation processing, report generation, and token management.

## Architecture

The backend follows a modular architecture with clear separation of concerns and well-defined interfaces between components:

```
src/
├── cli.ts                           # Main CLI orchestrator and entry point
├── interceptor.ts                   # Network traffic interception engine
├── interceptor-loader.js            # TypeScript interceptor loader
├── token-extractor.js               # OAuth token capture utility
├── html-generator.ts                # HTML report generation
├── index-generator.ts               # AI-powered conversation indexing
├── shared-conversation-processor.ts # Core conversation analysis engine
├── types.ts                         # Complete TypeScript type definitions
└── index.ts                         # Package entry point and exports
```

## Core Components

### CLI Interface (`cli.ts`)

**Purpose**: Main orchestrator that handles command-line arguments and coordinates all backend operations.

**Operational Modes**:

1. **Interactive Logging**: Spawns Claude with traffic interception enabled
2. **Token Extraction**: Captures OAuth tokens for SDK development
3. **HTML Generation**: Converts JSONL logs to interactive reports
4. **Index Generation**: Creates AI-powered conversation summaries

**Key Implementation Details**:

- **Claude Binary Resolution**: Automatically detects Claude installations including symlinks and wrapper scripts
- **Process Management**: Spawns child processes with proper signal forwarding and cleanup
- **Environment Configuration**: Supports extensive environment variable customization
- **Error Handling**: Graceful degradation with comprehensive error reporting
- **Cross-platform Support**: Works on macOS, Linux, and Windows with platform-specific adaptations

**Critical Functions**:

```typescript
async function runClaudeWithInterception(args: string[], options: CLIOptions): Promise<void>;
async function extractToken(options: TokenExtractionOptions): Promise<string>;
async function generateHTMLFromCLI(inputPath: string, outputPath: string, options: HTMLOptions): Promise<void>;
async function generateIndex(options: IndexOptions): Promise<void>;
```

### Traffic Interceptor (`interceptor.ts`)

**Purpose**: Advanced networking interception system that captures Claude API traffic in real-time without interfering with normal operations.

**Core Architecture**:

```typescript
export class ClaudeTrafficLogger {
	private logFile: fs.WriteStream;
	private htmlGenerator?: HTMLGenerator;

	constructor(options: LoggerOptions) {
		/* ... */
	}

	public instrumentFetch(): void {
		/* Global fetch interception */
	}
	public instrumentNodeHTTP(): void {
		/* Node.js HTTP module interception */
	}
	public generateHTML(): Promise<void> {
		/* Real-time HTML generation */
	}
}
```

**Advanced Features**:

- **Multi-API Support**: Handles Anthropic API, AWS Bedrock, and custom `ANTHROPIC_BASE_URL` configurations
- **Streaming Support**: Processes both standard SSE and Bedrock binary EventStream formats
- **Security Features**: Automatic redaction of authentication tokens and sensitive headers
- **Performance Optimization**: Minimal overhead through selective URL filtering and asynchronous processing
- **Error Isolation**: Prevents interceptor errors from affecting Claude Code operations

**Supported API Endpoints**:

- `api.anthropic.com/v1/messages` (Anthropic API)
- `bedrock-runtime.*.amazonaws.com` (AWS Bedrock)
- Custom endpoints via `ANTHROPIC_BASE_URL`

### Conversation Processor (`shared-conversation-processor.ts`)

**Purpose**: Sophisticated conversation analysis engine shared between backend and frontend components.

**Core Processing Pipeline**:

1. **Raw Pair Processing**: Converts HTTP request/response pairs to structured data
2. **Stream Parsing**: Handles both Anthropic SSE and Bedrock binary formats
3. **Conversation Merging**: Groups related requests into conversation threads
4. **Tool Analysis**: Pairs tool calls with results and tracks usage patterns
5. **Compact Detection**: Identifies and merges continuation sessions

**Key Classes and Methods**:

```typescript
export class SharedConversationProcessor {
	public processRawPairs(rawPairs: RawPair[]): ProcessedPair[];
	public parseStreamingResponse(response: any): ParsedStreamResponse;
	public mergeConversations(pairs: ProcessedPair[]): SimpleConversation[];
	public detectAndMergeCompactConversations(conversations: SimpleConversation[]): SimpleConversation[];
}
```

**Advanced Features**:

- **Multi-format Streaming**: Handles both text-based SSE and binary EventStream protocols
- **Token Usage Extraction**: Comprehensive tracking across all API response formats
- **Message Deduplication**: Intelligent handling of repeated or partial messages
- **Temporal Grouping**: Time-based conversation thread detection
- **Tool Intelligence**: Sophisticated pairing of tool calls with their execution results

### HTML Generator (`html-generator.ts`)

**Purpose**: Creates self-contained, interactive HTML reports with embedded frontend application.

**Architecture**:

```typescript
export class HTMLGenerator {
	private frontendBundle: string;
	private template: string;

	public async generateHTML(pairs: RawPair[], outputPath: string): Promise<void>;
	public async generateHTMLFromJSONL(jsonlPath: string, outputPath: string): Promise<void>;
	private prepareDataForInjection(data: ClaudeData): string;
}
```

**Template System**:

- **Placeholder Replacement**: Uses unique markers (`___CLAUDE_DATA_PLACEHOLDER___`) to avoid conflicts
- **Data Embedding**: Base64-encoded JSON injection for security and reliability
- **Bundle Integration**: Embeds complete frontend JavaScript and CSS bundles
- **Real-time Generation**: Supports live HTML updates during logging sessions

**Security Features**:

- **XSS Prevention**: Safe data embedding through base64 encoding
- **Content Isolation**: Proper separation of data and code in generated files
- **Template Validation**: Ensures all placeholders are properly replaced

### Index Generator (`index-generator.ts`)

**Purpose**: Creates conversation summaries and directory indexes using Claude API for intelligent summarization.

**Core Functionality**:

```typescript
export class IndexGenerator {
	public async generateIndex(logDirectory: string): Promise<void>;
	private async processLogFile(filePath: string): Promise<ConversationSummary[]>;
	private async summarizeConversation(conversation: SimpleConversation): Promise<string>;
	private async generateIndexHTML(summaries: ConversationSummary[]): Promise<void>;
}
```

**Intelligent Processing**:

- **Automatic Detection**: Identifies outdated summaries and regenerates as needed
- **Conversation Filtering**: Excludes short conversations and tool-only interactions
- **Caching Strategy**: JSON-based caching of generated summaries for performance
- **HTML Generation**: Creates navigable index pages with conversation links

**AI Integration**:

- Uses Claude CLI for summarization to ensure consistency with project tooling
- Processes conversations through the same analysis pipeline as the frontend
- Generates contextual summaries that highlight key conversation elements

### Type System (`types.ts`)

**Purpose**: Comprehensive TypeScript type definitions ensuring type safety throughout the backend.

**Core Type Categories**:

1. **Raw Data Types**: `RawPair`, `HTTPRequest`, `HTTPResponse`
2. **Processed Data Types**: `ProcessedPair`, `ProcessedConversation`, `SimpleConversation`
3. **Stream Processing**: `SSEEvent`, `BedrockBinaryEvent`, `BedrockInvocationMetrics`
4. **Template System**: `HTMLGenerationData`, `TemplateReplacements`
5. **Tool Handling**: `ToolCall`, `ToolResult`, `EnhancedMessageParam`

**Type Safety Implementation**:

- **No `any` Types**: All data structures use proper interfaces
- **SDK Integration**: Leverages official `@anthropic-ai/sdk` types
- **Runtime Validation**: Type guards for dynamic content validation
- **Generic Constraints**: Proper use of TypeScript generics where applicable

### Support Components

#### Interceptor Loader (`interceptor-loader.js`)

**Purpose**: CommonJS loader for TypeScript interceptor files with fallback strategies.

**Implementation**:

```javascript
const loadInterceptor = (interceptorPath) => {
	try {
		// Attempt direct JavaScript execution
		return require(interceptorPath);
	} catch (error) {
		// Fallback to TypeScript execution via tsx
		return require("tsx/cjs")(interceptorPath);
	}
};
```

#### Token Extractor (`token-extractor.js`)

**Purpose**: Lightweight OAuth token capture utility for SDK development.

**Features**:

- **Silent Operation**: Runs without interfering with main Claude process
- **Temporary Storage**: File-based token communication with automatic cleanup
- **Header Interception**: Captures Authorization headers from API requests
- **Error Resilience**: Graceful handling of extraction failures

## Configuration and Environment

### Environment Variables

The backend supports extensive configuration through environment variables:

```bash
# Logging Behavior
CLAUDE_TRACE_INCLUDE_ALL_REQUESTS=true    # Include all API requests vs. message-only
CLAUDE_TRACE_OPEN_BROWSER=false           # Auto-open HTML reports
CLAUDE_TRACE_LOG_NAME=custom-session      # Custom log file base name

# API Configuration
ANTHROPIC_BASE_URL=https://api.custom.com # Custom API endpoint

# Token Management
CLAUDE_TRACE_TOKEN_FILE=/tmp/token.txt    # Token extraction output file
```

### File Structure

The backend creates and manages the following file structure:

```
.claude-trace/
├── log-YYYY-MM-DD-HH-MM-SS.jsonl    # Raw traffic logs in JSONL format
├── log-YYYY-MM-DD-HH-MM-SS.html     # Interactive HTML reports
├── summary-YYYY-MM-DD-HH-MM-SS.json # AI-generated conversation summaries
├── index.html                        # Master index page with navigation
└── token.txt                         # Temporary OAuth token file
```

## Advanced Implementation Details

### Network Interception Strategy

The interceptor uses a multi-layered approach to capture API traffic:

1. **Global Fetch Instrumentation**: Patches the global `fetch` function in Node.js
2. **HTTP Module Interception**: Instruments Node.js `http` and `https` modules
3. **URL Filtering**: Selective interception based on Claude API endpoint detection
4. **Stream Processing**: Real-time parsing of both text and binary streaming formats

### Performance Optimizations

- **Selective Filtering**: Only intercepts requests to known Claude API endpoints
- **Asynchronous Processing**: Non-blocking request/response handling
- **Memory Management**: Efficient stream processing without buffering entire responses
- **Lazy Loading**: On-demand loading of large dependencies

### Error Handling Architecture

- **Graceful Degradation**: Silent error handling to avoid disrupting Claude operations
- **Fallback Strategies**: Multiple approaches for critical operations like token extraction
- **Comprehensive Cleanup**: Proper resource management and temporary file cleanup
- **Detailed Logging**: Extensive error reporting for debugging without exposing sensitive data

### Security Implementation

- **Token Redaction**: Automatic removal of authentication headers from logs
- **Temporary File Security**: Secure handling of token files with automatic cleanup
- **Input Validation**: Comprehensive validation of external data sources
- **Error Message Sanitization**: Prevents sensitive information leakage in error messages

## Integration Points

### Frontend Integration

The backend provides data to the frontend through:

- **Data Format**: Standardized `ClaudeData` interface with `rawPairs` and processed conversations
- **Template System**: HTML generation with embedded frontend bundle
- **Shared Processing**: Common conversation processing logic via `shared-conversation-processor`

### External Dependencies

```typescript
// Core Dependencies
import { spawn } from "child_process";
import { promises as fs } from "fs";
import { marked } from "marked";

// Type Dependencies
import type { MessageParam, ContentBlock } from "@anthropic-ai/sdk/resources/messages";
```

## Testing and Quality Assurance

The backend includes comprehensive testing strategies:

- **Unit Tests**: Individual component testing with proper mocking
- **Integration Tests**: End-to-end testing of interceptor functionality
- **Type Testing**: Validation of TypeScript type definitions
- **Performance Testing**: Benchmarking of interception overhead

## Development and Debugging

### Development Workflow

```bash
# Backend development
npm run dev:core              # Watch TypeScript compilation
npm run typecheck            # Validate types

# Testing
npm run test                 # Run interceptor tests
npm run test:generate        # Test HTML generation
```

### Debugging Features

- **Verbose Logging**: Detailed operation logging for debugging
- **Source Maps**: Full source map support for TypeScript debugging
- **Error Reporting**: Comprehensive error reporting with stack traces
- **Performance Monitoring**: Built-in timing and performance metrics

This backend system represents a production-ready, enterprise-grade implementation that successfully balances functionality, performance, security, and maintainability while providing comprehensive observability into Claude API interactions.
