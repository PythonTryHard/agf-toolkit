import sys
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload


class Encodable(ABC):
    """Base class for all encodable objects."""

    @abstractmethod
    def __eq__(self, other):
        ...

    @abstractmethod
    def as_dict(self) -> dict:
        """Return a dictionary representation of the object."""

    @abstractmethod
    def encode(self) -> str:
        """Encode the object into a string."""

    @classmethod
    @overload
    def decode(cls, encoded_string: str):
        ...

    @classmethod
    @overload
    def decode(cls, encoded_string: Sequence[str]):
        ...

    @classmethod
    def decode(cls, encoded_string: str | Sequence[str]):
        """
        Decode the encoded string into an object.

        Method is overloaded to accept either a string, or a collection of strings.
        """
