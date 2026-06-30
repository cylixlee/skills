# Components

## GSX File Shape

`.gsx` files are Go source files with `templ` declarations for terminal UI. They use normal packages, imports, types, functions, methods, and Go expressions.

```gsx
package main

import (
    "fmt"

    tui "github.com/grindlemire/go-tui"
)

templ Greeting(name string) {
    <span class="text-cyan font-bold">{"Hello, " + name}</span>
}
```

GSX supports HTML-like elements, attributes, Go control flow, local element bindings, and component calls.

```gsx
templ List(items []string, selected int) {
    <div class="flex-col gap-1">
        for i, item := range items {
            if i == selected {
                <span class="text-cyan font-bold">{fmt.Sprintf("> %s", item)}</span>
            } else {
                <span class="font-dim">{"  " + item}</span>
            }
        }
    </div>
}
```

## Pure Components

Use pure components for stateless, reusable visual fragments.

```gsx
templ Card(title string) {
    <div class="border-rounded p-1 flex-col gap-1">
        <span class="font-bold">{title}</span>
        {children...}
    </div>
}

templ AppView() {
    @Card("Status") {
        <span class="text-green">Ready</span>
    }
}
```

Choose pure components for labels, badges, rows, panels, repeated layout wrappers, and static display fragments. They should not own `State`, refs, watchers, or key handlers.

## Struct Components

Use struct components for interactive or stateful UI. The `Render` method is written as a `templ` method.

```gsx
type counter struct {
    count *tui.State[int]
}

func Counter() *counter {
    return &counter{count: tui.NewState(0)}
}

func (c *counter) KeyMap() tui.KeyMap {
    return tui.KeyMap{
        tui.On(tui.Rune('+'), func(ke tui.KeyEvent) {
            c.count.Update(func(v int) int { return v + 1 })
        }),
        tui.On(tui.Rune('q'), func(ke tui.KeyEvent) { ke.App().Stop() }),
    }
}

templ (c *counter) Render() {
    <div class="flex-col items-center justify-center h-full">
        <span>{fmt.Sprintf("Count: %d", c.count.Get())}</span>
    </div>
}
```

Choose struct components when the component needs state, events, refs, key handling, mouse handling, timers, lifecycle hooks, async work, or app access.

## Children

Pure components can use `{children...}` directly. Struct components with children usually store `children []*tui.Element` and accept children as the last constructor argument.

```gsx
type panel struct {
    title    string
    children []*tui.Element
}

func Panel(title string, children []*tui.Element) *panel {
    return &panel{title: title, children: children}
}

templ (p *panel) Render() {
    <div class="border-rounded p-1 flex-col gap-1">
        <span class="font-bold">{p.title}</span>
        {children...}
    </div>
}
```

Render with a children block:

```gsx
@Panel("Details") {
    <span>Line one</span>
    <span>Line two</span>
}
```

## Control Flow and Expressions

Use Go expressions in braces:

```gsx
<span>{fmt.Sprintf("%d items", len(items))}</span>
<span class={statusClass(ok)}>Status</span>
<div width={20} height={5} flexGrow={1}>Content</div>
```

Local element binding is useful for repeated fragments in one render method:

```gsx
badge := <span class="text-cyan font-bold">{label}</span>
<div class="gap-1">{badge}{badge}</div>
```

The right side of a local element binding must be an element, not an arbitrary Go value.

## File Organization

Multiple `.gsx` files in the same package can call each other's components without extra imports.

```text
myapp/
  main.go
  app.gsx
  sidebar.gsx
  content.gsx
  input.gsx
```

Split files when a struct component has its own state, key map, refs, or lifecycle. Keep small pure components near the parent if they are only used there.

## Mounting and Cached Children

When a struct component renders another struct component with `@Child(args)`, generated code mounts and caches the child instance. The child keeps local state across parent re-renders.

```gsx
templ (a *app) Render() {
    <div class="h-full">
        @Sidebar(a.selected)
        @Content(a.selected)
    </div>
}
```

Do not call `app.Mount` manually in normal application code. Write component calls in GSX and let the generated code manage cache keys, binding, cleanup, and props updates.

Inside loops, stable keys matter when component identity matters. Prefer a real item ID where supported by the local project pattern instead of relying only on changing indexes.

## Props and Generated UpdateProps

Mounted struct components are cached. On later renders, generated code can update non-state props from a fresh instance without losing local state.

Practical rule:

- Pass shared reactive values as `*tui.State[T]` when parent and child must both observe changes.
- Pass simple props such as titles, IDs, widths, and options normally.
- Keep local state fields as `*tui.State[T]` initialized in the child constructor.
- Match the installed version and project pattern if manual `PropsUpdater` code exists.

## BindApp and App Access

Generated code binds `*tui.State`, `*tui.Events`, and `app *tui.App` fields on mounted struct components.

```go
type downloader struct {
    app      *tui.App
    progress *tui.State[int]
}
```

Do not write custom `BindApp` unless there is a concrete need. If you do, call the generated helper first:

```go
func (d *downloader) BindApp(app *tui.App) {
    d.bindAppFields(app)
    // custom binding logic
}
```

Skipping `bindAppFields` can leave state or event fields unbound.

## Lifecycle Hooks

Struct components may implement lifecycle methods used by the framework. Match names and signatures used by the installed version.

Common patterns:

```go
func (c *component) Init() func() {
    // start timers, subscribe, allocate resources
    return func() {
        // cleanup when unmounted
    }
}
```

Use lifecycle hooks for subscriptions, timers, and external resources. Prefer watchers for channel and timer integration when they fit.

## Component Design Rules

- Start with one root struct component, then split only when a child owns behavior or repeated UI is genuinely reusable.
- Keep rendering declarative. Compute display values from state in `Render` instead of mutating state while rendering.
- Do not start goroutines from `Render`; use constructors, handlers, watchers, or lifecycle hooks.
- Use pure components to avoid repeating class strings and small layout fragments.
- Use struct components for anything with `KeyMap`, `HandleMouse`, refs, `State`, `Events`, or watchers.
- Do not over-abstract one-off terminal markup before layout and behavior are stable.
