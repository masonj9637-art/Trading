---
source: arxiv
category: model compression & quantization
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# BaKron: Efficient Quantization with Kronecker-Factored Hessians

- **Category Theme**: [[Model Compression & Quantization]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06291v1](https://arxiv.org/abs/2608.06291v1)

## Curator Reasoning

Introduces BaKron for adaptive rounding neural network quantization using Kronecker-factored Hessians, using anti-diagonal parallelism to reduce total computation from \(O(m^2 n^2)\) to \(O(mn(m+n))\) while capturing cross-output correlations.

## Summary / Abstract

We accelerate a family of algorithms for neural network quantization whose geometry is informed by any Kronecker-factored approximation of the Hessian. GPTQ-style adaptive rounding typically uses one-sided information derived from input activations. Two-sided Kronecker-factored Hessian approximations can additionally capture correlations across output coordinates, but applying GPTQ directly in the vectorized weight domain is computationally expensive. Building on the two-sided adaptive-rounding formulation used by BoA and YAQA, we introduce BaKron, an efficient solver that combines anti-diagonal parallelism with a recursive divide-and-conquer construction. For an $m\times n$ weight matrix, BaKron uses $O(m+n)$ sequential steps while reducing the total work from $O(m^2n^2)$ to $O(mn(m+n))$. Thus, it matches the cubic scaling of GPTQ while exploiting richer curvature information. Moreover, BaKron is modular with respect to both the base quantizer and the Hessian estimator. We also provide practical benchmarks, consider a range of Hessians that BaKron can be called with, find an efficient technique to compute these Hessians, and evaluate the algorithm experimentally.

## My Notes
