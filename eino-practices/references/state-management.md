# State Management

Graph provides local state management, allowing state data to be maintained and shared during node execution.

## Creating a Graph with State

```go
type MyState struct {
    Data []string
    Count int
}

g := compose.NewGraph[string, string](compose.WithGenLocalState(func(ctx context.Context) *MyState {
    return &MyState{}
}))
```

## State Handlers

### State Pre Handler

Modify input and update state before node execution:

```go
g.AddLambdaNode("process", handler,
    compose.WithStatePreHandler(func(ctx context.Context, in string, state *MyState) (string, error) {
        state.Data = append(state.Data, in)
        return in, nil
    }),
)
```

### State Post Handler

Modify output and update state after node execution:

```go
g.AddLambdaNode("process", handler,
    compose.WithStatePostHandler(func(ctx context.Context, out string, state *MyState) (string, error) {
        state.Count++
        return out, nil
    }),
)
```

## Complete Example

```go
type CounterState struct {
    History []string
}

g := compose.NewGraph[string, string](compose.WithGenLocalState(func(ctx context.Context) *CounterState {
    return &CounterState{}
}))

g.AddLambdaNode("upper", strings.ToUpper,
    compose.WithStatePreHandler(func(ctx context.Context, in string, state *CounterState) (string, error) {
        state.History = append(state.History, "before:"+in)
        return in, nil
    }),
    compose.WithStatePostHandler(func(ctx context.Context, out string, state *CounterState) (string, error) {
        state.History = append(state.History, "after:"+out)
        return out, nil
    }),
)

g.AddEdge(compose.START, "upper")
g.AddEdge("upper", compose.END)

compiled, _ := g.Compile(ctx)
result, _ := compiled.Invoke(ctx, "hello")
// result: "HELLO"
// State is not persisted across Invoke calls, only shared within a single Invoke
```

## Use Cases

- Accumulating data during multi-node execution flow
- Counting node execution times
- Sharing context information across conditional branches

## Related APIs

- `compose.WithGenLocalState` - Create state generator
- `compose.WithStatePreHandler` - Node pre-execution handler
- `compose.WithStatePostHandler` - Node post-execution handler

## Related Package

- `github.com/cloudwego/eino/compose`
