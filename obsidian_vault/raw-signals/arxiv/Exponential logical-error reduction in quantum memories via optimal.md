---
source: arxiv
category: quantum computing & qec
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# Exponential logical-error reduction in quantum memories via optimal syndrome-measurement timing

- **Category Theme**: [[Quantum Computing & Qec]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06242v1](https://arxiv.org/abs/2608.06242v1)

## Curator Reasoning

Demonstrates that optimizing syndrome-measurement timing relative to code distance yields exponential logical error rate reduction, achieving up to 40% predicted error rate reduction on Google Quantum AI surface-code parameters.

## Summary / Abstract

Syndrome-measurements timing is usually treated as a fixed clock cycle of a quantum error-correcting code. For quantum memories, however, the intra-measurement interval is itself an optimizable control parameter: measuring too rarely allows idling errors to accumulate, whereas measuring too often introduces measurement-induced faults. We propose a phenomenological logical-noise model for this trade-off and analytically show that the optimal syndrome-measurements interval scales inversely proportionally with the code distance and that this produces an exponential reduction of logical-error rates in the distance relative to constant-interval schedules. Furthermore, for time-dependent idling noise, we develop an adaptive timing strategy based on the measured syndrome activity that outperforms every fixed-interval protocol, with largest gains for short but strong noise bursts. Simulations of rotated surface-code memories with matching decoding validate the phenomenological model, the distance-dependent optimum, and the adaptive-strategy improvement. Moreover, with the experimental noise parameters reported by Google in Nature 638 (2025), our model predicts reductions in logical-error rates per unit time of up to $40\%$.

## My Notes
