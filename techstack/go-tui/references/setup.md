# Setup

## What go-tui Provides

go-tui is a Go terminal UI framework with declarative `.gsx` templates. `.gsx` files compile into ordinary Go source files, so the final application is a normal Go binary.

The build path is:

```text
.gsx files -> tui generate -> *_gsx.go files -> go build -> binary
```

Runtime flow is event loop, layout, render diff, terminal output.

## Installation

Add the library to the Go module:

```bash
go get github.com/grindlemire/go-tui
```

Install the CLI used to compile, check, format, and serve language features for `.gsx` files:

```bash
go install github.com/grindlemire/go-tui/cmd/tui@latest
```

If `tui` is not found, check that `$GOPATH/bin` or `$GOBIN` is on `PATH`.

## CLI Commands

Generate Go files from GSX:

```bash
tui generate ./...
tui generate ./components
tui generate header.gsx
tui generate -v ./...
```

`tui generate` writes one generated file beside each source file. `hello.gsx` becomes `hello_gsx.go`; filenames with hyphens are converted to underscores. Generated files are overwritten on the next generation run.

Validate GSX without writing generated output:

```bash
tui check ./...
tui check header.gsx
```

Format GSX files:

```bash
tui fmt ./...
tui fmt --check ./...
tui fmt --stdout file.gsx
```

Start the language server:

```bash
tui lsp
tui lsp --log /tmp/tui-lsp.log
```

Print the installed CLI version:

```bash
tui version
```

## Generated File Rules

- Do not hand-edit `*_gsx.go` files.
- After editing `.gsx`, run `tui generate ./...`.
- If a compile error references a generated file, inspect the corresponding `.gsx` source first.
- Keep generated files in version control only if the project already does so.
- When generated output looks stale, run `tui check ./...` first for source errors, then `tui generate ./...`.

## Standard App Lifecycle

Use `tui.NewApp`, pass a root component, defer `Close`, then call `Run`:

```go
package main

import (
    "fmt"
    "os"

    tui "github.com/grindlemire/go-tui"
)

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

`NewApp` prepares terminal handling, `Run` starts the event loop, and `Close` restores terminal state. Always arrange for `Close` to run after a successful `NewApp`.

## App Options

Common options:

```go
tui.WithRootComponent(component)
tui.WithMouse()
tui.WithFrameRate(60)
tui.WithInlineHeight(rows)
tui.WithGlobalKeyHandler(func(ke tui.KeyEvent) bool { return false })
```

Use `WithMouse` when click, scroll, or mouse tracking behavior matters. Use `WithInlineHeight` for widgets that should sit below normal terminal output instead of occupying the full alternate screen.

## One-Shot Printing

For styled terminal output without an interactive app, use printing helpers. They accept generated GSX views and raw `*tui.Element` values.

```go
tui.Print(View("hello"))

s := tui.Sprint(View("hello"), tui.WithPrintWidth(80))

err := tui.Fprint(w, View("hello"), tui.WithPrintWidth(120))
```

Use this for report rendering, previews, command output, and tests where no event loop is needed.

## Custom Event Loops

Prefer `app.Run()` for normal applications. Use lower-level app methods only when integrating with another loop:

```go
if err := app.Open(); err != nil {
    return err
}
defer app.Close()

events := app.Events()
for {
    select {
    case ev := <-events:
        app.Dispatch(ev)
    case msg := <-external:
        updateState(msg)
    case <-app.StopCh():
        return nil
    }
    app.Render()
}
```

When work already runs on this main loop, state can be mutated directly. From separate goroutines, use `app.QueueUpdate`.

## Editor Setup

For VS Code-compatible editors, use the official go-tui extension if available. It provides syntax highlighting, LSP diagnostics, completions, hover docs, formatting, and generated file nesting.

For Neovim or custom editors, connect the editor's LSP client to `tui lsp` over stdio.

## Setup Checklist

- `go.mod` includes `github.com/grindlemire/go-tui`.
- `tui` CLI is installed and on `PATH`.
- `.gsx` files have normal Go package declarations and imports.
- Generated `*_gsx.go` files are current.
- `main.go` creates `NewApp`, defers `Close`, and calls `Run`.
- Verification commands pass: `tui fmt --check ./...`, `tui check ./...`, `tui generate ./...`, `go test ./...`.
