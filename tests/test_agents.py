"""Guards for agents/: every subagent here is read-only and listed in docs/SUBAGENTS.md.

Passport
  input:   agents/*.md (Claude Code subagent files) and docs/SUBAGENTS.md
  checks:  frontmatter has name, description, tools; name matches the file; tools are a
           subset of the read-only set; every agent appears in the docs table; the
           table names no agent that does not exist; agents/ holds nothing but agents
           (the plugin loader treats every .md there as an agent)
  called:  by CI (python3 -m unittest discover -s tests), and by hand after editing agents/
  breaks:  if Claude Code renames its read-only tools, update READ_ONLY below
  stdlib only.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
DOC = ROOT / "docs" / "SUBAGENTS.md"
READ_ONLY = {"Read", "Glob", "Grep"}


def frontmatter(text: str) -> dict[str, str]:
    text = text.replace("\r\n", "\n")  # a Windows checkout with autocrlf must not read as "no frontmatter"
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def agent_files() -> list[Path]:
    return sorted(p for p in AGENTS.glob("*.md") if p.is_file())


class AgentsTest(unittest.TestCase):
    def test_there_are_agents(self):
        self.assertTrue(agent_files(), "agents/ has no subagent files")

    def test_frontmatter_complete_and_read_only(self):
        for p in agent_files():
            with self.subTest(agent=p.name):
                fm = frontmatter(p.read_text(encoding="utf-8"))
                for key in ("name", "description", "tools"):
                    self.assertTrue(fm.get(key), f"{p.name}: missing '{key}' in frontmatter")
                self.assertEqual(fm["name"], p.stem, f"{p.name}: name must match the file name")
                tools = {t.strip() for t in fm["tools"].split(",") if t.strip()}
                extra = tools - READ_ONLY
                self.assertFalse(extra, f"{p.name}: write-capable tools {sorted(extra)}; agents/ is read-only")

    def test_agents_dir_holds_only_agents(self):
        stray = sorted(
            p.name for p in AGENTS.iterdir()
            if not p.is_file() or p.suffix != ".md" or not frontmatter(p.read_text(encoding="utf-8")).get("name")
        )
        self.assertFalse(stray, f"non-agent files in agents/ would load as agents: {stray}")

    def test_readme_table_matches_files(self):
        doc = DOC.read_text(encoding="utf-8")
        listed = set(re.findall(r"\[`([a-z0-9-]+)`\]\(\.\./agents/\1\.md\)", doc))
        present = {p.stem for p in agent_files()}
        self.assertEqual(listed, present, f"docs/SUBAGENTS.md lists {sorted(listed)}, files are {sorted(present)}")


if __name__ == "__main__":
    unittest.main()
