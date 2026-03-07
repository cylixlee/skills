# ReAct Agent Development

ReAct Agent is an Agent implementation that supports tool calling, based on the ReAct (Reason + Act) pattern.

## Creating a ReAct Agent

```go
import (
    "github.com/cloudwego/eino/flow/agent/react"
    "github.com/cloudwego/eino/compose"
)

rAgent, err := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: chatModel,  // Model that supports tool calling
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{yourTool},
    },
})
```

## Complete Example

```go
ctx := context.Background()

// 1. Create tool
sumTool := &SumTool{}

// 2. Create ChatModel
cm, _ := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    Model:   "gpt-4o",
    APIKey:  key,
    // Enable tool calling
})

// 3. Create ReAct Agent
agent, _ := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{sumTool},
    },
})

// 4. Run Agent
messages := []*schema.Message{
    schema.UserMessage("Calculate 123 + 456"),
}

result, err := agent.Generate(ctx, messages)
```

## Handling Unknown Tools

You can set UnknownToolsHandler to handle cases where the model calls unknown tools:

```go
unknownHandler := func(ctx context.Context, toolName string) (string, error) {
    return fmt.Sprintf("Unknown tool: %s", toolName), nil
}

agent, _ := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools:               []tool.BaseTool{sumTool},
        UnknownToolsHandler: unknownHandler,
    },
})
```

## Streaming Output

```go
stream, _ := agent.Stream(ctx, messages)

defer stream.Close()
for {
    chunk, err := stream.Recv()
    if err == io.EOF {
        break
    }
    // Handle streaming output
    fmt.Println(chunk.Content)
}
```

## Agent Configuration Options

| Option                            | Description                          |
| --------------------------------- | ------------------------------------ |
| `ToolCallingModel`                | ChatModel that supports tool calling |
| `ToolsConfig.Tools`               | List of available tools              |
| `ToolsConfig.UnknownToolsHandler` | Handler for unknown tools            |
| `MaxSteps`                        | Maximum iterations (default 100)     |

## Related Information

- Core package: `github.com/cloudwego/eino/flow/agent/react`
