from plotkin import API

api = API()

kind_object = api.create_kind("object")
kind_object.add_field("name", "&'static str")

kind_person = api.create_kind("person", kind_object)
kind_person.add_field("gender", "&'static str")

kind_food = api.create_kind("food", kind_object)

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
    entity = api.create_entity(name, kind_person)
    entity.add_initializer("name", fullname)
    entity.add_initializer("gender", gender)
    entities_cabinet.append(entity)

entity_pizza = api.create_entity("pizza", kind_food)
entity_broccoli = api.create_entity("broccoli", kind_food)

entity_pizza.add_initializer("name", '''"pizza"''')
entity_broccoli.add_initializer("name", '''"broccoli"''')

rulebook_player = api.create_rulebook("player", "()")
rulebook_player.add_action(
    "Attack(H<world::kinds::person::Type>, H<world::kinds::person::Type>)"
)

rulebook_player.add_instead("door", "instead_of_opening")
rulebook_player.add_before("door", "before_opening")
rulebook_player.add_perform("door", "perform_opening")
rulebook_player.add_after("door", "after_opening")

# TODO: Relation cardinality is backwards. Fix that
api.relate("inside_of").from_many("inner", "usize", None).to_one(
    "outer", "isize", None
).create()

api.relate("outside_of").from_one("outer", "usize", None).to_many(
    "inner", "isize", None
).create()

api.relate("has_attacked").from_many("attacker", "usize", None).to_many(
    "target", "isize", None
).create()

api.relate("supplies_to").from_one("seller", "usize", None).to_one(
    "buyer", "isize", None
).create()

api.relate("married_to").one_symmetric("spouse", "usize", None).create()

favorite_food = (
    api.relate("favorite_food")
    .from_many("favorer", "H<world::kinds::person::Type>", kind_person.ref)
    .to_one("food", "H<world::kinds::food::Type>", kind_food.ref, optional=False)
    .create()
)

for i, ent in enumerate(entities_cabinet):
    favorite_food.add_initializer(
        ent.ref, entity_broccoli.ref if i in [2, 3, 6] else entity_pizza.ref
    )

api.update("sampleproject/src")

"""
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
"""
