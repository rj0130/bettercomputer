#!/usr/bin/env python3
"""Repo hygiene gate for bettercomputer. Standard library only.

Checks:
  1. Every path referenced in code spans in CLAUDE.md and project/state.md exists.
  2. project/state.md has an **Updated:** line.
  3. Every file in phone/docs/research/ (if any) carries an `as-of` line.
  4. Every unit marked done in project/plan.md has its listed files present.
Exit 1 on any failure; prints what to fix.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAIL = []
WARN = []


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def check_refs(rel):
    text = read(rel)
    for m in re.finditer(r"`([A-Za-z0-9_./-]+\.(?:md|py|yaml|json|csv|svg|step|stl|plist))`", text):
        p = m.group(1)
        if "*" in p or "{" in p or p.startswith("<"):
            continue
        if p.startswith("/"):
            if not os.path.exists(p):
                FAIL.append(f"{rel}: references missing file `{p}`")
            continue
        cands = [p, os.path.join("phone", p), os.path.join("project", p), os.path.join("phone/design", p), os.path.join("phone/tools", p)]
        if not any(os.path.exists(os.path.join(ROOT, c)) for c in cands):
            FAIL.append(f"{rel}: references missing file `{p}`")


def check_state():
    if "**Updated:**" not in read("project/state.md"):
        FAIL.append("project/state.md: missing **Updated:** line")


def check_research():
    d = os.path.join(ROOT, "phone/docs/research")
    if not os.path.isdir(d):
        return
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md") and "as-of" not in read(f"phone/docs/research/{fn}").lower():
            FAIL.append(f"phone/docs/research/{fn}: no as-of date")


def check_plan():
    for line in read("project/plan.md").splitlines():
        if not line.startswith("| U"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6 or cells[5] != "done":
            continue
        for m in re.finditer(r"`([A-Za-z0-9_./-]+\.(?:md|py|yaml|json|csv))`", cells[2]):
            p = m.group(1)
            cands = [p, os.path.join("phone", p), os.path.join("project", p), os.path.join("phone/design", p)]
            if not any(os.path.exists(os.path.join(ROOT, c)) for c in cands):
                FAIL.append(f"project/plan.md: {cells[0]} is done but `{p}` is missing")


def main():
    check_refs("CLAUDE.md")
    check_refs("project/state.md")
    check_state()
    check_research()
    check_plan()
    for w in WARN:
        print("WARN", w)
    for f in FAIL:
        print("FAIL", f)
    print("check.py:", "FAIL" if FAIL else "OK", f"({len(FAIL)} failures, {len(WARN)} warnings)")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
