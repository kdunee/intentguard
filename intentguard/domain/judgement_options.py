from dataclasses import dataclass


@dataclass
class JudgementOptions:
    """
    Configuration options for the code evaluation judgement process.

    This class is designed to hold settings that control how multiple evaluations
    are aggregated into a final judgement. While currently empty, it provides
    a structure for future configuration options such as:
    - Custom voting thresholds
    - Weighting strategies for different evaluations
    - Explanation selection preferences
    - Conflict resolution strategies
    """

    pass
