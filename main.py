from ir.records.primitive import Domain, ItemRef as RecItemRef
from ir.records.ontology import Ontology as RecordOntology
from ir.relations.primitive import ItemRef as RelationItemRef
from ir.relations.ontology import Ontology as RelationOntology
from ir.relations.relation import Side, Cardinality
from ir.rulebooks.primitive import ItemRef as RuleItemRef
from ir.rulebooks.ontology import Ontology as RulebookOntology
from ir.rulebooks.rulebook import Trigger

records = RecordOntology()
kind_object = records.create_record(RecItemRef.checked(Domain.Kind, "object"))
kind_object.add_field("name", "&'static str")

kind_person = records.create_record(
    RecItemRef.checked(Domain.Kind, "person"), kind_object
)
kind_person.add_field("gender", "&'static str")

kind_food = records.create_record(RecItemRef.checked(Domain.Kind, "food"), kind_object)

entities_cabinet = []
for name, fullname, gender in [
    ("george_bush", '''"George W. Bush"''', '''"Male"'''),
    ("dick_cheney", '''"Dick Cheney"''', '''"Male"'''),
    ("colin_powell", '''"Colin Powell"''', '''"Male"'''),
    ("condoleeza_rice", '''"Condoleeza Rice"''', '''"Female"'''),
    ("paul_oneill", '''"Paul O'Neill"''', '''"Male"'''),
    ("john_snow", '''"John W. Snow"''', '''"Male"'''),
    ("henry_paulson", '''"Henry Paulson"''', '''"Male"'''),
    ("donald_rumsfeld", '''"Donald Rumsfeld"''', '''"Male"'''),
    ("robert_gates", '''"Robert Gates"''', '''"Male"'''),
]:
    entity = records.create_record(RecItemRef.checked(Domain.Entity, name), kind_person)
    entity.add_initializer("name", fullname)
    entity.add_initializer("gender", gender)
    entities_cabinet.append(entity)

entity_pizza = records.create_record(
    RecItemRef.checked(Domain.Entity, "pizza"), kind_food
)
entity_broccoli = records.create_record(
    RecItemRef.checked(Domain.Entity, "broccoli"), kind_food
)
entity_pizza.add_initializer("name", '''"pizza"''')
entity_broccoli.add_initializer("name", '''"broccoli"''')


rulebooks = RulebookOntology()
rulebook_player = rulebooks.create_rulebook(RuleItemRef.checked("player"), "()")

rulebook_player.add_action(
    "Attack(H<world::kinds::person::Type>, H<world::kinds::person::Type>)"
)

rulebook_player.add(Trigger.Instead, "door", "instead_of_opening")
rulebook_player.add(Trigger.Before, "door", "before_opening")
rulebook_player.add(Trigger.Perform, "door", "perform_opening")
rulebook_player.add(Trigger.After, "door", "after_opening")


relations = RelationOntology()
for name, lhs, lhs_card, rhs, rhs_card in [
    ("inside_of", "outer", Cardinality.ManyZero, "inner", Cardinality.OneZero),
    ("outside_of", "inner", Cardinality.OneZero, "outer", Cardinality.ManyZero),
    (
        "has_attacked",
        "attacker",
        Cardinality.ManyZero,
        "defender",
        Cardinality.ManyZero,
    ),
    ("supplies_to", "seller", Cardinality.OneZero, "customer", Cardinality.OneZero),
]:
    relations.create_relation(
        RelationItemRef(name),
        Side(lhs, "usize", lhs_card, None),
        Side(rhs, "isize", rhs_card, None),
        False,
    )

relations.create_relation(
    RelationItemRef("married"),
    Side("spouse", "usize", Cardinality.OneZero, None),
    Side("spouse", "usize", Cardinality.OneZero, None),
    True,
)

favorite_food = relations.create_relation(
    RelationItemRef("favorite_food"),
    Side("favorer", "H<world::kinds::person::Type>", Cardinality.One, kind_person.ref),
    Side("food", "H<world::kinds::food::Type>", Cardinality.ManyZero, kind_food.ref),
    False,
)

for i, ent in enumerate(entities_cabinet):
    favorite_food.add_initializer(
        ent.ref, entity_broccoli.ref if i in [2, 3, 6] else entity_pizza.ref
    )

from codegen import entrypoint
from fs.filesystem import View

v = View("sampleproject/src")
v.update(lambda a1, a2: entrypoint.main(a1, a2, records, rulebooks, relations))
