from enum import Enum
from .primitive import ItemRef
from typing import NamedTuple


class Cardinality(Enum):
    # ZEKKA NOTE: "One" is not supported yet, hence not available yet
    # One = "one" # has no "remove" api
    OneZero = "one?"  # has a "remove" api
    ManyZero = "many?"
    # there's no plain many because having a "remove" api, as many would require, implicitly creates nullability


class Side(NamedTuple):
    name: str
    type: str
    cardinality: Cardinality


class Relation(object):
    def __init__(self, ref: ItemRef, lhs: Side, rhs: Side, symmetrical: bool):
        self.ref = ref
        self.lhs = lhs
        self.rhs = rhs
        self.symmetrical = symmetrical

        if self.symmetrical and self.lhs.cardinality != self.rhs.cardinality:
            raise ValueError("left and right hand side must be the same cardinality")

        if self.symmetrical and self.lhs.type != self.rhs.type:
            raise ValueError("left and right hand side must be the same type")

        # ZEKKA NOTE: One continues to be disabled
        if False:  # Cardinality.One in [self.lhs.cardinality, self.rhs.cardinality]:
            # avoid things that can implicitly remove
            if self.symmetrical:
                raise ValueError(
                    "if the relation is symmetrical, then neither side may be `one`"
                )

            if self.rhs.cardinality != Cardinality.ManyZero:
                raise ValueError(
                    "if one side is `one`, the other side must be `manyzero`"
                )
            # TODO: Don't generate edit operations for the other side, only permit the other side to be ManyZero

    def codegen_metadata(self):
        side = lambda x: {
            "name": x.name,
            "type": x.type,
            "cardinality": x.cardinality.value,
        }
        lhs, rhs = side(self.lhs), side(self.rhs)
        return {
            "module_name": "world::relations::" + self.ref.element,
            "ref": self.ref,
            "lhs": lhs,
            "rhs": rhs,
            "symmetrical": self.symmetrical,
            "sides": [lhs, rhs],
            "opposing_sides": [(lhs, rhs)]
            if self.symmetrical
            else [(lhs, rhs), (rhs, lhs)],
        }
