---
source: arxiv
category: Artificial Intelligence
created_at: 2026-08-03 01:53:23
status: triaged
---

# ARB: A Matched Authorship-Rewriting Benchmark Dataset for AI-Text Detector Evaluation

- **Category Theme**: [[Artificial Intelligence]]
- **Source**: ARXIV
- **Original URL**: [https://arxiv.org/abs/2607.29539v1](https://arxiv.org/abs/2607.29539v1)

## Curator Reasoning

High relevance to Artificial Intelligence research priorities identified during automated triage.

## Summary / Abstract

Standard AI-text detection benchmarks compare human-written text against text generated directly by large language models (LLMs). While prior work has shown that rewriting and paraphrasing can degrade detector performance, it remains unclear whether performance measured on this conventional benchmark predicts detector behavior when human-authored content is rewritten by an LLM. To address this gap, we introduce Authorship-Rewriting Benchmark (ARB), built from 1,800 human source texts (600 each from XSum, WritingPrompts, and OpenWebText) and four open-weight generators (Llama-3.2-3B, Qwen2.5-7B, Mistral-7B, Gemma-2-9B). Each source item yields four matched variants: human-written (HUMAN), direct LLM generation (Free-LLM), LLM-rewritten human text (H2L), and same-generator LLM-rewritten LLM text (LLM2L). We evaluated five detectors (FastDetectGPT, Binoculars-falcon-7b, RADAR, BERT-Defense, RoBERTa-Defense) at a strict 1%-false-positive operating point (TPR@1%FPR). FastDetectGPT and Binoculars-falcon-7b detected 91.2% and 93.5\% of direct LLM text, but only 30.8% and 15.1% of human text an LLM had rewritten, a drop of 60-78 percentage points. The same detectors retained 78.3% and 83.0% recall when LLM text was rewritten by the same model, a much smaller decline of 10-13 points. RADAR followed the same pattern (66.8% to 12.2%), while BERT-Defense and RoBERTa-Defense stayed below 3% recall across all regimes. These results show that detector performance measured on the conventional human-vs-LLM benchmark does not transfer to human-authored text revised by an LLM, even though the same detectors remain largely robust to LLM-only rewriting.

## My Notes
