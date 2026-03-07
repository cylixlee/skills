# Multi-Agent Collaboration

Eino supports building multi-Agent systems, coordinating multiple sub-Agents through Supervisor to complete tasks.

## Supervisor Pattern

Supervisor is a special Agent responsible for coordinating sub-Agent execution.

```go
import (
    "github.com/cloudwego/eino/adk"
    "github.com/cloudwego/eino/adk/multiagent/supervisor"
)
```

## Creating Sub-Agents

```go
// Create search Agent
searchAgent, _ := buildSearchAgent(ctx)

// Create math Agent
mathAgent, _ := buildMathAgent(ctx)

// Create coordinator Agent (Supervisor)
supervisorAgent, _ := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "supervisor",
    Description: "Coordinates other Agents",
    Instruction: `You are a coordinator. Based on user questions, select the appropriate Agent to handle.
    - Use search_agent for searching information
    - Use math_agent for math calculations`,
    Model: model,
})
```

## Configuring Supervisor

```go
sv, err := supervisor.New(ctx, &supervisor.Config{
    Supervisor: supervisorAgent,
    SubAgents:  []adk.Agent{searchAgent, mathAgent},
})
```

## Complete Example

```go
func buildSearchAgent(ctx context.Context) (adk.Agent, error) {
    return adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
        Name:        "search_agent",
        Description: "Search information",
        Instruction: "You are a search assistant. Use search tools to find information.",
        Model:       model,
    })
}

func buildMathAgent(ctx context.Context) (adk.Agent, error) {
    return adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
        Name:        "math_agent",
        Description: "Math calculations",
        Instruction: "You are a math assistant. Perform mathematical calculations.",
        Model:       model,
    })
}

// Compose
ctx := context.Background()
searchAgent, _ := buildSearchAgent(ctx)
mathAgent, _ := buildMathAgent(ctx)

sv, _ := supervisor.New(ctx, &supervisor.Config{
    Supervisor: supervisorAgent,
    SubAgents:  []adk.Agent{searchAgent, mathAgent},
})

// Run
runner := adk.NewRunner(ctx, adk.RunnerConfig{
    Agent: sv,
})

events := runner.Query(ctx, "Search for Go language info and calculate 100 squared")
```

## ADK Agent Types

| Type                 | Description                           |
| -------------------- | ------------------------------------- |
| **ChatModelAgent**   | Simple Agent based on ChatModel       |
| **Loop Agent**       | Agent that executes in a loop         |
| **Parallel Agent**   | Executes multiple Agents in parallel  |
| **Sequential Agent** | Executes multiple Agents sequentially |

## Plan-Execute-Replan Pattern

This pattern separates planning from execution, with a replanner to adjust plans:

```go
import "github.com/cloudwego/eino/adk/multiagent/planexecute"
```

### Creating the Agent

```go
entryAgent, err := planexecute.New(ctx, &planexecute.Config{
    Planner:   planAgent,    // Creates execution plan
    Executor: execAgent,    // Executes plan steps
    Replanner: replanAgent, // Adjusts plan if needed
    MaxIterations: 20,
})
```

### Plan Agent

```go
planAgent := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "planner",
    Description: "Creates execution plans",
    Instruction: `Given a task, create a step-by-step plan.
    Output format: JSON array of steps with "description" and "status" fields.`,
    Model:       model,
    Tools:       availableTools,
})
```

### Executor Agent

```go
execAgent := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "executor",
    Description: "Executes plan steps",
    Instruction: `Execute the given step and report the result.`,
    Model:       model,
    Tools:       availableTools,
})
```

### Replanner Agent

```go
replanAgent := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "replanner",
    Description: "Evaluates and adjusts plans",
    Instruction: `Evaluate if the current plan is still valid.
    If not, create a revised plan.`,
    Model: model,
})
```

### Complete Example

```go
planAgent := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "planner",
    Instruction: "Create a step-by-step plan. Return JSON array.",
    Model:       model,
})

execAgent := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "executor",
    Instruction: "Execute the given step.",
    Model:       model,
    Tools:       tools,
})

replanAgent := adk.NewChatModelAgent(ctx, &adk.ChatModelAgentConfig{
    Name:        "replanner",
    Instruction: "Review results, revise plan if needed.",
    Model:       model,
})

entryAgent, _ := planexecute.New(ctx, &planexecute.Config{
    Planner:       planAgent,
    Executor:      execAgent,
    Replanner:     replanAgent,
    MaxIterations: 10,
})

runner := adk.NewRunner(ctx, adk.RunnerConfig{Agent: entryAgent})
events := runner.Query(ctx, "Research and summarize Go language")
```

## Loop Agent

Executes multiple agents in a loop until condition is met:

```go
import "github.com/cloudwego/eino/adk/multiagent/loop"

loopAgent, err := loop.New(ctx, &loop.Config{
    Body:    sequentialAgent,
    Condition: func(ctx context.Context, state map[string]any) (bool, error) {
        done := state["done"].(bool)
        return !done, nil
    },
})
```

## Parallel Agent

Executes multiple agents concurrently:

```go
import "github.com/cloudwego/eino/adk/multiagent/parallel"

parallelAgent, err := parallel.New(ctx, &parallel.Config{
    Nodes: map[string]adk.Agent{
        "search": searchAgent,
        "math":   mathAgent,
    },
    Aggregation: "merge",  // or "first"
})
```

## Sequential Agent

Executes agents one after another:

```go
import "github.com/cloudwego/eino/adk/multiagent/sequential"

seqAgent, err := sequential.New(ctx, &sequential.Config{
    Nodes: []adk.Agent{
        researcherAgent,
        writerAgent,
        reviewerAgent,
    },
})
```

## Related Information

- Core packages: `github.com/cloudwego/eino/adk`, `github.com/cloudwego/eino/adk/multiagent`
