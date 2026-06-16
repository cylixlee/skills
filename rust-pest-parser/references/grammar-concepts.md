# Grammar Concepts

## PEG Semantics

`pest` uses Parsing Expression Grammars. Parsing is deterministic and ordered:

- A sequence consumes input as each expression succeeds.
- A failed expression consumes nothing.
- Ordered choice `a | b` tries `a` first and only tries `b` if `a` fails.
- Repetitions such as `*` and `+` are greedy.
- Pest does not do regex-style backtracking after a successful expression consumes input.

Important examples:

```pest
choice = { "ab" | "a" }  // prefer this order when both can match
bad = { ANY* ~ ANY }      // fails on non-empty input
```

Source: `https://pest.rs/book/grammars/peg.html`

## Rule Syntax

Common grammar expressions:

```pest
rule = { expression }
exact = { "abc" }
case_insensitive = { ^"abc" }
range = { 'a'..'z' }
seq = { a ~ b }
choice = { a | b }
repeat = { a* ~ b+ ~ c? }
bounded = { ASCII_DIGIT{2, 4} }
positive_lookahead = { &a ~ b }
negative_lookahead = { !a ~ ANY }
```

Source: `https://pest.rs/book/grammars/syntax.html`

## Rule Modifiers

Normal rules produce `Pair`s:

```pest
object = { "{" ~ pair* ~ "}" }
```

Silent rules `_` parse normally but do not produce pairs:

```pest
value = _{ object | array | string | number }
```

Atomic rules `@` disable implicit whitespace inside themselves, cascade atomic behavior into called rules, and suppress inner pairs:

```pest
number = @{ "-"? ~ ASCII_DIGIT+ ~ ("." ~ ASCII_DIGIT+)? }
```

Compound atomic rules `$` disable implicit whitespace but preserve inner pairs:

```pest
string = ${ "\"" ~ inner ~ "\"" }
inner = @{ char* }
```

Non-atomic rules `!` cancel inherited atomic behavior. Use them for cases such as interpolated expressions inside atomic strings.

Source: `https://pest.rs/book/grammars/syntax.html#silent-and-atomic-rules`

## Whitespace and Comments

If `WHITESPACE` or `COMMENT` exists, pest inserts it automatically between sequence elements and repetitions except inside atomic rules:

```pest
WHITESPACE = _{ " " | "\t" | "\r" | "\n" }
COMMENT = _{ "//" ~ (!NEWLINE ~ ANY)* }
```

Guidelines:

- Make them silent with `_` unless they must be visible.
- Match one whitespace or comment unit; pest repeats them automatically.
- Use a root rule such as `file = { SOI ~ item* ~ EOI }` to allow leading and trailing implicit whitespace.
- Use atomic lexical rules when spaces must not be accepted inside tokens.

Source: `https://pest.rs/book/grammars/syntax.html#implicit-whitespace`

## Built-ins

Useful built-in rules include:

```pest
ANY
SOI
EOI
NEWLINE
ASCII_DIGIT
ASCII_NONZERO_DIGIT
ASCII_ALPHA
ASCII_ALPHANUMERIC
ASCII_HEX_DIGIT
XID_START
XID_CONTINUE
```

Use `XID_START` and `XID_CONTINUE` for Unicode identifiers when the target language follows Unicode identifier conventions.

Source: `https://pest.rs/book/grammars/built-ins.html`

## Stack Operations

Pest has grammar-level stack operations for matching previously captured text:

```pest
raw_string = {
    "r" ~ PUSH("#"*) ~ "\""
    ~ raw_string_inner
    ~ "\"" ~ POP
}

raw_string_inner = { (!("\"" ~ PEEK) ~ ANY)* }
```

Use stack operations for variable delimiters, raw strings, paired markers, or indentation-sensitive grammars. Operations include `PUSH`, `PEEK`, `POP`, `DROP`, `PEEK_ALL`, and indexed `PEEK` variants.

Source: `https://pest.rs/book/grammars/syntax.html#the-stack`
