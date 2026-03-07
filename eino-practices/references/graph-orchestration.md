# Graph Orchestration

Graph is Eino's Directed Acyclic Graph (DAG) orchestration approach, suitable for complex flow control.

## Creating a Graph

```go
import (
    "github.com/cloudwego/eino/compose"
    "github.com/cloudwego/eino/schema"
)

g := compose.NewGraph[map[string]any, *schema.Message]()
```

## Adding Nodes

### Basic Node Types

```go
// Lambda node (custom function)
g.AddLambdaNode("myLambda", func(ctx context.Context, input map[string]any) (map[string]any, error) {
    input["processed"] = true
    return input, nil
})

// ChatTemplate node
g.AddChatTemplateNode("prompt", template)

// ChatModel node
g.AddChatModelNode("model", chatModel)

// Tools node
g.AddToolsNode("tools", toolsNode)
```

### Node Configuration

```go
g.AddLambdaNode("nodeName", lambdaFunc, compose.WithNodeName("displayName"))
```

## Defining Edges

```go
// Basic edge (sequential execution)
g.AddEdge(compose.START, "prompt")
g.AddEdge("prompt", "model")
g.AddEdge("model", compose.END)

// Conditional edge (branch based on condition)
g.AddEdge("model", compose.If{
    Condition: func(ctx context.Context, input map[string]any) (bool, error) {
        // Return true for tools branch, false for END
        return input["need_tool"] == true, nil
    },
    TrueNode:  "tools",
    FalseNode: compose.END,
})
```

## Conditional Branch Example

```go
g.AddEdge("model", compose.If{
    Condition: func(ctx context.Context, input map[string]any) (bool, error) {
        msg := input["message"].(*schema.Message)
        return len(msg.ToolCalls) > 0, nil
    },
    TrueNode:  "tools",
    FalseNode: "output",
})
```

## Compiling and Invoking

```go
// Compile Graph
r, err := g.Compile(ctx)
if err != nil {
    // handle error
}

// Invoke
input := map[string]any{
    "question": "Hello",
}
result, err := r.Invoke(ctx, input)
```

## Complete Example

```go
g := compose.NewGraph[map[string]any, *schema.Message]()

g.AddChatTemplateNode("prompt", chatTpl)
g.AddChatModelNode("model", chatModel)
g.AddToolsNode("tools", toolsNode)

g.AddEdge(compose.START, "prompt")
g.AddEdge("prompt", "model")
g.AddEdge("model", compose.If{
    Condition: func(ctx context.Context, input map[string]any) (bool, error) {
        msg := input["message"].(*schema.Message)
        return len(msg.ToolCalls) > 0, nil
    },
    TrueNode:  "tools",
    FalseNode: compose.END,
})
g.AddEdge("tools", "model")  // Continue to model after tool call

r, _ := g.Compile(ctx)
result, _ := r.Invoke(ctx, input)
```

## Related Information

- Core package: `github.com/cloudwego/eino/compose`
