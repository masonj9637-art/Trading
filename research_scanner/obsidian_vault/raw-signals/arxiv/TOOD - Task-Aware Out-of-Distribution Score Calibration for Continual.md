---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# TOOD: Task-Aware Out-of-Distribution Score Calibration for Continual Learners

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29592v1](https://arxiv.org/abs/2607.29592v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

The primary challenge of continual learning (CL) systems is to learn new tasks while remaining performant on previously learned tasks. A similarly important though less well-studied aspect of CL systems is their ability to distinguish inputs that are unlikely to come from within the set of tasks the system has already encountered, often called out-of-distribution (OOD) detection. This paper presents several findings related to the dynamics of OOD detection in CL systems, causes of performance degradation over time which we call OOD forgetting (OODF), and proposed mitigation strategies for this degradation. Chiefly, we find the unintuitive result that OODF is only weakly anti-correlated with classification performance on previous tasks, suggesting that the underlying mechanisms producing OODF are distinct. Moreover, this effect is observed for both energy-based and feature-based OOD detection methods. Energy-based detectors suffer a drop in logit scale as additional tasks are learned, which we term the Confidence Gap, while feature-based detectors also degrade under a complementary effect we call Manifold Crowding. Motivated by these observations, we propose TOOD, a training-free post-hoc method that decomposes logits into per-task energy scores and re-calibrates them using replay-buffer statistics. Experiments on CIFAR-10, CIFAR-100, and a 100-task ImageNet-1K stream show that TOOD improves OOD detection performance over uncalibrated energy in most settings and ranks first or second in nine of ten CIFAR configurations, with the largest gains when the confidence gap is most severe. These results suggest that a substantial portion of OOD deterioration in continual learning arises from score miscalibration rather than from a complete loss of discriminative structure.

## My Notes
