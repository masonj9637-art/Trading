---
source: arxiv
category: llm post-training & reasoning
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# On-Policy Self-Distillation without Any Supervision

- **Category Theme**: [[Llm Post-training & Reasoning]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06296v1](https://arxiv.org/abs/2608.06296v1)

## Curator Reasoning

Proposes U-OPSD for fully unsupervised on-policy self-distillation using internal consistency, matching or outperforming supervised ground-truth baselines (+8.5% to +10.7% on AIME/MATH benchmarks) without external feedback.

## Summary / Abstract

On-policy (Self-)Distillation (OPD / OPSD) has shown strong potential for post-training large language models (LLMs). However, existing methods still rely heavily on external supervision, including ground-truth signals, environmental feedback, or guidance from larger models, and therefore fall short of genuine "self"-distillation. In this study, we show that on-policy self-distillation can be achieved using only a model's own generations via internal consistency. We propose Unsupervised On-Policy Self-Distillation (U-OPSD). U-OPSD first samples multiple rollouts and constructs a pseudo-solution by majority vote under a self-consistency threshold. It then conditions a teacher distribution on the shortest pseudo-solution and distills it into prefixes of the model's longest incorrect completion, allowing the model to correct itself precisely where it is confidently wrong. Across diverse benchmarks, base models, and training settings, U-OPSD consistently improves over the base models and matches or surpasses supervised methods with ground truth (GT), such as OPSD and GRPO. On AIME24, AIME25, HMMT25, MATH500, and AMC23, U-OPSD improves over the base model by 8.5% and 10.7% on Qwen3 non-thinking mode at the 4B and 8B scales, respectively, and outperforms OPSD by an average of 3.2% and 2.3%. In thinking mode, U-OPSD remains on par with OPSD, outperforming it by 0.9% at 4B and matching it at 8B, while surpassing GRPO by 0.7% and 1.1%, respectively.

## My Notes
