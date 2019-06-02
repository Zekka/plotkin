from typing import Dict
from .primitive import ItemRef
from .relation import Relation


class Ontology(object):
    def __init__(self):
        self.relations: Dict[ItemRef, Relation] = {}
        self.next_id = 0

    def create_relation(self, item_ref: ItemRef, lhs, rhs, symmetric):
        if item_ref in self.relations:
            raise ValueError("cannot create another relation called %s" % item_ref)

        self.relations[item_ref] = Relation(item_ref, lhs, rhs, symmetric)
        return self.relations[item_ref]

    def get_relation(self, item_ref: ItemRef):
        return self.relations[item_ref]

    def codegen_metadata(self):
        return {
            ref: relation.codegen_metadata() for ref, relation in self.relations.items()
        }
