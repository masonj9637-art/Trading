---
source: arxiv
category: robotics & embodied ai
created_at: 2026-08-08 14:21:57
status: triaged
tags:
  - triaged
---

# $ω$-0: A Latent Predictive World Action Model for Concurrent Humanoid Loco-Manipulation

- **Category Theme**: [[Robotics & Embodied AI]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06375v1](https://arxiv.org/abs/2608.06375v1)

## Curator Reasoning

Presents \(\omega\)-0, a latent predictive world-action model for humanoid loco-manipulation predicting whole-body action latents directly from visual/proprioceptive states. Validated on physical humanoid hardware across 11 household tasks with an open 40+ hour dataset.

## Summary / Abstract

Humanoid household tasks often require concurrent loco-manipulation, where the robot must move, adjust posture, maintain balance, and manipulate objects as a single coordinated behavior. Yet existing humanoid policies typically decompose locomotion and manipulation, while recent world-action models remain either arm-centric or video-centered. We present $ω$-0, a latent predictive whole-body world-action model for real-world humanoid concurrent loco-manipulation. Given a language instruction, current visual observation, and robot proprioceptive state, $ω$-0 directly predicts controller-compatible whole-body action latents for real-robot execution. Rather than reconstructing future videos, $ω$-0 learns compact future observation embeddings as a lightweight predictive objective, coupling latent visual foresight with diffusion-based whole-body action generation. The model supports egocentric RGB, exocentric RGB, and exocentric depth inputs, and leverages controller-based simulation replay to ground human/public visual-motion priors into robot-executable action latents. We further collect $ω$-HOME, a 40+ hour real-world household humanoid dataset with synchronized multi-view observations, whole-body SMPL motions, robot states, and action latents. Real-world experiments on 11 household tasks demonstrate that a single $ω$-0 model can produce smooth manipulate-while-moving behaviors and consistently outperform representative imitation learning, VLA, humanoid, and WAM baselines.

## My Notes
