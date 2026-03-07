# Graph as Tool

You can wrap a compiled Graph as a Tool to be used within an Agent, enabling nested Graph execution.

## Creating Graph Tool

```go
import "github.com/cloudwego/eino/compose/graph"
```

```go
// 1. Build and compile Graph
g := compose.NewGraph[map[string]any, string]()
g.AddLambdaNode("process", func(ctx context.Context, input map[string]any) (string, error) {
    return fmt.Sprintf("Processed: %v", input["data"]), nil
})
g.AddEdge(compose.START, "process")
g.AddEdge("process", compose.END)

compiled, err := g.Compile(ctx)
if err != nil {
    return err
}

// 2. Wrap as Tool
graphTool, err := graph.NewInvokableGraphTool[map[string]any, string](
    compiled,
    "process_data",
    "Process data through a workflow",
)
if err != nil {
    return err
}
```

## Using in Agent

```go
agent, err := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{graphTool},
    },
})
```

## Complete Example

```go
func buildGraphTool(ctx context.Context) (tool.BaseTool, error) {
    // Build Graph
    g := compose.NewGraph[map[string]any, string]()
    
    g.AddLambdaNode("validate", func(ctx context.Context, input map[string]any) (map[string]any, error) {
        input["validated"] = true
        return input, nil
    })
    
    g.AddLambdaNode("transform", func(ctx context.Context, input map[string]any) (string, error) {
        return fmt.Sprintf("Result: %v", input["data"]), nil
    })
    
    g.AddEdge(compose.START, "validate")
    g.AddEdge("validate", "transform")
    g.AddEdge("transform", compose.END)
    
    // Compile
    compiled, err := g.Compile(ctx)
    if err != nil {
        return nil, err
    }
    
    // Create Tool
    return graph.NewInvokableGraphTool[map[string]any, string](
        compiled,
        "data_processor",
        "Process and validate data through a workflow",
    )
}

// Use in Agent
graphTool, _ := buildGraphTool(ctx)

agent, _ := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{graphTool},
    },
})
```

## Parameter Mapping

Graph input/output can be mapped to Tool parameters:

```go
graphTool, err := graph.NewInvokableGraphTool[I, O](
    compilable,
    "tool_name",
    "tool_description",
    graph.WithInputMapper(func(args string) (I, error) {
        // Parse tool arguments
        var input I
        json.Unmarshal([]byte(args), &input)
        return input, nil
    }),
    graph.WithOutputMapper(func(o O) string {
        // Convert output to tool result
        return fmt.Sprintf("%v", o)
    }),
)
```

## Use Cases

- Complex multi-step operations as single tool
- Reusable workflow components
- Nested Graph execution
- Tool composition

## Related APIs

- `graph.NewInvokableGraphTool` - Create Graph tool
- `graph.WithInputMapper` - Configure input mapping
- `graph.WithOutputMapper` - Configure output mapping

## Related Packages

- `github.com/cloudwego/eino/compose/graph`
- `github.com/cloudwego/eino/components/tool`
