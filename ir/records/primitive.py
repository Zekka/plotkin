from enum import Enum
from typing import NamedTuple


class Domain(Enum):
    Kind = "kind"
    Entity = "entity"


class ItemRef(NamedTuple):
    domain: Domain
    element: str

    @classmethod
    def checked(cls, domain: Domain, element: str):
        assert isinstance(domain, Domain)
        assert isinstance(element, str)
        return ItemRef(domain, element)


class Field(NamedTuple):
    type: str
    path: str
