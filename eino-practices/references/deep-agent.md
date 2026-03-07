# Deep Agent

Deep Agent is a pre-built agent in the ADK framework that specializes in complex task orchestration. It uses a task decomposition approach to break down complex problems into manageable sub-tasks, executing them with built-in TODO management and sub-agent coordination.

## Key Features

- **Task Decomposition**: Automatically breaks complex tasks into smaller, executable sub-tasks
- **TODO Management**: Built-in TODO tool for tracking task progress
- **Sub-Agent Support**: Can coordinate specialized sub-agents for specific domains
- **General-Purpose Sub-Agent**: Includes a built-in general agent for handling arbitrary tasks

## Creating a Deep Agent

```go
import (
    "context"
    "github.com/cloudwego/eino/adk"
    "github.com/cloudwego/eino/adk/prebuilt/deep"
    "github.com/cloudwego/eino/components/model"
)

ctx := context.Background()

// Create ChatModel
cm, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{
    Model:  "gpt-4o",
    APIKey: "your-api-key",
})

// Create Deep Agent
agent, err := deep.New(ctx, &deep.Config{
    Name:        "deep_assistant",
    Description: "A powerful assistant for complex task orchestration",
    ChatModel:  cm,
})
```

## Configuration Options

| Option                   | Type                       | Description                                  |
| ------------------------ | -------------------------- | -------------------------------------------- |
| `Name`                   | string                     | Agent identifier                             |
| `Description`            | string                     | Description for supervisor selection         |
| `ChatModel`              | model.ToolCallingChatModel | LLM for reasoning and execution              |
| `Instruction`            | string                     | Custom system prompt (uses default if empty) |
| `SubAgents`              | []adk.Agent                | Specialized agents for specific tasks        |
| `ToolsConfig`            | adk.ToolsConfig            | Additional tools available to the agent      |
| `MaxIteration`           | int                        | Maximum reasoning iterations                 |
| `WithoutWriteTodos`      | bool                       | Disable built-in TODO management             |
| `WithoutGeneralSubAgent` | bool                       | Disable built-in general-purpose sub-agent   |
| `OutputKey`              | string                     | Key to store final output in session         |

## Using Sub-Agents

Deep Agent can coordinate specialized sub-agents for different domains:

```go
// Create specialized sub-agents
researchAgent, _ := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{searchTool},
    },
})

codeAgent, _ := react.NewAgent(ctx, &react.AgentConfig{
    ToolCallingModel: cm,
    ToolsConfig: compose.ToolsNodeConfig{
        Tools: []tool.BaseTool{codeExecutionTool},
    },
})

// Create Deep Agent with sub-agents
deepAgent, _ := deep.New(ctx, &deep.Config{
    Name:        "multi_domain_assistant",
    Description: "Handles research and coding tasks",
    ChatModel:   cm,
    SubAgents:   []adk.Agent{researchAgent, codeAgent},
})
```

## TODO Management

Deep Agent includes a built-in `write_todos` tool for task tracking:

```go
// The agent will automatically use TODO management
// You can access TODO state through session values
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent: deepAgent,
})

events := runner.Query(ctx, "Research and implement a sorting algorithm")

for {
    event, ok := events.Next()
    if !ok {
        break
    }
    // Access TODO state if needed
    todos, _ := adk.GetSessionValue[](ctx, "todos")
}
```

To disable TODO management:

```go
deepAgent, _ := deep.New(ctx, &deep.Config{
    Name:               "simple_assistant",
    ChatModel:          cm,
    WithoutWriteTodos:  true,
})
```

## Custom Task Tool Description

You can customize how sub-agents are presented to the main agent:

```go
deepAgent, _ := deep.New(ctx, &deep.Config{
    Name:        "custom_assistant",
    ChatModel:   cm,
    SubAgents:   []adk.Agent{specializedAgent},
    TaskToolDescriptionGenerator: func(ctx context.Context, availableAgents []adk.Agent) (string, error) {
        return "You have access to specialized agents for data analysis.", nil
    },
})
```

## Complete Example

```go
package main

import (
    "context"
    "fmt"

    "github.com/cloudwego/eino/adk"
    "github.com/cloudwego/eino/adk/prebuilt/deep"
    "github.com/cloudwego/eino/components/tool"
    "github.com/cloudwego/eino/components/tool/utils"
    "github.com/cloudwego/eino/schema"
)

type CalculatorInput struct {
    Expression string `json:"expression"`
}

func main() {
    ctx := context.Background()

    // Create ChatModel
    cm, _ := openai.NewChatModel(ctx, &openai.ChatModelConfig{
        Model:  "gpt-4o",
        APIKey: "your-api-key",
    })

    // Create a calculator tool
    calcTool, _ := utils.InferTool[CalculatorInput, string]("calculator", "Performs mathematical calculations",
        func(ctx context.Context, input CalculatorInput) (string, error) {
            // Simple calculation logic
            return fmt.Sprintf("Calculated: %s", input.Expression), nil
        })

    // Create Deep Agent
    agent, _ := deep.New(ctx, &deep.Config{
        Name:        "math_assistant",
        Description: "Helps with mathematical problems",
        ChatModel:   cm,
        ToolsConfig: adk.ToolsConfig{
            Tools: []tool.BaseTool{calcTool},
        },
    })

    // Run with Runner
    runner := adk.NewRunner(ctx, adk.RunnerConfig{
        Agent:           agent,
        EnableStreaming: true,
    })

    events := runner.Query(ctx, "Calculate the square root of 144 and explain the result")
    for {
        event, ok := events.Next()
        if !ok {
            break
        }
        if msg, _ := event.Output.MessageOutput.GetMessage(); msg != nil {
            fmt.Println(msg.Content)
        }
    }
}
```

## Related Information

- Core package: `github.com/cloudwego/eino/adk/prebuilt/deep`
- See also: [adk-framework](adk-framework.md), [react-agent](react-agent.md), [multi-agent](multi-agent.md)
