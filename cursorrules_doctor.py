#!/usr/bin/env python3
"""Audit AI coding-agent instruction files before agents obey them."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


INSTRUCTION_FILES = {
    ".cursorrules",
    "CLAUDE.md",
    "AGENTS.md",
    ".github/copilot-instructions.md",
    ".cursor/rules",
}

IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    title: str
    severity: str
    pattern: re.Pattern[str]
    advice: str


@dataclass
class Finding:
    rule_id: str
    title: str
    severity: str
    path: str
    line: int
    snippet: str
    advice: str


RULES = [
    Rule(
        "agent.ignore_safety",
        "Instruction tells agent to ignore safety or policy",
        "critical",
        re.compile(r"(?i)\b(ignore|bypass|disable)\b.{0,40}\b(safety|policy|guardrail|permission)\b"),
        "Remove instructions that ask agents to bypass safety checks or permissions.",
    ),
    Rule(
        "agent.skip_tests",
        "Instruction discourages tests or verification",
        "high",
        re.compile(r"(?i)\b(skip|avoid|do not run|don't run)\b.{0,40}\b(test|tests|lint|typecheck|verification)\b"),
        "Prefer explicit verification commands instead of telling agents to skip checks.",
    ),
    Rule(
        "agent.destructive_shell",
        "Destructive shell command appears in agent instructions",
        "critical",
        re.compile(r"(?i)\b(rm\s+-rf|chmod\s+777|mkfs|dd\s+if=|sudo\s+rm|git\s+push\s+--force)\b"),
        "Move destructive commands behind human approval and document safer alternatives.",
    ),
    Rule(
        "agent.remote_shell",
        "Remote script piped to shell",
        "critical",
        re.compile(r"(?i)\b(curl|wget)\b.+\|\s*(bash|sh|zsh)"),
        "Do not ask agents to pipe remote scripts directly into a shell.",
    ),
    Rule(
        "agent.secret_request",
        "Instruction asks agent to read or print secrets",
        "critical",
        re.compile(r"(?i)\b(read|print|show|dump|cat)\b.{0,40}\b(\.env|secret|token|api[_-]?key|password)\b"),
        "Keep secrets outside agent-readable instructions and use secret managers.",
    ),
    Rule(
        "agent.no_confirmation",
        "Instruction removes confirmation for risky actions",
        "high",
        re.compile(r"(?i)\b(no confirmation|without asking|do not ask|don't ask)\b.{0,60}\b(delete|deploy|push|overwrite|migrate|drop)\b"),
        "Require human confirmation for delete, deploy, push, overwrite, migration, and data-loss actions.",
    ),
    Rule(
        "agent.production_mutation",
        "Instruction references production mutation",
        "high",
        re.compile(r"(?i)\b(production|prod)\b.{0,60}\b(drop|delete|truncate|migrate|overwrite|deploy)\b"),
        "Separate production operations from agent default instructions.",
    ),
]


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(severity, 9)


def iter_instruction_files(root: Path):
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        current = Path(current_root)
        for filename in filenames:
            path = current / filename
            rel = path.relative_to(root).as_posix()
            if filename in INSTRUCTION_FILES or rel in INSTRUCTION_FILES or rel.startswith(".cursor/rules/"):
                yield path


def redact(snippet: str) -> str:
    snippet = snippet.strip()
    snippet = re.sub(r"github_pat_[A-Za-z0-9_]{8,}", "github_pat_...redacted", snippet)
    snippet = re.sub(r"ghp_[A-Za-z0-9]{8,}", "ghp_...redacted", snippet)
    snippet = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-...redacted", snippet)
    snippet = re.sub(r"(?i)(token|secret|password|api[_-]?key)(\s*[:=]\s*)\S+", r"\1\2...redacted", snippet)
    return snippet[:220]


def scan_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings

    rel = path.relative_to(root).as_posix()
    for line_no, line in enumerate(lines, start=1):
        if "doctor: allow" in line:
            continue
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(
                    Finding(
                        rule.rule_id,
                        rule.title,
                        rule.severity,
                        rel,
                        line_no,
                        redact(line),
                        rule.advice,
                    )
                )
    return findings


def scan(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for path in iter_instruction_files(root):
        findings.extend(scan_file(path, root))
    return sorted(findings, key=lambda item: (severity_rank(item.severity), item.path, item.line))


def print_text(findings: list[Finding]) -> None:
    if not findings:
        print("No risky Cursor/Claude/Codex agent instructions found.")
        return
    for finding in findings:
        print(f"[{finding.severity.upper()}] {finding.title}")
        print(f"  {finding.path}:{finding.line}")
        print(f"  {finding.snippet}")
        print(f"  fix: {finding.advice}")


def sarif(findings: list[Finding]) -> dict:
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "cursorrules-doctor",
                        "informationUri": "https://github.com/houdemingfagewuzhigong/cursorrules-doctor",
                        "rules": [],
                    }
                },
                "results": [
                    {
                        "ruleId": finding.rule_id,
                        "level": "error" if finding.severity == "critical" else "warning",
                        "message": {"text": finding.title + ": " + finding.advice},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": finding.path},
                                    "region": {"startLine": finding.line},
                                }
                            }
                        ],
                    }
                    for finding in findings
                ],
            }
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit .cursorrules, CLAUDE.md, AGENTS.md, and Copilot instructions for risky agent directives."
    )
    parser.add_argument("path", nargs="?", default=".", help="repo path")
    parser.add_argument("--json", action="store_true", help="print JSON findings")
    parser.add_argument("--sarif", help="write SARIF findings to a file")
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "low"],
        default="high",
        help="exit non-zero on this severity or worse",
    )
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    findings = scan(root)
    if args.json:
        print(json.dumps([asdict(item) for item in findings], indent=2))
    else:
        print_text(findings)

    if args.sarif:
        Path(args.sarif).write_text(json.dumps(sarif(findings), indent=2) + "\n")

    threshold = severity_rank(args.fail_on)
    return 1 if any(severity_rank(item.severity) <= threshold for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
