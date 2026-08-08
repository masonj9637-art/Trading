---
source: arxiv
category: llm reasoning & alignment
created_at: 2026-08-08 14:21:57
status: triaged
tags:
  - triaged
---

# Learning When to Trust via Selective Context Preference Optimization

- **Category Theme**: [[Llm Reasoning & Alignment]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06377v1](https://arxiv.org/abs/2608.06377v1)

## Curator Reasoning

Introduces the MIST benchmark and SCOPE DPO preference optimization framework for selective trust in LLMs. Solves a major vulnerability in RAG and context-conditioned reasoning where models either blindly trust misleading signals or ignore valid context completely.

## Summary / Abstract

Language models increasingly condition their answers on external signals, and a single misleading one can turn a correct answer wrong. The obvious remedy, training models to resist such signals, hides a failure mode: a model that ignores all context looks robust yet is useless when the context is worth trusting. We recast the problem as selective trust and introduce MIST, a human-annotated benchmark that renders each reasoning item under four matched conditions (clean, misleading, correct-context, and irrelevant-context), together with SC2W, a paired metric counting how often a misleading signal flips a clean-correct answer to wrong. Across a comprehensive benchmark study, we observe that such a susceptibility is universal. We then propose SCOPE, which mines clean-correct/misleading-wrong failures and optimizes a standard Direct Preference Optimization (DPO) objective over matched preference pairs balanced equally across all four conditions, rather than over misleading items alone. Our approach substantially reduces SC2W on popular open-sourced models while preserving accuracy when the added context is clean, correct, or irrelevant. With this work, we argue that models should be judged on selective trust, not on resistance alone.

## My Notes
