import pprint
import jinja2
from ir.records.primitive import Domain
from fs.scraps import Scraps

pp = pprint.PrettyPrinter(indent=2)


def main(scraps: Scraps, env: jinja2.Environment, ontology):
    files = {}

    def join(*args):
        return "/".join(args)

    def add_file(*path, impl):
        path2 = join(*path)
        with scraps.move_to(path2):
            files[join(*path)] = impl()

    cg_meta, assignable = ontology.codegen_metadata()
    pp.pprint(cg_meta)
    pp.pprint(assignable)

    print()
    print()
    for item_ref, rec in cg_meta.items():
        base_path = rec["module_name"].split("::")

        kw = {
            "this": rec,
            "super": cg_meta[rec["super_ref"]] if rec["super_ref"] else None,
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

    entities = {k: v for k, v in cg_meta.items() if k.domain == Domain.Entity}
    kinds = {k: v for k, v in cg_meta.items() if k.domain == Domain.Kind}

    assignable_entities = {
        kind: {
            name: "."
            + metadata["super_ref"].element
            + assignable.get((metadata["super_ref"], kind))
            for name, metadata in entities.items()
            if (metadata["super_ref"], kind) in assignable
        }
        for kind in kinds.keys()
    }

    directory_kw = dict(
        entities=entities,
        kinds=kinds,
        assignable=assignable,
        assignable_entities=assignable_entities,
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
