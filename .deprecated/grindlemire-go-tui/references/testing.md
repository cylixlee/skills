# Testing

## Testing Rendered Output

Use `MockTerminal` and `Buffer` for low-level render assertions. This is stable for testing drawing helpers, cells, and style output.

```go
func TestOutput(t *testing.T) {
    term := tui.NewMockTerminal(40, 10)
    buf := tui.NewBuffer(40, 10)

    buf.SetString(2, 1, "Hello, Alice", tui.NewStyle())
    tui.Render(term, buf)

    if !strings.Contains(term.StringTrimmed(), "Alice") {
        t.Fatalf("missing greeting:\n%s", term.StringTrimmed())
    }
}
```

For generated GSX views or whole components, prefer app-level tests with `NewMockEventReader`, `Dispatch`, `Render`, and `SnapshotFrame`. Reuse project helpers when they already exist.

## Testing Cells and Styles

Use cell-level assertions for style-sensitive output.

```go
cell := term.CellAt(2, 1)
if cell.Rune != 'A' {
    t.Fatalf("unexpected rune: %q", cell.Rune)
}
if !cell.Style.HasAttr(tui.AttrBold) {
    t.Fatal("expected bold style")
}
```

Prefer substring or cell assertions over brittle full-screen snapshots unless the layout is intentionally fixed.

## Testing Events

Use `MockEventReader` to simulate input when the project has app-level event tests.

```go
reader := tui.NewMockEventReader(
    tui.KeyEvent{Key: tui.KeyRune, Rune: 'j'},
    tui.KeyEvent{Key: tui.KeyEnter},
)

event, ok := reader.PollEvent(0)
if !ok {
    t.Fatal("expected event")
}
```

For component behavior, prefer direct handler tests when possible. Bind state through the app or use the project's existing component test helper before calling handlers that mutate state.

```go
c := Counter()
c.increment(tui.KeyEvent{})
if got := c.count.Get(); got != 1 {
    t.Fatalf("count = %d, want 1", got)
}
```

Use the project's existing test setup for app binding. Do not invent broad integration harnesses for small behavior changes.

## Testing Layout

Test small terminal sizes for UIs with sidebars, scroll regions, tables, and long text. Check that important controls remain visible and content does not overwrite headers or footers.

Useful checks:

- Render at narrow width, such as 40 columns.
- Render at short height, such as 8 rows.
- Assert headers and footers still appear.
- Assert scroll containers do not expand beyond their region.
- Assert long labels are truncated, wrapped, or constrained according to the intended design.

## Verification Commands

Run these after GSX changes:

```bash
tui fmt --check ./...
tui check ./...
tui generate ./...
go test ./...
```

When formatting should be applied automatically:

```bash
tui fmt ./...
tui generate ./...
go test ./...
```

For interactive behavior, also run the app manually:

```bash
go run .
```

Smoke-test expected keys, resize behavior, scrolling, focus, mouse clicks if enabled, quit behavior, and terminal restoration after exit.

## Debugging Checklist

- Generated files are stale: run `tui generate ./...`.
- GSX parse or type errors: run `tui check ./...` and inspect the `.gsx` line, not just generated Go.
- State does not re-render: confirm the state is bound to the app and mutation occurs on the event loop.
- Panic or dropped update after custom binding: call generated `bindAppFields(app)`.
- Key ignored: inspect conditional `KeyMap`, focus state, `OnStop`, and active modal or preemptive handlers.
- Click ignored: confirm `WithMouse`, ref binding, non-nil ref element after render, and `HandleClicks` return value.
- Scroll does not work: bound the scroll region height and store scroll offset in state.
- Inline stream missing: confirm app was created with `WithInlineHeight` and the writer is closed when done.
- Terminal left in a bad state: ensure `app.Close()` is deferred after successful `NewApp`.
