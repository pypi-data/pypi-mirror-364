# Copyright 2001 Gareth Rees.  All rights reserved.
# Copyright 2004-2024 Ned Batchelder.  All rights reserved.

# Except where noted otherwise, this software is licensed under the Apache
# License, Version 2.0 (the "License"); you may not use this work except in
# compliance with the License.  You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""XML reporting for slipcover"""

from __future__ import annotations

import functools
import os
import os.path
import re
import sys
import time
import xml.dom.minidom
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Dict, Iterable, List, Tuple

from slipcover.version import __url__, __version__

if TYPE_CHECKING:
    from typing import Sequence, TypeVar

    from .schemas import Coverage, CoverageFile

    SortableItem = TypeVar("SortableItem", bound=Sequence[Any])

DTD_URL = "https://raw.githubusercontent.com/cobertura/web/master/htdocs/xml/coverage-04.dtd"


@functools.lru_cache(maxsize=None)
def _human_key(s: str) -> tuple[list[str | int], str]:
    """Turn a string into a list of string and number chunks.

    "z23a" -> (["z", 23, "a"], "z23a")

    The original string is appended as a last value to ensure the
    key is unique enough so that "x1y" and "x001y" can be distinguished.
    """

    def tryint(s: str) -> str | int:
        """If `s` is a number, return an int, else `s` unchanged."""
        try:
            return int(s)
        except ValueError:
            return s

    return ([tryint(c) for c in re.split(r"(\d+)", s)], s)


def human_sorted(strings: Iterable[str]) -> list[str]:
    """Sort the given iterable of strings the way that humans expect.

    Numeric components in the strings are sorted as numbers.

    Returns the sorted list.

    """
    return sorted(strings, key=_human_key)


def human_sorted_items(
    items: Iterable[SortableItem],
    reverse: bool = False,
) -> list[SortableItem]:
    """Sort (string, ...) items the way humans expect.

    The elements of `items` can be any tuple/list. They'll be sorted by the
    first element (a string), with ties broken by the remaining elements.

    Returns the sorted list of items.
    """
    return sorted(items, key=lambda item: (_human_key(item[0]), *item[1:]), reverse=reverse)


def rate(hit: int, num: int) -> str:
    """Return the fraction of `hit`/`num`, as a string."""
    if num == 0:
        return "1"
    else:
        return "%.4g" % (hit / num)


@dataclass
class PackageData:
    """Data we keep about each "package" (in Java terms)."""

    elements: dict[str, xml.dom.minidom.Element]
    hits: int
    lines: int
    br_hits: int
    branches: int


def appendChild(parent: Any, child: Any) -> None:
    """Append a child to a parent, in a way mypy will shut up about."""
    parent.appendChild(child)


def get_missing_branch_arcs(file_data: CoverageFile) -> Dict[int, List[int]]:
    """Return arcs that weren't executed from branch lines.

    Returns {l1:[l2a,l2b,...], ...}

    """
    mba: Dict[int, List[int]] = {}
    for branch in file_data["missing_branches"]:
        mba.setdefault(branch[0], []).append(branch[1])

    return mba


def get_branch_stats(
    file_data: CoverageFile, missing_arcs: Dict[int, List[int]]
) -> Dict[int, Tuple[int, int]]:
    """Get stats about branches.

    Returns a dict mapping line numbers to a tuple:
    (total_exits, taken_exits).

    """
    all_branches = sorted(file_data["executed_branches"] + file_data["missing_branches"])

    exits: Dict[int, int] = defaultdict(lambda: 0)
    for branch in all_branches:
        exits[branch[0]] += 1

    stats = {}
    for branch in all_branches:
        lnum = branch[0]
        stats[lnum] = (exits[lnum], exits[lnum] - len(missing_arcs.get(lnum, [])))

    return stats


class XmlReporter:
    """A reporter for writing Cobertura-style XML coverage results."""

    def __init__(
        self,
        coverage: Coverage,
        source: Iterable[str],
        with_branches: bool,
        xml_package_depth: int
    ) -> None:
        self.coverage = coverage
        self.xml_package_depth = xml_package_depth
        self.with_branches = with_branches

        self.source_paths = set()
        for src in source:
            if os.path.exists(src):
                self.source_paths.add(src.rstrip(r"\/"))
        self.packages: dict[str, PackageData] = {}
        self.xml_out: xml.dom.minidom.Document

    def report(self, outfile: IO[str] | None = None) -> None:
        """Generate a Cobertura-compatible XML report.

        `outfile` is a file object to write the XML to.

        """
        # Initial setup.
        outfile = outfile or sys.stdout

        # Create the DOM that will store the data.
        impl = xml.dom.minidom.getDOMImplementation()
        assert impl is not None
        self.xml_out = impl.createDocument(None, "coverage", None)

        # Write header stuff.
        xcoverage = self.xml_out.documentElement
        xcoverage.setAttribute("version", __version__)
        xcoverage.setAttribute("timestamp", str(int(time.time() * 1000)))
        xcoverage.appendChild(self.xml_out.createComment(f" Generated by slipcover: {__url__} "))
        xcoverage.appendChild(self.xml_out.createComment(f" Based on {DTD_URL} "))

        # Call xml_file for each file in the data.
        for file_path, file_data in self.coverage["files"].items():
            self.xml_file(file_path, file_data)

        xsources = self.xml_out.createElement("sources")
        xcoverage.appendChild(xsources)

        # Populate the XML DOM with the source info.
        for path in human_sorted(self.source_paths):
            xsource = self.xml_out.createElement("source")
            appendChild(xsources, xsource)
            txt = self.xml_out.createTextNode(path)
            appendChild(xsource, txt)

        lnum_tot, lhits_tot = 0, 0
        bnum_tot, bhits_tot = 0, 0

        xpackages = self.xml_out.createElement("packages")
        xcoverage.appendChild(xpackages)

        # Populate the XML DOM with the package info.
        for pkg_name, pkg_data in human_sorted_items(self.packages.items()):
            xpackage = self.xml_out.createElement("package")
            appendChild(xpackages, xpackage)
            xclasses = self.xml_out.createElement("classes")
            appendChild(xpackage, xclasses)
            for _, class_elt in human_sorted_items(pkg_data.elements.items()):
                appendChild(xclasses, class_elt)
            xpackage.setAttribute("name", pkg_name.replace(os.sep, "."))
            xpackage.setAttribute("line-rate", rate(pkg_data.hits, pkg_data.lines))
            if self.with_branches:
                branch_rate = rate(pkg_data.br_hits, pkg_data.branches)
            else:
                branch_rate = "0"
            xpackage.setAttribute("branch-rate", branch_rate)
            xpackage.setAttribute("complexity", "0")

            lhits_tot += pkg_data.hits
            lnum_tot += pkg_data.lines
            bhits_tot += pkg_data.br_hits
            bnum_tot += pkg_data.branches

        xcoverage.setAttribute("lines-valid", str(lnum_tot))
        xcoverage.setAttribute("lines-covered", str(lhits_tot))
        xcoverage.setAttribute("line-rate", rate(lhits_tot, lnum_tot))
        if self.with_branches:
            xcoverage.setAttribute("branches-valid", str(bnum_tot))
            xcoverage.setAttribute("branches-covered", str(bhits_tot))
            xcoverage.setAttribute("branch-rate", rate(bhits_tot, bnum_tot))
        else:
            xcoverage.setAttribute("branches-covered", "0")
            xcoverage.setAttribute("branches-valid", "0")
            xcoverage.setAttribute("branch-rate", "0")
        xcoverage.setAttribute("complexity", "0")

        # Write the output file.
        outfile.write(serialize_xml(self.xml_out))

    def xml_file(self, file_path: str, file_data: CoverageFile) -> None:
        """Add to the XML report for a single file."""

        # Create the "lines" and "package" XML elements, which
        # are populated later.  Note that a package == a directory.
        filename = file_path.replace("\\", "/")
        for source_path in self.source_paths:
            if filename.startswith(source_path.replace("\\", "/") + "/"):
                rel_name = filename[len(source_path) + 1:]
                break
        else:
            full_name = Path(file_path).resolve()
            rel_name = str(full_name.relative_to(Path.cwd()))
            self.source_paths.add(str(full_name)[:-len(rel_name)].rstrip(r"\/"))

        dirname = os.path.dirname(rel_name) or "."
        dirname = "/".join(dirname.split("/")[: self.xml_package_depth])
        package_name = dirname.replace("/", ".")

        package = self.packages.setdefault(package_name, PackageData({}, 0, 0, 0, 0))

        xclass: xml.dom.minidom.Element = self.xml_out.createElement("class")

        appendChild(xclass, self.xml_out.createElement("methods"))

        xlines = self.xml_out.createElement("lines")
        appendChild(xclass, xlines)

        xclass.setAttribute("name", os.path.relpath(rel_name, dirname))
        xclass.setAttribute("filename", rel_name.replace("\\", "/"))
        xclass.setAttribute("complexity", "0")

        if self.with_branches:
            missing_branch_arcs = get_missing_branch_arcs(file_data)
            branch_stats = get_branch_stats(file_data, missing_branch_arcs)

        # For each statement, create an XML "line" element.
        all_lines = sorted(file_data["executed_lines"] + file_data["missing_lines"])
        for line in all_lines:
            xline = self.xml_out.createElement("line")
            xline.setAttribute("number", str(line))
            xline.setAttribute("hits", str(int(line not in file_data["missing_lines"])))

            if self.with_branches:
                if line in branch_stats:
                    total, taken = branch_stats[line]
                    xline.setAttribute("branch", "true")
                    xline.setAttribute(
                        "condition-coverage",
                        "%d%% (%d/%d)" % (100 * taken // total, taken, total),
                    )
                if line in missing_branch_arcs:
                    annlines = ["exit" if b <= 0 else str(b) for b in missing_branch_arcs[line]]
                    xline.setAttribute("missing-branches", ",".join(annlines))

            appendChild(xlines, xline)

        class_lines = len(all_lines)
        class_hits = class_lines - len(file_data["missing_lines"])

        if self.with_branches:
            class_branches = sum(t for t, k in branch_stats.values())
            missing_branches = sum(t - k for t, k in branch_stats.values())
            class_br_hits = class_branches - missing_branches
        else:
            class_branches = 0
            class_br_hits = 0

        # Finalize the statistics that are collected in the XML DOM.
        xclass.setAttribute("line-rate", rate(class_hits, class_lines))
        if self.with_branches:
            branch_rate = rate(class_br_hits, class_branches)
        else:
            branch_rate = "0"
        xclass.setAttribute("branch-rate", branch_rate)

        package.elements[rel_name] = xclass
        package.hits += class_hits
        package.lines += class_lines
        package.br_hits += class_br_hits
        package.branches += class_branches


def serialize_xml(dom: xml.dom.minidom.Document) -> str:
    """Serialize a minidom node to XML."""
    return dom.toprettyxml()
