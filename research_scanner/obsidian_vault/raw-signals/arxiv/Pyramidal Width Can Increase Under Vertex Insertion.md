---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# Pyramidal Width Can Increase Under Vertex Insertion

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29555v1](https://arxiv.org/abs/2607.29555v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Lacoste-Julien and Jaggi conjectured in 2015 that the pyramidal width of a polytope cannot increase when a vertex is added, provided that every old point remains a vertex. We give an exact counterexample with six integer points in $\R^3$. For \[ P=\conv\{v_0,\ldots,v_4\},\qquad Q=\conv\{v_0,\ldots,v_5\}, \] where \[ \begin{aligned} v_0&=(-1,-3,-1), & v_1&=(3,2,-2), & v_2&=(0,2,1),\\ v_3&=(-1,-3,3), & v_4&=(-2,0,1), & v_5&=(-1,0,-2), \end{aligned} \] all five vertices of $P$ remain vertices of $Q$, but \[ \PWidth(P)^2=\frac{48}{353} \quad\text{and}\quad \PWidth(Q)^2=\frac{36}{133}. \] Thus vertex insertion increases pyramidal width by the factor $\sqrt{1059/532}\approx 1.410886779$. The proof uses the equivalence between pyramidal width and facial distance, certifies both face lattices by integer supporting hyperplanes, and evaluates every facial distance by a finite rational calculation. A dependency-free exact verifier accompanies the paper.

## My Notes
