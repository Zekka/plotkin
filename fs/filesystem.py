import glob
import json
import os.path
from .j2customization import environment, dumpall_scraps, extract_scraps
from .scraps import Scraps


class View(object):
    def __init__(self, fs_prefix="out"):
        self.fs_prefix = fs_prefix

    def join(self, *path):
        # use slashes even on windows
        return "/".join(path)

    def rel(self, path):
        return self.join(self.fs_prefix, path)

    def list_generated_code(self):
        lst = []
        try:
            with open(self.rel("generated_code.txt"), "rt") as f:
                for line in f:
                    l = line.strip("\n")
                    if l == "":
                        continue
                    if not os.path.exists(self.rel(l)):
                        continue
                    lst.append(l)
        except FileNotFoundError as fnfe:
            pass
        return lst

    def remove(self, path):
        dirname = os.path.dirname(path)
        try:
            os.remove(self.rel(path))
        except FileNotFoundError as fnfe:
            pass
        while dirname:
            try:
                if os.listdir(self.rel(dirname)) != []:
                    break
            except FileNotFoundError as fnfe:
                break
            os.rmdir(self.rel(dirname))
            dirname = os.path.dirname(dirname)

    def write(self, path, content):
        fullpath = self.rel(path)
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        with open(fullpath, "wt") as f:
            f.write(content)

    def remove_generated_code(self):
        for i in self.list_generated_code():
            self.remove(i)
        self.remove("generated_code.txt")

    def add_to_scraps(self, scraps, fname):
        try:
            with open(self.rel(fname), "rt") as fexisting:
                content = fexisting.read()
                for scrapname, data in extract_scraps(content):
                    print("found scrap: {0} for {1}".format(scrapname, fname))
                    scraps.add(scrapname, data)
        except FileNotFoundError as fnfe:
            print(fnfe)

        try:
            with open(self.rel(fname + ".scraps"), "rt") as fexisting:
                content = fexisting.read()
                for scrapname, data in extract_scraps(content):
                    print("found scrap: {0} for {1}".format(scrapname, fname))
                    scraps.add(scrapname, data)
        except FileNotFoundError as fnfe:
            print(fnfe)

    def update(self, new_code_fn):
        print("Loading old generated code...")
        scraps = Scraps(self)

        for fname in self.list_generated_code():
            with scraps.move_to(fname):
                pass

        def backup_ungrabbed_scraps():
            lists = {}
            for fname in scraps.list_extra_consulted():
                lists[fname] = []

            for fname, fkey, data in scraps.list_all(include_grabbed=False):
                lists[fname] = lists.get(fname, [])
                if data.strip() == "":
                    continue
                lists[fname].append((fkey, data))

            for fname, data in lists.items():
                dumped = dumpall_scraps(data)
                if dumped.strip() == "":
                    self.remove(fname + ".scraps")
                else:
                    self.write(fname + ".scraps", dumpall_scraps(data))

        print("Writing scraps for old generated code...")
        backup_ungrabbed_scraps()

        print("Generating new code...")
        env = environment(scraps)
        new_code = new_code_fn(scraps, env)

        print("Deleting old generated code...")
        for fname in self.list_generated_code():
            self.remove(fname)

        print("Writing new generated code (list)...")
        with open(self.rel("generated_code.txt"), "wt") as f:
            for fname in sorted(new_code.keys()):
                f.write(fname + "\n")

        print("Writing new generated code...")
        for fname, content in new_code.items():
            self.write(fname, content)

        print("Writing condensed scraps...")
        backup_ungrabbed_scraps()
