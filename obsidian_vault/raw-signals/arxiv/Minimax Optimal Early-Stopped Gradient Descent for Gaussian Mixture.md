---
source: arxiv
category: machine learning theory
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# Minimax Optimal Early-Stopped Gradient Descent for Gaussian Mixture Classification

- **Category Theme**: [[Machine Learning Theory]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06250v1](https://arxiv.org/abs/2608.06250v1)

## Curator Reasoning

Proves that early stopping in overparameterized logistic gradient descent overcomes implicit max-margin bias to achieve minimax optimal zero-one risk under noise, whereas full interpolation requires exponentially more samples.

## Summary / Abstract

In overparameterised classification, training data can be linearly separable even when the underlying distribution is not. In this setting, gradient descent (GD) on the logistic loss diverges in norm while converging in direction to a max-margin interpolating classifier, whose implicit bias can be statistically suboptimal. In this work, we show that early stopping can overcome this suboptimality: in a Gaussian mixture model with label-flipping noise, GD stopped at an appropriate oracle time achieves minimax-optimal excess zero-one risk for covariance spectra with fast and continuous decay, including polynomial and exponential spectral decays. Our analysis combines a sharp upper bound for the early-stopped iterate with a matching statistical lower bound over arbitrary classifiers, yielding optimal rates that are validated by experiments. A central technical contribution is a new calibration result that converts excess logistic risk into excess zero-one risk; it handles the model misspecification induced by the label-flipping noise, and removes the square-root rate in standard bounds. We also establish a lower bound for linear interpolators, showing that interpolation can require exponentially more samples than early stopping to achieve the same excess risk.

## My Notes
