# Frontend Source Directory

## Overview

The `frontend/src/` directory contains the complete frontend application for Claude Trace, a web-based visualization tool for analyzing AI model conversations and API interactions. Built with modern web technologies including Lit web components, TypeScript, and Tailwind CSS, this directory provides a comprehensive solution for visualizing conversation traces, raw API calls, and processed data from various AI models.

The frontend follows a component-based architecture with strict type safety, avoiding `any` types in favor of proper TypeScript interfaces and leveraging official SDK types from `@anthropic-ai/sdk`. The application emphasizes security through XSS prevention, performance through efficient rendering, and usability through interactive data exploration.

## Structure

```
frontend/src/
├── app.ts                          # Main application component and state management
├── index.ts                        # Application entry point and initialization
├── styles.css                      # Global styles and markdown formatting
├── components/                     # UI component library
│   ├── CLAUDE.md                   # Component documentation
│   ├── json-view.ts                # JSON data visualization component
│   ├── raw-pairs-view.ts           # Raw API request/response viewer
│   └── simple-conversation-view.ts # Primary conversation display component
└── utils/                          # Utility functions and helpers
    ├── CLAUDE.md                   # Utilities documentation
    └── markdown.ts                 # Secure markdown to HTML conversion
```

## Key Components

### Main Application (`app.ts`)

**Purpose**: The root application component that orchestrates the entire frontend experience, managing state, data processing, and view switching.

**Core Functionality**:

- **Data Processing**: Integrates with `SharedConversationProcessor` to transform raw API data into structured conversations
- **View Management**: Provides tab-based navigation between conversations, raw calls, and JSON debug views
- **Model Filtering**: Dynamic filtering by AI model type with multi-selection support
- **State Management**: Reactive state updates using Lit's `@state` decorator
- **Performance Monitoring**: Built-in timing for data processing operations

**Key Features**:

```typescript
@customElement("claude-app")
export class ClaudeApp extends LitElement {
	@state() private data: ClaudeData = { rawPairs: [] };
	@state() private conversations: SimpleConversation[] = [];
	@state() private processedPairs: ProcessedPair[] = [];
	@state() private currentView: "conversations" | "raw" | "json" = "conversations";
	@state() private selectedModels: Set<string> = new Set();
}
```

**Data Flow**:

1. Loads data from global `window.claudeData` object
2. Processes raw pairs through `SharedConversationProcessor`
3. Generates filtered views based on selected models
4. Provides real-time counts and statistics

**Type Safety**: Uses proper `ClaudeData`, `SimpleConversation`, and `ProcessedPair` types throughout, avoiding any use of `any` types.

### Application Entry Point (`index.ts`)

**Purpose**: Application bootstrap and initialization logic with dynamic CSS injection.

**Key Features**:

- **Component Registration**: Imports and registers all custom web components
- **CSS Injection**: Dynamic stylesheet loading via build-time variable substitution
- **DOM Ready Handling**: Proper initialization timing for both loaded and loading states
- **Error Handling**: Graceful fallback when mount point is not found

**Initialization Pattern**:

```typescript
function initApp() {
	const app = new ClaudeApp();
	const appElement = document.getElementById("app");
	if (appElement) {
		appElement.appendChild(app);
	} else {
		console.error("App mount point not found");
	}
}
```

### Global Styles (`styles.css`)

**Purpose**: Defines the visual identity and theming for the entire application using VS Code dark theme colors and Tailwind CSS utilities.

**Key Features**:

- **VS Code Theme Integration**: Consistent color scheme matching VS Code dark theme
- **Markdown Styling**: Terminal-style formatting for markdown content with proper typography
- **Typography Hierarchy**: Structured heading levels with consistent spacing
- **Code Formatting**: Syntax highlighting and proper monospace font handling
- **List Styling**: Custom bullet points and numbering for terminal aesthetics
- **Responsive Design**: Word wrapping and overflow handling for various screen sizes

**Color Scheme**:

- Background: `#1e1e1e` (vs-bg)
- Text: Various VS Code theme colors for syntax highlighting
- Function: `#dcdcaa` (vs-function)
- Assistant: `#ce9178` (vs-assistant)
- Accent: `#569cd6` (vs-accent)

## Dependencies

### Internal Dependencies

- `../../src/shared-conversation-processor` - Core data processing and type definitions
- `../../src/types` - Application-wide TypeScript type definitions
- `./components/*` - UI component modules
- `./utils/*` - Utility function modules

### External Dependencies

- **`lit`** - Lightweight web components framework for reactive UI
- **`lit/decorators.js`** - Property and state decorators for component reactivity
- **`@anthropic-ai/sdk`** - Official Anthropic SDK types for API data structures
- **`marked`** - High-performance markdown parser (used via utils)
- **`diff`** - Text diffing library for edit visualization (used in components)

### Build Dependencies

- **Tailwind CSS** - Utility-first CSS framework for styling
- **TypeScript** - Type safety and modern JavaScript features
- **tsup** - Build tooling for TypeScript compilation and bundling

## Patterns & Conventions

### Component Architecture

- **Lit Web Components**: Modern custom elements with efficient rendering and change detection
- **Shadow DOM Disabled**: Components use `createRenderRoot() { return this; }` to access global Tailwind CSS
- **Reactive Properties**: `@property()` and `@state()` decorators for automatic re-rendering
- **Type Safety**: Strict TypeScript with proper interface definitions, no `any` types
- **Event Handling**: Type-safe event listeners with proper Event typing

### Type Safety Standards

- **SDK Type Integration**: Direct import and usage of `@anthropic-ai/sdk` types
- **Interface Definitions**: Custom interfaces for application-specific data structures
- **Type Guards**: Runtime type validation where necessary
- **Null Safety**: Proper null/undefined handling throughout all components
- **Generic Avoidance**: Specific types preferred over generic `any` usage

### State Management

- **Centralized State**: Main application state managed in `ClaudeApp` component
- **Reactive Updates**: Lit's reactive system handles UI updates automatically
- **Derived State**: Computed properties for filtered data and statistics
- **Immutable Updates**: State changes create new objects rather than mutating existing ones

### Security Practices

- **XSS Prevention**: All user content processed through secure markdown utility
- **Input Validation**: Type checking and safe parsing for all external data
- **HTML Escaping**: Comprehensive entity escaping before any HTML rendering
- **Content Security**: Use of `unsafeHTML` directive only with pre-sanitized content

### Performance Optimizations

- **Change Detection**: Efficient Lit rendering with property-based change detection
- **Lazy Loading**: Components render content on-demand with collapsible sections
- **Memory Management**: Proper cleanup and no memory leaks in event handlers
- **Bundle Size**: Tree-shaking friendly ES modules for optimal bundle size

## Usage Examples

### Basic Application Setup

```typescript
// Initialize the application
import { ClaudeApp } from "./app";
import "./components/simple-conversation-view";
import "./components/raw-pairs-view";
import "./components/json-view";

// Application automatically loads data from window.claudeData
const app = new ClaudeApp();
document.getElementById("app")?.appendChild(app);
```

### Data Integration Pattern

```typescript
// Data flow from raw API data to rendered components
const processor = new SharedConversationProcessor();
const processedPairs = processor.processRawPairs(rawPairs);
const conversations = processor.mergeConversations(processedPairs);

// Components automatically update when data changes
html`<simple-conversation-view .conversations=${conversations}></simple-conversation-view>`;
```

### Custom Component Integration

```typescript
// Adding new components to the application
@customElement("custom-view")
export class CustomView extends LitElement {
	@property({ type: Array }) data: CustomData[] = [];

	createRenderRoot() {
		return this; // Access global CSS
	}

	render() {
		return html`
			<div class="custom-component">
				<!-- Component content -->
			</div>
		`;
	}
}
```

## Type Safety Implementation

### Critical Type Safety Features

The frontend strictly adheres to TypeScript best practices:

1. **No `any` Types**: All data structures use proper interfaces
2. **SDK Integration**: Official `@anthropic-ai/sdk` types for API data
3. **Runtime Validation**: Type guards for dynamic content
4. **Null Safety**: Explicit null/undefined handling

### Type Definitions Usage

```typescript
import type { MessageParam, ContentBlock, Message } from "@anthropic-ai/sdk/resources/messages";

import { SimpleConversation, ProcessedPair, EnhancedMessageParam } from "../../src/shared-conversation-processor";

import { ClaudeData, RawPair } from "../../src/types";
```

### Type-Safe Event Handling

```typescript
private handleToggle(e: Event, options: {
    type?: "content" | "write" | "custom";
    targetSelector?: string;
    customHandler?: (element: HTMLElement, isHidden: boolean) => void;
} = {}) {
    const currentElement = e.currentTarget as HTMLElement;
    // Type-safe element manipulation
}
```

## Notes

### Performance Characteristics

- **Efficient Rendering**: Lit's reactive system minimizes DOM updates
- **Memory Usage**: Components properly clean up event listeners and references
- **Bundle Size**: Tree-shaking enabled for optimal production builds
- **Load Time**: Dynamic CSS injection and lazy component loading

### Browser Support

- **Modern Browsers**: Requires ES2020+ support for modules and custom elements
- **Web Components**: Uses native custom elements API
- **CSS Support**: Requires CSS custom properties for theming
- **JavaScript Features**: Uses modern syntax including optional chaining and nullish coalescing

### Development Experience

- **Hot Reload**: Development server supports live reloading
- **Type Checking**: Full TypeScript integration with IDE support
- **Debugging**: Source maps enabled for development builds
- **Testing**: Components designed for testability with clear interfaces

### Security Considerations

- **Content Security Policy**: Compatible with strict CSP requirements
- **XSS Prevention**: Multi-layered protection against script injection
- **Data Validation**: All external data validated before processing
- **Secure Defaults**: Safe configuration for all third-party libraries

### Accessibility Features

- **Keyboard Navigation**: All interactive elements support keyboard access
- **Screen Readers**: Semantic HTML structure for assistive technology
- **Color Contrast**: VS Code theme ensures adequate contrast ratios
- **Focus Management**: Proper focus handling for dynamic content

The frontend/src/ directory represents a mature, production-ready frontend application that successfully balances developer experience, performance, security, and maintainability while providing powerful tools for analyzing AI conversation data.
