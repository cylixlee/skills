# Interaction

## KeyMap

Struct components handle keyboard input by implementing `KeyMap() tui.KeyMap`.

```go
func (a *app) KeyMap() tui.KeyMap {
    return tui.KeyMap{
        tui.On(tui.Rune('q'), func(ke tui.KeyEvent) { ke.App().Stop() }),
        tui.On(tui.KeyEscape, func(ke tui.KeyEvent) { ke.App().Stop() }),
        tui.On(tui.Rune('j'), func(ke tui.KeyEvent) { a.moveDown() }),
        tui.On(tui.Rune('k'), func(ke tui.KeyEvent) { a.moveUp() }),
    }
}
```

Common binding constructors:

- `tui.On(matcher, fn)` handles a key and allows propagation.
- `tui.OnStop(matcher, fn)` handles a key and stops later handlers.
- `tui.OnFocused(matcher, fn)` handles a key only when the component or element has focus.
- `tui.OnPreemptStop(matcher, fn)` handles before normal dispatch and stops propagation.

Common matchers:

- `tui.Rune('q')` for printable runes.
- `tui.AnyRune` for text entry.
- `tui.AnyKey` for catch-all blockers.
- `tui.KeyEscape`, `tui.KeyEnter`, `tui.KeyBackspace`, `tui.KeyTab`, `tui.KeyCtrlC` for special keys.
- Modifier helpers such as `.Ctrl()` and `.Shift()` for key combinations.

## Conditional KeyMaps

`KeyMap()` can return different bindings based on state. This is the normal way to implement modes.

```go
func (s *search) KeyMap() tui.KeyMap {
    if !s.active.Get() {
        return nil
    }
    return tui.KeyMap{
        tui.OnStop(tui.AnyRune, s.appendRune),
        tui.OnStop(tui.KeyBackspace, s.backspace),
        tui.OnStop(tui.KeyEnter, s.submit),
        tui.OnStop(tui.KeyEscape, s.cancel),
    }
}
```

When a text input, search box, command palette, or modal is active, parent-level shortcuts should usually be disabled or guarded with conditions.

## Dispatch and Stop Rules

The framework collects key bindings from mounted components and checks them in tree order. Preemptive bindings run first. A stop binding prevents later matching handlers from running.

Rules of thumb:

- Put global quit keys on the root component, but guard them when a text mode is active.
- Use `OnStop` when a component owns a key.
- Use `OnPreemptStop` for overlays that must block parent handlers.
- Do not register multiple active `OnStop` handlers for the same key.

## Mouse and Refs

Use refs for click hit-testing instead of raw coordinates.

```go
type app struct {
    saveBtn   *tui.Ref
    itemRefs  *tui.RefList
    tabRefs   *tui.RefMap[string]
}

func App() *app {
    return &app{
        saveBtn:  tui.NewRef(),
        itemRefs: tui.NewRefList(),
        tabRefs:  tui.NewRefMap[string](),
    }
}
```

Bind refs in GSX:

```gsx
<button ref={a.saveBtn} class="px-2">Save</button>

for _, tab := range tabs {
    <button ref={a.tabRefs} key={tab.ID} class="px-1">{tab.Label}</button>
}
```

Handle clicks:

```go
func (a *app) HandleMouse(me tui.MouseEvent) bool {
    return tui.HandleClicks(me,
        tui.Click(a.saveBtn, a.save),
    )
}
```

`HandleClicks` handles left-button press events and returns true when a binding matched. For keyed refs, iterate the ref map when the handler needs the key that was clicked.

Enable mouse input on the app when click or scroll behavior matters:

```go
tui.NewApp(tui.WithMouse(), tui.WithRootComponent(App()))
```

## Focus

Mark elements as focusable when they should receive focused keyboard activation or visual focus state.

```gsx
<button focusable={true} class="px-2 border-rounded" onActivate={a.save}>Save</button>
```

Focus navigation is normally wired to Tab and Shift+Tab:

```go
func (f *form) KeyMap() tui.KeyMap {
    return tui.KeyMap{
        tui.On(tui.KeyTab, func(ke tui.KeyEvent) { ke.App().FocusNext() }),
        tui.On(tui.KeyTab.Shift(), func(ke tui.KeyEvent) { ke.App().FocusPrev() }),
    }
}
```

Use `FocusGroup` for section-level focus such as sidebar, content, and footer panels. Use `OnFocused` for element-level key ownership.

## Input Components

Use built-in inputs for text editing instead of manually collecting runes when possible.

```gsx
<input
    value={a.query}
    placeholder="Search"
    width={30}
    border={true}
    onSubmit={a.submitSearch}
    onChange={a.onSearchChange}
/>
```

```gsx
<textarea
    value={a.body}
    placeholder="Message"
    maxHeight={6}
    border={true}
    onSubmit={a.submitMessage}
/>
```

`<input />` supports change callbacks in GSX. For programmatic text widget callbacks, use `tui.WithInputOnChange(func(string))` and `tui.WithTextAreaOnChange(func(string))`.

## Interaction Checklist

- Text modes use conditional key maps and `OnStop`.
- Mouse code uses refs and `HandleClicks`.
- App uses `WithMouse` when mouse behavior matters.
- Focusable controls have Tab navigation when the UI contains forms or modals.
- Parent shortcuts are guarded while a child input, search mode, or modal owns keys.
- Broad catch-all handlers are preemptive only when an overlay must block the rest of the tree.
