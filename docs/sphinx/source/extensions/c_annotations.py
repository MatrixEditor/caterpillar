# -*- coding: utf-8 -*-
# This file has been modified to be used in the caterpillar documentation.
# original license:
# :copyright: Copyright 2007-2014 by Georg Brandl.
# :license: Python license.
from os import path
import docutils
from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.locale import _ as sphinx_gettext

from sphinx import addnodes, application


class RCEntry:
    def __init__(self, name):
        self.name = name
        self.result_type = ""
        self.result_refs = None


class Annotations:
    def __init__(self, refcount_filename):
        self.refcount_data = {}
        self.typedef_data = {}
        with open(refcount_filename, "r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line[:1] in ("", "#"):
                    # blank lines and comments
                    continue
                def_type, *parts = line.split(":")
                match def_type:
                    case "func":
                        index, name, rtype, refcount = parts
                        # Get the entry, creating it if needed:
                        entry = self.refcount_data.get(name)
                        if not entry:
                            entry = self.refcount_data[name] = RCEntry(name)
                        if not refcount or refcount == "null":
                            refcount = None
                        else:
                            refcount = int(refcount)
                        entry.result_type = rtype
                        entry.result_refs = refcount

                    case "type":
                        index, struct_name, typedef_name, py_type = parts
                        if py_type != "-":
                            self.typedef_data[py_type] = typedef_name

    def add_py_annotations(
        self, app: application.Sphinx, node: docutils.nodes.Element, par
    ):

        if not par[0].has_key("ids") or not par[0]["ids"]:
            return

        name = par[0]["ids"][0]
        if not name.startswith("caterpillar.c."):
            return

        if par["objtype"] != "class":
            return

        name = name[14:]
        if name in self.typedef_data:
            typedef_name = self.typedef_data[name]

            rc = sphinx_gettext(f"C API Type: {typedef_name}")
            node.insert(0, nodes.emphasis(rc, rc, classes=["refcount", "text-info"]))
            node.insert(1, nodes.line())

    def add_c_annotation(self, app, node, par):
        if not par[0].has_key("ids") or not par[0]["ids"]:
            return

        name = par[0]["ids"][0]
        if name.startswith("c."):
            name = name[2:]

        objtype = par["objtype"]
        if objtype != "function":
            return
        entry = self.refcount_data.get(name)
        if not entry:
            return

        if not entry.result_type.endswith("Object*"):
            return

        if entry.result_refs is None:
            rc = sphinx_gettext("Return value: Always NULL.")
        elif entry.result_refs:
            rc = sphinx_gettext("Return value: New reference.")
        else:
            rc = sphinx_gettext("Return value: Borrowed reference.")
        node.insert(0, nodes.emphasis(rc, rc, classes=["refcount", "text-info"]))

    def add_annotations(self, app, doctree):
        for node in doctree.findall(addnodes.desc_content):
            par = node.parent
            match par["domain"]:
                case "c":
                    self.add_c_annotation(app, node, par)

                case "py":
                    self.add_py_annotations(app, node, par)


def init_annotations(app):
    annotations = Annotations(
        path.join(app.srcdir, getattr(app.config, "refcount_file", None)),
    )
    app.connect("doctree-read", annotations.add_annotations)


def setup(app):
    app.add_config_value("refcount_file", "", True)
    app.connect("builder-inited", init_annotations)
    return {"version": "1.0", "parallel_read_safe": True}
