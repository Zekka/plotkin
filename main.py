from ir.records.primitive import Domain, ItemRef
from ir.records.ontology import Ontology

onto = Ontology()
kind_object = onto.create_record(ItemRef.checked(Domain.Kind, "object"))
kind_object.add_field("name", "&'static str")

kind_person = onto.create_record(ItemRef.checked(Domain.Kind, "person"), kind_object)
kind_room = onto.create_record(ItemRef.checked(Domain.Kind, "room"), kind_object)

# kind_object.add_initializer("name", '''"test"''')
# kind_room.add_initializer("name", '''"barf"''')

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
    entity = onto.create_record(ItemRef.checked(Domain.Entity, name), kind_person)
    entity.add_initializer("name", fullname)
    entity.add_initializer("gender", gender)

# pp.pprint(onto.codegen_metadata())

from codegen import entrypoint
from fs.filesystem import View

v = View("sampleproject/src")
v.update(lambda *args: entrypoint.main(*args, onto))

"""
from fs.j2customization import environment
from fs.scraps import Scraps

scraps = Scraps()
with scraps.move_to("test.rs"):
    scraps.add("test", "test block content")

env = environment(scraps)
with scraps.move_to("test.rs"):
    print(env.get_template("test.rs.j2").render())
"""

"""
def new_code(env):
    return {
        "test1.rs": "test code",
        "test2.rs": "test code 2",
    }

from fs.filesystem import View
v = View("sampleproject")
v.update(new_code)
"""
