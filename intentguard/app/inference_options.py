from dataclasses import dataclass


@dataclass
class InferenceOptions:
    """
    Configuration options for Language Model inference.

    This class encapsulates parameters that control the behavior of LLM inference
    operations. It provides settings that influence how the model generates responses.

    Attributes:
        temperature: A float value controlling randomness in model outputs.
            Higher values (e.g., 1.0) make output more random and creative.
            Lower values (e.g., 0.1) make output more focused and deterministic.
    """

    temperature: float
