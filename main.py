from ir.records.primitive import Domain, ItemRef as RecItemRef
from ir.records.ontology import Ontology as RecordOntology
from ir.rulebooks.primitive import ItemRef as RuleItemRef
from ir.rulebooks.ontology import Ontology as RulebookOntology
from ir.rulebooks.rulebook import Trigger

records = RecordOntology()
kind_object = records.create_record(RecItemRef.checked(Domain.Kind, "object"))
kind_object.add_field("name", "&'static str")

kind_person = records.create_record(RecItemRef.checked(Domain.Kind, "person"), kind_object)
kind_person.add_field("gender", "&'static str")

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


rulebooks = RulebookOntology()
rulebook_player = rulebooks.create_rulebook(RuleItemRef.checked("player"), "()")

rulebook_player.add_action("Attack(H<world::kinds::person::Type>, H<world::kinds::person::Type>)")

rulebook_player.add(Trigger.Instead, "door", "instead_of_opening")
rulebook_player.add(Trigger.Before, "door", "before_opening")
rulebook_player.add(Trigger.Perform, "door", "perform_opening")
rulebook_player.add(Trigger.After, "door", "after_opening")

from codegen import entrypoint
from fs.filesystem import View

v = View("sampleproject/src")
v.update(lambda a1, a2: entrypoint.main(a1, a2, records, rulebooks))
