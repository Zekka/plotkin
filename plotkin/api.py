from plotkin.ir.records.ontology import Ontology as RecordOntology
from plotkin.ir.relations.ontology import Ontology as RelationOntology
from plotkin.ir.rulebooks.ontology import Ontology as RulebookOntology

from plotkin.ir.records.primitive import Domain, ItemRef as RecItemRef
from plotkin.ir.relations.primitive import ItemRef as RelationItemRef
from plotkin.ir.relations.relation import Side, Cardinality
from plotkin.ir.rulebooks.primitive import ItemRef as RuleItemRef
from plotkin.ir.rulebooks.rulebook import Trigger

from plotkin.codegen import entrypoint
from plotkin.fs.filesystem import View


# TODO: Forbid duplicate or reserved names
class API(object):
    def __init__(self):
        self.records = RecordOntology()
        self.relations = RelationOntology()
        self.rulebooks = RulebookOntology()

    def update(self, path):
        v = View(path)
        # TODO: The args to entrypoint.main are in the wrong order (not alphabetical)
        v.update(
            lambda scraps, env: entrypoint.main(
                scraps, env, self.records, self.rulebooks, self.relations
            )
        )

    def create_entity(self, name, kind=None):
        return self.records.create_record(RecItemRef.checked(Domain.Entity, name), kind)

    def create_kind(self, name, super_kind=None):
        return self.records.create_record(
            RecItemRef.checked(Domain.Kind, name), super_kind
        )

    def create_rulebook(self, name, output):
        return self.rulebooks.create_rulebook(RuleItemRef.checked(name), output)

    def _create_relation(self, ref, lhs, rhs, symmetric):
        return self.relations.create_relation(ref, lhs, rhs, symmetric)

    def create_relation_symmetric(
        self, name, lr_name, lr_type, lr_cardinality, lr_domain
    ):
        return self.relations.create_relation(
            RelationItemRef(name),
            Side(lr_name, lr_type, lr_cardinality, lr_domain),
            Side(lr_name, lr_type, lr_cardinality, lr_domain),
            True,
        )

    # == DSL for relations ==
    # TODO: Higher-level type for type/domains
    def relate(self, name):
        return _Relate(self, name)


class _Relate(object):
    def __init__(self, api, name):
        self.api = api
        self.name = name

    def from_one(self, lhs_name, lhs_type, lhs_domain, optional=True):
        return _RelateLHS(
            self.api,
            self.name,
            lhs_name,
            lhs_type,
            Cardinality.OneZero if optional else Cardinality.One,
            lhs_domain,
        )

    def from_many(self, lhs_name, lhs_type, lhs_domain):
        return _RelateLHS(
            self.api, self.name, lhs_name, lhs_type, Cardinality.ManyZero, lhs_domain
        )

    def one_symmetric(self, lr_name, lr_type, lr_domain, optional=True):
        side = Side(
            lr_name,
            lr_type,
            Cardinality.OneZero if optional else Cardinality.One,
            lr_domain,
        )
        return _RelateLHS_RHS(self.api, RelationItemRef(self.name), side, side, True)

    def many_symmetric(self, lr_name, lr_type, lr_domain):
        side = (Side(lr_name, lr_type, Cardinality.ManyZero, lr_domain),)
        return _RelateLHS_RHS(self.api, RelationItemRef(self.name), side, side, True)


class _RelateLHS(object):
    def __init__(self, api, name, lhs_name, lhs_type, lhs_cardinality, lhs_domain):
        self.api = api
        self.name = name
        self.lhs_name = lhs_name
        self.lhs_type = lhs_type
        self.lhs_cardinality = lhs_cardinality
        self.lhs_domain = lhs_domain

    def to_one(self, rhs_name, rhs_type, rhs_domain, optional=True):
        return self._to(
            rhs_name,
            rhs_type,
            Cardinality.OneZero if optional else Cardinality.One,
            rhs_domain,
        )

    def to_many(self, rhs_name, rhs_type, rhs_domain):
        return self._to(rhs_name, rhs_type, Cardinality.ManyZero, rhs_domain)

    def _to(self, rhs_name, rhs_type, rhs_cardinality, rhs_domain):
        return _RelateLHS_RHS(
            self.api,
            RelationItemRef(self.name),
            Side(self.lhs_name, self.lhs_type, self.lhs_cardinality, self.lhs_domain),
            Side(rhs_name, rhs_type, rhs_cardinality, rhs_domain),
            False,
        )


class _RelateLHS_RHS(object):
    def __init__(self, api, ref, lhs, rhs, symmetric):
        self.api = api
        self.ref = ref
        self.lhs = lhs
        self.rhs = rhs
        self.symmetric = symmetric

    def create(self):
        return self.api._create_relation(self.ref, self.lhs, self.rhs, self.symmetric)
