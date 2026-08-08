---
source: arxiv
category: agentic systems & rag
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# Beyond Top-K: Replacing Black-Box Retrieval with Interpretable Agentic Operations

- **Category Theme**: [[Agentic Systems & Rag]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06305v1](https://arxiv.org/abs/2608.06305v1)

## Curator Reasoning

Introduces READ, replacing top-k embedding retrieval on complex multi-page financial reports with deterministic MCP tools (lexical search, structural navigation, span reads), boosting accuracy from 15.7% to 58.8% with complete auditability.

## Summary / Abstract

Retrieval-augmented generation over long documents is dominated by one design: chunk the text, embed the chunks, and surface the top-k nearest neighbours of the query. We argue that for an important class of documents -- financial statements, audit reports, regulatory returns -- this design is structurally unsound, and we make the argument measurable. On a 780-page government financial report, 86.8% of content lines are table rows, thousands of near-identical figures compete in one embedding space, and a figure inherits its unit from a header a median of 13 lines above it -- so a chunk boundary routinely separates a number from whether it is in lakh or crore, an error of two orders of magnitude. A table-aware chunker built as a steelman fixes the unit problem but leaves 27-30% of numeric chunks with no fiscal-year header at every chunk size we tried. We propose READ (Reliable Embedding-free Agentic Document-search), in which an agent reads the raw document through three deterministic operations -- normalized lexical search, structural navigation, and bounded span reads -- exposed over the Model Context Protocol, so a trajectory is a replayable audit trail, not an opaque similarity score. On 51 verified questions READ answers 58.8% against dense retrieval's 15.7% (p_Holm = 2 x 10^-5) -- or 35.3% tuned, which READ still leads by 23.5 points (p_Holm = 0.017). An agent given the same loop but a top-k tool reaches only 27.5%, locating the gain in the interface rather than in iteration. We also report what the evidence does not support: BM25 is statistically indistinguishable from READ, so our result separates embedding-based from embedding-free retrieval, not agentic from lexical search.

## My Notes
