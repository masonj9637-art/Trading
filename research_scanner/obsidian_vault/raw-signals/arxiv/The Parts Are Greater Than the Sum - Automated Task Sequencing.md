---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# The Parts Are Greater Than the Sum: Automated Task Sequencing for Efficient Training of Multi-Policy LLMs

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29601v1](https://arxiv.org/abs/2607.29601v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Parameter-Efficient Fine-Tuning (PEFT) commonly adapts large language models using a single shared Low-Rank Adapter (LoRA). This shared optimization space often suffers from interference when adapting heterogeneous task sequences, leading to poor transfer and catastrophic forgetting. Existing approaches mainly improve adapter expressiveness by increasing parameter capacity or composing multiple adapters, yet they still rely on a shared optimization path. In this paper, we propose an optimization-path organization framework for parameter-efficient fine-tuning of large language models, implemented as an automatic multi-policy PEFT architecture. Specifically, optimization-compatible adaptation paths are automatically organized through task grouping and task sequencing under a fixed parameter budget. The organized optimization paths are implemented as independent Quantized Low-Rank Adapters (QLoRA), enabling heterogeneous tasks to be optimized in decoupled adaptation spaces while preserving positive transfer among compatible tasks. Experiments on the TRACE benchmark demonstrate that performance consistently improves from conventional single-policy PEFT to multi-policy PEFT, with the proposed automatic multi-policy framework achieving the best performance of 44.78 under the same trainable capacity. This suggests that optimization-path organization is more effective than simply increasing adapter capacity for heterogeneous parameter-efficient fine-tuning.

## My Notes
