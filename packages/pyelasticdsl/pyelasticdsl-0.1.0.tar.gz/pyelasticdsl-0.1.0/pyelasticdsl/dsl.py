from abc import ABC, abstractmethod
from typing import Dict, Any


class Query(ABC):

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the query object to a JSON-serializable dictionary.
        """
        pass