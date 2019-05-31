from ir.rulebooks.primitive import ItemRef
from ir.rulebooks.rulebook import Rulebook
from typing import Dict, Optional


class Ontology(object):
    def __init__(self):
        self.rulebooks: Dict[ItemRef, Rulebook] = {}

    def create_rulebook(self, item_ref: ItemRef, outcome: str):
        if item_ref in self.rulebooks:
            raise ValueError("cannot create another rulebook called %s" % item_ref)

        self.rulebooks[item_ref] = Rulebook(item_ref, outcome)
        return self.rulebooks[item_ref]

    def get_rulebook(self, item_ref: ItemRef):
        return self.rulebooks[item_ref]

    def codegen_metadata(self):
        return {ref: rulebook.codegen_metadata() for ref, rulebook in self.rulebooks.items()}
