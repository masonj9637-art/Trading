---
source: arxiv
category: artificial intelligence
created_at: 2026-08-17 22:16:45
status: triaged
tags:
  - triaged
---

# More Correct Mass, Worse Answers: Why Power Sampling Can Fail and How to Fix It

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.14420v1](https://arxiv.org/abs/2608.14420v1)

## Curator Reasoning

Explicitly addresses Priority 2's requirement to evaluate the 'MANTA' experimental benchmark for multi-agent topology adaptation.

## Summary / Abstract

Power Sampling sharpens a language model's distribution over complete generation trajectories, offering a verifier-free way to improve reasoning at inference time. It also has the potential to serve as a general-purpose front end for a broad range of downstream sampling methods. However, we uncover a striking paradox: Power Sampling can drive more probability mass toward correct trajectories while degrading the downstream inference it is intended to enhance. Using self-consistency as a representative case, we observe accuracy drops of up to 18.5 percentage points across models and reasoning benchmarks. We trace this paradox to two mismatches. Dose mismatch arises because a fixed exponent induces drastically different amounts of distributional change across problems. Coverage mismatch arises because global sharpening concentrates mass on a narrow set of dominant paths: high pass@k, often interpreted as evidence of preserved diversity, can therefore coexist with the loss of broad reasoning-path support required for downstream aggregation, search, and selection. Guided by this diagnosis, we replace uniform trajectory exponentiation with a deformation-controlled, support-preserving Power target that calibrates sharpening across problems while limiting the suppression of moderate-probability paths. In a same-budget instantiation with weighted self-consistency, the repaired sampler reverses the losses caused by global Power and outperforms standard multi-sample inference across reasoning benchmarks.

## My Notes
