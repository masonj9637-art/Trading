---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# STAGE: STyle-controllable Action GEneration for personalized autonomous driving

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29517v1](https://arxiv.org/abs/2607.29517v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Driving style refers to the behavioral preferences that drivers maintain during driving, shaped by their diverse experiences, habits, and needs, and is typically reflected in varying levels of aggressiveness. If humans choose to use autonomous driving systems, they would expect the driving style of the systems to closely resemble their own habit. However, this is challenging for current industrial autonomous driving systems. To address this, we developed a style controllable action generation method, STAGE, for driving tasks. Its training process is based on imitation learning, incorporating both style value and latent value action modality encoding. Preference learning is then used to identify the user's driving style as a continuous, monotonic style value. And to reduce the cost of human involvement in the preference training process, we also developed a set of rules to compare driving style in data pairs. Then, during inference, the user inputs the style value to control the generated action patterns, dynamically meeting the user's expectations. Using the STAGE method, we verified that the style-controlled action generation results in several typical road scenarios significantly align with human expectations. Furthermore, through comparisons between the STAGE method and various other approaches, we reveal the unique functionalities of STAGE, including its style controllability, style continuity, driving style alignment capability and driving safety. The code for this work is available at: https://github.com/CarlDegio/STAGE

## My Notes
