---
name: design-pattern
description: Applies object-oriented design principles and design patterns to generate maintainable, extensible code. Use when generating code that requires proper architectural layering, SOLID principles, and appropriate design patterns to solve recurring software design problems.
---

# Design Pattern

This skill guides the generation of high-quality, maintainable, and extensible code by applying established software design principles. When generating code for any non-trivial application, always follow these principles to ensure the resulting codebase is easy to understand, modify, test, and extend over time.

## Core Principles

### 1. Layered Architecture

Layered Architecture is essential for maintainable software because it separates concerns, making code easier to understand, test, and modify. When all code is mixed together in a single layer, changes in one area can unexpectedly break unrelated functionality. By separating responsibilities into distinct layers, each layer can be developed, tested, and modified independently.

The key principle is that dependencies should only flow in one direction, typically from outer layers toward inner layers. This ensures that core business logic does not depend on external concerns like databases, UI frameworks, or external services.

#### Why Layered Architecture Matters

- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Testability**: Inner layers can be tested without involving outer layers
- **Maintainability**: Changes to one layer (e.g., switching databases) don't affect other layers
- **Reusability**: Core business logic can be reused across different interfaces
- **Parallel Development**: Different teams can work on different layers simultaneously

#### Common Layering Approaches

**Model-View-Controller (MVC)**:
A pattern that separates an application into three main components: the Model (data and business logic), the View (presentation layer), and the Controller (handles user input and orchestrates Model and View). MVC is particularly common in web applications and UI frameworks.

**Domain-Driven Design (DDD)**:
DDD emphasizes modeling software around business domains. It uses concepts like entities, value objects, aggregates, bounded contexts, and domain services. DDD is particularly valuable for complex business applications where the domain logic is sophisticated and frequently changing. For more details, see [Domain-Driven Design](references/ddd.md).

#### General Rule

Regardless of the specific layering approach chosen, always ensure:
- Each layer has clear, single responsibility
- Dependencies flow inward only
- Layer boundaries are enforced through interfaces or abstractions
- Code is distributed across multiple files and packages, not lumped together

### 2. OOP Over Imperative

Write code using Object-Oriented Programming principles rather than procedural or functional style. OOP provides better abstraction, encapsulation, and polymorphism for building complex systems.

#### Use Interfaces or Abstract Classes to Define Contracts

Always define the "what" separately from the "how". Define what operations are available through an interface or abstract class, then provide concrete implementations. This allows clients to depend on abstractions rather than specific implementations, enabling flexibility and testability.

#### Prefer Composition Over Inheritance

Favor "has-a" relationships over "is-a" relationships. Inheritance creates tight coupling between classes, making changes difficult and testing problematic. Composition (组装) allows you to combine behaviors by injecting dependencies, which is more flexible and easier to test.

#### Encapsulate Behavior Within Classes

Keep related behavior and data together. Avoid scattered utility functions or global state. Each class should bundle its data with the operations that manipulate that data.

#### Extract Hardcoded Logic to Strategy Classes

When you find conditional logic that varies by type or category, consider extracting each variant into its own class. This follows the Strategy pattern and makes the code easier to extend without modification.

### 3. SOLID Principles

Apply these five principles as code quality checks. Whenever you write code, verify that it does not violate any SOLID principle.

#### Single Responsibility Principle

Every class should have only one reason to change. A class should do one thing well. If a class is responsible for multiple concerns, changes to one concern may affect others unexpectedly.

#### Open/Closed Principle

Software entities should be open for extension but closed for modification. Add new features by adding new code rather than modifying existing code. This is typically achieved through abstraction, polymorphism, and composition.

#### Liskov Substitution Principle

Subtypes must be substitutable for their base types. A subclass should honor the contract of its parent class. If a subclass cannot fully implement parent behavior, the inheritance relationship is incorrect.

#### Interface Segregation Principle

Clients should not be forced to depend on interfaces they do not use. Many small, specific interfaces are better than one large interface. This prevents classes from being burdened with methods they don't need.

#### Dependency Inversion Principle

High-level modules should not depend on low-level modules. Both should depend on abstractions. This enables swapping implementations without affecting clients.

### 4. Design Pattern Selection

Design patterns are reusable solutions to commonly occurring problems. Choose appropriate patterns based on the specific problem context.

#### Creation Patterns

| Pattern | Purpose |
|---------|---------|
| Factory Method | Delegate instantiation to subclasses |
| Abstract Factory | Create families of related objects |
| Builder | Construct complex objects step by step |
| Singleton | Ensure single instance with global access |
| Prototype | Create objects by cloning existing ones |

#### Structural Patterns

| Pattern | Purpose |
|---------|---------|
| Adapter | Convert interface compatibility |
| Bridge | Separate abstraction from implementation |
| Composite | Tree structures for part-whole hierarchies |
| Decorator | Add responsibilities dynamically |
| Facade | Simplified interface to complex subsystem |
| Flyweight | Share common state efficiently |
| Proxy | Control access to another object |

#### Behavioral Patterns

| Pattern | Purpose |
|---------|---------|
| Chain of Responsibility | Pass request along a chain of handlers |
| Command | Encapsulate request as an object |
| Iterator | Access elements sequentially |
| Mediator | Centralized communication |
| Memento | Capture and restore internal state |
| Observer | Notify dependents of state changes |
| State | Alter behavior based on internal state |
| Strategy | Interchangeable algorithms |
| Template Method | Define algorithm skeleton, let subclasses override steps |
| Visitor | Operations on elements of an object structure |

### 5. Dependency Management

Proper dependency management is critical for maintainability and testability.

#### Use Dependency Injection

Inject dependencies rather than creating them inside classes. Pass dependencies through constructors or setters rather than having classes create their own dependencies. This enables loose coupling and makes testing straightforward.

#### Inject Abstractions, Not Concretions

Always depend on interfaces or abstract types, not concrete implementations. This allows implementations to be swapped without affecting client code.

#### Avoid Circular Dependencies

Circular dependencies make code hard to test and reason about. The dependency graph should be acyclic. If two modules depend on each other, extract shared abstractions to break the cycle.

### 6. Testability

Design code to be easily testable. Testable code is usually well-designed code.

- Avoid static state that persists between tests
- Avoid singletons with mutable state
- Use dependency injection to enable mocking
- Favor pure functions where possible
- Keep methods focused and single-purpose

### 7. Code Quality Rules

- **Meaningful Naming**: Use descriptive names for classes, methods, and variables that convey intent
- **Short Methods**: Each method should do one thing; keep methods concise
- **No Duplication**: Extract repeated logic into reusable abstractions (DRY principle)
- **Error Handling**: Use exceptions rather than error codes; provide meaningful error messages

### 8. Anti-Patterns to Avoid

- **God Class**: A class with too many responsibilities; split into focused classes
- **Spaghetti Code**: Tangled, unstructured control flow; apply proper design
- **Magic Values**: Hardcoded numbers or strings without constants; use named constants
- **Premature Optimization**: Optimize only when measurement proves it necessary
- **Excessive Inheritance**: Deep hierarchies create tight coupling; prefer composition

## References

For language-specific implementations with detailed code examples, see:
- [Java](references/java.md)
- [Go](references/go.md)
- [Python](references/python.md)
- [Domain-Driven Design](references/ddd.md)
