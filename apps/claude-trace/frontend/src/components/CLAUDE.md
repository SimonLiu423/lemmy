# Frontend Components

## Overview

This directory contains the core UI components for the Claude Trace frontend application. These components are built using [Lit](https://lit.dev/), a lightweight web components library, and are designed to visualize and interact with conversation trace data from AI models.

The components follow a data-driven approach, accepting typed props and rendering immutable views of conversation traces, raw API pairs, and JSON data structures. They prioritize type safety and avoid the use of `any` types wherever possible.

## Structure

```
frontend/src/components/
├── json-view.ts              # Generic JSON data visualization component
├── raw-pairs-view.ts         # Raw API request/response pair viewer
└── simple-conversation-view.ts # Main conversation trace viewer
```

## Key Components

### JsonView (`json-view.ts`)

**Purpose**: Displays processed conversation pairs in a collapsible JSON format for debugging and detailed inspection.

**Key Features**:

- Collapsible sections for request and response data
- Streaming indicator support
- Model and timestamp metadata display
- Syntax-highlighted JSON formatting

**Props**:

- `processedPairs: ProcessedPair[]` - Array of processed conversation pairs from `SharedConversationProcessor`

**Key Methods**:

- `formatJson(obj: any): string` - Formats objects as JSON strings with error handling
- `toggleContent(e: Event): void` - Handles expand/collapse functionality

**Usage Example**:

```html
<json-view .processedPairs="${processedPairs}"></json-view>
```

### RawPairsView (`raw-pairs-view.ts`)

**Purpose**: Renders raw HTTP request/response pairs with detailed API call information, particularly useful for debugging API interactions.

**Key Features**:

- HTTP method and URL path display
- Model name extraction and normalization
- Server-Sent Events (SSE) visualization
- Status code and timestamp metadata
- Bedrock and standard API format support

**Props**:

- `rawPairs: RawPair[]` - Array of raw request/response pairs from the logging system

**Key Methods**:

- `getModelName(pair: RawPair): string` - Extracts and normalizes model names from various API formats
- `normalizeModelName(modelName: string): string` - Converts Bedrock and other model formats to display names
- `getUrlPath(url: string): string` - Extracts pathname from URLs
- `formatJson(obj: any): string` - Safe JSON formatting with fallback handling

**Type Safety Notes**:

- Uses proper `RawPair` type instead of `any`
- Handles null responses gracefully with type guards
- Model name extraction uses string matching with proper fallbacks

### SimpleConversationView (`simple-conversation-view.ts`)

**Purpose**: The primary conversation visualization component that renders complete conversation threads with advanced formatting, tool usage, and interactive features.

**Key Features**:

- Complete conversation thread display
- System prompt and tools visualization
- Markdown content rendering with XSS protection
- Tool usage tracking and diff visualization
- Collapsible sections and interactive content
- System reminder extraction and highlighting
- Compacted conversation support

**Props**:

- `conversations: SimpleConversation[]` - Array of processed conversations from `SharedConversationProcessor`

**Core Type Definitions**:

- Uses `SimpleConversation` from `shared-conversation-processor`
- Leverages proper Anthropic SDK types: `MessageParam`, `ContentBlock`, `Message`, etc.
- Avoids `any` types through proper type imports from `@anthropic-ai/sdk`

**Key Methods**:

#### Content Formatting

- `formatContent(content: string | ContentBlockParam[], toolResults?: Record<string, any>): TemplateResult` - Main content formatter
- `formatStringContent(content: string): TemplateResult` - Handles text content with system reminder extraction
- `formatResponseContent(response: Message): TemplateResult` - Formats AI assistant responses
- `formatSystem(system: string | TextBlockParam[] | undefined): string` - System prompt formatter

#### Tool Usage Visualization

- `renderToolContainer(toolUse: any, toolResult?: any, options?: object): TemplateResult` - Tool usage wrapper
- `renderToolUseContent(toolUse: any): TemplateResult` - Tool parameter display with special handling for different tool types
- `renderToolResult(toolResult: any, toolUse?: any): TemplateResult` - Tool execution result display
- `getToolDisplayName(toolUse: any, toolResult?: any): TemplateResult` - Tool name formatting with parameter preview

#### Diff Visualization

- `renderDiff(oldStr: string, newStr: string): TemplateResult[]` - Line-by-line diff rendering for file edits
- Uses the `diff` library for accurate change detection

#### Interactive Features

- `handleToggle(e: Event, options?: object): void` - Generic toggle handler for collapsible content
- `toggleContent(e: Event): void` - Standard content visibility toggle
- `toggleWriteContent(e: Event): void` - Special handler for file write operations

#### Utility Methods

- `renderCollapsibleSection(title: string, content: TemplateResult, options?: object): TemplateResult` - Reusable collapsible UI pattern
- `wrapInScrollable(content: TemplateResult | string, usePreFormatting?: boolean): TemplateResult` - Scrollable content wrapper
- `unescapeHtml(str: string): string` - Safe HTML unescaping for display

## Dependencies

### Internal Dependencies

- `../../../src/shared-conversation-processor` - Core conversation processing logic and type definitions
- `../../../src/types` - Application-specific type definitions
- `../utils/markdown` - Safe markdown to HTML conversion utility

### External Dependencies

- `lit` - Web components framework
- `lit/decorators.js` - Property decorators for reactive updates
- `lit/directives/unsafe-html.js` - Controlled HTML rendering for markdown content
- `diff` - Text diffing library for edit visualization
- `@anthropic-ai/sdk/resources/messages` - Official Anthropic API types

## Patterns & Conventions

### Type Safety

- **Strict Type Usage**: All components use proper TypeScript interfaces instead of `any`
- **SDK Type Integration**: Leverages official `@anthropic-ai/sdk` types for API data structures
- **Null Safety**: Proper null/undefined checks throughout all components
- **Type Guards**: Runtime type validation for dynamic content

### Component Architecture

- **Lit Web Components**: Uses modern web component standards with Lit framework
- **Shadow DOM Disabled**: Components use `createRenderRoot() { return this; }` to access global CSS
- **Reactive Properties**: Uses `@property()` decorators for automatic re-rendering
- **Event-Driven**: Interactive features use proper event handling with type-safe event objects

### Content Security

- **XSS Prevention**: Markdown rendering uses proper HTML escaping via `markdownToHtml` utility
- **Controlled HTML**: Uses `unsafeHTML` directive only for pre-processed, safe content
- **Input Validation**: JSON parsing includes try-catch blocks with fallback handling

### UI/UX Patterns

- **Collapsible Content**: Consistent expand/collapse pattern across all views
- **Progressive Disclosure**: Important information visible by default, details hidden behind toggles
- **Syntax Highlighting**: JSON and code content use appropriate formatting
- **Responsive Design**: Content wraps and scrolls appropriately for different screen sizes

## Usage Examples

### Basic Component Usage

```typescript
// In a Lit component or HTML template
html`
	<json-view .processedPairs=${this.processedPairs}></json-view>
	<raw-pairs-view .rawPairs=${this.rawPairs}></raw-pairs-view>
	<simple-conversation-view .conversations=${this.conversations}></simple-conversation-view>
`;
```

### Integration with Data Processing

```typescript
import { SharedConversationProcessor } from "../../../src/shared-conversation-processor";
import { RawPair } from "../../../src/types";

const processor = new SharedConversationProcessor();
const processedPairs = processor.processRawPairs(rawPairs);
const conversations = processor.mergeConversations(processedPairs);

// Render components with processed data
const template = html` <simple-conversation-view .conversations=${conversations}></simple-conversation-view> `;
```

## Type Safety Notes

### Critical Type Safety Improvements

The components follow the project guideline of avoiding `any` types wherever possible:

1. **ProcessedPair Interface**: Used instead of generic objects for conversation data
2. **RawPair Interface**: Proper typing for raw API request/response pairs
3. **Anthropic SDK Types**: Direct import and usage of official API types
4. **Event Typing**: Proper `Event` and `HTMLElement` typing for interactive features

### Areas for Continued Type Safety Enhancement

While the components generally follow good type safety practices, there are a few areas where type improvements could be made:

1. **Tool Use Handling**: Some tool-related methods use `any` for flexibility - could be improved with union types
2. **JSON Formatting**: The `formatJson` method parameter uses `any` but could use `unknown` for better safety
3. **Dynamic Property Access**: Some dynamic property access could benefit from mapped types or type assertions

## Notes

### Performance Considerations

- Components use Lit's efficient rendering system with change detection
- Large JSON objects are formatted on-demand with caching considerations
- DOM manipulation is minimized through reactive property updates

### Styling Integration

- Components disable Shadow DOM to integrate with global Tailwind CSS classes
- VS Code theme color variables are used throughout for consistent styling
- Responsive design patterns ensure usability across different screen sizes

### Accessibility

- Keyboard navigation support for interactive elements
- Proper ARIA labels for screen readers (could be enhanced further)
- Color contrast considerations with VS Code theme integration

### Browser Compatibility

- Modern browser features are used (ES modules, custom elements)
- Polyfills may be needed for older browser support
- Progressive enhancement approach for advanced features
