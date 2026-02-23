# Abstract Factory

Provide an interface for creating families of related objects without specifying concrete classes.

## Intent

- Provide an interface for creating families of related objects
- Ensure that created objects are compatible with each other
- Isolate concrete implementations from client code

## Implementation

```go
package main

import "fmt"

// Abstract products
type Button interface {
	Render()
}

type TextField interface {
	Render()
}

// Abstract factory
type UIFactory interface {
	CreateButton() Button
	CreateTextField() TextField
}

// Concrete products - Windows
type WindowsButton struct{}

func (b *WindowsButton) Render() {
	fmt.Println("Rendering Windows button")
}

type WindowsTextField struct{}

func (t *WindowsTextField) Render() {
	fmt.Println("Rendering Windows text field")
}

// Concrete products - Mac
type MacButton struct{}

func (b *MacButton) Render() {
	fmt.Println("Rendering Mac button")
}

type MacTextField struct{}

func (t *MacTextField) Render() {
	fmt.Println("Rendering Mac text field")
}

// Concrete factories
type WindowsFactory struct{}

func (f *WindowsFactory) CreateButton() Button {
	return &WindowsButton{}
}

func (f *WindowsFactory) CreateTextField() TextField {
	return &WindowsTextField{}
}

type MacFactory struct{}

func (f *MacFactory) CreateButton() Button {
	return &MacButton{}
}

func (f *MacFactory) CreateTextField() TextField {
	return &MacTextField{}
}

// Client code - depends on abstraction
func renderUI(factory UIFactory) {
	button := factory.CreateButton()
	textField := factory.CreateTextField()
	
	button.Render()
	textField.Render()
}

// Usage
func main() {
	// On Mac
	macFactory := &MacFactory{}
	renderUI(macFactory)
	
	// On Windows
	windowsFactory := &WindowsFactory{}
	renderUI(windowsFactory)
}
```

## When to Use

- When your system needs to work with various families of related products
- When you want to provide a library without exposing implementation details
- When you need to ensure created objects are compatible with each other
