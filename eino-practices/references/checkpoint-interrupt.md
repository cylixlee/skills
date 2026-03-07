# Checkpoint and Interruption

Graph supports checkpoint storage and node interruption, allowing execution to be paused, state saved, and resumed later.

## Checkpoint Store

Checkpoint store is used to persist Graph execution state:

```go
type CheckpointStore interface {
    Save(ctx context.Context, checkpointID string, data []byte) error
    Load(ctx context.Context, checkpointID string) ([]byte, error)
}
```

## Configuring Checkpoint

```go
g := compose.NewGraph[map[string]any, any]()
g.AddChatModelNode("model", chatModel)
g.AddEdge(compose.START, "model")
g.AddEdge("model", compose.END)

runner, err := g.Compile(ctx,
    compose.WithCheckPointStore(myStore),
)
```

## Configuring Interrupt Nodes

Interrupt before specified node executes:

```go
runner, err := g.Compile(ctx,
    compose.WithCheckPointStore(myStore),
    compose.WithInterruptBeforeNodes([]string{"tools"}),
)
```

## Executing with Checkpoint

```go
result, err := runner.Invoke(ctx, input,
    compose.WithCheckPointID("session-123"),
)
```

## Handling Interruption

```go
result, err := runner.Invoke(ctx, input)
if err != nil {
    info, ok := compose.ExtractInterruptInfo(err)
    if ok {
        // Execution was interrupted, save checkpointID for user confirmation
        checkpointID := info.CheckpointID
        // Display info to user, wait for confirmation to continue
    }
}
```

## Resuming Execution

```go
// After user confirms, resume with same checkpointID
result, err := runner.Invoke(ctx, modifiedInput,
    compose.WithCheckPointID("session-123"),
)
```

## Complete Flow

```go
// 1. Create Graph with interruption
g := compose.NewGraph[map[string]any, string]()
g.AddLambdaNode("step1", step1)
g.AddToolsNode("tools", toolsNode)
g.AddEdge(compose.START, "step1")
g.AddEdge("step1", "tools")
g.AddEdge("tools", compose.END)

runner, _ := g.Compile(ctx,
    compose.WithCheckPointStore(store),
    compose.WithInterruptBeforeNodes([]string{"tools"}),
)

// 2. First invocation, triggers interruption
_, err := runner.Invoke(ctx, map[string]any{"query": "test"})
info, _ := compose.ExtractInterruptInfo(err)
checkpointID := info.CheckpointID

// 3. After user confirmation, resume
result, _ := runner.Invoke(ctx, map[string]any{"query": "test"},
    compose.WithCheckPointID(checkpointID),
)
```

## Use Cases

- Human approval required for critical steps
- Long-running Agent tasks
- Interactive user confirmation flows

## Related APIs

- `compose.WithCheckPointStore` - Configure checkpoint store
- `compose.WithInterruptBeforeNodes` - Configure interrupt nodes
- `compose.WithCheckPointID` - Specify checkpoint ID
- `compose.ExtractInterruptInfo` - Extract interruption info from error

## Related Package

- `github.com/cloudwego/eino/compose`
