---
source: arxiv
category: physical robotics & humanoid safety control
created_at: 2026-07-31 21:46:59
status: triaged
tags:
  - triaged
---

# PAC-MAN: Perception-Aware CBF-RL for Whole-Body Safety in Humanoid Dodgeball

- **Category Theme**: [[Physical Robotics & Humanoid Safety Control]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28623v1](https://arxiv.org/abs/2607.28623v1)

## Curator Reasoning

Promoting PAC-MAN research paper (arXiv:2607.28623v1) directly addressing Priority 3: Control barrier function reinforcement learning (CBF-RL) for whole-body safety and balance in humanoid control.

## Summary / Abstract

We present PAC-MAN, a perception-aware CBF-RL framework that couples control-barrier safety with deployment-realistic onboard sensing for whole-body humanoid dodgeball. The deployed policy sees the ball only as segmentation-masked depth from a head-mounted camera, while training-time CBF guidance represents clearance to every body link, and an adversarial motion prior regularizes the resulting evasive reflexes. We evaluate on a controlled any-link contact benchmark with seeded throws in two regimes: single throws and a deployment loop in which the robot walks back to its station and recovers between throws. On this benchmark, the policy comes within a few points of a privileged state oracle: a fixed onboard camera alone is adequate for evasion. We find that usable barrier structure depends on perceptual observability: Joint-CBF gives the best performance with accurate ball states, degrades under fixed-camera observations when used only as training guidance, and recovers with a ball-tracking gimbal or privileged runtime filter. We therefore deploy a lightweight Link-CBF policy zero-shot on the Unitree G1 in the real world, where it tolerates imperfect perception, succeeds on 95% of throws, and uses semantic segmentation to dodge different balls.

## My Notes
