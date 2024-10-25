class AILintTestOptions:
    """
    Configuration options for AILintTest.

    This class encapsulates the configurable parameters used in the AILintTest
    process, allowing for customization of the assertion behavior.
    """

    def __init__(self, quorum_size: int = 1, model: str = "gpt-4o-mini-2024-07-18"):
        """
        Initialize the AILintTestOptions instance.

        Args:
            quorum_size (int, optional): The number of LLM inferences to perform
                for each assertion. A higher number increases reliability but
                also increases computation time and cost. Defaults to 1.
            model (str, optional): The identifier of the LLM model to use for
                inferences. Defaults to "gpt-4o-mini-2024-07-18".

        Attributes:
            quorum_size (int): The number of LLM inferences to perform.
            model (str): The identifier of the LLM model to use.
        """
        self.quorum_size = quorum_size
        self.model = model
