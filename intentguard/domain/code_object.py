import inspect
import logging
from dataclasses import dataclass
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


@dataclass
class CodeObject:
    """
    A class representing a named piece of code for evaluation.

    This class encapsulates source code along with an identifier, making it suitable
    for use in LLM-based code analysis and evaluation. It provides functionality to
    extract source code from Python objects and create CodeObject instances from
    dictionary mappings.

    Attributes:
        code: The source code content as a string
        name: An identifier for the code object, typically the variable or function name
    """

    code: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> List["CodeObject"]:
        """
        Create CodeObject instances from a dictionary of Python objects.

        This method attempts to extract source code from each object in the provided
        dictionary using Python's inspect module. For objects where source code
        cannot be retrieved, a placeholder comment is used instead.

        Args:
            data: Dictionary mapping names to Python objects (functions, classes, etc.)

        Returns:
            List of CodeObject instances, one for each entry in the input dictionary

        Example:
            >>> def example_func():
            ...     pass
            >>> code_objects = CodeObject.from_dict({'func': example_func})
            >>> print(code_objects[0].name)  # 'func'
            >>> print(code_objects[0].code)  # Source code of example_func
        """
        logger.debug("Creating code objects from dictionary with %d items", len(data))
        result = []
        for name, obj in data.items():
            try:
                source: str = inspect.getsource(obj)
                logger.debug("Successfully extracted source code for '%s'", name)
            except TypeError:
                logger.warning(
                    "Could not extract source code for '%s', using placeholder", name
                )
                source = f"# Could not retrieve source code for object '{name}'"
            except Exception as e:
                logger.error(
                    "Unexpected error extracting source code for '%s': %s", name, str(e)
                )
                source = f"# Error retrieving source code for object '{name}': {str(e)}"
            result.append(CodeObject(code=source, name=name))
        logger.debug("Created %d code objects", len(result))
        return result
