---
source: arxiv
category: agentic systems & benchmarking
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# HarnessOpt-Bench: Evaluating LLMs at Harness Optimization

- **Category Theme**: [[Agentic Systems & Benchmarking]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06301v1](https://arxiv.org/abs/2608.06301v1)

## Curator Reasoning

Introduces HarnessOpt-Bench to benchmark LLMs at automated, evaluation-guided harness optimization (editing prompts, tools, memory, and orchestration code), establishing a standardized evaluation protocol for self-improving agents.

## Summary / Abstract

As LLMs are increasingly deployed within agentic systems, their capabilities depend not only on the model weights but also on the harness: the prompts, tools, control flow, memory, and orchestration code surrounding them. This makes automated harness optimization -- the iterative and evaluation-guided improvement of a harness by an AI system -- both an important route to improving AI systems and a demanding capability for AI systems themselves. Yet the community lacks a common protocol for measuring how well frontier LLMs perform at this task. We introduce HarnessOpt-Bench, a benchmark for end-to-end harness optimization under expensive and stochastic evaluation. An optimizer, an LLM paired with a coding harness, receives a target agent's seed harness, graded evaluation feedback, and a fixed target-evaluation budget. It edits the harness and nominates a final candidate, which is scored by its normalized gain over the seed on a held-out test partition that remains inaccessible throughout search. A trusted execution environment enforces the evaluation boundary, meters target-agent resource use, and preserves candidate versions for audit. We evaluate 5 frontier LLMs as optimizers both under a shared coding harness and under their native harnesses across 4 downstream tasks, over 111 scored runs. Experiment results show that optimizer models separate more than the coding harnesses they act through, native harnesses are not consistently superior, and gains vary substantially across tasks and seed regimes. These results establish harness optimization as a measurable and discriminative capability with large space for improvement.

## My Notes
