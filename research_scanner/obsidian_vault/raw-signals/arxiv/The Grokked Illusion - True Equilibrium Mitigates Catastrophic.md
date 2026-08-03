---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:24
status: triaged
---

# The Grokked Illusion: True Equilibrium Mitigates Catastrophic Forgetting

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29503v1](https://arxiv.org/abs/2607.29503v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

While neural networks are typically evaluated by their training and test performance, these metrics do not reveal how robust a learned representation is. Recent studies have shown that solutions occupying larger volumes in parameter space, as quantified by Boltzmann entropy, often exhibit superior generalizability compared to those reached by conventional optimization, a phenomenon known as the high entropy advantage. Here we ask whether this advantage persists beyond generalization. Specifically, we investigate models' robustness, the ability to retain the learned knowledge when the model is subsequently trained to acquire new information. Using grokking in modular arithmetic as a controlled setting, we design a noise injection experiment to evaluate the robustness difference between AdamW-trained transformers and high-entropy model sampled from Wang-Landau Molecular Dynamics with identical saturated performance. By forcing both models to fully remember new data with random labels, we find that AdamW-trained models suffer from catastrophic forgetting, with original task test accuracy dropping from 100% to below 75%, whereas the high-entropy models maintain approximately 95% test accuracy. We term this hidden fragility behind apparent generalization the "grokked illusion." Through singular value decomposition of the neural network weights, we discover that high-entropy neural networks possess significantly higher effective rank in attention and MLP layers both before and after noise injection, indicating richer feature representations can serve as a buffer against catastrophic forgetting. Our findings demonstrate that perfect generalization does not imply equal robustness, offering a new perspective on what makes a trained model robust to interference.

## My Notes
