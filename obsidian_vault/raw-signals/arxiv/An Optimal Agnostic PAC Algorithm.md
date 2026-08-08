---
source: arxiv
category: machine learning theory
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# An Optimal Agnostic PAC Algorithm

- **Category Theme**: [[Machine Learning Theory]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06363v1](https://arxiv.org/abs/2608.06363v1)

## Curator Reasoning

Establishes an optimal agnostic PAC learning algorithm achieving tight statistical risk bounds matching Devroye et al. (1996) lower bounds up to universal constants, resolving a foundational theoretical problem in learning theory.

## Summary / Abstract

Let $H\subseteq\{-1,+1\}^X$ be a class of finite VC dimension $d\ge1$. Writing $L$ for the binary risk and $L^*=\min_{h\in H}L(h)$, we construct a learner achieving the statistically optimal risk bound: from an i.i.d.\ sample of size $n$, for every $0<δ\le 1/2$, with probability at least $1-δ$, \[ L(\widehat h) \le L^*+ 7\cdot10^8\left( \sqrt{\frac{L^*(d+\log(1/δ))}{n}} +\frac{d+\log(1/δ)}{n} \right). \] This settles the sample complexity of agnostic PAC learning up to universal constants at every fixed $L^*$, matching the lower bounds of Devroye, Györfi, and Lugosi [A Probabilistic Theory of Pattern Recognition, Springer, 1996].

## My Notes
