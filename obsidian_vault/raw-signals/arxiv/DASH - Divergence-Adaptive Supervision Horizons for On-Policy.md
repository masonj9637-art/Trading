---
source: arxiv
category: llm post-training & reasoning
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# DASH: Divergence-Adaptive Supervision Horizons for On-Policy Self-Distillation of Reasoning Models

- **Category Theme**: [[Llm Post-training & Reasoning]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06243v1](https://arxiv.org/abs/2608.06243v1)

## Curator Reasoning

Introduces Divergence-Adaptive Supervision Horizons (DASH) for OPSD, using discrepancy history propagation gates to dynamically adjust token-level self-distillation weights without extra model forward passes.

## Summary / Abstract

Reinforcement learning with verifiable rewards (RLVR) improves the reasoning capabilities of large language models using automatically verifiable outcome signals, but these signals are typically sparse and at the sequence-level. On-policy self-distillation (OPSD) mitigates this sparsity by querying a privileged teacher at student-visited prefixes and providing dense token-level distributional supervision. Although this dense supervision alleviates signal sparsity, we find that standard OPSD still underexploits the temporal structure of the rollout. It assigns every local divergence the same coefficient, regardless of its position or the divergence sequence in which it occurs. In on-policy autoregressive generation, the same divergence magnitude can follow different discrepancy histories, reflecting different evolutions of the mismatch between the teacher and student. Since the local scalar alone cannot distinguish these temporal contexts, standard OPSD cannot adapt its token-level weights to the realized discrepancy sequence. To address this limitation, we propose Divergence-Adaptive Supervision Horizons (DASH). DASH maps the gap between each local distillation signal and the sequence-level mean to an adaptive propagation gate and then uses these gates to control backward multi-step aggregation. By doing so, DASH adjusts token-level supervision weights according to how local divergences evolve during generation. Experiments on three mathematical reasoning benchmarks across three model scales show that DASH improves over our matched vanilla OPSD reruns on every benchmark at all three scales. DASH reuses the teacher and student distributions that OPSD already computes, so the gains require no additional teacher or student forward pass. Code: https://github.com/DBtxy/DASH-OPSD

## My Notes
