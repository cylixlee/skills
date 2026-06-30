# Patterns and Debugging

## Root Rule

Use a root rule that consumes the whole input:

```pest
file = { SOI ~ statement* ~ EOI }
```

Without `EOI`, invalid trailing input can be ignored because a prefix parse may succeed.

## Identifiers and Keywords

ASCII identifiers:

```pest
ident = @{ (ASCII_ALPHA | "_") ~ (ASCII_ALPHANUMERIC | "_")* }
```

Unicode identifiers:

```pest
ident = @{ XID_START ~ XID_CONTINUE* }
```

Put keywords before identifiers and guard keyword boundaries:

```pest
keyword = { "while" ~ !ASCII_ALPHANUMERIC }
token = { keyword | ident }
```

## Numbers

JSON-like number grammar:

```pest
number = @{
    "-"?
    ~ ("0" | ASCII_NONZERO_DIGIT ~ ASCII_DIGIT*)
    ~ ("." ~ ASCII_DIGIT+)?
    ~ (^"e" ~ ("+" | "-")? ~ ASCII_DIGIT+)?
}
```

Use `@` so whitespace cannot appear inside the number.

## Strings and Escapes

Common escaped string shape:

```pest
string = ${ "\"" ~ inner ~ "\"" }
inner = @{ char* }
char = {
    !("\"" | "\\") ~ ANY
    | "\\" ~ ("\"" | "\\" | "/" | "b" | "f" | "n" | "r" | "t")
    | "\\" ~ ("u" ~ ASCII_HEX_DIGIT{4})
}
```

The grammar validates escape syntax. Rust code must still convert escape sequences into actual string values if the AST needs decoded strings.

Source: `https://pest.rs/book/examples/json.html`

## Expressions

Do not use left recursion:

```pest
// Bad
expr = { expr ~ "+" ~ term | term }
```

Use a flat PEG-friendly grammar and handle precedence in Rust with `PrattParser`:

```pest
expr = { prefix? ~ primary ~ postfix? ~ (infix ~ prefix? ~ primary ~ postfix?)* }
primary = { int | "(" ~ expr ~ ")" }
infix = _{ add | sub | mul | div | pow }
add = { "+" }
sub = { "-" }
mul = { "*" }
div = { "/" }
pow = { "^" }
```

```rust
use pest::pratt_parser::{Assoc, Op, PrattParser};

let pratt = PrattParser::new()
    .op(Op::infix(Rule::add, Assoc::Left) | Op::infix(Rule::sub, Assoc::Left))
    .op(Op::infix(Rule::mul, Assoc::Left) | Op::infix(Rule::div, Assoc::Left))
    .op(Op::infix(Rule::pow, Assoc::Right));
```

Source: `https://pest.rs/book/precedence.html`

## Testing

Test categories to include:

- Minimal valid input
- Complex valid input
- Invalid syntax
- Invalid trailing input to prove `EOI` works
- Whitespace and comment variations
- String escapes
- Identifier and keyword boundaries
- AST conversion shape and values

Useful commands:

```bash
cargo test
cargo run
cargo doc --open
```

Use `pest::parses_to!` and `pest::fails_with!` for detailed parse-tree assertions when appropriate.

## Debugging Checklist

When a grammar behaves unexpectedly, check:

- Is the root rule missing `EOI`?
- Is an earlier ordered-choice alternative stealing input?
- Is a greedy repetition consuming too much?
- Should a lexical rule be atomic?
- Is an atomic rule accidentally suppressing needed inner pairs?
- Is a silent rule hiding a node needed by AST conversion?
- Is implicit `WHITESPACE` allowed or forbidden in the intended places?
- Is the expression grammar left-recursive?
- Does a keyword need a negative predicate boundary?

Useful resources:

- Pest editor: `https://pest.rs/#editor`
- Parser API: `https://pest.rs/book/parser_api.html`
- Calculator example: `https://pest.rs/book/examples/calculator.html`
