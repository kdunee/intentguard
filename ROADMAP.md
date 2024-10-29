# IntentGuard Roadmap

- [ ] Failed Assertion Explanations
  - Detailed reasoning for why assertions failed
  - Suggestions for fixing the issues

- [ ] Result Caching
  - Speed up local execution by caching assertion results
  - Avoid redundant LLM calls for unchanged code

- [ ] Quorum Modes (strict/balanced/relaxed)
  - Strict: requires unanimous agreement
  - Balanced: uses majority voting
  - Relaxed: requires only one agreement

- [ ] CPU-Optimized Model
  - Small fine-tuned model focused on local analysis
  - Optimized for CPU execution
  - Faster and cheaper inference
