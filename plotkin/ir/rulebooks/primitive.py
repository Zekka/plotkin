from typing import NamedTuple


class ItemRef(NamedTuple):
    element: str

    @classmethod
    def checked(cls, element: str):
        assert isinstance(element, str)
        return ItemRef(element)
