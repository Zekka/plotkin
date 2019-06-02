from io import StringIO
from jinja2 import Environment, PackageLoader


def environment(scraps):
    env = Environment(
        loader=PackageLoader(__name__, "../templates"),
        line_statement_prefix="%",
        cache_size=0,  # some of our templates are quite bad and have side effects
    )
    env.filters["scrap"] = lambda *a, **kw: _scrap(scraps, *a, **kw)
    return env


START_SCRAP = "// START SCRAP "
END_SCRAP = "// END SCRAP "


def _scrap(scraps, name, indent=0):
    return "{1}{3}{0}\n{2}\n{1}{4}{0}".format(
        name, " " * (indent * 4), scraps.grab(name), START_SCRAP, END_SCRAP
    )


def extract_scraps(content):
    in_scrap = None
    current_scrap = []

    for line in content.split("\n"):
        start_scrap = (
            line.strip()[len(START_SCRAP) :]
            if line.strip().startswith(START_SCRAP)
            else None
        )
        end_scrap = (
            line.strip()[len(END_SCRAP) :]
            if line.strip().startswith(END_SCRAP)
            else None
        )

        if start_scrap and " " in start_scrap:
            start_scrap = None

        if end_scrap and " " in end_scrap:
            end_scrap = None

        if start_scrap is None and START_SCRAP in line:
            raise ValueError(
                "looks like a failed attempt to start a scrap: must be whole line"
            )

        if end_scrap is None and END_SCRAP in line:
            raise ValueError(
                "looks like a failed attempt to end a scrap: must be whole line"
            )

        if in_scrap is not None:
            if start_scrap is not None:
                raise ValueError(
                    "cannot start scrap {0} while in the middle of scrap {1}".format(
                        start_scrap, in_scrap
                    )
                )

            if end_scrap is not None:
                if end_scrap != in_scrap:
                    raise ValueError(
                        "cannot end scrap {0} while in the middle of scrap {1}".format(
                            end_scrap, in_scrap
                        )
                    )

                yield (in_scrap, "\n".join(current_scrap))
                in_scrap = None
                current_scrap = []

            current_scrap.append(line)

        else:
            if start_scrap is not None:
                in_scrap = start_scrap
                current_scrap = []

            if end_scrap is not None:
                raise ValueError(
                    "cannot end scrap {0} while not in a scrap".format(end_scrap)
                )


def dumpall_scraps(items):
    # items: a list of tuples of string scrapname, string content
    output = StringIO()

    for scrap_name, content in items:
        output.write(START_SCRAP)
        output.write(scrap_name)
        output.write("\n")

        output.write(content)
        output.write("\n")

        output.write(END_SCRAP)
        output.write(scrap_name)
        output.write("\n")
        output.write("\n")

    return output.getvalue()
