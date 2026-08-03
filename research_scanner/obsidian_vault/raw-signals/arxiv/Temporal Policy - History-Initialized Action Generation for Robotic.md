---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:24
status: triaged
---

# Temporal Policy: History-Initialized Action Generation for Robotic Learning from Demonstration

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29482v1](https://arxiv.org/abs/2607.29482v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

By relying on independent couplings from uninformative Gaussian priors, standard diffusion and flow matching models are forced to learn complex, high-cost vector fields to reach the physical action space. Generative models excel at capturing multimodal behaviors for robotic Learning from Demonstration (LfD), but often suffer from high inference cost. This paper introduces Temporal Policy, a generative framework based on stochastic interpolants that formulates action generation as a temporally coupled transport problem. By initializing the generative flow at the robot's recent history, we explicitly couple past states to future action sequences. This data-dependent coupling reduces transport cost and produces straight vector fields. We validate Temporal Policy across visuomotor simulation benchmarks and on a physical Barrett WAM 2x 7DoF teleoperation platform. Our approach reduces transport costs by nearly an order of magnitude compared to noise-initialized baselines, achieving a 19.1 ms inference latency on a single NVIDIA RTX 4080. Crucially, these geometric and computational efficiencies are achieved while matching the success rates of state-of-the-art baselines. This simplified transport geometry bypasses the computational bottleneck of independent Gaussian priors, helping enable high-frequency, closed-loop control. The code is publicly available at https://github.com/dmiller12/TemporalPolicy.

## My Notes
