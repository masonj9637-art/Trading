---
source: arxiv
category: Quantum Computing
created_at: 2026-08-03 01:53:23
status: triaged
---

# Structure-Preserving Quantum Simulation of Wave Equations on a Trapped-Ion Processor

- **Category Theme**: [[Quantum Computing]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.28499v1](https://arxiv.org/abs/2607.28499v1)

## Curator Reasoning

High relevance to Quantum Computing research priorities identified during automated triage.

## Summary / Abstract

Wave equations provide a natural testbed for near-term quantum simulation of partial differential equations, but hardware demonstrations have remained limited in spatial dimension, equation class, system size, and physically meaningful output. We develop and benchmark structure-preserving, Fourier-based quantum circuits for the one- and two dimensional acoustic wave equations and Dirac dynamics with variable mass on the Quantinuum H2-2 trapped-ion processor. The experiments include one-dimensional grids with up to \(1024\) points and \(32\times32\) two-dimensional grids, corresponding to an encoded state-space dimension of up to \(4096\). Rather than reconstructing the full fields, we estimate subdomain kinetic energies directly from measurement samples. Across all tested acoustic and Dirac dynamics problems, the H2-2 results track the classical kinetic-energy dynamics with mean absolute errors between \(5.9\times10^{-3}\) and \(2.4\times10^{-2}\). At fixed retained bandwidth, the compiled gate counts grow approximately quadratically with the number of grid qubits; the acoustic circuit sizes are essentially independent of evolution time, whereas the cost also grows with the number of product-formula steps. These results provide hardware-level evidence that accurate observable dynamics can remain resolvable for structured wave problems with thousands of encoded degrees of freedom on a present-day trapped-ion processor.

## My Notes
