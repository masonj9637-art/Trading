---
source: arxiv
category: time series & quantitative modeling
created_at: 2026-08-08 14:21:58
status: triaged
tags:
  - triaged
---

# Scalable estimation of VARMA models

- **Category Theme**: [[Time Series & Quantitative Modeling]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2608.06340v1](https://arxiv.org/abs/2608.06340v1)

## Curator Reasoning

Develops a VARMA estimation framework with per-iteration cost independent of series length T using partial-autocorrelation reparametrization and Parseval statistics, demonstrating stable estimation at dimensions (d=40) where classical MLE fails.

## Summary / Abstract

Vector autoregressive moving-average (VARMA) models have long been considered impractical beyond moderate dimensions: the likelihood is non-convex, the parametrization is identified only up to equivalence, and every evaluation costs a pass over the entire series. Yet their moving-average term captures with a few parameters what a pure autoregression matches only with many lags. We introduce an estimation framework that removes this computational barrier: each optimization iteration is independent of the series length $T$. The framework combines a partial-autocorrelation reparametrization that guarantees stationarity and invertibility by construction, Gaussian priors on the reparametrized coefficients with separate scales for diagonal and off-diagonal entries, and losses that depend on the data only through fixed-size sufficient statistics, evaluated by a Parseval (Fourier) identity at near-linear cost in the truncation length. This yields two point estimators: a regularized least-squares fit and a covariance-marginalized maximum-a-posteriori estimator. We prove that both recover the infinite-autoregressive representation of the true process at a near-parametric rate in fixed dimension, so the truncation introduces no asymptotic bias. The same machinery extends, at the same leading cost, to seasonal dynamics, exogenous regressors (VARMAX), and rolling-window refits. Empirically, the estimators stay close to the oracle forecast error from $d=10$ to $d=40$ (where classical conditional MLE returns non-invertible fits whose forecasts diverge) and match or beat VAR, Bayesian-VAR, component-wise ARMA, and sparse-VARMA baselines on retail-demand, meteorological, and air-quality data. This brings likelihood-based VARMA estimation, at a per-iteration cost independent of the series length, to the problem sizes where practitioners have so far relied on VAR models.

## My Notes
