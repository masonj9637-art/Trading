---
source: arxiv
category: autonomous llm agents & sequential decision making
created_at: 2026-08-06 17:59:09
status: triaged
tags:
  - triaged
---

# Argus: A General-Purpose Agentic Runtime for Long-Horizon Reasoning

- **Category Theme**: [[Autonomous Llm Agents & Sequential Decision Making]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.05144v1](https://arxiv.org/abs/2608.05144v1)

## Curator Reasoning

Promoting Argus long-horizon agentic runtime directly addressing Priority 2: Autonomous LLM agents, agentic execution, and sequential decision making.

## Summary / Abstract

Long-horizon reasoning requires an agentic runtime that can persist when evidence supports its current approach and pivot when measurements reveal failure, hidden constraints, or a misspecified objective. We present Argus, a persistent, self-evolving runtime in which Manager, Planner, Engineer, and Reviewer execute bounded missions over durable project state. Argus separates stable user intent from operational objectives, constraints, and verification criteria, and admits memories, skills, procedures, verifiers, routing decisions, and rejected routes only after role-owned review and, when available, task-native verification. Model weights remain fixed; self-evolution occurs through persistent runtime state and control policy, with autonomous execution between operator-owned escalation points. Across seven GPT-5.5 benchmark arenas, Argus achieves about 78% on SWE-Bench Pro versus 59% for Direct Copilot while using 1.41 times the aggregate tokens. After verification-gated self-evolution, mature SWE-Bench waves use 21% fewer solve-input tokens and 15% less active workflow time per task than startup waves, while recording 34 verifier recoveries and 22 strict review-loop rescues. Argus also reaches 76.8% on AARRI-Bench and a 28.0-point gap on mathematical data synthesis, with competitive GPU-kernel and language-model-training results. Beyond benchmarks, an optimized RWKV6 kernel was merged upstream; a multi-day mathematics campaign retained falsified routes and proof-backed frontier updates; and six paper pipelines completed 254 missions with 16 stage rollbacks. These results show that a fixed-weight, self-evolving harness can revise, recover, and accumulate verified approaches while producing structured trajectories for future supervised and reinforcement learning.

## My Notes
