# Frontend Components Implementation Guide

## Overview

This directory contains the core UI components that visualize and interact with conversation trace data. Each component is a specialized Lit web component designed for specific visualization tasks, following consistent patterns for type safety, security, and performance.

## Component Architecture

```
components/
├── simple-conversation-view.ts # Primary conversation visualization
├── raw-pairs-view.ts           # HTTP request/response debugging
└── json-view.ts                # Structured data inspection
```

## Implementation Patterns

### Component Base Pattern

All components follow this standardized implementation pattern:

```typescript
@customElement("component-name")
export class ComponentName extends LitElement {
	@property({ type: Array }) data: DataType[] = [];

	createRenderRoot() {
		return this; // Access global Tailwind CSS
	}

	render(): TemplateResult {
		if (!this.data?.length) {
			return html`<div class="text-vs-text-muted">No data available</div>`;
		}

		return html`<div class="component-container">${this.renderContent()}</div>`;
	}
}
```

**Critical Implementation Requirements**:

- **Shadow DOM Disabled**: Always return `this` from `createRenderRoot()` for global CSS access
- **Empty State Handling**: Provide meaningful empty states for better UX
- **Type Safety**: Use proper TypeScript interfaces, avoid `any` types
- **Consistent Styling**: Use Tailwind classes with VS Code theme variables

## Component-Specific Implementation

### SimpleConversationView Implementation

**Purpose**: Primary conversation visualization with advanced formatting, tool tracking, and interactive features.

**Key Implementation Methods**:

```typescript
// Content formatting with tool result integration
private formatContent(content: string | ContentBlockParam[], toolResults?: Record<string, any>): TemplateResult {
    if (typeof content === 'string') {
        return this.formatStringContent(content);
    }

    return html`
        <div class="content-blocks">
            ${content.map(block => this.renderContentBlock(block, toolResults))}
        </div>
    `;
}

// Tool container with collapsible sections
private renderToolContainer(toolUse: any, toolResult?: any, options = {}): TemplateResult {
    const { showInput = true, showResult = true } = options;
    const toolName = this.getToolDisplayName(toolUse, toolResult);

    return html`
        <div class="tool-container bg-vs-bg-secondary rounded-md border border-gray-600 mb-4">
            <button
                class="tool-header w-full text-left p-3 flex items-center justify-between"
                @click=${this.toggleContent}
            >
                <span class="tool-name text-vs-function">${toolName}</span>
                <span class="toggle-icon">▼</span>
            </button>
            <div class="tool-content hidden p-3 pt-0">
                ${showInput ? this.renderToolUseContent(toolUse) : ''}
                ${showResult && toolResult ? this.renderToolResult(toolResult, toolUse) : ''}
            </div>
        </div>
    `;
}
```

**Advanced Features Implementation**:

1. **Diff Visualization**: Uses the `diff` library for file edit tracking
2. **System Reminder Extraction**: Parses system reminders from content
3. **Tool Parameter Preview**: Shows abbreviated tool parameters in headers
4. **Write Content Handling**: Special handling for file write operations

**Interactive Features**:

```typescript
// Generic toggle handler with flexible options
private handleToggle(e: Event, options: {
    type?: "content" | "write" | "custom";
    targetSelector?: string;
    customHandler?: (element: HTMLElement, isHidden: boolean) => void;
} = {}): void {
    const currentElement = e.currentTarget as HTMLElement;
    const nextElement = currentElement.nextElementSibling as HTMLElement;

    if (nextElement) {
        const isHidden = nextElement.style.display === "none";
        nextElement.style.display = isHidden ? "block" : "none";

        // Update toggle icon
        const toggleIcon = currentElement.querySelector('.toggle-icon');
        if (toggleIcon) {
            toggleIcon.textContent = isHidden ? "▲" : "▼";
        }
    }
}
```

### RawPairsView Implementation

**Purpose**: Technical debugging interface for raw HTTP request/response pairs.

**Key Implementation Methods**:

```typescript
// Model name extraction with normalization
private getModelName(pair: RawPair): string {
    if (pair.request?.body?.model) {
        return this.normalizeModelName(pair.request.body.model);
    }

    // Fallback extraction from URL path
    const url = pair.request?.url || '';
    if (url.includes('bedrock-runtime')) {
        return 'bedrock-claude';
    }

    return 'unknown';
}

// Model name normalization for consistent display
private normalizeModelName(modelName: string): string {
    if (modelName.startsWith('anthropic.claude')) {
        return modelName.replace('anthropic.claude-', 'claude-');
    }
    return modelName;
}

// Safe JSON formatting with error handling
private formatJson(obj: any): string {
    try {
        return JSON.stringify(obj, null, 2);
    } catch (error) {
        console.warn('Failed to stringify object:', error);
        return String(obj);
    }
}
```

**HTTP Method and Status Visualization**:

```typescript
// HTTP method styling
private getMethodClass(method: string): string {
    const methodMap: Record<string, string> = {
        'GET': 'text-green-400',
        'POST': 'text-blue-400',
        'PUT': 'text-yellow-400',
        'DELETE': 'text-red-400'
    };
    return methodMap[method] || 'text-vs-text';
}

// Status code styling
private getStatusClass(statusCode: number): string {
    if (statusCode >= 200 && statusCode < 300) return 'text-green-400';
    if (statusCode >= 400 && statusCode < 500) return 'text-yellow-400';
    if (statusCode >= 500) return 'text-red-400';
    return 'text-vs-text';
}
```

### JsonView Implementation

**Purpose**: Structured data inspection with collapsible JSON formatting.

**Key Implementation Methods**:

```typescript
// Collapsible JSON structure rendering
private renderProcessedPair(pair: ProcessedPair, index: number): TemplateResult {
    const modelName = pair.model || 'unknown';
    const timestamp = pair.request?.timestamp ?
        new Date(pair.request.timestamp).toLocaleString() : 'Unknown';

    return html`
        <div class="processed-pair border border-vs-bg-secondary rounded-lg mb-4">
            <button
                class="pair-header w-full text-left p-4 bg-vs-bg-secondary rounded-t-lg"
                @click=${this.toggleContent}
            >
                <div class="flex justify-between items-center">
                    <span class="text-vs-function">Pair ${index + 1}</span>
                    <div class="text-sm text-vs-text-muted">
                        ${modelName} • ${timestamp}
                        ${pair.isStreaming ? html`<span class="text-vs-accent"> • Streaming</span>` : ''}
                    </div>
                </div>
            </button>
            <div class="pair-content hidden p-4">
                ${this.renderJsonSections(pair)}
            </div>
        </div>
    `;
}

// JSON section rendering with syntax highlighting
private renderJsonSections(pair: ProcessedPair): TemplateResult {
    return html`
        <div class="json-sections space-y-4">
            <div class="json-section">
                <h4 class="text-vs-accent font-medium mb-2">Request</h4>
                <pre class="bg-vs-bg p-3 rounded text-sm overflow-x-auto">
                    <code>${this.formatJson(pair.request)}</code>
                </pre>
            </div>
            <div class="json-section">
                <h4 class="text-vs-accent font-medium mb-2">Response</h4>
                <pre class="bg-vs-bg p-3 rounded text-sm overflow-x-auto">
                    <code>${this.formatJson(pair.response)}</code>
                </pre>
            </div>
        </div>
    `;
}
```

## Security Implementation Patterns

### XSS Prevention in Components

**Content Sanitization Pattern**:

```typescript
import { markdownToHtml } from '../utils/markdown';

// Safe content rendering
private renderUserContent(content: string): TemplateResult {
    const sanitizedHtml = markdownToHtml(content);
    return html`<div class="user-content">${unsafeHTML(sanitizedHtml)}</div>`;
}

// Direct text rendering (automatically escaped by Lit)
private renderSystemText(text: string): TemplateResult {
    return html`<div class="system-text">${text}</div>`;
}
```

**Input Validation Pattern**:

```typescript
// Type-safe property validation
private validateData(data: unknown): data is RequiredDataType {
    return Array.isArray(data) && data.every(item =>
        typeof item === 'object' &&
        item !== null &&
        'requiredProperty' in item
    );
}

// Safe data processing
connectedCallback(): void {
    super.connectedCallback();

    if (!this.validateData(this.data)) {
        console.warn('Invalid data provided to component');
        this.data = [];
    }
}
```

## Performance Implementation Patterns

### Lazy Rendering for Large Data Sets

```typescript
// Virtual scrolling pattern for large lists
private renderLargeList(items: DataItem[]): TemplateResult {
    const ITEMS_PER_PAGE = 50;
    const currentPage = this.currentPage || 0;
    const startIndex = currentPage * ITEMS_PER_PAGE;
    const visibleItems = items.slice(startIndex, startIndex + ITEMS_PER_PAGE);

    return html`
        <div class="large-list">
            ${visibleItems.map(item => this.renderItem(item))}
            ${this.renderPagination(items.length, ITEMS_PER_PAGE, currentPage)}
        </div>
    `;
}

// Efficient toggle implementation
private toggleContent = (e: Event): void => {
    const header = e.currentTarget as HTMLElement;
    const content = header.nextElementSibling as HTMLElement;

    if (content) {
        // Use display toggle for better performance than classList
        const isHidden = content.style.display === 'none';
        content.style.display = isHidden ? 'block' : 'none';

        // Update arrow indicator
        const arrow = header.querySelector('.toggle-icon');
        if (arrow) {
            arrow.textContent = isHidden ? '▲' : '▼';
        }
    }
}
```

### Memory Management

```typescript
// Cleanup pattern for event listeners
disconnectedCallback(): void {
    super.disconnectedCallback();

    // Remove any external event listeners
    if (this.resizeObserver) {
        this.resizeObserver.disconnect();
    }

    // Clear any timers or intervals
    if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
    }
}

// Efficient data caching
private dataCache = new Map<string, ProcessedData>();

private getProcessedData(key: string, rawData: RawData[]): ProcessedData {
    if (this.dataCache.has(key)) {
        return this.dataCache.get(key)!;
    }

    const processed = this.processData(rawData);
    this.dataCache.set(key, processed);
    return processed;
}
```

## Testing Patterns for Components

### Component Testing Utilities

```typescript
// Test helper for component setup
export function setupComponent<T extends LitElement>(ComponentClass: new () => T, props: Partial<T> = {}): T {
	const component = new ComponentClass();
	Object.assign(component, props);

	document.body.appendChild(component);
	return component;
}

// Mock data generators
export function createMockConversation(): SimpleConversation {
	return {
		id: crypto.randomUUID(),
		messages: [createMockMessage()],
		model: "claude-3-sonnet-20240229",
		systemPrompt: "Test system prompt",
	};
}

// Async testing pattern
export async function testComponentRender<T extends LitElement>(component: T, expectedContent: string): Promise<void> {
	await component.updateComplete;
	const content = component.shadowRoot?.textContent || component.textContent;
	assert(content?.includes(expectedContent), "Component should render expected content");
}
```

## Accessibility Implementation

### Keyboard Navigation

```typescript
// Keyboard event handling
private handleKeyDown = (e: KeyboardEvent): void => {
    switch (e.key) {
        case 'Enter':
        case ' ':
            e.preventDefault();
            this.toggleContent(e);
            break;
        case 'ArrowDown':
            e.preventDefault();
            this.focusNext();
            break;
        case 'ArrowUp':
            e.preventDefault();
            this.focusPrevious();
            break;
    }
}

// ARIA attributes for screen readers
private renderAccessibleButton(content: string, expanded: boolean): TemplateResult {
    return html`
        <button
            class="accessible-toggle"
            aria-expanded=${expanded}
            aria-controls="content-section"
            @keydown=${this.handleKeyDown}
        >
            ${content}
        </button>
    `;
}
```

This implementation guide provides practical patterns and code examples for developing, maintaining, and extending the Claude Trace component library with proper type safety, security, performance, and accessibility considerations.
