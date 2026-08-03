---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# QASP: Query-Adaptive Robust Vector Search Policy

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29606v1](https://arxiv.org/abs/2607.29606v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

A fundamental challenge of vector search is achieving consistently high recall while minimizing computational costs. Fixed search parameters cause significant performance variance across queries, and conventional evaluation on average recall masks these per-query disparities. We introduce QASP (Query-Adaptive robust vector Search Policy), which predicts the complete recall progression curve per query via a single upfront supervised regression, from which a search policy is derived for any recall target; this avoids iterative model invocations during search or separate predictors per target. By predicting normalized recall values with scale-invariant features and pre-search inference, QASP generalizes across recall targets, index configurations, and datasets. Its fine-grained progress predictions further enable a lightweight reactive complement that adjusts search depth based on predicted-versus-observed deviations without additional inference. We prove that QASP requires a finite training sample independent of dataset size and dimensionality, that its loss exceeds the irreducible lower bound of any fixed policy by a vanishing margin, and that its data access savings over fixed probing grow exponentially in intrinsic dimensionality. Experimentally, QASP achieves significantly lower recall variance and deviation from target, higher query satisfaction rate, and scales to large data and hierarchical indices without retraining, achieving 99% recall with 80% less data access.

## My Notes
