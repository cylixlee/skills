# LLM/ChatModel Usage

Eino wraps various LLMs through the `ChatModel` interface, supporting both synchronous generation and streaming output.

## Creating a ChatModel

### OpenAI Example

```go
import (
    "github.com/cloudwego/eino/components/model/openai"
)

cm, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    BaseURL: "https://api.openai.com/v1",
    Model:   "gpt-4o",
    APIKey: os.Getenv("OPENAI_API_KEY"),
})
```

### Supported Models

Eino supports multiple model providers:
- OpenAI
- Ollama
- DeepSeek
- Volcano Engine Ark
- Other OpenAI API-compatible models

## Text Generation

### Synchronous Generation

```go
import "github.com/cloudwego/eino/schema"

messages := []*schema.Message{
    schema.UserMessage("Tell me about Go language"),
}

result, err := cm.Generate(ctx, messages)
if err != nil {
    // handle error
}
fmt.Println(result.Content)
```

### Streaming Output

```go
stream, err := cm.Stream(ctx, messages)
if err != nil {
    // handle error
}

defer stream.Close()

for {
    chunk, err := stream.Recv()
    if err == io.EOF {
        break
    }
    if err != nil {
        // handle error
    }
    fmt.Print(chunk.Content)
}
```

## StreamReader API

StreamReader是流式输出的核心接口：

```go
type StreamReader[T any] interface {
    Recv() (T, error)
    Close() error
}
```

### Recv 模式

```go
defer stream.Close()
for {
    msg, err := stream.Recv()
    if err == io.EOF {
        break
    }
    if err != nil {
        return err
    }
    // 处理 msg
}
```

### 使用 Pipe 创建流

`schema.Pipe` 用于在代码中创建自定义流：

```go
sr, sw := schema.Pipe[string](bufferSize)

go func() {
    defer sw.Close()
    sw.Send("chunk1", nil)
    sw.Send("chunk2", nil)
}()

// 读取
for {
    chunk, err := sr.Recv()
    if err == io.EOF { break }
    fmt.Println(chunk)
}
```

### Transform Stream

对流进行转换处理：

```go
stream, err := runnable.Transform(ctx, inputStream)
if err != nil {
    // handle error
}

defer stream.Close()
for {
    chunk, err := stream.Recv()
    if err == io.EOF {
        break
    }
    // 处理转换后的chunk
}
```

## Message Building

Use the `schema` package to construct messages:

```go
// User message
msg := schema.UserMessage("Hello")

// System message
msg := schema.SystemMessage("You are a helpful assistant")

// Assistant message
msg := schema.AssistantMessage("Hello", withToolCalls)

// Tool result message
msg := schema.ToolMessage("tool result", "tool_call_id")
```

## Common Configuration

```go
cm, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    Model:       "gpt-4o",
    APIKey:      key,
    Temperature: 0.7,   // Controls randomness
    MaxTokens:   4096,  // Max generation length
    TopP:        0.9,   // nucleus sampling
    BaseURL:     "custom endpoint",
})
```

## Tool Calling Mode

Enable tool calling for the model:

```go
// Bind forced tools (model must choose one to call)
err := cm.BindForcedTools([]*schema.ToolInfo{toolInfo})

// Or bind available tools
err := cm.BindTools([]*schema.ToolInfo{toolInfo})
```

## Related Information

- Core package: `github.com/cloudwego/eino/components/model`
