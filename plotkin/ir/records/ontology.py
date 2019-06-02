from plotkin.ir.records.primitive import ItemRef, Domain
from plotkin.ir.records.record import Record
from typing import Dict, Optional


class Ontology(object):
    def __init__(self):
        self.records: Dict[ItemRef, Record] = {}
        self.next_id = 0

    def create_record(self, item_ref: ItemRef, super: Optional[Record] = None):
        if item_ref.domain == Domain.Entity:
            id = self.next_id
            self.next_id += 1
        else:
            id = None
        self.records[item_ref] = Record(id, item_ref, super)
        return self.records[item_ref]

    def get_record(self, item_ref: ItemRef):
        return self.records[item_ref]

    def codegen_metadata(self):
        table = {}
        for ir in self.records.keys():
            self._generate(table, ir)

        assignable = {}
        for src, dest_metadata in table.items():
            how = ""
            while True:
                assignable[(src, dest_metadata["ref"])] = how
                dest_metadata = table.get(dest_metadata["super_ref"])
                if dest_metadata is None:
                    break
                how += "." + dest_metadata["ref"].element

        return table, assignable

    def _generate(self, table, item_ref):
        record = self.records[item_ref]
        if record.super_record is not None:
            if record.super_record not in table:
                self._generate(table, record.super_record.ref)
            gen_super = table[record.super_record.ref]
            unf = gen_super["uninitialized_fields"]
        else:
            unf = []

        table[item_ref] = record.codegen_metadata(super_uninitialized_fields=unf)
        table[item_ref]["module_name"] = self.get_module_name(item_ref)

    def get_module_name(self, item_ref: ItemRef):
        if item_ref.domain == Domain.Entity:
            return "world::entities::{0}".format(item_ref.element)

        elif item_ref.domain == Domain.Kind:
            return "world::kinds::{0}".format(item_ref.element)

        else:
            raise ValueError("unknown module name: {0}".format(item_ref))
