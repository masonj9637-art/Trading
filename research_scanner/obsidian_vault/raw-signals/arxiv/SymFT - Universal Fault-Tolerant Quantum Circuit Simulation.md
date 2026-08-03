---
source: arxiv
category: Quantum Computing
created_at: 2026-08-03 01:53:23
status: triaged
---

# SymFT: Universal Fault-Tolerant Quantum Circuit Simulation via Symbolic Clifford--Pauli Frames and Stabilizer Coordinates

- **Category Theme**: [[Quantum Computing]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28600v1](https://arxiv.org/abs/2607.28600v1)

## Curator Reasoning

High relevance to Quantum Computing research priorities identified during automated triage.

## Summary / Abstract

Fault-tolerant protocols often consist largely of stabilizer subcircuits, yet the non-Clifford operations required for universality make exact sampling costly. We present SymFT, a high-throughput simulator for Clifford-dominated circuits with Pauli rotations, stochastic Pauli noise, mid-circuit Pauli measurements, and measurement-record-controlled Pauli feedback. It combines two ideas. First, symbolic Clifford--Pauli frame factorization reduces branch-probability sampling to Pauli rotations and measurement projectors, with noise and feedback represented by symbolic signs. Since the residual Clifford and Pauli frames are unitary, they do not affect branch probabilities and need not be applied in every shot. Second, adaptive stabilizer-coordinate planning uses a shared stabilizer--destabilizer tableau to define the basis and stores only the active non-stabilizer degrees of freedom in a dynamically sized dense active-state vector. It resolves basis changes once and emits direct multi-coordinate sampling instructions, thereby avoiding per-shot tableau updates and localization-induced Clifford transformations of the dense vector. Across the tested pure-Clifford and near-Clifford circuits, SymFT achieves state-of-the-art sampling performance. On a single CPU core, it is $2.51\text{--}2.56\times$ faster than Stim for surface-code circuits and $1.86\text{--}3.51\times$ faster than Clifft for magic-state cultivation and distillation circuits. For the tested cultivation circuits, its sampling throughput also exceeds that of our previous simulator, SOFT, by more than two orders of magnitude.

## My Notes
