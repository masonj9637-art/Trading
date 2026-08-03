---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# OSReward: Instituting Standardized Evaluation for Cross-Platform Computer-Use Reward Models

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28609v1](https://arxiv.org/abs/2607.28609v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Computer-using agents (CUAs) are advancing rapidly across the digital world. A CUA trajectory records the agent's actions, states, and reasoning. Verifying whether it fulfilled the task instruction is central to CUA evaluation, data curation, and reinforcement learning. Neither human-written verifiers nor human annotators can provide such verification at scale, so the field increasingly turns to vision-language models (VLMs) as judges of CUA trajectories. But a fundamental question has long gone unexamined: are these VLM judges reliable enough? To study it systematically, we introduce OSReward, a realistic, high-quality benchmark that evaluates VLM judges on CUA trajectories. The trajectories come from diverse agent backbones executing human-verified instructions across platforms, then rigorously labeled with ground-truth verdicts through multi-stage human annotation. Building on it, we derive OSReward-Hard, a challenge set concentrating genuinely hard cases, and OSReward-Multi for fine-grained efficiency and alignment scoring. The most comprehensive evaluation of VLM judges to date finds even state-of-the-art models fall short of an ideal judge, sharing a systematic leniency bias that mislabels failed runs as successes. The few reliable enough to trust are too expensive to run at scale, while affordable open models trail far behind. To close this gap, we construct and release OS-Shepherd-100K, an open corpus of reasoning-annotated trajectory judgments for the CUA community. On it, we train OS-Shepherd (9B and 35B), open reward models that supply low-cost, stable, and reliable reward signals, matching commercial judges at 30-60% lower cost than the frontier. Extensive analyses further inform the design of reliable CUA reward at scale. Our code, benchmark, dataset, and model checkpoints are available at https://os-copilot.github.io/OSReward-Home/.

## My Notes
