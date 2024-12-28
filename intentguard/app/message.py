from dataclasses import dataclass


@dataclass
class Message:
    """
    A class representing a message in an LLM conversation.

    This class encapsulates a single message exchanged with a language model,
    containing both the message content and the role of the participant
    (e.g., 'system', 'user', 'assistant').

    Attributes:
        content: The actual text content of the message
        role: The role of the participant sending the message.
            Common values include:
            - 'system': System-level instructions or context
            - 'user': Input from the user
            - 'assistant': Responses from the language model
    """

    content: str
    role: str
