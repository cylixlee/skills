# Workflow Usage

Workflow is Eino's workflow orchestration approach, lighter than Graph and supports field mapping.

## Creating a Workflow

```go
import "github.com/cloudwego/eino/compose"

wf := compose.NewWorkflow[map[string]any, map[string]any]()
```

## Adding Nodes

```go
// Lambda node
wf.AddLambdaNode("step1", compose.InvokableLambda(func(ctx context.Context, input map[string]any) (map[string]any, error) {
    return map[string]any{"result": input["value"].(int) * 2}, nil
}))

// Graph subgraph
subGraph := compose.NewGraph[map[string]any, map[string]any]()
// ... configure subGraph
wf.AddGraphNode("sub", subGraph)
```

## Field Mapping

Workflow supports input/output field mapping through the WorkflowNode's AddInput method:

```go
// Create lambda node and get the node reference
step1Node := wf.AddLambdaNode("step1", lambda1)

// Map input field to step1 input field
// Map specific field from input to node input
step1Node.AddInput(compose.START, compose.MapFields("input_field", "step1_input_field"))

// Map step1 output field to final output
wf.End().AddInput("step1", compose.MapFields("result", "output_field"))
```

## Chain Usage

Chain is simple sequential chaining:

```go
chain := compose.NewChain[map[string]any, string]()

chain.
    AppendLambda(lambda1).
    AppendBranch(branch).
    AppendParallel(parallelNode).
    AppendGraph(subGraph).
    AppendLambda(lambda2)

// Invoke
result, _ := chain.Invoke(ctx, input)
```

## Branch (Conditional)

```go
branchCond := func(ctx context.Context, input map[string]any) (string, error) {
    if input["n"].(int) < 10 {
        return "small", nil
    }
    return "large", nil
}

branch := compose.NewChainBranch(branchCond).
    AddLambda("small", lambdaForSmall).
    AddLambda("large", lambdaForLarge)

chain.AppendBranch(branch)
```

## Parallel (Parallel Execution)

```go
parallel := compose.NewParallel[map[string]any, map[string]any]()
parallel.AddNode("p1", lambda1)
parallel.AddNode("p2", lambda2)
parallel.AddEndNode("final", compose.InvokableLambda(func(ctx context.Context, input map[string]any) (map[string]any, error) {
    // Aggregate results from p1 and p2
    return input, nil
}))

chain.AppendParallel(parallel)
```

## Difference from Graph

| Feature            | Graph                  | Workflow               |
| ------------------ | ---------------------- | ---------------------- |
| Use Case           | Complex flow control   | Simple linear flows    |
| Field Mapping      | Not supported          | Supported              |
| Conditional Branch | Supported              | Supported via Branch   |
| Parallel Execution | Not directly supported | Supported via Parallel |

## Related Information

- Core package: `github.com/cloudwego/eino/compose`
