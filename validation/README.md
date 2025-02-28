# Model Validation Framework

This framework provides a systematic approach to evaluate the model's performance in code property verification tasks.

## Methodology

### Test Configuration
- Each test example is evaluated multiple times (15 total evaluations)
- Tests are organized in groups of 3 evaluations (5 trials × 3 evaluations per trial)
- A voting mechanism is applied within each group (jury size = 3)

### Success Criteria
- A single trial succeeds if the majority vote within its jury agrees (≥2 out of 3)
- A test example passes only if ALL 5 trials succeed
- This strict requirement ensures high confidence in the model's consistency

## Metrics

The framework calculates the following metrics:

### Primary Metrics
- **Accuracy**: (True Positives + True Negatives) / Total Cases
- **Precision**: True Positives / (True Positives + False Positives)
- **Recall**: True Positives / (True Positives + False Negatives)

## Implementation Notes

- The multiple trial approach helps identify inconsistencies in model behavior
- The strict all-trials-must-pass requirement minimizes false positives
- Caching must be disabled during validation experiments to ensure independent evaluations
- Each evaluation must be performed with a fresh model context
