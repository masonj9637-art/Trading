---
source: arxiv
category: Machine Learning
created_at: 2026-08-03 01:53:23
status: triaged
---

# Convergence and Regret of the Policy Gradient for Multi-Armed Bandits in Diffusion Environment

- **Category Theme**: [[Machine Learning]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29593v1](https://arxiv.org/abs/2607.29593v1)

## Curator Reasoning

High relevance to Machine Learning research priorities identified during automated triage.

## Summary / Abstract

This paper studies the policy gradient update for a multi-arm bandit problem in diffusion environment that is described by a stochastic differential equation (SDE) under the continuous-time reinforcement learning framework by Wang et al. (2020), Jia and Zhou (2022b). With the logit parameterization for the stochastic policy, we show that it converges almost surely to the optimal arm under an arbitrary constant learning rate. Furthermore, we derive the non-asymptotic regret upper bound when the constant learning rate is below a time-invariant threshold; and the regret bound has order $O(\log T)$. We improve the analysis in Lattimore (2026a) for the same SDE by constructing a novel Lyapunov function and demonstrate the transparency of analyzing policy gradient using the tools in SDEs. In addition, the same Lyapunov function is also helpful in analyzing the discrete-time policy gradient algorithm.

## My Notes
