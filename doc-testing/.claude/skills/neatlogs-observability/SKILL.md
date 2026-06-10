---
name: neatlogs-observability
description: Guide for adding Neatlogs instrumentation to new code in this project
compatibility: Claude Code
metadata:
  author: neatlogs
  version: "1.0"
---

# Neatlogs Instrumentation Guide

## This Project's Setup

- Language: typescript
- Package manager: npm

- No auto-instrumentations configured
- Endpoint: https://staging-cloud.neatlogs.com

## When to Add Instrumentation

Add `@span` (Python) or `span()` (TypeScript) to functions that:
- Orchestrate multi-step LLM workflows → kind="WORKFLOW"
- Represent autonomous agent behavior → kind="AGENT"
- Chain processing steps sequentially → kind="CHAIN"
- Wrap external tool/API calls → kind="TOOL"
- Retrieve from vector stores/search → kind="RETRIEVER"
- Generate embeddings → kind="EMBEDDING"
- Validate/filter LLM output → kind="GUARDRAIL"

## Do NOT Instrument

- Functions covered by auto-instrumentation (none configured)
- Pure utility functions (string formatting, config loading, logging)
- Test functions
- Functions with fewer than 3 lines of logic
- Thin wrappers around a single auto-instrumented call

## Usage (TypeScript)

```typescript
import { span, Span } from 'neatlogs';

const myWorkflow = span(
  { kind: 'WORKFLOW', name: 'my_workflow' },
  async (input: string) => { ... },
);

const searchDocs = span(
  { kind: 'TOOL', name: 'search', toolName: 'search' },
  async (query: string) => { ... },
);

// For class methods:
class MyAgent {
  @Span({ kind: 'AGENT', name: 'run' })
  async run(input: string) { ... }
}
```


## Re-run the wizard

To scan for new uninstrumented functions:
```bash
npx @neatlogs/wizard scan
```
