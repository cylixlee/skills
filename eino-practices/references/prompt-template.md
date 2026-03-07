# Prompt Templates

Eino provides `ChatTemplate` for dynamically building prompts, supporting message placeholders and conditional rendering.

## Creating a Template

### Basic Usage

```go
import (
    "github.com/cloudwego/eino/components/prompt"
    "github.com/cloudwego/eino/schema"
)

template := prompt.FromMessages(schema.FString,
    schema.SystemMessage("You are a {role}."),
    schema.UserMessage("Question: {question}"),
)
```

### Supported Message Types

```go
// System message
schema.SystemMessage("You are a {role}")

// User message
schema.UserMessage("Hello {name}")

// Assistant message
schema.AssistantMessage("Answer: {answer}")

// Messages placeholder (for chat history)
schema.MessagesPlaceholder("chat_history", true)
// Parameters: variable name, whether to render as history

// Tool calls placeholder
schema.ToolCallsPlaceholder("tool_calls")
```

## Formatting Templates

```go
ctx := context.Background()

messages, err := template.Format(ctx, map[string]any{
    "role":     "helpful assistant",
    "question": "My code keeps showing errors",
})

// messages is of type []*schema.Message
for _, msg := range messages {
    fmt.Println(msg.Role, msg.Content)
}
```

## Chat History Template

```go
template := prompt.FromMessages(schema.FString,
    schema.SystemMessage("You are a helpful assistant."),
    schema.MessagesPlaceholder("history", true),  // Insert chat history
    schema.UserMessage("My question is: {question}"),
)

// Pass chat history when formatting
history := []*schema.Message{
    schema.UserMessage("What is Go language?"),
    schema.AssistantMessage("Go is..."),
}

messages, _ := template.Format(ctx, map[string]any{
    "history":  history,
    "question": "What are its advantages?",
})
```

## Using with ChatModel

```go
// 1. Create template
template := prompt.FromMessages(schema.FString,
    schema.SystemMessage("You are a {role}."),
    schema.UserMessage("{question}"),
)

// 2. Format to generate messages
messages, _ := template.Format(ctx, map[string]any{
    "role":     "assistant",
    "question": "Hello",
})

// 3. Invoke model
result, _ := cm.Generate(ctx, messages)
```

## Related Information

- Core package: `github.com/cloudwego/eino/components/prompt`
