class IntentGuardOptions:
    """
    Configuration options for IntentGuard assertions.

    This class holds configuration parameters that control the behavior
    of IntentGuard assertions.
    """

    def __init__(
        self,
        num_evaluations: int = 1,
        temperature: float = 0.4,
    ) -> None:
        """
        Initialize IntentGuardOptions with the specified parameters.

        Args:
            num_evaluations (int, optional): The number of LLM inferences to perform
                for each assertion. The final result is determined by majority vote.
                Defaults to 1.
            temperature (float, optional): The temperature parameter for the LLM.
                Defaults to 0.4.
        """
        self.num_evaluations: int = num_evaluations
        self.temperature: float = temperature
