# Error Handling Best Practices

Proper error handling is crucial for building robust AI applications. This guide covers common error scenarios and best practices for handling them in Eino applications.

## Common Error Types

### 1. ChatModel Errors

```go
import "github.com/cloudwego/eino/components/model"

// Handle API errors
messages := []*schema.Message{
    schema.UserMessage("Hello"),
}

result, err := cm.Generate(ctx, messages)
if err != nil {
    var apiErr *model.APIError
    if errors.As(err, &apiErr) {
        switch apiErr.Code {
        case model.RateLimitError:
            // Implement retry with backoff
            return retryWithBackoff(ctx)
        case model.AuthenticationError:
            // Check API key
            return fmt.Errorf("authentication failed: %w", err)
        case model.QuotaExceededError:
            // Handle quota
            return fmt.Errorf("quota exceeded: %w", err)
        default:
            return err
        }
    }
    return err
}
```

### 2. Tool Invocation Errors

Tool functions should return meaningful error messages:

```go
func myTool(ctx context.Context, input *MyInput) (string, error) {
    if input == nil {
        return "", fmt.Errorf("input is required")
    }
    
    if input.Query == "" {
        return "", fmt.Errorf("query cannot be empty")
    }
    
    result, err := externalService.Call(input.Query)
    if err != nil {
        // Provide context in error message
        return "", fmt.Errorf("external service failed: %w", err)
    }
    
    return result, nil
}
```

### 3. JSON Parsing Errors

Handle LLM response parsing errors gracefully:

```go
type ToolInput struct {
    Action  string `json:"action"`
    Target  string `json:"target"`
}

func toolHandler(ctx context.Context, input string) (string, error) {
    var parsed ToolInput
    if err := json.Unmarshal([]byte(input), &parsed); err != nil {
        // Use errorremover middleware to clean malformed JSON
        return "", fmt.Errorf("failed to parse tool arguments: %w", err)
    }
    
    // Process valid input
    return processAction(parsed)
}
```

### 4. Stream Errors

Handle streaming errors properly:

```go
stream, err := agent.Stream(ctx, messages)
if err != nil {
    return err
}

defer stream.Close()

for {
    chunk, err := stream.Recv()
    if err != nil {
        if err == io.EOF {
            break
        }
        // Handle stream errors
        return fmt.Errorf("stream error: %w", err)
    }
    // Process chunk
}
```

## Error Handling Strategies

### 1. Retry with Backoff

```go
func retryWithBackoff(ctx context.Context, fn func() error) error {
    maxRetries := 3
    baseDelay := time.Second
    
    var err error
    for i := 0; i < maxRetries; i++ {
        err = fn()
        if err == nil {
            return nil
        }
        
        delay := baseDelay * time.Duration(math.Pow(2, float64(i)))
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(delay):
        }
    }
    
    return fmt.Errorf("max retries exceeded: %w", err)
}
```

### 2. Using Middleware for Error Handling

```go
import "github.com/cloudwego/eino/compose"

tool, _ := utils.InferTool("my_tool", "description",
    func(ctx context.Context, input Input) (string, error) {
        // Tool implementation
    },
)

// Use errorremover middleware for JSON robustness
toolWithMiddleware := compose.InvokableToolMiddleware(
    func(next compose.InvokableToolEndpoint) compose.InvokableToolEndpoint {
        return func(ctx context.Context, input *compose.ToolInput) (*compose.InvokableToolOutput, error) {
            output, err := next(ctx, input)
            if err != nil {
                // Log error but don't expose internal details
                log.Printf("tool error: %v", err)
                return &compose.InvokableToolOutput{
                    Result: "An error occurred. Please try again.",
                }, nil
            }
            return output, nil
        }
    },
)(tool)
```

### 3. Graph Error Handling

```go
g := compose.NewGraph()

g.AddLambdaNode("step1", compose.Lambda(
    func(ctx context.Context, input string) (string, error) {
        // Step that might fail
        result, err := riskyOperation(input)
        if err != nil {
            return "", fmt.Errorf("step1 failed: %w", err)
        }
        return result, nil
    },
))

g.AddLambdaNode("fallback", compose.Lambda(
    func(ctx context.Context, input string) (string, error) {
        // Fallback logic
        return "fallback result", nil
    },
))

// Use conditional edges for error handling
g.AddEdge("step1", "fallback")
```

### 4. Error Recovery in Agents

```go
agent, _ := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{riskyTool},
    },
})

messages := []*schema.Message{
    schema.UserMessage("your query"),
}

result, err := agent.Generate(ctx, messages)
if err != nil {
    // Implement fallback strategy
    return handleAgentFailure(ctx, cm, messages)
}
```

## Best Practices

### 1. Wrap Errors with Context

```go
// Good
return "", fmt.Errorf("failed to process request: %w", err)

// Bad
return "", err
```

### 2. Don't Expose Internal Errors to Users

```go
// Good - user-friendly message
return "Sorry, I encountered an error processing your request.", nil

// Bad - exposes internal details
return "", fmt.Errorf("database connection failed: %s", err)
```

### 3. Log Errors for Debugging

```go
import "log"

func toolHandler(ctx context.Context, input string) (string, error) {
    result, err := process(input)
    if err != nil {
        log.Printf("tool handler error: input=%s, err=%v", input, err)
        return "", err
    }
    return result, nil
}
```

### 4. Use Typed Errors

```go
var (
    ErrInvalidInput   = errors.New("invalid input")
    ErrRateLimited    = errors.New("rate limited")
    ErrAuthentication = errors.New("authentication failed")
)

func toolHandler(ctx context.Context, input Input) (string, error) {
    if !validate(input) {
        return "", ErrInvalidInput
    }
    // ...
}
```

### 5. Handle Timeouts

```go
ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
defer cancel()

messages := []*schema.Message{
    schema.UserMessage("your query"),
}

result, err := agent.Generate(ctx, messages)
if err != nil {
    if errors.Is(err, context.DeadlineExceeded) {
        return "", fmt.Errorf("request timed out")
    }
    return "", err
}
```

## Related Information

- See also: [callbacks](callbacks.md) for error monitoring
- See also: [checkpoint-interrupt](checkpoint-interrupt.md) for long-running task error handling
