---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# RayViT: Ray-Conditioned Visual Representations for Viewpoint-Robust Imitation Learning

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29622v1](https://arxiv.org/abs/2607.29622v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Visual imitation learning enables robots to acquire visuomotor skills directly from images, yet RGB observations lack explicit geometric cues, making learned policies brittle to camera perturbations. To address this, we propose \textbf{Ray-conditioned Vision Transformer Encoder (RayViT)}, a lightweight architecture that injects camera geometry into pretrained ViT backbones. RayViT represents camera geometry as a Plücker ray map, patchifies it into ray features, and uses gated cross-attention to produce a ray-conditioned class token. These ray features are added as dense positional embeddings, while the ray class token replaces the original ViT class token to provide a geometry-aware summary representation. We combine this approach with an auxiliary cosine similarity loss to consistently improve the performance and robustness for geometry-aware tokens. Experiments on sim- and real-robot tasks demonstrate that RayViT improves robustness by approximately 13 percentage points under camera perturbations in multi-task RoboCasa benchmark and by 1.78 average completed stages in real-world multi-task success rate compared to baselines.

## My Notes
