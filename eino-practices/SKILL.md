---
name: eino-practices
description: Provides guidance on using the CloudWeGo Eino framework for building Go AI applications, including LLM calls, prompt templates, tool definitions, Graph/Workflow orchestration, and Agent development. Use this skill when users mention eino, LLM calls, ChatModel, tool calling, workflow orchestration, Agent development, RAG, or related keywords.
---

# Eino Practices

CloudWeGo Eino is an AI application development framework for Go, providing capabilities for LLM invocation, component orchestration, and Agent development.

## When to Use This Skill

Use this skill when:
- You need to call large language models from Go
- You need to build LLM-based applications
- You need to define tools for LLM to call
- You need to orchestrate multiple AI components into workflows
- You need to develop Agent applications (ReAct, Multi-Agent, etc.)
- You need to implement RAG (Retrieval Augmented Generation)
- You need advanced features like state management, checkpoints, or callbacks

## Core Concepts

Core components of the Eino framework:

| Component               | Description      | Typical Use                           |
| ----------------------- | ---------------- | ------------------------------------- |
| **ChatModel**           | LLM wrapper      | Text generation, streaming            |
| **Prompt/ChatTemplate** | Prompt template  | Dynamic prompt building               |
| **Tool**                | Tool definition  | External function calls by LLM        |
| **Retriever**           | Vector retriever | Knowledge retrieval for RAG           |
| **Lambda**              | Custom function  | Data transformation, logic processing |
| **Document**            | Document parser  | PDF, Word, etc.                       |
| **Embedding**           | Text vectorizer  | Convert text to vectors               |
| **VectorStore**         | Vector database  | Store and search vectors              |

## Orchestration Patterns

Eino provides multiple orchestration patterns:

| Pattern      | Description                  | Use Case                                   |
| ------------ | ---------------------------- | ------------------------------------------ |
| **Chain**    | Sequential chaining          | Simple linear flows                        |
| **Graph**    | Directed Acyclic Graph (DAG) | Complex flow control, conditional branches |
| **Workflow** | Workflow                     | Data flow with field mapping               |
| **Batch**    | Batch processing             | Parallel/concurrent processing of inputs   |

## Agent Types

| Agent Type           | Description                          |
| -------------------- | ------------------------------------ |
| **ChatModelAgent**   | Simple Agent based on ChatModel      |
| **ReAct Agent**      | ReAct pattern with tool calling      |
| **Deep Agent**       | Deep task orchestration with TODO    |
| **Supervisor**       | Multi-Agent coordinator              |
| **Plan-Execute**     | Plan-execute-replan pattern          |
| **Loop Agent**       | Executes agents in a loop            |
| **Parallel Agent**   | Executes multiple agents in parallel |
| **Sequential Agent** | Executes agents sequentially         |

## Advanced Features

Eino provides advanced features for complex applications:

- **State Management**: Maintain state across node executions within a Graph
- **Checkpoint & Interruption**: Pause and resume execution with state persistence
- **Callbacks/Tracing**: Monitor and trace Graph/Workflow execution
- **Memory/Persistence**: Store and retrieve conversation history
- **Human-in-the-Loop**: Human approval, review, and feedback loops
- **Graph as Tool**: Wrap Graph as reusable Tool in Agent

## References

See the following files for detailed usage:

### Core Components

- [llm-usage](references/llm-usage.md) - LLM and ChatModel usage
- [prompt-template](references/prompt-template.md) - Prompt template creation and usage
- [tool-definition](references/tool-definition.md) - Tool definition and binding
- [stream-processing](references/stream-processing.md) - Stream processing in Graph/Workflow

### Orchestration

- [graph-orchestration](references/graph-orchestration.md) - Graph DAG orchestration
- [workflow-usage](references/workflow-usage.md) - Workflow orchestration
- [batch-processing](references/batch-processing.md) - Batch node for parallel processing

### Agent Development

- [react-agent](references/react-agent.md) - ReAct Agent development
- [deep-agent](references/deep-agent.md) - Deep Agent with task orchestration
- [multi-agent](references/multi-agent.md) - Multi-Agent collaboration
- [adk-framework](references/adk-framework.md) - ADK Runner, Event, Session

### Advanced Features

- [state-management](references/state-management.md) - Graph state management
- [checkpoint-interrupt](references/checkpoint-interrupt.md) - Checkpoint and interruption
- [callbacks](references/callbacks.md) - Callbacks and tracing
- [memory](references/memory.md) - Memory and persistence
- [human-in-loop](references/human-in-loop.md) - Human-in-the-Loop patterns
- [graph-as-tool](references/graph-as-tool.md) - Graph as Tool
- [graph-visualize](references/graph-visualize.md) - Mermaid diagram generation

### RAG

- [rag](references/rag.md) - RAG implementation guide

### Best Practices

- [error-handling](references/error-handling.md) - Error handling strategies
- [security-best-practices](references/security-best-practices.md) - Security guidelines
- [performance-optimization](references/performance-optimization.md) - Performance tuning

## Key Packages

```go
import (
    "github.com/cloudwego/eino/compose"
    "github.com/cloudwego/eino/flow/agent/react"
    "github.com/cloudwego/eino/schema"
    "github.com/cloudwego/eino/components/tool"
    "github.com/cloudwego/eino/components/prompt"
    "github.com/cloudwego/eino/components/embedding"
    "github.com/cloudwego/eino/components/retriever"
    "github.com/cloudwego/eino/adk"
    "github.com/cloudwego/eino/callbacks"
)
```

## Best Practices

1. **Use interfaces over concrete types**: Eino components implement common interfaces for easy swapping
2. **Leverage Graph/Workflow**: Use orchestration for complex logic to keep code clean
3. **Define tools precisely**: Clear ToolInfo descriptions help LLM call correctly
4. **Use streaming**: Prefer Stream for conversation scenarios to improve UX
5. **Handle errors**: Tool invocations need to handle JSON parsing errors and execution exceptions
6. **Use middleware**: Leverage tool middleware (jsonfix, errorremover) for robustness
7. **Consider state management**: Use state handlers when sharing data across nodes
8. **Implement checkpoints**: For long-running flows requiring human intervention
9. **Apply rate limiting**: Protect services from abuse with rate limiting middleware
10. **Cache responses**: Use caching for expensive operations like LLM calls
11. **Use concurrency**: Leverage Batch nodes and parallel execution for throughput
12. **Secure API keys**: Never hardcode secrets; use environment variables or secret managers
