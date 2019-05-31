from typing import NamedTuple


class ItemRef(NamedTuple):
    element: str

    @classmethod
    def checked(cls, element: str):
        return ItemRef(element)

