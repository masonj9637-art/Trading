---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# Same Graph Cross-Task Transfer in GNNs: Protocols and Predictors

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28525v1](https://arxiv.org/abs/2607.28525v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Many real-world graphs support multiple predictive tasks over the same underlying structure, creating an opportunity to reuse supervision across node classification (NC) and link prediction (LP). However, existing evaluations often rely on incompatible splits, observed-graph assumptions, and negative sampling rules, making conclusions about same-graph cross-task transfer unreliable. We formalize same-graph NC-LP transfer and propose a leakage-free protocol that fixes node and edge splits, uses a shared message-passing graph that excludes evaluated edges, and employs fixed negatives for LP. Across three backbones (GCN, GraphSAGE, GPS), we find that transfer is strongly directional and predictable: NC $\to$ LP is consistently beneficial on homophilic graphs, while LP $\to$ NC is fragile and can even degrade accuracy under naive representation reuse. LP $\to$ NC becomes reliably positive mainly in a structure-dominant regime where LP is easy but NC is unsaturated, suggesting that LP acts as structural pretraining. Finally, we introduce the CoTask Score (CTS) to summarize joint NC+LP utility when a shared encoder must serve both tasks, and show that simple dataset statistics, especially homophily, can guide mechanism choice and help avoid negative transfer.

## My Notes
