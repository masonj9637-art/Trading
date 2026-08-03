---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# TCA-SIR: Learning Target-Conditioned Abstractions for Scientific Inspiration Retrieval

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28498v1](https://arxiv.org/abs/2607.28498v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Scientific hypothesis generation for AI for Science typically involves Scientific Inspiration Retrieval (SIR) followed by hypothesis composition. Existing SIR methods rank papers by topical similarity and do not explicitly represent how a candidate inspiration transfers to a target problem. This is especially limiting for remote inspirations, whose value often lies in reusable problem-solving principles rather than topical overlap. Motivated by how humans abstract transferable aspects of a source and remap them to a new target, we reformulate SIR as target-conditioned abstraction (TCA). The retrieval object is a transferable abstract principle extracted from a candidate specifically for the target. We present TCA-SIR, which learns to generate target-conditioned abstractions and uses their representations to predict transferability. On ResearchBench, TCA-SIR outperforms prior SIR methods and direct LLM retrieval, improving HitRate@top4% over MOOSE-Chem by more than 10 percentage points. Learned abstractions also recover target-relevant mechanisms more clearly than an untrained TCA prompt, yielding both stronger retrieval and an interpretable rationale for scientific inspiration.

## My Notes
