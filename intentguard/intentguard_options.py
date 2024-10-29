class IntentGuardOptions:
    """
    Configuration options for IntentGuard assertions.

    This class holds configuration parameters that control the behavior
    of IntentGuard assertions, including model selection and voting parameters.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini-2024-07-18",
        quorum_size: int = 1,
    ):
        """
        Initialize IntentGuardOptions with the specified parameters.

        Args:
            model (str, optional): The LLM model to use for assertions.
                Defaults to "gpt-4o-mini-2024-07-18".
            quorum_size (int, optional): The number of LLM inferences to perform
                for each assertion. The final result is determined by majority vote.
                Defaults to 1.
        """
        self.model = model
        self.quorum_size = quorum_size
