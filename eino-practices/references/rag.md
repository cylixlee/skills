# RAG (Retrieval Augmented Generation)

RAG is a technique combining retrieval and generation, enhancing LLM outputs by fetching relevant information from a knowledge base.

## RAG Architecture

```
User Query → Embedding → Vector Retrieval → Knowledge Chunks → LLM Generation → Final Answer
```

## Embedding

Embedding converts text to vector representations:

```go
import (
    "github.com/cloudwego/eino/components/embedding"
    "github.com/cloudwego/eino/components/embedding/openai"
)

emb, err := openai.NewEmbedding(ctx, &openai.EmbeddingConfig{
    Model: "text-embedding-3-small",
    APIKey: key,
})
```

### Generating Embeddings

```go
text := "The quick brown fox jumps over the lazy dog"
vectors, err := emb.EmbedStrings(ctx, []string{text})
// vectors[0] is a slice of floats
```

## Retriever

Retriever fetches relevant information from knowledge base based on query:

```go
import "github.com/cloudwego/eino/components/retriever"
```

### Creating a Retriever

```go
r := retriever.FromEmbeddings(emb,
    retriever.WithTopK(5),
    retriever.WithScoreThreshold(0.8),
)
```

### Executing Retrieval

```go
docs, err := r.Retrieve(ctx, "What is Go language?")
// docs is []*schema.Document
```

## Document

Document is the basic unit of retrieval:

```go
type Document struct {
    Content    string
    Metadata   map[string]any
    Score      float64
}
```

### Document Fields

| Field      | Description                               |
| ---------- | ----------------------------------------- |
| `Content`  | Document content text                     |
| `Metadata` | Additional metadata (source, title, etc.) |
| `Score`    | Relevance score                           |

## Complete RAG Flow

```go
func ragQuery(ctx context.Context, query string) (string, error) {
    emb, _ := openai.NewEmbedding(ctx, &openai.EmbeddingConfig{
        Model: "text-embedding-3-small",
        APIKey: os.Getenv("OPENAI_API_KEY"),
    })

    r := retriever.FromEmbeddings(emb,
        retriever.WithTopK(3),
    )

    docs, err := r.Retrieve(ctx, query)
    if err != nil {
        return "", err
    }

    context := ""
    for _, doc := range docs {
        context += doc.Content + "\n---\n"
    }

    template := prompt.FromMessages(schema.FString,
        schema.SystemMessage("Use the following context to answer the question."),
        schema.UserMessage("Context:\n{context}\n\nQuestion: {query}"),
    )

    messages, _ := template.Format(ctx, map[string]any{
        "context": context,
        "query":   query,
    })

    result, err := chatModel.Generate(ctx, messages)
    if err != nil {
        return "", err
    }

    return result.Content, nil
}
```

## Vector Store

Vector Store persists Embeddings:

```go
import "github.com/cloudwego/eino/components/vectorstore"
```

### Common Vector Stores

| Type     | Description                 |
| -------- | --------------------------- |
| Milvus   | Distributed vector database |
| Pinecone | Cloud vector service        |
| Qdrant   | Lightweight vector engine   |
| Chroma   | Local vector library        |

### Basic Operations

```go
vs, _ := milvus.New(ctx, &milvus.Config{
    Host: "localhost",
    Port: 19530,
})

// Add documents
docs := []*schema.Document{
    {Content: "Go is a programming language", Metadata: map[string]any{"source": "doc1"}},
}
err := vs.AddDocuments(ctx, docs)

// Similarity search
results, err := vs.SimilaritySearch(ctx, "What is Go?", 5)
```

## Advanced RAG Patterns

### Chunking Strategies

```go
type ChunkStrategy interface {
    Split(text string) []string
}

splitter := document.NewRecursiveCharacterTextSplitter(
    document.WithChunkSize(500),
    document.WithChunkOverlap(50),
)

chunks := splitter.SplitText(longDocument)
```

### Hybrid Search

Combines keyword and vector retrieval:

```go
r := retriever.NewHybridRetriever(
    vectorRetriever,
    keywordRetriever,
    retriever.WithFusionMethod("rrf"),  // Reciprocal Rank Fusion
)
```

### Re-ranking

Re-rank retrieval results:

```go
rr := rerank.NewCohereReranker(ctx, &cohere.RerankerConfig{
    APIKey: key,
})

reranked := rr.Rerank(query, docs, 10)
```

## Related APIs

- `embedding.EmbedStrings` - Generate text vectors
- `retriever.Retrieve` - Execute retrieval
- `vectorstore.AddDocuments` - Add documents
- `vectorstore.SimilaritySearch` - Similarity search

## Related Packages

- `github.com/cloudwego/eino/components/embedding`
- `github.com/cloudwego/eino/components/retriever`
- `github.com/cloudwego/eino/components/vectorstore`
- `github.com/cloudwego/eino/components/document`
