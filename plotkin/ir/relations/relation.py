from enum import Enum
from .primitive import ItemRef
from ..records.primitive import ItemRef as RecordRef
from typing import NamedTuple, Optional, Union

import pprint


class Cardinality(Enum):
    One = "one"  # has no "remove" api
    OneZero = "one?"  # has a "remove" api
    ManyZero = "many?"
    # there's no plain many because having a "remove" api, as many would require, implicitly creates nullability


def oneish(c: Cardinality):
    return c in [Cardinality.One, Cardinality.OneZero]


class Side(NamedTuple):
    name: str
    type: str
    other_cardinality: Cardinality
    kind: Optional[RecordRef]


class Initializer(NamedTuple):
    lhs: Union[str, RecordRef]
    rhs: Union[str, RecordRef]


class Relation(object):
    def __init__(self, ref: ItemRef, lhs: Side, rhs: Side, symmetrical: bool):
        # NOTE: these tables can detect overlapping initializers
        self._initializer_lhs_last = {}
        self._initializer_rhs_last = {}
        self._initializers = []

        self.ref = ref
        self.lhs = lhs
        self.rhs = rhs
        self.symmetrical = symmetrical

        if self.symmetrical and self.lhs.other_cardinality != self.rhs.other_cardinality:
            raise ValueError("left and right hand side must be the same cardinality")

        if self.symmetrical and self.lhs.type != self.rhs.type:
            raise ValueError("left and right hand side must be the same type")

        for side in [self.lhs, self.rhs]:
            has_kind = side.kind is not None
            is_one = side.other_cardinality == Cardinality.One
            if is_one and not has_kind:
                raise ValueError("any side with `one` must have a kind")

        if Cardinality.One in [self.lhs.other_cardinality, self.rhs.other_cardinality]:
            # avoid things that can implicitly remove
            if self.symmetrical:
                raise ValueError(
                    "if the relation is symmetrical, then neither side may be `one`"
                )

        if self.lhs.other_cardinality == Cardinality.One and self.rhs.other_cardinality != Cardinality.ManyZero:
            # because otherwise we would need to remove from the One side to update the other side
            raise ValueError(
                "if one side is `one`, the other side must be `manyzero`"
            )

        if self.rhs.other_cardinality == Cardinality.One and self.lhs.other_cardinality != Cardinality.ManyZero:
            # because otherwise we would need to remove from the One side to update the other side
            raise ValueError(
                "if one side is `one`, the other side must be `manyzero`"
            )

    def add_initializer(self, lhs, rhs):
        assert isinstance(lhs, str) or isinstance(lhs, RecordRef)
        assert isinstance(rhs, str) or isinstance(rhs, RecordRef)

        print(self.lhs)
        print(self.rhs)
        rhs_old = self._initializer_lhs_last.get(lhs)
        if rhs_old and oneish(self.lhs.other_cardinality):
            raise ValueError(
                "can't have duplicate initializers for {} {} ({} vs {})".format(
                    self.lhs.name, lhs, rhs_old, rhs
                )
            )

        lhs_old = self._initializer_rhs_last.get(rhs)
        if lhs_old and oneish(self.rhs.other_cardinality):
            raise ValueError(
                "can't have duplicate initializers for {} {} ({} vs {})".format(
                    self.rhs.name, rhs, lhs_old, lhs
                )
            )

        self._initializer_lhs_last[lhs] = rhs
        self._initializer_rhs_last[rhs] = lhs

        self._initializers.append(Initializer(lhs, rhs))

    def codegen_metadata(
        self, cg_records, cg_records_assignable, cg_assignable_entities
    ):
        print("Generating: {}".format(self))

        for side, accessor in [
            (self.lhs, lambda i: i.lhs),
            (self.rhs, lambda i: i.rhs),
        ]:
            if side.kind is None:
                continue

            needed = set()
            if side.other_cardinality == Cardinality.One:
                needed.update(cg_assignable_entities[side.kind].keys())

            for i in self._initializers:
                needed.discard(accessor(i))

            if len(needed) != 0:
                raise ValueError(
                    "need initializers for: {}".format(
                        sorted(i.element for i in needed)
                    )
                )

            for ent in cg_assignable_entities[side.kind]:
                pprint.pprint(cg_records[ent])

        gen = lambda x, y: {
            "name": x.name,
            "type": x.type,
            "my_cardinality": y.other_cardinality.value,
            "other_cardinality": x.other_cardinality.value,
            "kind": x.kind,
            "other_nullable": x.other_cardinality is not Cardinality.One,
            "other_oneish": oneish(x.other_cardinality),
            "other_manyish": not oneish(x.other_cardinality),
        }
        lhs, rhs = gen(self.lhs, self.rhs), gen(self.rhs, self.lhs)
        return {
            "module_name": "world::relations::" + self.ref.element,
            "ref": self.ref,
            "lhs": lhs,
            "rhs": rhs,
            "initializers": [
                codegen_for_initializer(i, cg_records) for i in self._initializers
            ],
            "symmetrical": self.symmetrical,
            "sides": [lhs, rhs],
            "opposing_sides": [(lhs, rhs)]
            if self.symmetrical
            else [(lhs, rhs), (rhs, lhs)],
        }


def codegen_for_initializer(initializer, cg_records):
    def cg_side(s):
        if isinstance(s, str):
            return s
        if isinstance(s, RecordRef):
            return cg_records[s]["module_name"] + "::ID.cast()"

        raise ValueError("invalid initializer: {}".format(s))

    return {"lhs": cg_side(initializer.lhs), "rhs": cg_side(initializer.rhs)}
