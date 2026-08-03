---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# CENDRe: Concept Extraction with Natural Domain Representations

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29621v1](https://arxiv.org/abs/2607.29621v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Convolutional neural networks (CNNs) are widely used for time-series classification, but their deployment in critical domains requires understanding the temporal and spectral patterns that drive their predictions. Concept extraction (CE) methods identify such patterns by analyzing representations within the models' latent space. However, existing time-series CE methods have three limitations: they operate only in the time domain and overlook frequency features, predefine the number of concepts, and produce localizations misaligned with the regions the model uses. We address these limitations by proposing CENDRe, a concept extraction method for CNNs. It first discovers concepts by clustering per-timestep latent representations in two stages, where silhouette-guided aggregation selects the number of concepts automatically. Then, it localizes each concept through gradients of a presence score that contrasts the latent representations with their prototypes, producing masks that concentrate on the regions driving the concept. These gradients, propagated through a differentiable invertible mapping of the input such as a Fourier transform, yield localizations for the same concepts in the frequency domain. Finally, each concept receives a relevance score that quantifies its contribution to each class. On synthetic benchmarks, CENDRe achieves representation correctness comparable to state-of-the-art CE methods and significantly higher importance correctness. On real bearing-fault data, CENDRe extracts the frequency bands driving the model's predictions, located in regions commonly inspected for fault diagnosis, producing evidence to assess the model that time-domain CE methods cannot.

## My Notes
