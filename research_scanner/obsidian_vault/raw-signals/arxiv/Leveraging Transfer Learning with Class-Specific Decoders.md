---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:24
status: triaged
---

# Leveraging Transfer Learning with Class-Specific Decoders for Laparoscopic Segmentation

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29509v1](https://arxiv.org/abs/2607.29509v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Effective multi-organ segmentation in surgical data requires learning the intricate anatomical features and alleviating the challenge of class imbalance, which results from relatively lower proportions of small and limitedly exposed structures. Recent works on laparoscopic multi-organ segmentation focus on learning structure-specific features through class-specific decoder architectures and report favorable results. This work extends the decoder-focused architectures to investigate knowledge sharing in the cross-surgical domain. We utilize two datasets representing different surgical domains, rectal and cholecystectomy surgeries, to explore how surgical conceptual knowledge transfers under partially common anatomical representations. Additionally, we compare the feature adaptation for the encoder and decoder at different training stages to analyse the knowledge adaptation and retention in the network. Our results corroborate previous findings on decoder-specific architectures and demonstrate that the organ-specific decoder model (CEMD), fully fine-tuned after cross-domain pre-training, achieves the highest segmentation performance (62.4\% dice) while converging substantially faster than training from scratch. However, we also find that class imbalance in surgical data remains a persistent challenge that transfer learning does not fully resolve for underrepresented anatomical structures.

## My Notes
