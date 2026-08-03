---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# DungeonBench: A Benchmark for Rules-Rich Tactical Reasoning in Dungeons & Dragons Combat

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29577v1](https://arxiv.org/abs/2607.29577v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Games and simulators make valuable benchmarks by turning decisions into measurable outcomes, but many current suites under-test rules-rich tactical reasoning: the ability to choose well when geometry, timing, resources, objectives, and rule interactions all matter at once. We introduce DungeonBench, a benchmark for tactical reasoning in Dungeons & Dragons combat, built to cover the vast majority of combat-relevant 2014 System Reference Document content whose effects can be resolved by the simulator while retaining mechanics that simplified combat simulators often abstract away. At each step, DungeonBench exposes a complete tactical observation, a pending decision, and an indexed list of executable options spanning movement, attacks, spells, reactions, objectives, preparation, and scarce resources. The task is to value legal choices whose consequences depend on action economy, creature traits, battlefield geometry, timing windows, and future encounters. DungeonBench has two tracks: Encounter, which evaluates local tactical play in single fights, and Day, which links encounters through persistent hit points, spell slots, consumables, preparation, and short-rest timing, forcing policies to trade off immediate tactical advantage against future survivability. The same engine-generated decision stream supports heuristic controllers, language-model policies, learned option rankers, and masked-action reinforcement-learning agents. We evaluate frontier language-model policies on this shared decision stream. Results show that full tactical observations do not saturate the benchmark: frontier policies often win direct encounters, but linked encounter days expose failures in resource budgeting, rest timing, and rule-aware tactical discipline.

## My Notes
