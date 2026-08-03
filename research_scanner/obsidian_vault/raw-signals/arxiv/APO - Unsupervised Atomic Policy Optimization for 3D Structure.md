---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# APO: Unsupervised Atomic Policy Optimization for 3D Structure Prediction of Atomic Systems

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28553v1](https://arxiv.org/abs/2607.28553v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Predicting the 3D structures of atomic systems is fundamental to advancing material science and drug discovery. While flow-matching models (, FlowDPO) have recently shown promise in this domain, their performance relies heavily on alignment with ground-truth coordinates via supervised preference learning. However, obtaining experimental labels for novel crystal phases or de novo proteins is prohibitively expensive, creating a bottleneck for structural modeling in data-scarce regimes. In this work, we propose (Atomic Policy Optimization), a fully unsupervised alignment framework that eliminates the need for ground-truth reference structures. APO adapts group-relative policy optimization to 3D atomic environments, utilizing a novel dual-reward mechanism: (i) a that reinforces the policy's dominant latent structural modes through eigen-decomposition of sample similarities, and (ii) a that enforces thermodynamic stability. Our framework enables the model to ``self-correct'' by identifying physically plausible configurations within sampled groups. Extensive benchmarks on crystal and antibody structure prediction demonstrate that APO consistently outperforms fully supervised baselines, achieving a new state-of-the-art in match rates and structural fidelity. Furthermore, we show that APO effectively straightens probability paths, significantly improving inference efficiency. Our results suggest that intrinsic physical consistency can serve as a superior guide for alignment compared to noisy, supervised coordinate matching.

## My Notes
