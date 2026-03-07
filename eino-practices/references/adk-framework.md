# ADK Framework

The Agent Development Kit (ADK) provides a complete framework for building and running AI Agents in production. It includes Runner, Event System, Session management, and various pre-built Agent types.

## Core Components

| Component   | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| **Runner**  | Agent execution engine with streaming and checkpoint support |
| **Agent**   | Base interface for all Agent implementations                 |
| **Event**   | Event system for tracking Agent execution                    |
| **Session** | Manages conversation state and values                        |

## Creating a ChatModelAgent

```go
import (
    "github.com/cloudwego/eino/adk"
    "github.com/cloudwego/eino/components/model"
)

// Assume model.NewChatModel() returns a model.ChatModel implementation
// In practice, you would use a concrete implementation like OpenAI, Claude, etc.
cm, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    Model:  "gpt-4o",
    APIKey: "your-api-key",
})

agent, err := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "my_agent",
    Description: "A helpful assistant",
    Instruction: "You are a helpful assistant. Respond concisely.",
    Model:       cm,
})
```

### Agent Configuration Options

| Option        | Description                                |
| ------------- | ------------------------------------------ |
| `Name`        | Agent identifier                           |
| `Description` | Agent description for supervisor selection |
| `Instruction` | System prompt defining agent behavior      |
| `Model`       | ChatModel for LLM calls                    |
| `Tools`       | Available tools for the agent              |
| `ToolsConfig` | Tool node configuration                    |
| `MaxSteps`    | Maximum execution steps (default: 100)     |

## Using Runner

Runner is the execution engine that runs Agents and manages the event lifecycle.

```go
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent:           agent,
    EnableStreaming: true,
})

// Run agent and get events
events := runner.Query(ctx, "Your query here")

for {
    event, ok := events.Next()
    if !ok {
        break
    }
    // Process event
}
```

### Runner Configuration

```go
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent:             agent,
    EnableStreaming:   true,
    CheckPointStore:   store,      // For state persistence
    SessionStore:      sessionStore, // For conversation history
    CallbacksHandler:  callbacks, // For monitoring
})
```

### Query Method

For simpler use cases without event iteration:

```go
iter := runner.Query(ctx, "Your question")
for {
    event, ok := iter.Next()
    if !ok {
        break
    }
    // Process event
}
```

## Event System

Events represent different stages of Agent execution.

### Event Types

| Event Type      | Description                                   |
| --------------- | --------------------------------------------- |
| `MessageOutput` | LLM response message                          |
| `ToolCall`      | Tool invocation request                       |
| `ToolCallDone`  | Tool execution completed                      |
| `Action`        | Agent action (like transfer to another agent) |
| `Error`         | Execution error                               |

### Processing Events

```go
messages := []*schema.Message{
    schema.UserMessage("Your query"),
}
events := runner.Run(ctx, messages)

for {
    event, ok := events.Next()
    if !ok {
        break
    }

    switch {
    case event.Output != nil && event.Output.MessageOutput != nil:
        msg := event.Output.MessageOutput.Message
        fmt.Printf("Assistant: %s\n", msg.Content)

    case event.Action != nil:
        fmt.Printf("Action: %+v\n", event.Action)

    case event.Err != nil:
        fmt.Printf("Error: %v\n", event.Err)
    }
}
```

### Message Output

```go
if msg, _ := event.Output.MessageOutput.GetMessage(); msg != nil {
    fmt.Printf("Content: %s\n", msg.Content)
    fmt.Printf("Role: %s\n", msg.Role)
    
    // Tool calls
    for _, tc := range msg.ToolCalls {
        fmt.Printf("Tool: %s, Args: %s\n", tc.Function.Name, tc.Function.Arguments)
    }
}
```

### Streaming Output

```go
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent:           agent,
    EnableStreaming: true,
})

events := runner.Query(ctx, "Your query")
for {
    event, ok := events.Next()
    if !ok {
        break
    }

    if event.Output != nil && event.Output.MessageOutput != nil {
        mo := event.Output.MessageOutput
        
        // Check if streaming
        if mo.IsStreaming {
            chunk := mo.GetChunk()
            if chunk != nil {
                fmt.Print(chunk.Content)
            }
        }
    }
}
```

## Session Values

Session Values allow sharing data between Tools within an Agent execution. This is useful for maintaining state across multiple tool calls.

```go
import "github.com/cloudwego/eino/adk"

// In a tool function - set value
func myTool(ctx context.Context, input *MyInput) (string, error) {
    adk.AddSessionValue(ctx, "user-name", input.Name)
    return "saved", nil
}

// In another tool - get value
func anotherTool(ctx context.Context, input *AnotherInput) (string, error) {
    userName, _ := adk.GetSessionValue[string](ctx, "user-name")
    return fmt.Sprintf("Hello, %s", userName), nil
}
```

### Session Value Functions

| Function                                              | Description                   |
| ----------------------------------------------------- | ----------------------------- |
| `AddSessionValue(ctx, key, value)`                    | Store a value in session      |
| `GetSessionValue[T](ctx, key)`                        | Retrieve a value from session |
| `GetSessionValueWithDefault[T](ctx, key, defaultVal)` | Retrieve with default         |

## Checkpoint and Interruption

ADK supports checkpoint persistence and human interruption.

### With Checkpoint Store

You need to implement the CheckpointStore interface:

```go
import (
    "github.com/cloudwego/eino/compose"
)

// Implement CheckpointStore interface
type InMemoryCheckpointer struct {
    data map[string][]byte
    mu   sync.RWMutex
}

func (s *InMemoryCheckpointer) Get(ctx context.Context, checkpointID string) ([]byte, bool, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    data, ok := s.data[checkpointID]
    return data, ok, nil
}

func (s *InMemoryCheckpointer) Set(ctx context.Context, checkpointID string, data []byte) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.data[checkpointID] = data
    return nil
}

// Create store instance
store := &InMemoryCheckpointer{data: make(map[string][]byte)}

runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent:           agent,
    CheckPointStore: store,
})

// Execute with checkpoint
events := runner.Query(ctx, "long running task")
checkpointID := "task-001"

// Resume from checkpoint
resumeEvents := runner.ResumeWithParams(ctx, checkpointID, &adk.ResumeParams{
    Targets: map[string]any{
        "interrupt_id": &ApprovalResult{Approved: true},
    },
})
```

## Custom Agent

You can create custom Agents by implementing the `adk.Agent` interface:

```go
type MyAgent struct{}

func (m *MyAgent) Name(ctx context.Context) string {
    return "MyAgent"
}

func (m *MyAgent) Description(ctx context.Context) string {
    return "Custom agent description"
}

func (m *MyAgent) Run(ctx context.Context, input *adk.AgentInput, options ...adk.AgentRunOption) *adk.AsyncIterator[*adk.AgentEvent] {
    iter, gen := adk.NewAsyncIteratorPair[*adk.AgentEvent]()
    
    go func() {
        defer gen.Close()
        
        // Your agent logic
        gen.Send(&adk.AgentEvent{
            Output: &adk.AgentOutput{
                MessageOutput: &adk.MessageVariant{
                    Message: &schema.Message{
                        Role:    schema.Assistant,
                        Content: "Hello from custom agent",
                    },
                },
            },
        })
    }()
    
    return iter
}
```

## Related Information

- Core package: `github.com/cloudwego/eino/adk`
