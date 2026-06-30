# Layout

## Built-In Elements

Common container and text elements:

| Element    | Use                                                    |
| ---------- | ------------------------------------------------------ |
| `<div>`    | Main flex layout container. Defaults to row direction. |
| `<span>`   | Inline text container.                                 |
| `<p>`      | Paragraph text with wrapping.                          |
| `<ul>`     | Unordered list container.                              |
| `<li>`     | List item with bullet-style prefix.                    |
| `<button>` | Clickable or activatable control.                      |
| `<modal>`  | Full-screen overlay dialog.                            |
| `<table>`  | Table container.                                       |
| `<tr>`     | Table row.                                             |
| `<td>`     | Table cell.                                            |
| `<th>`     | Header cell.                                           |

Common self-closing elements:

| Element        | Use                                                          |
| -------------- | ------------------------------------------------------------ |
| `<input />`    | Single-line text input.                                      |
| `<textarea />` | Multi-line text input.                                       |
| `<hr />`       | Horizontal rule.                                             |
| `<br />`       | Line break.                                                  |
| `<progress />` | Progress bar where supported by the installed version.       |
| `<markdown />` | Markdown rendering where supported by the installed version. |

If a built-in differs across versions, inspect local generated code or existing project examples before using the element in new code.

## Flex Layout Mental Model

`<div>` is a flex container. Its default direction is row, so children are placed horizontally unless you add `flex-col` or set direction explicitly.

```gsx
<div class="h-full flex-col">
    <div class="shrink-0">Header</div>
    <div class="grow min-h-0 overflow-y-scroll">Content</div>
    <div class="shrink-0">Footer</div>
</div>
```

Important defaults:

- `div` defaults to row direction.
- Terminal dimensions are character columns and rows.
- Text wraps only when rendered by elements that support wrapping or when layout constrains it.
- Dynamic content can change layout unless sizes or flex behavior are constrained.

## Sizing and Spacing Attributes

Use typed attributes when classes are not enough or when values are dynamic:

```gsx
<div width={24} height={10}>Fixed panel</div>
<div minWidth={20} maxWidth={40} flexGrow={1}>Flexible panel</div>
<div padding={1} margin={1} gap={1}>Spaced content</div>
```

Common layout attributes:

- `width`, `height` for fixed character dimensions.
- `widthPercent`, `heightPercent` for percentage sizing.
- `minWidth`, `maxWidth`, `minHeight`, `maxHeight` for constraints.
- `direction` for `tui.Row` or `tui.Column`.
- `justify`, `align`, `alignSelf` for alignment.
- `gap`, `padding`, `margin` for spacing.
- `flexGrow`, `flexShrink` for flexible layouts.

## Common Classes

Sizing and flex:

```text
w-full h-full grow shrink-0 flex flex-col items-center justify-center justify-between gap-1 min-h-0
```

Spacing:

```text
p-1 p-2 px-1 px-2 py-1 m-1
```

Borders:

```text
border-single border-rounded border-cyan border-red border-bright-white
```

Text and color:

```text
text-cyan text-green text-yellow text-red text-bright-white font-bold font-dim font-italic
```

Background and effects:

```text
bg-blue bg-black text-gradient-cyan-magenta blink
```

Scrolling:

```text
overflow-y-scroll overflow-x-scroll overflow-scroll overflow-hidden scrollbar-hidden scrollbar-cyan scrollbar-thumb-bright-white
```

## Styling Rules

Styles do not cascade like CSS. A parent `class="text-cyan"` should not be assumed to color every child. Apply classes to the specific element that needs the style, or create a pure component wrapper.

```gsx
templ Label(text string) {
    <span class="text-cyan font-bold">{text}</span>
}
```

Prefer classes for common static styling. Use dynamic `class={...}` when state controls style.

```gsx
<span class={itemClass(active)}>{label}</span>
```

## Full-Screen Layout Pattern

Use this structure for many terminal apps:

```gsx
templ (a *app) Render() {
    <div class="h-full flex-col">
        <div class="shrink-0 px-1">
            <span class="font-bold">{a.title}</span>
        </div>

        <div class="grow min-h-0 flex overflow-hidden">
            @Sidebar(a.selected)
            @Content(a.selected)
        </div>

        <div class="shrink-0 px-1">
            @CommandBar(a.command)
        </div>
    </div>
}
```

Use `grow min-h-0 overflow-hidden` on the middle region so scrollable children can be bounded instead of expanding forever.

## Sidebars and Panels

Sidebars usually need fixed width and `shrink-0`:

```gsx
<div class="flex-col shrink-0 border-rounded p-1" width={24}>
    <span class="font-bold text-cyan">Menu</span>
    <hr />
    @MenuItems(items)
</div>
```

Main panels usually need `grow` plus explicit constraints when long text or tables can otherwise force layout expansion. Use width, max width, truncation, wrapping, or scroll behavior according to the installed version and local patterns.

## Scrolling

A scrollable region needs bounded height. In a flex column, give the scrollable child `grow min-h-0 overflow-y-scroll`, or set a fixed `height`.

```gsx
<div
    class="grow min-h-0 overflow-y-scroll scrollbar-cyan"
    scrollOffset={0, a.scrollY.Get()}
>
    for _, line := range a.lines.Get() {
        <span>{line}</span>
    }
</div>
```

Keep scroll offset in state if it must survive re-renders:

```go
scrollY *tui.State[int]
```

Mouse wheel or key handlers should update the scroll state on the event loop.

## Inputs

Single-line input:

```gsx
<input
    value={a.query}
    placeholder="Search"
    width={30}
    border={true}
    focusColor={tui.Cyan}
    onSubmit={a.submit}
    onChange={a.changed}
/>
```

Multi-line input:

```gsx
<textarea
    value={a.message}
    placeholder="Message"
    maxHeight={6}
    border={true}
    submitKey={tui.KeyEnter.Ctrl()}
    onSubmit={a.submit}
/>
```

Use built-in inputs for cursor movement, editing, focus behavior, and grapheme-aware text handling. Only build manual text entry when the built-ins cannot model the interaction.

## Buttons and Activation

Buttons can be focusable and activated by Enter or clicks depending on context.

```gsx
<button class="px-2 border-rounded focusable" onActivate={a.save}>Save</button>
```

Outside modals, mouse clicks are usually handled with refs and `HandleClicks`. Inside modals, `onActivate` is usually enough for buttons.

## Tables

Use table elements for aligned row and column data when the installed version supports them.

```gsx
<table class="w-full">
    <tr>
        <th>Name</th>
        <th>Status</th>
    </tr>
    for _, row := range rows {
        <tr>
            <td>{row.Name}</td>
            <td>{row.Status}</td>
        </tr>
    }
</table>
```

For complex dynamic tables, constrain column widths so long text does not make the whole layout unstable.

## Modals

Modals are full-screen overlays. They are not suitable for inline mode unless the app first enters alternate screen mode.

```gsx
<modal open={a.confirmOpen} trapFocus={true} closeOnEscape={true}>
    <div class="border-rounded p-2 flex-col gap-1" width={40}>
        <span class="font-bold">Delete item?</span>
        <div class="gap-1 justify-end">
            <button class="px-2 border-rounded focusable" onActivate={a.cancel}>Cancel</button>
            <button class="px-2 border-rounded focusable" onActivate={a.confirm}>Delete</button>
        </div>
    </div>
</modal>
```

Use modal key maps or preemptive handlers when the modal must block parent shortcuts.

## Layout Pitfalls

- Forgetting `flex-col` on a vertical stack.
- Letting scroll regions expand without a bounded height.
- Expecting styles to cascade from parent to child.
- Failing to use `shrink-0` for headers, footers, sidebars, and input bars.
- Using dynamic text without width constraints in tables or side-by-side panels.
- Assuming modals work in inline mode.
- Assuming every documented element exists in every pre-1.0 version.
