---
name: rust-pest-parser
description: Creates, debugs, and extends Rust parsers using the pest and pest_derive crates. Use when writing .pest grammars, integrating pest parsers in Rust, building ASTs from Pair/Pairs, handling WHITESPACE or COMMENT, parsing expressions with PrattParser, or debugging pest grammar behavior.
---

# Rust Pest Parser

## When to Use This Skill

Use this skill when:
- Creating or modifying a Rust parser with `pest` or `pest_derive`
- Writing, reviewing, or debugging `.pest` grammar files
- Building typed ASTs from `Pair<Rule>` or `Pairs<Rule>`
- Handling `WHITESPACE`, `COMMENT`, string escapes, identifiers, numbers, or full-input parsing
- Implementing expression precedence or associativity with `PrattParser`

Do not use this skill for general Rust work unless parser grammar or parse-tree handling is central to the task.

## Core Workflow

1. Clarify the target input language or format. Identify whether the parser should validate input only, produce a parse tree, or build a typed AST.
2. Inspect the existing Rust project first. Check `Cargo.toml`, existing `.pest` files, parser modules, tests, and error handling style.
3. Design the grammar incrementally. Start with lexical atoms, then compose larger syntax rules, then add a root rule with `SOI ~ ... ~ EOI` when full-input parsing is required.
4. Choose parse-tree visibility intentionally. Use normal rules for AST-relevant nodes, silent rules `_` for helpers, atomic rules `@` for lexical tokens, and compound atomic rules `$` when whitespace must be disabled but inner pairs are still needed.
5. Integrate with Rust using `#[derive(Parser)]`, `#[grammar = "..."]`, and `ParserName::parse(Rule::root, input)`.
6. Inspect the parse tree before building abstractions. Use `as_rule()`, `as_str()`, `as_span()`, and `into_inner()` to confirm the actual pair structure.
7. Add tests for valid examples, invalid examples, trailing garbage, whitespace/comment variations, and AST conversion.
8. Debug failures by checking ordered choice order, greedy repetitions, atomicity, implicit whitespace, and missing `EOI`.

## Minimal Setup

Add dependencies unless the project already pins versions:

```toml
[dependencies]
pest = "2"
pest_derive = "2"
```

Create a grammar file under `src/`, because `#[grammar = "..."]` is relative to the crate `src` directory:

```pest
file = { SOI ~ item* ~ EOI }
item = { ident }
ident = @{ (ASCII_ALPHA | "_") ~ (ASCII_ALPHANUMERIC | "_")* }
WHITESPACE = _{ " " | "\t" | NEWLINE }
```

Define the parser:

```rust
use pest::Parser;
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "example.pest"]
struct ExampleParser;

fn parse(input: &str) -> Result<(), pest::error::Error<Rule>> {
    ExampleParser::parse(Rule::file, input)?;
    Ok(())
}
```

## Grammar Rules of Thumb

- Use `SOI ~ ... ~ EOI` for root rules that must consume the whole input.
- Put longer or more specific ordered-choice alternatives before shorter or broader ones.
- Remember that repetitions are greedy and pest does not backtrack after a successful expression consumes input.
- Define `WHITESPACE` and `COMMENT` as silent rules unless they must appear in the parse tree.
- Make identifiers, numbers, strings, and operators atomic when internal whitespace must be forbidden.
- Avoid left-recursive grammar such as `expr = { expr ~ "+" ~ term | term }`.
- Use `PrattParser` for expression precedence and associativity.
- Keep string escape matching and string escape interpretation separate. The grammar matches text; Rust code should interpret escapes if needed.

## Parse Tree Handling

Use `Pair` and `Pairs` directly until the parse tree shape is stable:

```rust
fn parse_value(pair: pest::iterators::Pair<Rule>) -> Value {
    match pair.as_rule() {
        Rule::number => Value::Number(pair.as_str().parse().unwrap()),
        Rule::string => Value::String(unescape(pair.as_str())),
        Rule::array => Value::Array(pair.into_inner().map(parse_value).collect()),
        _ => unreachable!("grammar only passes value rules here"),
    }
}
```

Use `pair.as_span()`, `span.start_pos()`, and `line_col()` when AST nodes or diagnostics need source locations.

## Testing and Debugging

Prefer parser tests close to the parser module:

```rust
#[test]
fn rejects_trailing_input() {
    assert!(ExampleParser::parse(Rule::file, "abc ???").is_err());
}
```

Useful commands:

```bash
cargo test
cargo run
cargo doc --open
```

Use `pest::parses_to!` and `pest::fails_with!` when parse-tree shape matters. Use the online pest editor at `https://pest.rs/#editor` for isolated grammar experiments.

## Common Pitfalls

- Missing `EOI` allows prefix-only parses to succeed.
- `"a" | "ab"` matches `"a"` first; it does not search for the longest alternative.
- `ANY* ~ ANY` fails on non-empty input because `ANY*` consumes everything.
- Implicit `WHITESPACE` is inserted between sequence elements and repetitions, not automatically around the entire root rule.
- Atomic rules disable implicit whitespace and hide inner token pairs.
- Silent rules remove pairs from the parse tree, which can break AST code if overused.
- `WHITESPACE` and `COMMENT` should usually match one unit; pest repeats them automatically.

## Detailed References

- [Grammar Concepts](references/grammar-concepts.md) - PEG semantics, rule modifiers, whitespace, built-ins, stack operations
- [Rust Integration](references/rust-integration.md) - dependencies, derive macro, `Pair`/`Pairs`, spans, errors
- [Patterns and Debugging](references/patterns-debugging.md) - common grammar patterns, expression parsing, tests, pitfalls
- Pest book grammar syntax: `https://pest.rs/book/grammars/syntax.html`
- Pest parser API: `https://pest.rs/book/parser_api.html`
- Pest Pratt parser: `https://pest.rs/book/precedence.html`
