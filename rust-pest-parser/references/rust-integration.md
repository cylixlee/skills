# Rust Integration

## Dependencies

Prefer existing project versions. For a new project, use compatible `2.x` versions:

```toml
[dependencies]
pest = "2"
pest_derive = "2"
```

Use `cargo add pest pest_derive` when the project accepts `cargo add` changes.

Source: `https://pest.rs/book/examples/csv.html`

## Parser Derive

Place `.pest` files under `src/`. The `#[grammar = "..."]` path is relative to the crate `src` directory:

```rust
use pest::Parser;
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "parser/grammar.pest"]
pub struct MyParser;
```

Inline grammar is possible but should usually be limited to tiny examples or tests:

```rust
#[derive(Parser)]
#[grammar_inline = "file = { SOI ~ EOI }"]
struct EmptyParser;
```

Sources:

- `https://docs.rs/pest/latest/pest/#pest-files`
- `https://docs.rs/pest_derive/latest/pest_derive/derive.Parser.html`

## Parsing Entry Point

The derived parser exposes:

```rust
ParserName::parse(Rule::some_rule, input)
```

The return type is:

```rust
Result<pest::iterators::Pairs<Rule>, pest::error::Error<Rule>>
```

Typical full parse:

```rust
let file = MyParser::parse(Rule::file, input)?
    .next()
    .expect("root rule should produce one pair");
```

Source: `https://pest.rs/book/parser_api.html#the-parse-method`

## Pair and Pairs

Use `Pair<Rule>` for one matched rule and `Pairs<Rule>` for child iterators:

```rust
fn walk(pair: pest::iterators::Pair<Rule>) {
    match pair.as_rule() {
        Rule::ident => println!("{}", pair.as_str()),
        Rule::item => {
            for child in pair.into_inner() {
                walk(child);
            }
        }
        _ => {}
    }
}
```

Common methods:

```rust
pair.as_rule()
pair.as_str()
pair.as_span()
pair.into_inner()
```

Source: `https://pest.rs/book/parser_api.html#pairs`

## Spans and Diagnostics

Use spans when the AST or error reporting needs source locations:

```rust
let span = pair.as_span();
let start = span.start_pos();
let end = span.end_pos();
let (line, col) = start.line_col();
```

Source: `https://pest.rs/book/parser_api.html#spans-and-positions`

## Error Handling

Parsing errors implement `Display` and are suitable for user-facing messages. Useful APIs include:

```rust
let err = err.with_path(path);
let line = err.line();
let location = err.location;
```

For friendlier diagnostics, consider `renamed_rules`. For debugging difficult grammar failures, enable detailed errors with `pest::set_error_detail(true)`, but avoid leaving expensive debug settings enabled without reason.

Source: `https://docs.rs/pest/latest/pest/error/struct.Error.html`
