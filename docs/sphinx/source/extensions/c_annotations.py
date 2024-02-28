# -*- coding: utf-8 -*-
# This file has been modified to be used in the caterpillar documentation.
# original license:
# :copyright: Copyright 2007-2014 by Georg Brandl.
# :license: Python license.
from os import path
import docutils
from docutils import nodes
from sphinx.locale import _ as sphinx_gettext

from sphinx import addnodes


# Monkeypatch nodes.Node.findall for forwards compatibility
# This patch can be dropped when the minimum Sphinx version is 4.4.0
# or the minimum Docutils version is 0.18.1.
if docutils.__version_info__ < (0, 18, 1):

    def findall(self, *args, **kwargs):
        return iter(self.traverse(*args, **kwargs))

    nodes.Node.findall = findall


class RCEntry:
    def __init__(self, name):
        self.name = name
        self.result_type = ""
        self.result_refs = None


class Annotations:
    def __init__(self, refcount_filename):
        self.refcount_data = {}
        with open(refcount_filename, "r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line[:1] in ("", "#"):
                    # blank lines and comments
                    continue
                parts = line.split(":", 2)
                if len(parts) != 3:
                    raise ValueError("Wrong field count in %r" % line)
                function, type, refcount = parts
                # Get the entry, creating it if needed:
                try:
                    entry = self.refcount_data[function]
                except KeyError:
                    entry = self.refcount_data[function] = RCEntry(function)
                if not refcount or refcount == "null":
                    refcount = None
                else:
                    refcount = int(refcount)
                entry.result_type = type
                entry.result_refs = refcount

    def add_annotations(self, app, doctree):
        for node in doctree.findall(addnodes.desc_content):
            par = node.parent
            if par["domain"] != "c":
                continue
            if not par[0].has_key("ids") or not par[0]["ids"]:
                continue
            name = par[0]["ids"][0]
            if name.startswith("c."):
                name = name[2:]

            objtype = par["objtype"]
            if objtype != "function":
                continue
            entry = self.refcount_data.get(name)
            if not entry:
                continue

            if not entry.result_type.endswith("Object*"):
                continue

            if entry.result_refs is None:
                rc = sphinx_gettext("Return value: Always NULL.")
            elif entry.result_refs:
                rc = sphinx_gettext("Return value: New reference.")
            else:
                rc = sphinx_gettext("Return value: Borrowed reference.")
            node.insert(0, nodes.emphasis(rc, rc, classes=["refcount"]))


def init_annotations(app):
    annotations = Annotations(
        path.join(app.srcdir, getattr(app.config, "refcount_file", None)),
    )
    app.connect("doctree-read", annotations.add_annotations)


def setup(app):
    app.add_config_value("refcount_file", "", True)
    app.connect("builder-inited", init_annotations)
    return {"version": "1.0", "parallel_read_safe": True}
