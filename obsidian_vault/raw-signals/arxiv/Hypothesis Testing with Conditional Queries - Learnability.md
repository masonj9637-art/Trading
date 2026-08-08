---
source: arxiv
category: machine learning theory
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# Hypothesis Testing with Conditional Queries: Learnability and the Value of Interaction

- **Category Theme**: [[Machine Learning Theory]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06262v1](https://arxiv.org/abs/2608.06262v1)

## Curator Reasoning

Proves an exact quadratic adaptivity gap (\(O(N^2)\) non-adaptive vs \(O(1)\) adaptive) for hypothesis testing under conditional queries, establishing fundamental bounds on non-interactive model evaluation.

## Summary / Abstract

Model evaluations may fix all tests before observing any responses or select later tests using earlier responses. We study this choice in a conditional-query model on a finite outcome space $\mathcal{X}$ with $|\mathcal{X}|=N$. We first ask which pairs of distribution classes can be reliably distinguished. We then ask how many additional queries are required to match an adaptive tester when all queried events must be fixed in advance. We show that learnability holds if and only if the two classes have positive separation in their pairwise conditional probabilities. When this separation is zero, the optimal worst-case error is exactly $1/2$ at every finite query budget. For any $T$-query adaptive policy and any $ρ\in (0,1)$, we construct a randomized non-adaptive procedure using $O(N^2(T + \log(1/ρ)))$ pair queries chosen before any response is observed. Its simulated transcript is within $ρ$ in total variation of the adaptive transcript, uniformly over all distributions in the model. We also construct a matching family with constant adaptive query complexity and $Ω_\varepsilon(N^2)$ non-adaptive query complexity. Consequently, the worst-case fixed-error adaptivity gap is $Θ_\varepsilon(N^2)$. Thus interaction can reduce the required number of tests by a quadratic factor, but the apparent exponential branching of an interactive evaluation does not yield an exponential query advantage.

## My Notes
