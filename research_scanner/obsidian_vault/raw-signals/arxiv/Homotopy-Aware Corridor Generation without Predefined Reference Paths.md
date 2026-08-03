---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# Homotopy-Aware Corridor Generation without Predefined Reference Paths

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29513v1](https://arxiv.org/abs/2607.29513v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Generating safe corridors is essential for collision-free robotic motion planning, yet most existing methods rely on predefined reference paths, which bias corridor geometry and implicitly limit the homotopy classes that can be explored. We propose a reference-path-free corridor generation framework on graphs of convex sets (GCS) that constructs corridors directly as sequences of convex sets, allowing corridor structure to emerge from the free-space representation rather than from a guiding path. To reason about similarity among corridors, we extend visibility-based deformation from paths to convex-set sequences, enabling the fusion of topologically redundant corridors while preserving distinct alternatives. To overcome the limited adaptability of existing GCS methods based on static global decompositions, we further develop an adaptive multi-scale GCS, in which a sampling-based fine-scale graph supports localized updates and a visibility-based coarse-scale graph enables compact global exploration. The two levels maintain topological consistency, allowing incremental updates without full graph reconstruction under environmental uncertainty. Numerical experiments characterize GCS construction, corridor generation, homotopy-aware exploration, and local updates, showing efficient graph construction, stable trajectory-level performance, and shorter-duration homotopy-aware trajectories than existing baselines. Hardware experiments on ground and aerial robots, including deployment with onboard localization, further validate the framework under translated and previously unknown obstacles.

## My Notes
