# Memory and Persistence

Eino provides session value interfaces for storing and retrieving conversation state within Agent execution. The session values are stored in the execution context and can be accessed across tool calls.

## Session Values

Session values allow sharing data between Tools within an Agent execution:

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

## Using with ReAct Agent

### Using MessageFuture for Streaming

When streaming with ReAct Agent, you can collect messages for persistence:

```go
import (
    "github.com/cloudwego/eino/flow/agent/react"
    "github.com/cloudwego/eino/adk"
)

// Get message future option for collecting messages
msgFutureOpt, msgFuture := react.WithMessageFuture()

stream, err := agent.Stream(ctx, messages, msgFutureOpt)
if err != nil {
    return err
}

// Collect messages from the future
var collectedMessages []*schema.Message
for {
    msg, err := msgFuture.Recv()
    if err == io.EOF {
        break
    }
    if err != nil {
        return err
    }
    collectedMessages = append(collectedMessages, msg)
}
```

### Reading Messages for Context

```go
// Use session values to get conversation history
history, ok := adk.GetSessionValue[[]*schema.Message](ctx, "conversation_history")
if !ok {
    history = []*schema.Message{}
}

// Use history in prompt
template := prompt.FromMessages(schema.FString,
    schema.SystemMessage("You are a helpful assistant."),
    schema.MessagesPlaceholder("history", true),
    schema.UserMessage("{question}"),
)

messages, _ := template.Format(ctx, map[string]any{
    "history":  history,
    "question": query,
})
```

## Implementing a Custom Memory Store

You can implement a custom MemoryStore interface for persistent storage:

```go
type MemoryStore interface {
    Write(ctx context.Context, sessionID string, msgs []*schema.Message) error
    Read(ctx context.Context, sessionID string) ([]*schema.Message, error)
    Query(ctx context.Context, sessionID string, text string, limit int) ([]*schema.Message, error)
}
```

### Example: In-Memory Implementation

```go
type InMemoryStore struct {
    mu       sync.RWMutex
    sessions map[string][]*schema.Message
}

func NewInMemoryStore() *InMemoryStore {
    return &InMemoryStore{
        sessions: make(map[string][]*schema.Message),
    }
}

func (s *InMemoryStore) Write(ctx context.Context, sessionID string, msgs []*schema.Message) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.sessions[sessionID] = msgs
    return nil
}

func (s *InMemoryStore) Read(ctx context.Context, sessionID string) ([]*schema.Message, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    return s.sessions[sessionID], nil
}

func (s *InMemoryStore) Query(ctx context.Context, sessionID string, text string, limit int) ([]*schema.Message, error) {
    // Implementation for semantic search would go here
    return s.Read(ctx, sessionID)
}
```

### Using with ADK Runner

```go
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent: agent,
})

// Store messages after each turn
events := runner.Query(ctx, "Your question")
for {
    event, ok := events.Next()
    if !ok {
        break
    }
    // Store messages to your custom MemoryStore
}
```

## Streaming with Persistence

```go
func chatWithMemory(ctx context.Context, sessionID, query string, store *InMemoryStore) (string, error) {
    // Load history
    history, _ := store.Read(ctx, sessionID)

    // Build messages with history
    messages := append(history, schema.UserMessage(query))

    // Get message future for collecting responses
    msgFutureOpt, msgFuture := react.WithMessageFuture()

    // Stream response
    stream, err := agent.Stream(ctx, messages, msgFutureOpt)
    if err != nil {
        return "", err
    }

    // Collect response
    var result string
    for {
        chunk, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            return "", err
        }
        result += chunk.Content
    }

    // Collect all messages for storage
    var producedMessages []*schema.Message
    for {
        msg, err := msgFuture.Recv()
        if err == io.EOF {
            break
        }
        producedMessages = append(producedMessages, msg)
    }

    // Persist to memory store
    newMessages := append(history, producedMessages...)
    store.Write(ctx, sessionID, newMessages)

    return result, nil
}
```

## Use Cases

- Conversation history persistence
- Session management
- Context-aware responses
- Multi-turn dialogs

## Related Information

- Session values: `github.com/cloudwego/eino/adk`
- Schema: `github.com/cloudwego/eino/schema`
- See also: [adk-framework](adk-framework.md)
