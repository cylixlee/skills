# Tool Definition

Eino allows defining tools for LLMs to call external functions. Tools need to implement the `InvokableTool` interface.

## Implementing Tool Interface

```go
import (
    "context"
    "github.com/cloudwego/eino/components/tool"
    "github.com/cloudwego/eino/schema"
)

type SumTool struct{}

func (t *SumTool) Info(ctx context.Context) (*schema.ToolInfo, error) {
    return &schema.ToolInfo{
        Name: "sum",
        Desc: "Calculate the sum of two integers",
        ParamsOneOf: schema.NewParamsOneOfByParams(map[string]*schema.ParameterInfo{
            "a": {Type: "number", Desc: "First integer", Required: true},
            "b": {Type: "number", Desc: "Second integer", Required: true},
        }),
    }, nil
}

func (t *SumTool) InvokableRun(ctx context.Context, argumentsInJSON string, opts ...tool.Option) (string, error) {
    // Parse arguments
    var args struct {
        A float64 `json:"a"`
        B float64 `json:"b"`
    }
    if err := json.Unmarshal([]byte(argumentsInJSON), &args); err != nil {
        return "", err
    }
    
    // Execute logic
    result := args.A + args.B
    return fmt.Sprintf("Result: %v", result), nil
}
```

## ToolInfo Fields

| Field         | Description                                               |
| ------------- | --------------------------------------------------------- |
| `Name`        | Tool name, used by LLM to identify which tool to call     |
| `Desc`        | Tool description, helps LLM understand the tool's purpose |
| `ParamsOneOf` | Parameter definition, supports multiple parameter schemes |

## Parameter Definition

```go
// Method 1: Define parameters using map
params := schema.NewParamsOneOfByParams(map[string]*schema.ParameterInfo{
    "a": {Type: "number", Desc: "First number", Required: true},
    "b": {Type: "number", Desc: "Second number", Required: true},
})

// Method 2: Using JSON Schema
params := schema.NewParamsOneOfByJSONSchema(jsonSchemaString)
```

## Binding to ChatModel

```go
// Forced tools (model must choose one to call)
cm.BindForcedTools([]*schema.ToolInfo{toolInfo})

// Or optional tools (model can choose not to call)
cm.BindTools([]*schema.ToolInfo{toolInfo})
```

## Tool Middleware

Eino provides tool middleware to handle common issues:

```go
import (
    "github.com/cloudwego/eino/components/tool/middleware/errorremover"
    "github.com/cloudwego/eino/components/tool/middleware/jsonfix"
)

// Error removal middleware
wrapped := errorremover.New(tool)

// JSON fix middleware (handles malformed JSON from model)
wrapped := jsonfix.New(tool)
```

### Using Middleware with Agent

```go
import "github.com/cloudwego/eino/compose"

agent, err := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{yourTool},
        ToolCallMiddlewares: []compose.ToolMiddleware{
            jsonfix.Middleware(),
            errorremover.Middleware(),
        },
    },
})
```

### Middleware Chaining

Middlewares can be chained:

```go
middleware := compose.ToolMiddlewareChain(
    jsonfix.Middleware(),
    errorremover.Middleware(),
)

compose.ToolsNodeConfig{
    Tools: []tool.BaseTool{yourTool},
    ToolCallMiddlewares: []compose.ToolMiddleware{middleware},
}
```

### Available Middlewares

| Middleware     | Purpose                                 |
| -------------- | --------------------------------------- |
| `jsonfix`      | Fixes malformed JSON in tool arguments  |
| `errorremover` | Removes error messages from tool output |
| `retrier`      | Automatically retries failed tool calls |

## Custom Middleware

```go
type MyMiddleware struct{}

func (m *MyMiddleware) Invoke(ctx context.Context, tool tool.BaseTool, args string, opts ...tool.Option) (string, error) {
    // Pre-processing
    start := time.Now()
    
    // Call original tool
    result, err := tool.InvokableRun(ctx, args, opts...)
    
    // Post-processing
    duration := time.Since(start)
    fmt.Printf("Tool executed in %v\n", duration)
    
    return result, err
}

func (m *MyMiddleware) Info(ctx context.Context) (*schema.ToolInfo, error) {
    return tool.Info(ctx)
}

func NewMyMiddleware(t tool.BaseTool) tool.BaseTool {
    return &MyMiddleware{}
}

## Quick Tool Creation

Eino provides utility functions to quickly create tools from Go functions without manually implementing the interface.

### Using SafeInferTool

```go
import (
    "github.com/cloudwego/eino/components/tool"
    "github.com/cloudwego/eino/components/tool/utils"
)

type SearchRequest struct {
    Query string `json:"query" jsonschema_description="The search query"`
}

type SearchResponse struct {
    Result string `json:"result"`
}

searchTool, err := utils.SafeInferTool("search", "search the internet",
    func(ctx context.Context, req *SearchRequest) (*SearchResponse, error) {
        // Implementation
        return &SearchResponse{Result: "search results for: " + req.Query}, nil
    })
```

### Using InferTool

```go
import "github.com/cloudwego/eino/components/tool/utils"

tool, err := utils.InferTool("tool_name", "tool description",
    func(ctx context.Context, input *MyInput) (string, error) {
        return "result", nil
    })
```

### Using GoStruct2ToolInfo

Generate ToolInfo from a Go struct:

```go
import "github.com/cloudwego/eino/components/tool/utils"

type MyParams struct {
    Name string `json:"name" jsonschema_description="User name"`
    Age  int    `json:"age" jsonschema_description="User age"`
}

tInfo, err := utils.GoStruct2ToolInfo[MyParams]("my_tool", "Does something useful")
```

## Related Information

- Core package: `github.com/cloudwego/eino/components/tool`
