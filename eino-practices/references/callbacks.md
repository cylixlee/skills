# Callbacks and Tracing

Eino provides callback mechanisms for monitoring and tracing Graph/Workflow execution.

## Global Callback Handlers

Register global callback handlers to affect all Graph/Workflow executions:

```go
import "github.com/cloudwego/eino/callbacks"

callbacks.AppendGlobalHandlers(&LoggerCallback{})
```

## Implementing Callback Interface

```go
type LoggerCallback struct{}

func (cb *LoggerCallback) OnStart(ctx context.Context, info *callbacks.RunInfo, input callbacks.CallbackInput) context.Context {
    fmt.Printf("Starting: %s\n", info.NodeName)
    return ctx
}

func (cb *LoggerCallback) OnEnd(ctx context.Context, info *callbacks.RunInfo, output callbacks.CallbackOutput) context.Context {
    fmt.Printf("Finished: %s\n", info.NodeName)
    return ctx
}

func (cb *LoggerCallback) OnError(ctx context.Context, info *callbacks.RunInfo, err error) context.Context {
    fmt.Printf("Error in %s: %v\n", info.NodeName, err)
    return ctx
}

func (cb *LoggerCallback) OnEndWithStreamOutput(ctx context.Context, info *callbacks.RunInfo, output *schema.StreamReader[callbacks.CallbackOutput]) context.Context {
    defer output.Close()
    for {
        chunk, err := output.Recv()
        if err == io.EOF {
            break
        }
        // Handle stream output
    }
    return ctx
}
```

## RunInfo Structure

```go
type RunInfo struct {
    RunID        string
    NodeName     string
    NodeType     string
    InvokeInputType  string
    InvokeOutputType string
}
```

## CallbackInput/Output

Callback input/output are empty interfaces, concrete types depend on node type:

```go
func (cb *LoggerCallback) OnEnd(ctx context.Context, info *callbacks.RunInfo, output callbacks.CallbackOutput) context.Context {
    switch out := output.(type) {
    case *schema.Message:
        fmt.Println("Message output:", out.Content)
    case string:
        fmt.Println("String output:", out)
    case map[string]any:
        fmt.Println("Map output:", out)
    }
    return ctx
}
```

## Use Cases

- Performance monitoring and logging
- Execution trace tracking
- Error alerting
- Debugging complex flows
- Integrating with third-party monitoring systems

## Related APIs

- `callbacks.AppendGlobalHandlers` - Register global handlers
- `callbacks.RunInfo` - Execution info structure
- `callbacks.CallbackInput` - Input callback
- `callbacks.CallbackOutput` - Output callback

## Related Packages

- `github.com/cloudwego/eino/components/callbacks`
- `github.com/cloudwego/eino/schema`
