---
source: arxiv
category: quantum computing
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# Dimension-Free Polylogarithmic Quantum Shadow Tomography from Sequential Pretty-Good Measurements

- **Category Theme**: [[Quantum Computing]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06345v1](https://arxiv.org/abs/2608.06345v1)

## Curator Reasoning

Resolves Aaronson's (STOC'18) open question by constructing a quantum shadow tomography protocol with sample complexity polylogarithmic in observable count and completely independent of quantum state dimension.

## Summary / Abstract

\textit{Shadow tomography} is a fundamental problem in quantum information theory. Given multiple copies of an unknown $d$-dimensional quantum state $ρ$ and a known collection of observables ${E_1,\ldots,E_m}$, the goal is to estimate all expectation values $\{\Tr(ρE_i)\}_{i=1}^m$ to additive accuracy $\varepsilon$ with probability at least $1-δ$. An elusive open question from the seminal shadow tomography work of Aaronson (STOC'18) is whether this task admits a dimension-independent sample complexity with only polylogarithmic dependence on $m$, as suggested by the best-known lower bounds. In this work, we give a quantum protocol for shadow tomography with sample complexity \[ O\left( \frac{1}{\varepsilon^2} \frac{(\log (m/δ))^4} {(\log\log (m/δ))^3} \right), \] which is polylogarithmic in the number of observables and independent of the dimension of the unknown state thereby answering Aaronson's original question while also providing an exponential improvement in the prior best dimension independent sample complexity of shadow tomography from Sinha (STOC'25). Our approach first reduces the general shadow-tomography problem to a finite-ensemble estimation problem via a minimax argument. We then develop an observable-independent protocol that repeatedly applies the pretty-good measurement and updates the priori distribution over the finite ensemble according to the measurement outcomes. A refined tail analysis of the resulting estimation error yields simultaneous accuracy guarantees for all observables.

## My Notes
