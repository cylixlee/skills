# Streaming

## Inline Mode

Inline mode reserves a fixed-height widget at the bottom of the terminal and leaves normal terminal output above it. Use it for chat prompts, command palettes, progress widgets, assistants, and tools that should coexist with regular stdout/stderr.

```go
app, err := tui.NewApp(
    tui.WithInlineHeight(5),
    tui.WithRootComponent(App()),
)
```

In inline mode, full-screen overlays are not available by default. Modals require alternate screen behavior.

## Printing Above Inline Widgets

Use `PrintAbove` or `PrintAboveln` when the output line is complete.

```go
app.PrintAbove("Saved %s", path)
app.PrintAboveln("Ready")
```

From goroutines, use queued variants where available in the installed version:

```go
app.QueuePrintAbove("Downloaded %s", name)
app.QueuePrintAboveElement(SummaryView(data))
```

Use element printing when the history should contain styled structured output:

```go
app.PrintAboveElement(ReportCard(report))
```

Inserted elements are rendered into terminal history. They are static output, not interactive mounted components.

## StreamAbove

Use `StreamAbove()` when output arrives incrementally, such as LLM tokens or long-running progress text.

```go
go func() {
    w := app.StreamAbove()
    defer w.Close()

    for token := range tokens {
        fmt.Fprint(w, token)
    }
}()
```

The stream writer is goroutine-safe. It queues terminal output internally. Always close it when the stream finishes so the partial line becomes permanent history.

Only one stream writer is active at a time. Starting another stream finalizes the previous stream.

## Styled Streaming

Use writer helpers for styled text instead of hand-building ANSI escapes when possible.

```go
w := app.StreamAbove()
defer w.Close()

w.WriteStyled("error: ", tui.NewStyle().Bold().Foreground(tui.Red))
w.WriteStyled("request failed\n", tui.NewStyle())
```

Gradient output:

```go
grad := tui.NewGradient(tui.Cyan, tui.Magenta)
w := app.StreamAbove()
defer w.Close()

for _, r := range response {
    w.WriteGradient(string(r), grad)
}
```

Structured output mid-stream:

```go
w.WriteElement(ReportCard(report))
```

`WriteElement` finalizes any partial line and inserts a rendered static view.

## Coordinating Streaming with State

Streaming writes do not update component state. If the UI should show progress, disable input, or show a spinner while streaming, use `QueueUpdate`.

```go
go func() {
    w := app.StreamAbove()
    defer w.Close()

    app.QueueUpdate(func() { streaming.Set(true) })

    for token := range tokens {
        fmt.Fprint(w, token)
        app.QueueUpdate(func() {
            tokenCount.Update(func(v int) int { return v + 1 })
        })
    }

    app.QueueUpdate(func() { streaming.Set(false) })
}()
```

Do not call `State.Set` directly from the streaming goroutine.

## LLM Chat Pattern

Recommended structure for an LLM-style inline app:

- Root component runs with `WithInlineHeight`.
- Prompt input is a built-in `<input />` or `<textarea />` in the reserved widget.
- Submitted user messages are printed above with `PrintAbove` or `PrintAboveElement`.
- Assistant responses stream above with `StreamAbove`.
- Component state tracks input text, streaming status, errors, and cancellation state.
- Background model calls update UI state through `QueueUpdate`.
- Disable submit while streaming unless cancellation is implemented.

Sketch:

```go
func (c *chat) submit(text string) {
    if c.streaming.Get() || strings.TrimSpace(text) == "" {
        return
    }

    c.input.Set("")
    c.app.PrintAbove("You: %s", text)
    c.streaming.Set(true)

    go func() {
        w := c.app.StreamAbove()
        defer w.Close()

        for token := range callModel(text) {
            fmt.Fprint(w, token)
        }

        c.app.QueueUpdate(func() {
            c.streaming.Set(false)
        })
    }()
}
```

## Streaming Pitfalls

- Creating an inline app without `WithInlineHeight`.
- Forgetting to close the writer returned by `StreamAbove()`.
- Updating `State` directly from the streaming goroutine.
- Treating `WriteElement` output as an interactive mounted component.
- Showing modal overlays in inline mode without switching to an alternate screen.
