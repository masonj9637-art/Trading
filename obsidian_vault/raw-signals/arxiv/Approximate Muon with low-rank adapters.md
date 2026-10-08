---
source: arxiv
category: robotics
created_at: 2026-08-17 22:16:45
status: triaged
tags:
  - triaged
---

# Approximate Muon with low-rank adapters

- **Category Theme**: [[Robotics]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.14492v1](https://arxiv.org/abs/2608.14492v1)

## Curator Reasoning

Directly matches Priority 3's focus on tracking reactive diffusion policies ('FA-RDP') for contact-rich manipulation.

## Summary / Abstract

The Muon optimizer shows clear benefits versus alternatives when pretraining neural networks. However, it is used less frequently for parameter-efficient fine-tuning (PEFT). One potential reason is that the most common PEFT method, LoRA, does not naturally combine with Muon since it is not mathematically possible to orthogonalize the weight update given by a low-rank parameterization. In this paper, we address this issue by approximating the solution to a relaxed Muon objective in the low-rank setting via linearization and then least-squares. We provide an efficient implementation that uses matmul operations only, as opposed to more complex linear algebra decomposition routines. Our method, sMuon (small Muon), performs favourably across SFT and a ReLoRA pretraining experiment. While results are model- and eval-dependent, we find overall that using Muon for low-rank fine-tuning provides moderate performance improvements.

## My Notes
