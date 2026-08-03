---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# Safe Vision Language Action Models via Barrier Enhanced Flow Matching

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29569v1](https://arxiv.org/abs/2607.29569v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

This article presents a modular inference framework that integrates Flow Matching generative models with formal Control Barrier Function (CBF) safety guarantees. Unlike existing methods that apply external safety filters to a model's final output, our approach modifies the Flow Matching denoising process within the model to inherently generate safe trajectories. By employing a smooth Log-Sum-Exponential aggregate barrier, we enforce safety over entire action chunks. This aggregate barrier ensures a minimal increase in computational overhead and does not alter the semantic intent of the model. We show that, within the proposed framework, the 2-Wasserstein distance between the generated distribution and the target distribution remains bounded. Our method eliminates the need for safety-specific datasets or costly model retraining, providing a versatile solution for safe inference. We validate the approach on two robotic manipulation platforms and a 2D navigation benchmark, verifying that our framework achieves reliable safety without degrading the success rate of the model.

## My Notes
