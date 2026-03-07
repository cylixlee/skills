# Stream Processing

Eino provides comprehensive stream processing capabilities for handling streaming data in Graph and Workflow nodes. Stream processing is essential for real-time applications like chat, live transcription, and event-driven architectures.

## StreamReader

The core type for stream processing is `schema.StreamReader[T]`, which represents a stream of data:

```go
import "github.com/cloudwego/eino/schema"

// Creating a stream
reader := schema.StreamReader[int]
```

### Basic Operations

```go
// Read from stream
chunk, err := reader.Recv()
if err == io.EOF {
    break
}

// Check if stream is done
if reader.Err() != nil {
    return reader.Err()
}

// Get all remaining data
all, err := reader.ReadAll()
```

## StreamableLambda

Use `StreamableLambda` to create nodes that produce streaming output:

```go
import (
    "github.com/cloudwego/eino/compose"
    "github.com/cloudwego/eino/schema"
)

g := compose.NewGraph()

// Create a streaming node
g.AddLambdaNode("stream_processor", compose.StreamableLambda(
    func(ctx context.Context, input string) (*schema.StreamReader[string], error) {
        reader, writer := schema.Pipe[string](0)
        
        go func() {
            defer writer.Close()
            for _, word := range strings.Fields(input) {
                writer.Write(word + " ")
                time.Sleep(100 * time.Millisecond)
            }
        }()
        
        return reader, nil
    },
))
```

## Stream Input/Output in Graph

### Node with Stream Input

```go
g.AddLambdaNode("process_stream", compose.Lambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (string, error) {
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
))
```

### Node with Stream Output

```go
g.AddLambdaNode("stream_output", compose.StreamableLambda(
    func(ctx context.Context, input string) (*schema.StreamReader[string], error) {
        reader, writer := schema.Pipe[string](0)
        
        go func() {
            defer writer.Close()
            for _, c := range input {
                writer.Write(string(c))
            }
        }()
        
        return reader, nil
    },
))
```

### Node with Both Stream Input and Output

```go
g.AddLambdaNode("stream_passthrough", compose.StreamableLambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (*schema.StreamReader[string], error) {
        reader, writer := schema.Pipe[string](0)
        
        go func() {
            defer writer.Close()
            for {
                chunk, err := input.Recv()
                if err == io.EOF {
                    break
                }
                if err != nil {
                    return
                }
                writer.Write(chunk)
            }
        }()
        
        return reader, nil
    },
))
```

## Stream Processing Patterns

### Concat Streams

Combine multiple streams into one:

```go
reader1, _ := schema.Pipe[int](0)
reader2, _ := schema.Pipe[int](0)

go func() {
    defer reader1.Close()
    reader1.Write(1)
    reader1.Write(2)
}()

go func() {
    defer reader2.Close()
    reader2.Write(3)
    reader2.Write(4)
}()

// Concat multiple streams
concatReader := schema.Concat(reader1, reader2)
```

### Merge Streams

Merge streams from multiple sources:

```go
reader, writer := schema.Merge[int](2)

// Producer 1
go func() {
    for i := 0; i < 5; i++ {
        writer.Write(i)
    }
    writer.Close()
}()

// Consumer
for {
    chunk, err := reader.Recv()
    if err == io.EOF {
        break
    }
    fmt.Println(chunk)
}
```

### Transform Stream

Apply transformations to stream data:

```go
import "strings"

g.AddLambdaNode("transform", compose.StreamableLambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (*schema.StreamReader[string], error) {
        reader, writer := schema.Pipe[string](0)
        
        go func() {
            defer writer.Close()
            for {
                chunk, err := input.Recv()
                if err == io.EOF {
                    break
                }
                if err != nil {
                    return
                }
                writer.Write(strings.ToUpper(chunk))
            }
        }()
        
        return reader, nil
    },
))
```

## Streaming with Graph/Workflow

### Streaming in Graph

```go
g := compose.NewGraph()

g.AddLambdaNode("source", compose.StreamableLambda(
    func(ctx context.Context, input int) (*schema.StreamReader[string], error) {
        // Produce streaming output
    },
))

g.AddLambdaNode("processor", compose.StreamableLambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (*schema.StreamReader[string], error) {
        // Process streaming input and output
    },
))

g.AddEdge("source", "processor")

// Invoke with streaming
stream, err := g.Stream(ctx, 42)
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
    fmt.Println(chunk)
}
```

### Streaming in Workflow

```go
wf := compose.NewWorkflow()

wf.AddLambdaNode("source", compose.StreamableLambda(
    func(ctx context.Context, input int) (*schema.StreamReader[string], error) {
        // Produce streaming output
    },
))

wf.AddLambdaNode("processor", compose.StreamableLambda(
    func(ctx context.Context, input *schema.StreamReader[string]) (*schema.StreamReader[string], error) {
        // Process stream
    },
))

wf.AddEdge("source", "processor")

// Execute with streaming
stream, _ := wf.Stream(ctx, 42)
```

## Best Practices

### 1. Always Close Streams

```go
defer stream.Close()
```

### 2. Handle EOF Properly

```go
for {
    chunk, err := stream.Recv()
    if err == io.EOF {
        break
    }
    if err != nil {
        return err
    }
    // Process chunk
}
```

### 3. Use Buffered Pipes for Backpressure

```go
// Create pipe with buffer to handle backpressure
reader, writer := schema.PipeWithBuffer[int](10) // Buffer of 10
```

### 4. Handle Errors in Goroutines

```go
go func() {
    defer writer.Close()
    // ... processing ...
    if err != nil {
        writer.Error(err) // Signal error to reader
    }
}()
```

## Related Information

- Schema package: `github.com/cloudwego/eino/schema`
- See also: [graph-orchestration](graph-orchestration.md), [workflow-usage](workflow-usage.md)
