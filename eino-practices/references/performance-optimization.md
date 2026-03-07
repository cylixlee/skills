# Performance Optimization

This guide covers best practices for optimizing performance in Eino applications.

## Streaming

### Use Streaming for Better UX

Streaming provides better perceived performance by delivering partial results as they become available:

```go
// Instead of Generate, use Stream for real-time responses
stream, err := agent.Stream(ctx, messages)
if err != nil {
    return err
}

defer stream.Close()

for {
    chunk, err := stream.Recv()
    if err == io.EOF {
        break
    }
    if err != nil {
        return err
    }
    // Send chunk to client immediately
    sendToClient(chunk.Content)
}
```

### Streaming in Graph/Workflow

```go
// Graph with streaming nodes
g := compose.NewGraph()

g.AddLambdaNode("generate", compose.StreamableLambda(
    func(ctx context.Context, input string) (*schema.StreamReader[string], error) {
        return llm.Stream(ctx, input)
    },
))

g.AddLambdaNode("process", compose.StreamableLambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (*schema.StreamReader[string], error) {
        reader, writer := schema.Pipe[string](0)
        go func() {
            defer writer.Close()
            for {
                chunk, err := input.Recv()
                if err == io.EOF {
                    break
                }
                // Process chunk immediately
                processed := processChunk(chunk)
                writer.Write(processed)
            }
        }()
        return reader, nil
    },
))

g.AddEdge("generate", "process")

// Stream through entire graph
stream, _ := g.Stream(ctx, "query")
```

## Concurrency

### Parallel Node Execution

Use parallel execution for independent tasks:

```go
g := compose.NewGraph()

// Two independent nodes that can run in parallel
g.AddLambdaNode("search_web", compose.Lambda(searchWeb))
g.AddLambdaNode("search_db", compose.Lambda(searchDB))

// Fan-out to parallel nodes
g.AddEdge("start", "search_web")
g.AddEdge("start", "search_db")

// Fan-in to combine results
g.AddEdge("search_web", "combine")
g.AddEdge("search_db", "combine")
```

### Concurrent Tool Execution

Use concurrent tool execution when tools are independent:

```go
// Instead of sequential
result1, _ := tool1.Call(ctx)
result2, _ := tool2.Call(ctx)

// Use goroutines
resultCh := make(chan string, 2)

go func() {
    result, _ := tool1.Call(ctx)
    resultCh <- result
}()

go func() {
    result, _ := tool2.Call(ctx)
    resultCh <- result
}()

result1 := <-resultCh
result2 := <-resultCh
```

### Batch Processing

For processing multiple inputs, use the Batch node:

```go
import "github.com/cloudwego/eino/compose/batch"

items := []string{"a", "b", "c", "d"}

// Process items in parallel
batchNode := batch.FromLambda(func(ctx context.Context, item string) (string, error) {
    return process(item)
})

results, _ := batchNode.Invoke(ctx, items)
// Results: ["processed_a", "processed_b", "processed_c", "processed_d"]

// Configure concurrency
batchNode := batch.FromLambdaWithOptions(
    func(ctx context.Context, item string) (string, error) {
        return process(item)
    },
    batch.WithConcurrency(10), // Process 10 items concurrently
)
```

## Caching

### Cache ChatModel Responses

```go
// Use caching to avoid redundant LLM calls
cm, _ := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    Model:       "gpt-4o",
    APIKey:      apiKey,
    CacheEnabled: true,
    CacheOptions: &model.CacheOptions{
        TTL: 24 * time.Hour,
    },
})
```

### Custom Caching Middleware

```go
type cacheEntry struct {
    result string
    expiry time.Time
}

var responseCache sync.Map

func cacheMiddleware(next tool.InvokableToolEndpoint) tool.InvokableToolEndpoint {
    return func(ctx context.Context, input *tool.ToolInput) (*tool.ToolOutput, error) {
        cacheKey := fmt.Sprintf("%s:%s", input.Name, input.Arguments)
        
        // Check cache
        if val, ok := responseCache.Load(cacheKey); ok {
            entry := val.(cacheEntry)
            if time.Now().Before(entry.expiry) {
                return &tool.ToolOutput{Result: entry.result}, nil
            }
        }
        
        // Execute tool
        output, err := next(ctx, input)
        if err == nil {
            // Store in cache
            responseCache.Store(cacheKey, cacheEntry{
                result: output.Result,
                expiry: time.Now().Add(1 * time.Hour),
            })
        }
        
        return output, err
    }
}
```

## Connection Pooling

### HTTP Client Configuration

```go
httpClient := &http.Client{
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 100,
        IdleConnTimeout:     90 * time.Second,
    },
    Timeout: 30 * time.Second,
}

cm, _ := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    APIKey:     apiKey,
    HTTPClient: httpClient,
})
```

### Connection Pool for VectorStore

```go
vs, _ := milvus.NewVectorStore(ctx, &milvus.Config{
    Address:     "localhost:19530",
    PoolSize:    100,
    MaxPoolSize: 200,
})
```

## Memory Management

### Stream Processing Memory

```go
// Use buffered pipes for backpressure control
reader, writer := schema.PipeWithBuffer[string](100) // Buffer of 100

go func() {
    defer writer.Close()
    for item := range items {
        // Will block if buffer is full
        writer.Write(item)
    }
}()
```

### Graph State Optimization

```go
g := compose.NewGraph()

// Use WithStreamStatePreHandler for memory-efficient streaming
g.AddLambdaNode("process", compose.Lambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (string, error) {
        // Process stream incrementally
        var result strings.Builder
        for {
            chunk, err := input.Recv()
            if err == io.EOF {
                break
            }
            if err != nil {
                return "", err
            }
            result.WriteString(chunk)
        }
        return result.String(), nil
    },
    compose.WithStreamStatePreHandler(func(ctx context.Context, 
        in *schema.StreamReader[string], state *string) (*schema.StreamReader[string], error) {
        // Stream state pre-processing
        return in, nil
    }),
))
```

## Profiling

### Using pprof

```go
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    go func() {
        http.ListenAndServe(":6060", nil)
    }()
    
    // Your application code
}
```

### Custom Metrics

```go
import "github.com/prometheus/client_golang/prometheus"

var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "request_duration_seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"endpoint", "status"},
    )
    
    activeRequests = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "active_requests",
        },
    )
)

func instrumentedCall(ctx context.Context, fn func() error) error {
    start := time.Now()
    activeRequests.Inc()
    defer func() {
        activeRequests.Dec()
        requestDuration.WithLabelValues("tool", "success").Observe(time.Since(start).Seconds())
    }()
    return fn()
}
```

## Resource Cleanup

### Proper Context Cancellation

```go
func longRunningTask(ctx context.Context) error {
    // Respect context cancellation
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            // Process batch
            err := processBatch(ctx)
            if err != nil {
                return err
            }
        }
    }
}
```

### Closing Resources

```go
stream, _ := agent.Stream(ctx, messages)
defer stream.Close()

// Always handle errors from Close
if err := stream.Close(); err != nil {
    log.Printf("stream close error: %v", err)
}
```

## Configuration Tuning

### Graph Configuration

```go
g := compose.NewGraph(compose.GraphConfig{
    MaxParallelism:    10,    // Limit parallel node execution
    BufferSize:        1024,  // Channel buffer size
    ExecutionTimeout:  5 * time.Minute,
})
```

### Batch Configuration

```go
batchNode := batch.FromLambdaWithOptions(
    processFn,
    batch.WithConcurrency(20),        // Concurrent items
    batch.WithBatchSize(50),          // Items per batch
    batch.WithBatchTimeout(5*time.Second), // Max wait time
)
```

## Related Information

- See also: [stream-processing](stream-processing.md) for streaming best practices
- See also: [batch-processing](batch-processing.md) for batch processing
- See also: [callbacks](callbacks.md) for monitoring
