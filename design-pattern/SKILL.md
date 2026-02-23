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

| Pattern          | Purpose                                   | Go                                      | Java                                        | Python                                          |
| ---------------- | ----------------------------------------- | --------------------------------------- | ------------------------------------------- | ----------------------------------------------- |
| Factory Method   | Delegate instantiation to subclasses      | [Go](references/go-factory-method.md)   | [Java](references/java-factory-method.md)   | [Python](references/python-factory-method.md)   |
| Abstract Factory | Create families of related objects        | [Go](references/go-abstract-factory.md) | [Java](references/java-abstract-factory.md) | [Python](references/python-abstract-factory.md) |
| Builder          | Construct complex objects step by step    | [Go](references/go-builder.md)          | [Java](references/java-builder.md)          | [Python](references/python-builder.md)          |
| Singleton        | Ensure single instance with global access | [Go](references/go-singleton.md)        | [Java](references/java-singleton.md)        | [Python](references/python-singleton.md)        |
| Prototype        | Create objects by cloning existing ones   | [Go](references/go-prototype.md)        | [Java](references/java-prototype.md)        | [Python](references/python-prototype.md)        |

#### Structural Patterns

| Pattern   | Purpose                                    | Go                               | Java                                 | Python                                   |
| --------- | ------------------------------------------ | -------------------------------- | ------------------------------------ | ---------------------------------------- |
| Adapter   | Convert interface compatibility            | [Go](references/go-adapter.md)   | [Java](references/java-adapter.md)   | [Python](references/python-adapter.md)   |
| Bridge    | Separate abstraction from implementation   | [Go](references/go-bridge.md)    | [Java](references/java-bridge.md)    | [Python](references/python-bridge.md)    |
| Composite | Tree structures for part-whole hierarchies | [Go](references/go-composite.md) | [Java](references/java-composite.md) | [Python](references/python-composite.md) |
| Decorator | Add responsibilities dynamically           | [Go](references/go-decorator.md) | [Java](references/java-decorator.md) | [Python](references/python-decorator.md) |
| Facade    | Simplified interface to complex subsystem  | [Go](references/go-facade.md)    | [Java](references/java-facade.md)    | [Python](references/python-facade.md)    |
| Flyweight | Share common state efficiently             | [Go](references/go-flyweight.md) | [Java](references/java-flyweight.md) | [Python](references/python-flyweight.md) |
| Proxy     | Control access to another object           | [Go](references/go-proxy.md)     | [Java](references/java-proxy.md)     | [Python](references/python-proxy.md)     |

#### Behavioral Patterns

| Pattern                 | Purpose                                                  | Go                                             | Java                                               | Python                                                 |
| ----------------------- | -------------------------------------------------------- | ---------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------ |
| Chain of Responsibility | Pass request along a chain of handlers                   | [Go](references/go-chain-of-responsibility.md) | [Java](references/java-chain-of-responsibility.md) | [Python](references/python-chain-of-responsibility.md) |
| Command                 | Encapsulate request as an object                         | [Go](references/go-command.md)                 | [Java](references/java-command.md)                 | [Python](references/python-command.md)                 |
| Iterator                | Access elements sequentially                             | [Go](references/go-iterator.md)                | [Java](references/java-iterator.md)                | [Python](references/python-iterator.md)                |
| Mediator                | Centralized communication                                | [Go](references/go-mediator.md)                | [Java](references/java-mediator.md)                | [Python](references/python-mediator.md)                |
| Memento                 | Capture and restore internal state                       | [Go](references/go-memento.md)                 | [Java](references/java-memento.md)                 | [Python](references/python-memento.md)                 |
| Observer                | Notify dependents of state changes                       | [Go](references/go-observer.md)                | [Java](references/java-observer.md)                | [Python](references/python-observer.md)                |
| State                   | Alter behavior based on internal state                   | [Go](references/go-state.md)                   | [Java](references/java-state.md)                   | [Python](references/python-state.md)                   |
| Strategy                | Interchangeable algorithms                               | [Go](references/go-strategy.md)                | [Java](references/java-strategy.md)                | [Python](references/python-strategy.md)                |
| Template Method         | Define algorithm skeleton, let subclasses override steps | [Go](references/go-template-method.md)         | [Java](references/java-template-method.md)         | [Python](references/python-template-method.md)         |
| Visitor                 | Operations on elements of an object structure            | [Go](references/go-visitor.md)                 | [Java](references/java-visitor.md)                 | [Python](references/python-visitor.md)                 |

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

