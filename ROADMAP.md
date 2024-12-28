# IntentGuard Roadmap

- [x] Failed Assertion Explanations (https://github.com/kdunee/intentguard/issues/2)
  - Detailed reasoning for why assertions failed
  - Suggestions for fixing the issues

- [x] Result Caching (https://github.com/kdunee/intentguard/issues/3)
  - Speed up local execution by caching assertion results
  - Avoid redundant LLM calls for unchanged code

- [ ] Aggregation Modes (strict/balanced/relaxed) (https://github.com/kdunee/intentguard/issues/4)
  - Strict: requires unanimous agreement across all evaluations
  - Balanced: uses majority voting
  - Relaxed: requires only one positive evaluation

- [ ] File Reference in Assertions (https://github.com/kdunee/intentguard/issues/6)
  - Allow referencing files in assertions
  - Handle potentially large files efficiently

- [x] CPU-Optimized Model (https://github.com/kdunee/intentguard/issues/5)
  - Small fine-tuned model focused on local analysis
  - Optimized for CPU execution
  - Faster and cheaper inference
