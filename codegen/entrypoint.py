import pprint
import jinja2
from ir.records.primitive import Domain
from fs.scraps import Scraps

pp = pprint.PrettyPrinter(indent=2)


def main(scraps: Scraps, env: jinja2.Environment, records, rulebooks, relations):
    files = {}

    def join(*args):
        return "/".join(args)

    def add_file(*path, impl):
        path2 = join(*path)
        with scraps.move_to(path2):
            files[join(*path)] = impl()

    cg_records, cg_records_assignable = records.codegen_metadata()
    pp.pprint(cg_records)
    pp.pprint(cg_records_assignable)



    print()
    print()
    for item_ref, rec in cg_records.items():
        base_path = rec["module_name"].split("::")

        kw = {
            "this": rec,
            "super": cg_records[rec["super_ref"]] if rec["super_ref"] else None,
        }

        add_file(
            *base_path,
            "mod.rs",
            impl=lambda: env.get_template("record/mod.rs.j2").render(**kw)
        )
        add_file(
            *base_path,
            "common.rs",
            impl=lambda: env.get_template("record/common.rs.j2").render(**kw)
        )

    cg_entities = {k: v for k, v in cg_records.items() if k.domain == Domain.Entity}
    cg_kinds = {k: v for k, v in cg_records.items() if k.domain == Domain.Kind}

    cg_assignable_entities = {
        kind: {
            name: "."
            + metadata["super_ref"].element
            + cg_records_assignable.get((metadata["super_ref"], kind))
            for name, metadata in cg_entities.items()
            if (metadata["super_ref"], kind) in cg_records_assignable
        }
        for kind in cg_kinds.keys()
    }

    cg_rulebooks = rulebooks.codegen_metadata()
    pp.pprint(cg_rulebooks)
    for item_ref, cg_rulebook in cg_rulebooks.items():
        base_path = ["world", "rulebooks", item_ref.element]
        add_file(
            *base_path,
            "handler.rs",
            impl=lambda: env.get_template("rulebook/handler.rs.j2").render(rulebook=cg_rulebook),
        )
        add_file(
            *base_path,
            "types.rs",
            impl=lambda: env.get_template("rulebook/types.rs.j2").render(rulebook=cg_rulebook),
        )
        add_file(
            *base_path,
            "mod.rs",
            impl=lambda: env.get_template("rulebook/mod.rs.j2").render(rulebook=cg_rulebook),
        )
        add_file(
            *base_path,
            "chapters",
            "mod.rs",
            impl=lambda: env.get_template("rulebook/mod_chapters.rs.j2").render(rulebook=cg_rulebook),
        )

        for chapter_name, chapter in cg_rulebook["chapters"].items():
            chapter_path = base_path + ["chapters", chapter_name + ".rs"]
            add_file(
                *chapter_path,
                impl=lambda: env.get_template("rulebook/chapter/chapter.rs.j2").render(chapter=chapter),
            )

    add_file(
        "world",
        "rulebooks",
        "mod.rs",
        impl=lambda: env.get_template("mod_rulebooks.rs.j2").render(rulebooks=cg_rulebooks)
    )

    cg_relations = relations.codegen_metadata()
    pp.pprint(cg_relations)

    for item_ref, cg_relation in cg_relations.items():
        base_path = ["world", "relations", item_ref.element]
        add_file(
            *base_path,
            "common.rs",
            impl=lambda: env.get_template("relation/common.rs.j2").render(relation=cg_relation),
        )
        add_file(
            *base_path,
            "mod.rs",
            impl=lambda: env.get_template("relation/mod.rs.j2").render(relation=cg_relation),
        )

    add_file(
        "world",
        "relations",
        "mod.rs",
        impl=lambda: env.get_template("mod_relations.rs.j2").render(relations=cg_relations)
    )

    directory_kw = dict(
        entities=cg_entities,
        kinds=cg_kinds,
        assignable=cg_records_assignable,
        assignable_entities=cg_assignable_entities,
        relations=cg_relations,
    )

    add_file(
        "world",
        "entities",
        "mod.rs",
        impl=lambda: env.get_template("mod_entities.rs.j2").render(**directory_kw),
    )

    add_file(
        "world",
        "kinds",
        "mod.rs",
        impl=lambda: env.get_template("mod_kinds.rs.j2").render(**directory_kw),
    )

    add_file(
        "world",
        "mod.rs",
        impl=lambda: env.get_template("mod_world.rs.j2").render(**directory_kw),
    )

    add_file(
        "world",
        "directory.rs",
        impl=lambda: env.get_template("directory.rs.j2").render(**directory_kw),
    )

    return files
