# Batch Processing

BatchNode enables processing multiple inputs concurrently or sequentially through a Graph or Workflow. It's ideal for scenarios like document review, bulk data processing, and parallel task execution.

**Note**: The batch processing package is available in the [eino-ext](https://github.com/cloudwego/eino-ext) repository.

## Creating a BatchNode

```go
import (
    "github.com/cloudwego/eino-ext/compose/batch"
)

batchNode := batch.NewBatchNode(&batch.NodeConfig[Input, Output]{
    Name:           "BatchProcessor",
    InnerTask:      workflow,  // A Graph or Workflow
    MaxConcurrency: 3,         // 0 = sequential, >0 = concurrent
})
```

## Configuration Options

| Option                | Description                                        |
| --------------------- | -------------------------------------------------- |
| `Name`                | Node identifier                                    |
| `InnerTask`           | The Graph or Workflow to execute for each input    |
| `MaxConcurrency`      | Maximum concurrent tasks (0 = sequential)          |
| `InnerCompileOptions` | Options passed to inner Graph/Workflow compilation |
| `RetryConfig`         | Retry configuration for failed tasks               |

## Basic Usage

### Sequential Processing

```go
// MaxConcurrency = 0 means sequential processing
batchNode := batch.NewBatchNode(&batch.NodeConfig[ReviewRequest, ReviewResult]{
    Name:           "SequentialReviewer",
    InnerTask:      workflow,
    MaxConcurrency: 0,
})

results, err := batchNode.Invoke(ctx, documents)
```

### Concurrent Processing

```go
// MaxConcurrency > 0 enables parallel execution
batchNode := batch.NewBatchNode(&batch.NodeConfig[ReviewRequest, ReviewResult]{
    Name:           "ConcurrentReviewer",
    InnerTask:      workflow,
    MaxConcurrency: 3,  // Up to 3 parallel tasks
})

results, err := batchNode.Invoke(ctx, documents)
```

## Interrupt and Resume

BatchNode supports human-in-the-loop workflows through interruption and resume.

### Interruption Pattern

```go
import (
    "github.com/cloudwego/eino/compose"
)

innerWorkflow := compose.NewWorkflow[ReviewRequest, ReviewResult]()

innerWorkflow.AddLambdaNode("process", compose.InvokableLambda(func(ctx context.Context, req ReviewRequest) (ReviewResult, error) {
    if req.Priority == "high" {
        // Check if interrupted
        wasInterrupted, _, _ := compose.GetInterruptState[any](ctx)
        if !wasInterrupted {
            // First run: interrupt for human review
            return ReviewResult{}, compose.Interrupt(ctx, map[string]string{
                "document_id": req.DocumentID,
                "reason":      "High priority requires approval",
            })
        }
        
        // Resume: check approval decision
        isResumeTarget, hasData, decision := compose.GetResumeContext[*ApprovalDecision](ctx)
        if isResumeTarget && hasData && decision != nil {
            return ReviewResult{
                DocumentID: req.DocumentID,
                Approved:   decision.Approved,
            }, nil
        }
    }
    // Normal processing
    return ReviewResult{Approved: true}, nil
})).AddInput(compose.START)

innerWorkflow.End().AddInput("process")
```

### Resume Pattern

```go
// First invocation - will interrupt for high priority docs
results, err := runner.Invoke(ctx, docs, compose.WithCheckPointID(checkpointID))

if err != nil {
    // Extract interrupt info
    info, ok := compose.ExtractInterruptInfo(err)
    if ok && len(info.InterruptContexts) > 0 {
        // Prepare resume data
        resumeData := make(map[string]any)
        for _, iCtx := range info.InterruptContexts {
            resumeData[iCtx.ID] = &ApprovalDecision{
                Approved: true,
                Comments: "Approved",
            }
        }
        
        // Resume with data
        resumeCtx := compose.BatchResumeWithData(ctx, resumeData)
        results, err = runner.Invoke(resumeCtx, nil, compose.WithCheckPointID(checkpointID))
    }
}
```

## Reduce Pattern

Aggregate batch results into a summary using a parent Graph:

```go
parentGraph := compose.NewGraph[BatchInput, ReviewReport]()

// Preprocess
parentGraph.AddLambdaNode("preprocess", compose.InvokableLambda(func(ctx context.Context, input BatchInput) ([]ReviewRequest, error) {
    return input.Documents, nil
}))

// Batch processing
parentGraph.AddLambdaNode("batch_review", compose.InvokableLambda(func(ctx context.Context, inputs []ReviewRequest) ([]ReviewResult, error) {
    return batchNode.Invoke(ctx, inputs)
}))

// Reduce
parentGraph.AddLambdaNode("reduce", compose.InvokableLambda(func(ctx context.Context, results []ReviewResult) (ReviewReport, error) {
    report := ReviewReport{TotalDocuments: len(results)}
    for _, r := range results {
        if r.Approved {
            report.ApprovedCount++
        }
    }
    return report, nil
}))

parentGraph.AddEdge(compose.START, "preprocess")
parentGraph.AddEdge("preprocess", "batch_review")
parentGraph.AddEdge("batch_review", "reduce")
parentGraph.AddEdge("reduce", compose.END)
```

## Callbacks

Monitor batch execution using callbacks:

```go
import (
    "github.com/cloudwego/eino/callbacks"
)

handler := callbacks.NewHandlerBuilder().
    OnStartFn(func(ctx context.Context, info *callbacks.RunInfo, input callbacks.CallbackInput) context.Context {
        fmt.Printf("Started: %s/%s\n", info.Component, info.Name)
        return ctx
    }).
    OnEndFn(func(ctx context.Context, info *callbacks.RunInfo, output callbacks.CallbackOutput) context.Context {
        fmt.Printf("Ended: %s/%s\n", info.Component, info.Name)
        return ctx
    }).
    Build()

ctxWithCallback := callbacks.InitCallbacks(ctx, nil, handler)
results, err := batchNode.Invoke(ctxWithCallback, docs)
```

## Inner Options

Pass runtime options to inner tasks:

```go
reviewHandler := callbacks.NewHandlerBuilder().
    OnEndFn(func(ctx context.Context, info *callbacks.RunInfo, output callbacks.CallbackOutput) context.Context {
        // Progress tracking
        return ctx
    }).
    Build()

results, err := batchNode.Invoke(ctx, docs,
    batch.WithInnerOptions(compose.WithCallbacks(reviewHandler)))
```

## Type Registration

For interrupt/resume to work, register types:

```go
func init() {
    schema.RegisterName[MyRequest]("myapp.MyRequest")
    schema.RegisterName[MyResult]("myapp.MyResult")
    schema.RegisterName[*ApprovalDecision]("myapp.ApprovalDecision")
}
```

## Related Information

- Batch package: `github.com/cloudwego/eino-ext/compose/batch`
