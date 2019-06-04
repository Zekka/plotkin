from plotkin.errors import CompilerError
from typing import Dict, Optional
from plotkin.ir.records.primitive import Domain, ItemRef, Field

Literal = str


class Record(object):
    def __init__(self, id: int, ref: ItemRef, super_record: Optional["Record"]):
        # TODO: Check if super_record is really a Record
        self.id = id
        self.ref = ref
        self.super_record: Optional[Record] = super_record
        self._unique_fields: Dict[str, Field] = {}
        self._unique_initializers: Dict[str, Literal] = {}

    def add_field(self, name, type):
        existing = self.try_get_field(name)
        field = Field(type, name)

        if existing is not None:
            if existing != field:
                raise CompilerError(
                    "field already exists (is defined as {0}): cannot add contradictory definition as {1}".format(
                        existing, field
                    )
                )
            return

        self._unique_fields[name] = field

    def add_initializer(self, field_name, initializer):
        existing_field = self.try_get_field(field_name)
        if existing_field is None:
            raise CompilerError(
                "cannot add initializer for field that is not defined yet ({0})".format(
                    field_name
                )
            )

        # we can override initializers from superrecords -- we can't have duplicate initializers at the same level
        if field_name in self._unique_initializers:
            raise CompilerError(
                "initializer already exists in record (already defined as {0}): cannot add contradictory definition as {1}".format(
                    self._unique_initializers.get(field_name, initializer)
                )
            )

        self._unique_initializers[field_name] = initializer

    def try_get_field(self, name):
        unique = self._unique_fields.get(name)
        if unique is not None:
            return unique

        if self.super_record is None:
            return None

        super_field = self.super_record.try_get_field(name)
        if super_field is None:
            return None

        return Field(
            type=super_field.type,
            path="{0}.{1}".format(self.super_record.ref.element, super_field.path),
        )

    def get_field(self, name):
        field = self.try_get_field(name)
        if field is None:
            raise CompilerError("missing field: {0}".format(name))
        return field

    def record_mro(self):
        yield self

        if self.super_record is not None:
            for i in self.super_record.record_mro():
                yield i

    # we don't respect any kind of resolution order for initializers
    # because it's handled by the order of calls to init()
    # so I don't provide MRO-style accessors for them yet

    # field listing
    def unique_fields(self):
        for field_name in self._unique_fields:
            yield field_name

    def inherited_fields(self):
        if self.super_record is None:
            return

        for field_name in self.super_record.all_fields():
            yield field_name

    def all_fields(self):
        for field_name in self.unique_fields():
            yield field_name

        for field_name in self.inherited_fields():
            yield field_name

    def codegen_metadata(self, super_uninitialized_fields):
        # super_uninitialized_fields should be [] if there's no super record
        # otherwise it should be the result of codegen_metadata
        result = {}
        result["id"] = self.id
        result["ref"] = self.ref
        result["super_ref"] = self.super_record.ref if self.super_record else None
        result["is_kind"] = self.ref.domain == Domain.Kind

        result["unique_fields"] = {
            field_name: self.get_field(field_name)
            for field_name in self.unique_fields()
        }
        result["inherited_fields"] = {
            field_name: self.get_field(field_name)
            for field_name in self.inherited_fields()
        }
        result["all_fields"] = {
            field_name: self.get_field(field_name) for field_name in self.all_fields()
        }
        # result["unique_initializers"] = self._unique_initializers

        # result["super_uninitialized_fields"] = super_uninitialized_fields
        result["uninitialized_fields"] = {
            field_name: self.get_field(field_name)
            for field_name in self.all_fields()
            if (
                field_name in super_uninitialized_fields
                or field_name in result["unique_fields"]
            )
            and field_name not in self._unique_initializers
        }

        # == initializers can appear in the args rec for super, the literal for this, or the code after the literal for this ==
        result["initializers_for_super"] = {
            field_name: self._unique_initializers[field_name]
            for field_name in self._unique_initializers
            if field_name in super_uninitialized_fields
        }
        result["propagate_for_super"] = {
            field_name: field_name
            for field_name in result["uninitialized_fields"]
            if field_name in super_uninitialized_fields
        }
        result["initializers_for_this_lit"] = {
            field_name: self._unique_initializers[field_name]
            for field_name in self._unique_initializers
            if field_name in result["unique_fields"]
        }
        result["propagate_for_this_lit"] = {
            field_name: field_name
            for field_name in result["uninitialized_fields"]
            if field_name in result["unique_fields"]
        }
        result["initializers_for_init"] = {
            field_name: self._unique_initializers[field_name]
            for field_name in self._unique_initializers
            if not (
                field_name in result["initializers_for_super"]
                or field_name in result["initializers_for_this_lit"]
            )
        }

        return result
