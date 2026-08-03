---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# FA-RDP: A Frequency-Adaptive Reactive Diffusion Policy for Contact-Rich Manipulation

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28596v1](https://arxiv.org/abs/2607.28596v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

In contact-rich manipulation, action multimodality and reactivity dominate different stages of a single episode. Before contact, multiple trajectories might be equally valid, making it important to preserve diverse action modes. After contact, geometric constraints and force limits narrow the solution space, while successful execution demands rapid responses to force feedback. However, standard diffusion policies use a fixed inference frequency and sampling steps throughout the episode, forcing a fundamental compromise: low-frequency, multi-step sampling better preserves pre-contact multimodality but responds slowly to force feedback, whereas high-frequency sampling improves reactivity but tends to collapse distinct pre-contact modes. To resolve this tradeoff, we present FA-RDP, a frequency-adaptive reactive diffusion policy. A shared multi-frequency visual-force Transformer predicts action chunks at both low and high frequencies, while a learned multimodality indicator dynamically selects multi-step low-frequency sampling before contact and one-step high-frequency sampling as action ambiguity decreases. We further introduce Manifold Consistency Distillation (MCD), which reparameterizes the diffusion network to predict actions on the robot action manifold while retaining DDPM-based residual supervision. Experiments on three contact-rich manipulation tasks show that FA-RDP achieves the highest success rate while preserving diverse pre-contact trajectory modes. Code and videos are available at https://fa-rdp.github.io.

## My Notes
