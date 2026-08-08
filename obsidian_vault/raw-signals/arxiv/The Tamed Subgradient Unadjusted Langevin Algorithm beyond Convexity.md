---
source: arxiv
category: optimization & ml theory
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# The Tamed Subgradient Unadjusted Langevin Algorithm beyond Convexity

- **Category Theme**: [[Optimization & Ml Theory]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06283v1](https://arxiv.org/abs/2608.06283v1)

## Curator Reasoning

Develops Subgradient Tamed Unadjusted Langevin Algorithm (SG-TULA) for non-smooth, non-convex potentials with explicit non-asymptotic Wasserstein-2 convergence bounds, demonstrating competitive pretraining performance on LLM potentials.

## Summary / Abstract

We study the problem of sampling from target distributions whose potentials are simultaneously non-smooth, subject to superlinear gradient growth, and non-convex. We introduce the Subgradient Tamed Unadjusted Langevin Algorithm (SG-TULA), a discretisation of the Langevin diffusion that operates directly on subgradients, without relying on computationally demanding smoothing procedures. To handle the superlinear regime, taming techniques are employed to produce a stable, explicit scheme. We derive non-asymptotic convergence bounds in Wasserstein-2 distance, with all constants tracked explicitly in terms of dimension and inverse temperature, improving upon the currently known rates for subgradient-based Langevin algorithms. We further provide excess risk estimates for the associated optimisation problem. We verify the assumptions, with explicit constants, for the regularized pretraining potential of a LLM in the GPT-2 lineage and the boosted coordinate-wise variant of SG-TULA pretrains the former competitively against finetuned AdamW and Muon, for which no comparable non-asymptotic guarantees are presently available.

## My Notes
