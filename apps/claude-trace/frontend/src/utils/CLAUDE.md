# Frontend Utils Implementation Guide

## Overview

The `frontend/src/utils/` directory contains essential utility functions that provide core services for the Claude Trace frontend. Currently focused on secure content processing, this directory serves as the foundation for reusable functionality across frontend components.

## Current Implementation

```
utils/
└── markdown.ts     # Secure markdown to HTML conversion with XSS protection
```

## Markdown Utility Implementation

### Core Function Implementation

```typescript
import { marked } from "marked";

// Configure marked for security and GitHub Flavored Markdown
marked.setOptions({
	gfm: true, // Enable GitHub Flavored Markdown
	breaks: true, // Convert \n to <br> for better formatting
	headerIds: false, // Disable auto-generated header IDs for security
	mangle: false, // Don't mangle email addresses
});

export function markdownToHtml(markdown: string): string {
	if (!markdown) {
		return "";
	}

	try {
		// First escape all HTML entities to prevent XSS
		const escapedMarkdown = escapeHtml(markdown);

		// Then process through marked
		const html = marked(escapedMarkdown) as string;

		return html;
	} catch (error) {
		console.warn("Failed to parse markdown:", error);

		// Fallback to escaped plain text with line breaks
		return escapeHtml(markdown).replace(/\n/g, "<br>");
	}
}
```

### Security Implementation Details

**HTML Entity Escaping Function**:

```typescript
function escapeHtml(text: string): string {
	return text
		.replace(/&/g, "&amp;") // Must be first to avoid double-escaping
		.replace(/</g, "&lt;") // Prevent tag injection
		.replace(/>/g, "&gt;") // Prevent tag injection
		.replace(/"/g, "&quot;") // Prevent attribute injection
		.replace(/'/g, "&#39;") // Prevent attribute injection
		.replace(/\//g, "&#x2F;"); // Additional safety for forward slashes
}
```

**Key Security Measures**:

1. **Pre-processing Escape**: All input is HTML-escaped before markdown processing
2. **Safe Configuration**: Marked configured with security-first options
3. **Error Handling**: Graceful degradation to escaped plain text on parsing errors
4. **No HTML Passthrough**: All HTML tags are escaped, preventing script injection

### Usage Patterns in Components

**Safe Content Rendering Pattern**:

```typescript
import { markdownToHtml } from "../utils/markdown";
import { unsafeHTML } from "lit/directives/unsafe-html.js";

class MyComponent extends LitElement {
	private renderUserContent(content: string): TemplateResult {
		// Content is pre-sanitized by markdownToHtml
		const safeHtml = markdownToHtml(content);

		// Safe to use unsafeHTML because content is already sanitized
		return html`<div class="user-content">${unsafeHTML(safeHtml)}</div>`;
	}
}
```

**Performance Optimization Pattern**:

```typescript
class ContentProcessor {
	private markdownCache = new Map<string, string>();

	public processMarkdown(content: string): string {
		// Cache processed markdown to avoid recomputing
		if (this.markdownCache.has(content)) {
			return this.markdownCache.get(content)!;
		}

		const processed = markdownToHtml(content);

		// Limit cache size to prevent memory leaks
		if (this.markdownCache.size > 1000) {
			const firstKey = this.markdownCache.keys().next().value;
			this.markdownCache.delete(firstKey);
		}

		this.markdownCache.set(content, processed);
		return processed;
	}
}
```

## Additional Utility Patterns

### Type-Safe Utility Pattern

```typescript
// Example utility following project type safety standards
export function validateAndProcess<T extends Record<string, any>>(
	data: unknown,
	validator: (item: unknown) => item is T,
	processor: (item: T) => T,
): T[] {
	if (!Array.isArray(data)) {
		console.warn("Expected array data for processing");
		return [];
	}

	return data
		.filter(validator) // Type-safe filtering
		.map(processor); // Type-safe processing
}

// Usage example with conversation data
interface ConversationData {
	id: string;
	messages: Message[];
	timestamp: number;
}

function isConversationData(item: unknown): item is ConversationData {
	return typeof item === "object" && item !== null && "id" in item && "messages" in item && "timestamp" in item;
}

function processConversationData(data: ConversationData): ConversationData {
	return {
		...data,
		messages: data.messages.filter((msg) => msg.content.length > 0),
	};
}

// Type-safe usage
const processedConversations = validateAndProcess(rawData, isConversationData, processConversationData);
```

### Error Handling Utility Pattern

```typescript
// Generic error handling utility
export function safeExecute<T>(operation: () => T, fallback: T, errorMessage?: string): T {
	try {
		return operation();
	} catch (error) {
		console.warn(errorMessage || "Operation failed:", error);
		return fallback;
	}
}

// Usage in markdown processing
export function safeMarkdownToHtml(markdown: string): string {
	return safeExecute(
		() => markdownToHtml(markdown),
		escapeHtml(markdown).replace(/\n/g, "<br>"),
		"Markdown processing failed",
	);
}
```

### Async Utility Pattern

```typescript
// Debounced async processing utility
export function createDebouncedProcessor<T, R>(
	processor: (input: T) => Promise<R>,
	delay: number = 300,
): (input: T) => Promise<R> {
	let timeoutId: number | null = null;
	let latestPromise: Promise<R> | null = null;

	return (input: T): Promise<R> => {
		// Cancel previous timeout
		if (timeoutId !== null) {
			clearTimeout(timeoutId);
		}

		// Create new debounced promise
		latestPromise = new Promise((resolve, reject) => {
			timeoutId = window.setTimeout(async () => {
				try {
					const result = await processor(input);
					resolve(result);
				} catch (error) {
					reject(error);
				}
				timeoutId = null;
			}, delay);
		});

		return latestPromise;
	};
}

// Usage for markdown processing with debouncing
const debouncedMarkdownProcessor = createDebouncedProcessor(async (content: string) => markdownToHtml(content), 200);
```

## Testing Utilities Implementation

### Markdown Testing Utilities

```typescript
// Test helpers for markdown processing
export function createMarkdownTestSuite() {
	return {
		// Test basic markdown features
		testBasicMarkdown(): void {
			const input = "# Header\n**bold** text";
			const output = markdownToHtml(input);

			assert(output.includes("<h1>"), "Should convert headers");
			assert(output.includes("<strong>"), "Should convert bold text");
		},

		// Test XSS prevention
		testXSSPrevention(): void {
			const maliciousInput = '<script>alert("xss")</script>';
			const output = markdownToHtml(maliciousInput);

			assert(!output.includes("<script>"), "Should escape script tags");
			assert(output.includes("&lt;script&gt;"), "Should show escaped content");
		},

		// Test error handling
		testErrorHandling(): void {
			// Test with null/undefined inputs
			assert(markdownToHtml("") === "", "Should handle empty input");

			// Test with malformed input that might cause marked to throw
			const problematicInput = "\x00\x01\x02"; // Control characters
			const output = markdownToHtml(problematicInput);

			// Should not throw and should return safe content
			assert(typeof output === "string", "Should return string even on error");
		},
	};
}
```

### Utility Testing Pattern

```typescript
// Generic utility testing helper
export function testUtilityFunction<T, R>(
	utilityFn: (input: T) => R,
	testCases: Array<{ input: T; expected: R; description: string }>,
): void {
	testCases.forEach(({ input, expected, description }) => {
		try {
			const result = utilityFn(input);
			assert(
				JSON.stringify(result) === JSON.stringify(expected),
				`${description}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(result)}`,
			);
			console.log(`✓ ${description}`);
		} catch (error) {
			console.error(`✗ ${description}:`, error);
			throw error;
		}
	});
}

// Usage example
testUtilityFunction(markdownToHtml, [
	{
		input: "**bold**",
		expected: "<p><strong>bold</strong></p>\n",
		description: "Should convert bold markdown",
	},
	{
		input: '<script>alert("test")</script>',
		expected: "<p>&lt;script&gt;alert(&quot;test&quot;)&lt;/script&gt;</p>\n",
		description: "Should escape HTML tags",
	},
]);
```

## Performance Monitoring Utilities

### Performance Measurement Pattern

```typescript
// Performance monitoring utility for expensive operations
export function measurePerformance<T>(
	operation: () => T,
	operationName: string,
	logThreshold: number = 10, // ms
): T {
	const start = performance.now();
	const result = operation();
	const duration = performance.now() - start;

	if (duration > logThreshold) {
		console.log(`⚡ ${operationName} took ${duration.toFixed(2)}ms`);
	}

	return result;
}

// Usage in markdown processing
export function performantMarkdownToHtml(content: string): string {
	return measurePerformance(
		() => markdownToHtml(content),
		`Markdown processing (${content.length} chars)`,
		5, // Log if takes more than 5ms
	);
}
```

## Future Utility Expansion

### Planned Utility Categories

When expanding the utils directory, follow these patterns:

1. **Date/Time Utilities**: Consistent timestamp formatting
2. **String Processing**: Text manipulation and validation
3. **API Helpers**: Request/response formatting utilities
4. **Validation Utilities**: Type guards and data validation
5. **Performance Utilities**: Caching and optimization helpers

### Utility Development Standards

**Type Safety Requirements**:

- Use proper TypeScript interfaces, avoid `any` types
- Provide type guards for runtime validation
- Include comprehensive error handling with typed exceptions

**Security Requirements**:

- Treat all external input as potentially malicious
- Implement proper sanitization for content processing
- Use secure defaults in all utility configurations

**Performance Requirements**:

- Include performance monitoring for expensive operations
- Implement caching where appropriate
- Use efficient algorithms for data processing

**Testing Requirements**:

- Provide test utilities alongside production utilities
- Include edge case testing for all public functions
- Test error handling paths thoroughly

This implementation guide provides practical patterns for developing secure, performant, and maintainable utility functions that support the Claude Trace frontend application.
