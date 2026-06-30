---
name: go-tui
description: Builds, debugs, and reviews terminal UIs using github.com/grindlemire/go-tui, .gsx templates, the tui CLI, reactive State, KeyMap events, flexbox terminal layout, inline mode, and stream output. Use when creating or modifying Go TUI apps with go-tui or when the user mentions .gsx, tui generate, go-tui components, or StreamAbove.
---

# Go TUI

## When to Use This Skill

Use this skill when:
- Creating, modifying, debugging, or reviewing a Go terminal UI built with `github.com/grindlemire/go-tui`.
- Working with `.gsx` files, `templ` components, generated `*_gsx.go` files, or the `tui` CLI.
- Designing component state, keyboard/mouse handling, focus, scrolling, inline widgets, or streaming output for a go-tui app.
- Diagnosing layout, rendering, event propagation, watcher, generated-code, inline, or terminal-restoration problems in a go-tui project.

Do not use this skill for Bubble Tea, tview, termui, curses, generic Go CLI work, or web frontend work unless go-tui is specifically involved.

## Mental Model

go-tui is a declarative terminal UI framework for Go with templ-like `.gsx` syntax and flexbox-style terminal layout.

```text
.gsx files -> tui generate -> *_gsx.go files -> go build -> terminal app
```

Runtime flow: event loop -> component render -> flex layout -> double-buffered diff render -> ANSI terminal output.

Components render an element tree from current state. Key handlers, mouse handlers, watchers, events, and queued updates mutate state on the app event loop. State changes mark the app dirty; the next frame re-renders.

Treat this skill as the working reference for Go TUI. Apply these patterns directly.

## Default Workflow

1. Inspect `go.mod`, `.gsx` files, generated `*_gsx.go` files, `main.go`, tests, and package layout.
2. Install dependencies only when missing: `go get github.com/grindlemire/go-tui` and `go install github.com/grindlemire/go-tui/cmd/tui@latest`.
3. Edit `.gsx` and normal `.go` files. Never hand-edit generated `*_gsx.go` files.
4. Prefer a root struct component that owns shared state and composes children.
5. Use pure `templ` components for stateless visual fragments; use struct components for state, refs, events, watchers, lifecycle, key maps, or mouse handling.
6. After GSX edits, run `tui generate ./...`.
7. Verify with `tui fmt --check ./...`, `tui check ./...`, `tui generate ./...`, `go test ./...`, and `go run .` for interactive smoke tests when feasible.

## CLI

```bash
tui generate [path...]       # Generate Go code from .gsx files
tui check [path...]          # Validate .gsx files without writing output
tui fmt [path...]            # Format .gsx files
tui fmt --check [path...]    # Check formatting without modifying
tui lsp                      # Start language server on stdio
```

Path forms: `./...` recursively processes all `.gsx` files, a directory processes that directory, and a file processes one source file. Generated files sit beside sources, e.g. `app.gsx` -> `app_gsx.go`.

## App Patterns

Standard interactive app:

```go
func main() {
    app, err := tui.NewApp(
        tui.WithRootComponent(App()),
        // tui.WithMouse(),
        // tui.WithFrameRate(60),
        // tui.WithInlineHeight(5),
    )
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
    defer app.Close()

    if err := app.Run(); err != nil {
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
}
```

One-shot styled output without an event loop:

```go
tui.Print(View("hello"))
s := tui.Sprint(View("hello"), tui.WithPrintWidth(80))
err := tui.Fprint(w, View("hello"), tui.WithPrintWidth(120))
```

Manual loops are for integration with external event loops only. Use `app.Open()`, `app.Events()`, `app.Dispatch(ev)`, `app.Step()`, `app.Render()`, and `app.StopCh()`. If work happens on that same main loop, mutate state directly; from other goroutines, use `app.QueueUpdate`.

## GSX Syntax

`.gsx` files are Go files with `templ` declarations. They support normal packages, imports, Go expressions, `if`, `for`, local element bindings, and component calls.

Pure component:

```gsx
package main

import tui "github.com/grindlemire/go-tui"

templ Card(title string) {
    <div class="border-rounded p-1 flex-col gap-1">
        <span class="font-bold">{title}</span>
        {children...}
    </div>
}

templ Status() {
    @Card("Status") {
        <span class="text-green">Ready</span>
    }
}
```

Struct component:

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
        tui.On(tui.KeyEscape, func(ke tui.KeyEvent) { ke.App().Stop() }),
    }
}

templ (c *counter) Render() {
    <div class="flex-col items-center justify-center h-full">
        <span class="text-cyan font-bold">{fmt.Sprintf("Count: %d", c.count.Get())}</span>
    </div>
}
```

Control flow and expressions:

```gsx
if loading {
    <span class="text-yellow">Loading</span>
} else {
    for i, item := range items {
        <span class={rowClass(i == selected)}>{item}</span>
    }
}

badge := <span class="font-bold">{label}</span>
<div width={20} height={5} flexGrow={1}>{badge}</div>
```

## Elements and Attributes

Common elements: `<div>`, `<span>`, `<p>`, `<ul>`, `<li>`, `<button>`, `<input />`, `<textarea />`, `<table>`, `<tr>`, `<td>`, `<th>`, `<modal>`, `<progress />`, `<hr />`, `<br />`, `<markdown />`.

Key attributes:

| Area | Attributes |
| --- | --- |
| Layout | `width`, `height`, `widthPercent`, `heightPercent`, `minWidth`, `maxWidth`, `minHeight`, `maxHeight`, `direction`, `justify`, `align`, `alignSelf`, `gap`, `flexGrow`, `flexShrink`, `padding`, `margin` |
| Visual | `border`, `background`, `text`, `textStyle`, `textAlign`, `borderStyle`, `borderTitle` |
| Behavior | `id`, `class`, `disabled`, `ref`, `deps`, `focusable`, `onFocus`, `onBlur`, `onActivate` |
| Scroll | `scrollable`, `scrollOffset`, `scrollbarStyle`, `scrollbarThumbStyle`, `hideScrollbar` |
| Modal | `open`, `backdrop`, `closeOnEscape`, `closeOnBackdropClick`, `trapFocus`, `keyMap` |

## Classes and Layout

`<div>` is the primary layout container and defaults to row direction. Add `flex-col` for vertical stacks. Styles do not cascade like CSS; style each element that needs styling or wrap repeated styles in pure components.

Common classes:

```text
flex flex-row flex-col grow grow-0 shrink shrink-0 flex-1
w-N h-N w-full h-full w-auto h-auto w-1/2 w-1/3 w-2/3 min-w-N max-w-N min-h-N max-h-N
items-start items-center items-end items-stretch justify-start justify-center justify-end justify-between
gap-N p-N px-N py-N m-N mx-N my-N
border border-single border-double border-rounded border-thick border-COLOR border-[#hex]
font-bold font-dim text-dim italic underline strikethrough blink reverse truncate wrap nowrap
text-COLOR text-bright-COLOR bg-COLOR bg-bright-COLOR text-[#hex] bg-[#hex]
text-gradient-C1-C2[-dir] bg-gradient-C1-C2[-dir] border-gradient-C1-C2[-dir]
overflow-scroll overflow-y-scroll overflow-x-scroll overflow-hidden scrollbar-hidden scrollbar-COLOR scrollbar-thumb-COLOR
focusable hidden
```

Layout patterns:

```gsx
// Header/content/footer
<div class="flex-col h-full">
    <div class="shrink-0 border-single p-1"><span>Header</span></div>
    <div class="grow min-h-0 overflow-y-scroll p-1"><span>Content</span></div>
    <div class="shrink-0 border-single p-1"><span>Footer</span></div>
</div>

// Sidebar + main
<div class="flex h-full">
    <div class="w-20 shrink-0 border-single flex-col p-1"><span>Sidebar</span></div>
    <div class="grow flex-col p-1"><span>Main</span></div>
</div>
```

Scrollable regions need bounded height: use fixed `height` or a flex chain with `h-full`, `grow`, and `min-h-0`. Store `scrollOffset` in `State[int]` when it must survive re-renders.

## State, Events, and Watchers

```go
count := tui.NewState(0)
count.Get()                           // safe from any goroutine
count.Set(5)                          // main event loop only
count.Update(func(v int) int { ... }) // main event loop only
unbind := count.Bind(func(v int) {})

bus := tui.NewEvents[MyEvent]("topic")
bus.Emit(MyEvent{})                   // main event loop only
unsub := bus.Subscribe(func(e MyEvent) {})
```

Threading rules:

| Operation | Main loop | Other goroutines |
| --- | --- | --- |
| `state.Get()` | Yes | Yes |
| `state.Set()` / `state.Update()` | Yes | Use `app.QueueUpdate()` |
| `events.Emit()` | Yes | Use `app.QueueUpdate()` |
| `app.QueueUpdate(func(){...})` | Yes | Yes |

If a component needs `QueueUpdate`, declare `app *tui.App`; generated binding assigns it on mount. Avoid custom `BindApp`; if needed, call generated `bindAppFields(app)` first.

Watchers run on the event loop:

```go
func (c *myComp) Watchers() []tui.Watcher {
    return []tui.Watcher{
        tui.OnTimer(time.Second, c.tick),
        tui.Watch(c.dataCh, c.onData),
        tui.OnChange(c.query, c.onQueryChanged),
    }
}
```

Batch related updates:

```go
ke.App().Batch(func() {
    state1.Set(v1)
    state2.Set(v2)
})
```

## Components and Interfaces

Generated struct components implement `Render(app *App) *Element`. Optional component interfaces include:

```go
type KeyListener interface { KeyMap() KeyMap }
type MouseListener interface { HandleMouse(MouseEvent) bool }
type WatcherProvider interface { Watchers() []Watcher }
type Initializer interface { Init() func() }
type PropsUpdater interface { UpdateProps(fresh Component) }
type AppBinder interface { BindApp(app *App) }
```

Generated code mounts child struct components rendered with `@Child(args)` and caches them by parent/key, so child local state survives parent re-renders. Do not call `app.Mount` manually in normal app code.

Recommended architecture:
- Root component owns shared app state, global bindings, and top-level layout.
- Child struct components own local UI state and handlers.
- Shared `*tui.State[T]` coordinates current data between components.
- `tui.Events[T]` handles transient notifications or decoupled commands.

## Keyboard, Mouse, Focus, and Inputs

Key maps:

```go
func (c *myComp) KeyMap() tui.KeyMap {
    return tui.KeyMap{
        tui.On(tui.KeyEscape, handler),
        tui.OnStop(tui.KeyEnter, handler),
        tui.On(tui.Rune('q'), handler),
        tui.OnStop(tui.AnyRune, handler),
        tui.OnFocused(tui.AnyRune, handler),
        tui.OnPreemptStop(tui.AnyKey, func(ke tui.KeyEvent) {}),
    }
}
```

Special keys include `KeyUp`, `KeyDown`, `KeyLeft`, `KeyRight`, `KeyEnter`, `KeyTab`, `KeyEscape`, `KeyBackspace`, `KeyDelete`, `KeyHome`, `KeyEnd`, `KeyPageUp`, `KeyPageDown`, `KeyInsert`, `KeyCtrlA` through `KeyCtrlZ`, and `KeyF1` through `KeyF12`. `KeyEvent` exposes `ke.Key`, `ke.Rune`, `ke.Mod`, and `ke.App()`.

Use conditional `KeyMap()` returns for modes such as search, command palettes, forms, and editors. Parent shortcuts should usually be disabled while a child input or modal owns keys.

Mouse requires `tui.WithMouse()`:

```go
func (c *myComp) HandleMouse(me tui.MouseEvent) bool {
    return tui.HandleClicks(me,
        tui.Click(c.saveBtn, c.onSave),
        tui.Click(c.itemRefs, c.onItemClick),
    )
}
```

Refs: `tui.NewRef()` for one element, `tui.NewRefList()` for loop elements, and `tui.NewRefMap[K]()` for keyed elements. Bind with `ref={...}` and optional `key={...}`.

Focus:

```go
element.Focus(); element.Blur(); element.IsFocused()
app.FocusNext(); app.FocusPrev(); app.Focused()
fg := tui.MustNewFocusGroup(sidebarActive, contentActive)
```

Inputs:

```gsx
<input value={s.query} placeholder="Search" width={30} border={true} onSubmit={s.submit} onChange={s.changed} />
<textarea value={s.body} placeholder="Message" maxHeight={6} border={true} onSubmit={s.submit} />
```

`Input` and `TextArea` runtime methods use grapheme-cluster positions: `CursorPos`, `SetCursorPos`, `InsertText`, `Text`, and `SetText`. Use `tui.WithInputOnChange(func(string))` and `tui.WithTextAreaOnChange(func(string))` for programmatic text-change callbacks.

## App Options and Methods

Common options:

```go
tui.WithRootComponent(comp)
tui.WithMouse()
tui.WithFrameRate(fps)
tui.WithInlineHeight(rows)
tui.WithGlobalKeyHandler(func(tui.KeyEvent) bool)
tui.WithInputLatency(d)
tui.WithEventQueueSize(n)
tui.WithPreRenderHook(func())
tui.WithPostRenderHook(func())
tui.WithManualCursor()
```

Common methods:

```go
app.Run(); app.Stop(); app.Close(); app.StopCh()
app.Open(); app.Events(); app.Dispatch(ev); app.DispatchEvents(); app.Step()
app.Render(); app.RenderFull(); app.MarkDirty()
app.Batch(func()); app.QueueUpdate(func())
app.FocusNext(); app.FocusPrev(); app.Focused()
```

Element APIs useful for advanced behavior:

```go
el.ScrollTo(x, y); el.ScrollBy(dx, dy); el.ScrollToTop(); el.ScrollToBottom()
el.ScrollIntoView(child); el.ScrollOffset(); el.MaxScroll(); el.ContentSize(); el.ViewportSize(); el.IsAtBottom()
el.SetWidth(tui.Fixed(40)); el.SetHeight(tui.Percent(50))
```

## Inline Mode and Streaming

Inline mode reserves rows at the bottom of the terminal instead of taking over the full screen:

```go
app, err := tui.NewApp(
    tui.WithRootComponent(App()),
    tui.WithInlineHeight(5),
)
```

Use `PrintAbove`/`PrintAboveln` for complete lines above the inline widget. Use `StreamAbove()` for token-by-token output such as LLM responses.

```go
go func() {
    w := app.StreamAbove()
    defer w.Close()

    fmt.Fprint(w, "hello ")
    w.WriteStyled("bold", tui.NewStyle().Bold().Foreground(tui.Red))
    grad := tui.NewGradient(tui.Cyan, tui.Magenta)
    w.WriteGradient(" gradient", grad)

    app.QueueUpdate(func() { streaming.Set(false) })
}()
```

`StreamAbove` is goroutine-safe and returns a no-op writer outside inline mode. Close it when done. It does not update component state; use `QueueUpdate` for state changes. Only one stream writer is active at a time. `PrintAbove`/`PrintAboveln` finalize active streams before printing.

`PrintAboveElement(view)` and `StreamWriter.WriteElement(view)` render a view into static inline history. They do not mount interactive components. From goroutines, use `QueuePrintAbove`, `QueuePrintAboveElement`, or `QueueUpdate` as appropriate.

Modals require full-screen mode and are ignored in inline mode. To show a modal from inline mode, enter alternate screen first and exit it after closing.

## Modal Pattern

```gsx
<modal open={s.showConfirm} class="justify-center items-center" backdrop="dim" trapFocus={true}>
    <div class="border-rounded p-2 flex-col gap-1 w-40">
        <span class="font-bold text-yellow">Confirm?</span>
        <button class="px-2 border-rounded focusable" onActivate={s.cancel}>Cancel</button>
        <button class="px-2 border-rounded focusable" onActivate={s.confirm}>OK</button>
    </div>
</modal>
```

Modal focus trapping blocks parent key handlers and cycles Tab/Shift+Tab inside focusable modal children. Enter triggers the focused element's `onActivate`.

## Testing

```go
term := tui.NewMockTerminal(80, 24)
output := term.StringTrimmed()
cell := term.CellAt(5, 2)

reader := tui.NewMockEventReader(
    tui.KeyEvent{Key: tui.KeyRune, Rune: 'a'},
    tui.KeyEvent{Key: tui.KeyEscape},
)
```

Separate render assertions from behavior/state tests when possible. Test small terminal sizes for scroll regions, sidebars, tables, long text, focus, and resize behavior.

## Common Pitfalls

- Editing `*_gsx.go` by hand instead of `.gsx`.
- Forgetting `tui generate ./...` after GSX changes.
- Updating state or emitting events from goroutines without `app.QueueUpdate`.
- Overriding `BindApp` without calling generated `bindAppFields(app)`.
- Expecting `<div>` to stack vertically without `flex-col`.
- Expecting styles to cascade from parent elements.
- Letting scrollable content grow without bounded height or `min-h-0`.
- Registering broad key handlers while an input, search mode, or modal owns keys.
- Using competing `OnStop` handlers for the same key at the same time.
- Assuming inline mode supports modal overlays.
- Forgetting to close `StreamAbove()` writers.

## References

Load references only when the task needs more detail than this main guide:

- [references/setup.md](references/setup.md): setup, CLI, app lifecycle, printing, manual loops.
- [references/components.md](references/components.md): GSX components, children, mounting, props, binding, lifecycle.
- [references/reactivity.md](references/reactivity.md): state, events, watchers, goroutines, batching.
- [references/interaction.md](references/interaction.md): keyboard, mouse refs, focus, input ownership.
- [references/layout.md](references/layout.md): elements, classes, layout, scroll, forms, tables, modals.
- [references/streaming.md](references/streaming.md): inline mode, `PrintAbove`, `StreamAbove`, LLM token output.
- [references/testing.md](references/testing.md): mock terminal, event tests, verification, debugging.

When Go TUI changes, update this skill. Downstream agents should follow this skill directly.
