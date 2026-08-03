---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# TraceViT: Grounded Trace Supervision for Visual Abstract Reasoning

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29586v1](https://arxiv.org/abs/2607.29586v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

The Abstraction and Reasoning Corpus (ARC) tests whether a model can infer an unseen transformation from a few input-output examples and apply it to a new grid. Looped visual reasoners refine predictions over multiple iterations, but conventional training constrains only the final output, leaving intermediate refinements unconstrained. We propose that these refinements should instead follow the transformation step by step. We introduce TraceViT, a looped visual reasoner trained with semantically monotonic transformation chains. We obtain these chains by rewriting and verifying programmatic task implementations, decomposing each solution into intermediate grid states. Each iteration is grounded by a task reference derived from the few-shot demonstrations and an object workspace representing the current grid state. Because these chains may differ in length from the loop, soft trace alignment enforces only their ordering, letting the model allocate iterations freely. TraceViT achieves 67.8% pass@2 on ARC-AGI-1 and 24.3% on ARC-AGI-2. Controlled ablations on ARC-AGI-1 show that trace supervision becomes beneficial only when paired with grounding. Code and data will be available at https://github.com/LiuBinnan/TraceViT.

## My Notes
