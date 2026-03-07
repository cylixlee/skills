# Human-in-the-Loop

Human-in-the-Loop (HITL) enables human collaboration in Agent execution flows. Eino supports multiple interaction patterns through checkpoint/interruption and event handling mechanisms.

## Patterns Overview

| Pattern           | Description                                   |
| ----------------- | --------------------------------------------- |
| **Approval**      | Wait for human approval before Agent executes |
| **Review**        | Human reviews after Agent execution           |
| **Feedback Loop** | Adjust execution based on human feedback      |

## Implementation Using Interruption

Eino provides interruption capabilities that can be used to implement human approval workflows.

### Using Graph Interruption

You can configure interrupt nodes in a Graph to pause execution and wait for human input:

```go
import (
    "github.com/cloudwego/eino/compose"
    "github.com/cloudwego/eino/adk"
)

// Configure interruption before specific nodes
runner, err := graph.Compile(ctx,
    compose.WithCheckPointStore(store),
    compose.WithInterruptBeforeNodes([]string{"execute_operation"}),
)

// Invoke and handle interruption
_, err = runner.Invoke(ctx, input)
if err != nil {
    info, ok := compose.ExtractInterruptInfo(err)
    if ok {
        // Display info to user and wait for confirmation
        checkpointID := info.CheckpointID
        
        // Get user approval (implementation depends on your application)
        approved := getUserApproval(info)
        
        if approved {
            // Resume with approval data using context
            resumeCtx := compose.ResumeWithData(ctx, info.InterruptContexts[0].ID, map[string]any{
                "approved": true,
            })
            result, _ = runner.Invoke(resumeCtx, input, 
                compose.WithCheckPointID(checkpointID),
            )
        }
    }
}
```

### Creating Approval Tool

You can create a custom approval tool that uses interruption:

```go
import (
    "github.com/cloudwego/eino/components/tool"
    "github.com/cloudwego/eino/schema"
)

type ApprovalTool struct{}

func (t *ApprovalTool) Info(ctx context.Context) (*schema.ToolInfo, error) {
    return &schema.ToolInfo{
        Name: "request_approval",
        Desc: "Request human approval for an operation",
        Parameters: schema.NewParamsOneOfByParams(map[string]*schema.ParameterInfo{
            "operation": {Type: "string", Desc: "The operation to approve", Required: true},
            "details": {Type: "string", Desc: "Additional details about the operation"},
        }),
    }, nil
}

func (t *ApprovalTool) InvokableRun(ctx context.Context, argumentsInJSON string, opts ...tool.Option) (string, error) {
    // Parse arguments
    var args struct {
        Operation string `json:"operation"`
        Details   string `json:"details"`
    }
    if err := json.Unmarshal([]byte(argumentsInJSON), &args); err != nil {
        return "", err
    }
    
    // Interrupt for human approval
    return "", compose.Interrupt(ctx, map[string]any{
        "operation": args.Operation,
        "details":   args.Details,
    })
}
```

### Using in ReAct Agent

```go
// Create approval tool
approvalTool := &ApprovalTool{}

// Create ReAct Agent with the tool
agent, err := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{approvalTool, otherTool},
    },
})
```

## Using with ADK Runner

You can implement human-in-the-loop by handling events from the Runner:

```go
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent:            agent,
    EnableStreaming:  true,
})

events := runner.Query(ctx, "Execute operation")
for {
    event, ok := events.Next()
    if !ok {
        break
    }
    
    // Handle tool calls that need human input
    if event.Action != nil && event.Action.ToolCall != nil {
        toolName := event.Action.ToolCall.Name
        if toolName == "request_approval" {
            // Wait for human input
            approved := waitForHumanInput()
            
            // Submit tool result with approval decision
            // (Implementation depends on your event handling)
        }
    }
    
    // Handle message output
    if event.Output != nil && event.Output.MessageOutput != nil {
        msg := event.Output.MessageOutput.Message
        fmt.Printf("Assistant: %s\n", msg.Content)
    }
}
```

## Review Mode Pattern

Implement review mode by using interruption after tool execution:

```go
// Create a review tool that reviews output
reviewTool := &ReviewTool{
    onAccept: func(result string) error {
        // Handle accepted result
        return nil
    },
    onReject: func(result string, reason string) error {
        // Handle rejected result
        return nil
    },
}

agent, err := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{reviewTool, processTool},
    },
})
```

## Feedback Loop Pattern

Implement feedback loops by capturing intermediate results and allowing modifications:

```go
// Use session values to track feedback
func feedbackToolInvokableRun(ctx context.Context, argumentsInJSON string, opts ...tool.Option) (string, error) {
    // Get previous result from session
    prevResult, _ := adk.GetSessionValue[string](ctx, "current_result")
    
    // Request feedback
    feedback := requestUserFeedback(prevResult)
    
    // Store feedback in session for next iteration
    adk.AddSessionValue(ctx, "user_feedback", feedback)
    
    return feedback, nil
}
```

## Complete Example: Approval Flow

```go
package main

import (
    "context"
    "fmt"

    "github.com/cloudwego/eino/adk"
    "github.com/cloudwego/eino/compose"
    "github.com/cloudwego/eino/components/model/openai"
    "github.com/cloudwego/eino/components/tool"
    "github.com/cloudwego/eino/flow/agent/react"
    "github.com/cloudwego/eino/schema"
)

type ApprovalTool struct{}

func (t *ApprovalTool) Info(ctx context.Context) (*schema.ToolInfo, error) {
    return &schema.ToolInfo{
        Name: "request_approval",
        Desc: "Request human approval for executing an operation",
        Parameters: schema.NewParamsOneOfByParams(map[string]*schema.ParameterInfo{
            "operation": {Type: "string", Desc: "Operation description", Required: true},
        }),
    }, nil
}

func (t *ApprovalTool) InvokableRun(ctx context.Context, argumentsInJSON string, opts ...tool.Option) (string, error) {
    return "", compose.Interrupt(ctx, map[string]any{
        "operation": "execute_critical_action",
    })
}

func main() {
    ctx := context.Background()

    // Create ChatModel
    cm, _ := openai.NewChatModel(ctx, &openai.ChatModelConfig{
        Model:  "gpt-4o",
        APIKey: "your-api-key",
    })

    // Create approval tool
    approvalTool := &ApprovalTool{}

    // Create ReAct Agent
    agent, _ := react.NewAgent(ctx, &react.AgentConfig{
        ToolCallingModel: cm,
        ToolsConfig: compose.ToolsNodeConfig{
            Tools: []tool.BaseTool{approvalTool},
        },
    })

    // Create Runner with checkpoint store
    runner := adk.NewRunner(ctx, adk.RunnerConfig{
        Agent: agent,
    })

    // Run and handle interruptions
    events := runner.Query(ctx, "Please approve executing a critical operation")
    
    for {
        event, ok := events.Next()
        if !ok {
            break
        }
        
        if event.Err != nil {
            // Check for interruption
            info, ok := compose.ExtractInterruptInfo(event.Err)
            if ok {
                fmt.Printf("Operation requires approval: %+v\n", info)
                // In real application, get user approval and resume
            }
        }
        
        if msg, _ := event.Output.MessageOutput.GetMessage(); msg != nil {
            fmt.Printf("Response: %s\n", msg.Content)
        }
    }
}
```

## Use Cases

- Critical operation confirmation
- Content moderation
- Quality assurance workflows
- Interactive debugging

## Related Information

- Checkpoint and interruption: [checkpoint-interrupt](checkpoint-interrupt.md)
- ADK framework: [adk-framework](adk-framework.md)
- Related packages: `github.com/cloudwego/eino/compose`, `github.com/cloudwego/eino/adk`
