---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:24
status: triaged
---

# Evidence-Type Competition: When Can Interventional Data Teach Language Models Causal Direction?

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29484v1](https://arxiv.org/abs/2607.29484v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Interventional data is widely regarded as the gold standard for teaching models causal reasoning. We test this assumption in a fully controlled synthetic environment pitting observational correlation against causal effect, and find it fails instructively. In Simpson's-paradox worlds, where the two have systematically opposite signs, increasing the fraction of interventional samples in pretraining does not improve causal direction: the magnitude of the model's do()-response grows monotonically, yet its sign is copied from the observational context. What governs whether interventional evidence is used is not the training mixture but the evidence type present in the context at inference time. Under an identical training recipe, a purely observational context induces systematic sign reversal in 29/50 worlds, a mixed context in 19/50, while aligned interventional probes alone yield 41/50 correct. Erasing observational evidence from the context immediately releases the suppressed causal interpolation ability (ratio_true = +0.56); a four-state content manipulation shows the switch is content-mediated and graded. The suppression is stable across training seeds (11/11 strong reversals persist on a matched-protocol second seed) and robust as a rate at 0.93B parameters (31.8% vs. 6% reversals in the matched probe-only arm), even as absolute gains shrink four-fold. An external audit on CLadder exposes a learned positive-effect prior with a two-layer structure: sign-randomized retraining removes it in-distribution but not out-of-distribution. We summarize: the capability lives in the weights; the switch lives in the context, and activation patching localizes the switch to the middle layers' observational rows. We further quantify the sampling noise floor of probe-based causal evaluation and an evidence-averaging protocol that cuts sign errors from 26% to 9%.

## My Notes
