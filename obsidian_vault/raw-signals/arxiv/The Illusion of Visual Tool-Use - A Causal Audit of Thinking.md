---
source: arxiv
category: multimodal llms & evaluation
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# The Illusion of Visual Tool-Use: A Causal Audit of Thinking with Images

- **Category Theme**: [[Multimodal Llms & Evaluation]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06270v1](https://arxiv.org/abs/2608.06270v1)

## Curator Reasoning

Provides a causal audit of active visual tool use in multimodal LLMs, establishing Visual Evidence Gain to expose 'Calling Without Looking' and 'Looking Without Planning' failure modes where tool calls fail to causally influence model answers.

## Summary / Abstract

The "thinking-with-images" paradigm equips multimodal LLMs with active visual operations such as crop-and-zoom. However, models using these operations often achieve only marginal or negative gains over direct inference at substantially higher token cost. They may also repeatedly crop irrelevant regions and fail on questions that direct inference answers correctly. We ask whether the returned visual evidence causally affects the answer. To answer this question, we formulate visual tool-use as a causal graph that separates observation-mediated paths from action-induced shortcuts. We then audit it through interventions at the three levels: policy (comparing tool-use with direct inference), trajectory (corrupting all observations during rollout), and step (counterfactually replacing one individual observation under a fixed prefix). Our step-level estimand, Visual Evidence Gain, isolates the contribution of each returned observation. Across six representative models and five fine-grained perception benchmarks, we uncover policy miscalibration with two failure modes. In Calling Without Looking, returned observations have no causal effect on the answer. In Looking Without Planning, observations are informative but the call schedule is incoherent. A trajectory-level diagnostic decomposes the policy-level accuracy gain and shows that the gain is concentrated in a Calibrated minority. We term this discrepancy the illusion of visual tool-use: despite aggregate accuracy gains, visual tool-use is not causally effective across a broad range of rollouts. The code is available at https://github.com/OpenCausaLab/CauAudit.

## My Notes
