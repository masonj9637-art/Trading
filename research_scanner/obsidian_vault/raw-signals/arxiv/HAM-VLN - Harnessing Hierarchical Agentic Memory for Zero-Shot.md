---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# HAM-VLN: Harnessing Hierarchical Agentic Memory for Zero-Shot Vision-and-Language Navigation

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29600v1](https://arxiv.org/abs/2607.29600v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Vision-and-language navigation (VLN) enables robots to follow instructions in previously unseen environments. Recently, a training-free paradigm has emerged: the robot queries a multimodal LLM to understand its observations and plan the next action. However, long-horizon navigation based on either image streams or dense map inevitably introduces a growing memory and reasoning bottleneck. We present HAM-VLN, a decision-coupled, agent-authored memory that equips the robot with a persistent, depth-grounded world graph. In the same model call used to select the next action, HAM-VLN also records semantic and reflective information---including room type, objects, navigation progress, and failure notes. Recent waypoints remain verbatim within a bounded window, while older history re-enters the context only through retrieval scored by relevance, recency, and salience, together with one-hop topological expansion. This design requires no additional LLM calls beyond the per-waypoint decision. Compared to previous methods, HAM-VLN not only improves various navigation metrics but also reduces the context length by more than 65%. Specifically, HAM-VLN achieves 61.0% Success Rate (SR) on VLN-CE R2R, 52.7% SR on VLN-CE RxR, and 79.7% SR on HM3D-v2 ObjectNav without any training.

## My Notes
