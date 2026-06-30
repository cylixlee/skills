# Reactivity

## State[T]

`State[T]` stores a reactive value. Changing it marks the app dirty so the next frame re-renders.

```go
type app struct {
    count *tui.State[int]
    name  *tui.State[string]
}

func App() *app {
    return &app{
        count: tui.NewState(0),
        name:  tui.NewState("Alice"),
    }
}
```

Use `Get` in render code and handlers:

```gsx
<span>{fmt.Sprintf("Count: %d", a.count.Get())}</span>
```

Use `Set` or `Update` in event-loop callbacks:

```go
a.count.Set(10)

a.count.Update(func(v int) int {
    return v + 1
})
```

Threading rules:

- `Get()` is safe from any goroutine.
- `Set()` and `Update()` must run on the main event loop.
- Key handlers, mouse handlers, watcher callbacks, and event subscribers run on the main event loop.
- Background goroutines must use `app.QueueUpdate` before mutating state.

## Background Goroutines

If a component launches background work, add an `app *tui.App` field and let generated binding populate it.

```go
type loader struct {
    app     *tui.App
    loading *tui.State[bool]
    result  *tui.State[string]
}

func (l *loader) start() {
    l.loading.Set(true)
    go func() {
        result := fetch()
        l.app.QueueUpdate(func() {
            l.result.Set(result)
            l.loading.Set(false)
        })
    }()
}
```

Use `QueueUpdate` for state and event mutations from goroutines. Do not rely on a mutex around `State.Set`; the UI event loop is the required synchronization point.

## Events[T]

Use `Events[T]` for topic-style notifications when components should communicate without sharing a stored value.

```go
type toast struct {
    messages *tui.Events[string]
    latest   *tui.State[string]
}

func Toast(bus *tui.Events[string]) *toast {
    return &toast{
        messages: bus,
        latest:   tui.NewState(""),
    }
}
```

Subscribe from a component lifecycle hook or constructor pattern used by the project:

```go
func (t *toast) Init() func() {
    unsubscribe := t.messages.Subscribe(func(msg string) {
        t.latest.Set(msg)
    })
    return unsubscribe
}
```

Emit from event-loop callbacks:

```go
notifications.Emit("Saved")
```

From goroutines, wrap `Emit` in `QueueUpdate`.

Choose shared state when components must agree on current data. Choose events when the message is transient, such as notifications, commands, or cross-component signals.

## Watchers

Watchers integrate timers, channels, and state changes into the event loop.

Common patterns:

```go
func (c *clock) Watchers() []tui.Watcher {
    return []tui.Watcher{
        tui.OnTimer(time.Second, func() {
            c.now.Set(time.Now())
        }),
    }
}
```

```go
func (l *logView) Watchers() []tui.Watcher {
    return []tui.Watcher{
        tui.Watch(l.linesCh, func(line string) {
            l.lines.Update(func(lines []string) []string {
                return append(lines, line)
            })
        }),
    }
}
```

```go
func (d *derived) Watchers() []tui.Watcher {
    return []tui.Watcher{
        tui.OnChange(d.source, func(value string) {
            d.upper.Set(strings.ToUpper(value))
        }),
    }
}
```

Watcher callbacks run on the event loop, so direct state mutation is allowed there.

## Batching

Use `app.Batch(func(){ ... })` when several state changes should update bindings as one logical change.

```go
app.Batch(func() {
    firstName.Set("Alice")
    lastName.Set("Smith")
    age.Set(30)
})
```

Batching reduces intermediate binding work. It does not make background goroutine mutation safe; goroutines still need `QueueUpdate`.

## Reactivity Checklist

- State mutations happen on the event loop.
- Background goroutines use `QueueUpdate`.
- Watcher callbacks mutate state directly because they already run on the event loop.
- Event buses are used for transient messages, not as hidden shared state.
- Shared `*tui.State[T]` is used when multiple components must agree on current data.
- Custom `BindApp` calls generated `bindAppFields(app)` before custom work.
