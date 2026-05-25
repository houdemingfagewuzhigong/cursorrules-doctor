# Launch Promotion

Repository: https://github.com/houdemingfagewuzhigong/cursorrules-doctor

## Hacker News

Title:

Show HN: cursorrules-doctor - audit Cursor/Claude/Codex agent instructions

Body:

I built a small zero-dependency CLI for a risk I keep seeing in AI coding-agent repos: instruction files are becoming executable culture.

`cursorrules-doctor` audits `.cursorrules`, `.cursor/rules/*`, `CLAUDE.md`, `AGENTS.md`, and `.github/copilot-instructions.md` before Cursor, Claude Code, Codex, Copilot, or another agent obeys them.

It flags instructions like skipping tests, bypassing safety, destructive shell commands, remote scripts piped to shell, secret reads, force pushes, and production mutations. It outputs terminal text, JSON, and SARIF.

Repo: https://github.com/houdemingfagewuzhigong/cursorrules-doctor

## Reddit r/opensource

I built `cursorrules-doctor`, a zero-dependency CLI that audits AI coding-agent instruction files before agents obey them.

It scans `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, and Copilot instructions for risky directives: skip tests, force push, read secrets, run `curl | bash`, destructive shell commands, or production mutation instructions.

Repo: https://github.com/houdemingfagewuzhigong/cursorrules-doctor

Question: what other risky agent instructions should be caught by default?

## Reddit r/selfhosted

For people running local AI coding agents or MCP workflows: I made `cursorrules-doctor`, a tiny Python CLI that audits instruction files like `.cursorrules`, `CLAUDE.md`, and `AGENTS.md`.

It is meant to catch dangerous defaults before an agent follows them: skip tests, read secrets, force push, run destructive shell commands, etc. Outputs JSON/SARIF for automation.

Repo: https://github.com/houdemingfagewuzhigong/cursorrules-doctor

## Reddit r/programming

Agent instruction files are becoming part of the codebase. I built `cursorrules-doctor` to audit `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and Copilot instructions before Cursor/Claude Code/Codex-style agents obey them.

It flags risky directives and exports SARIF/JSON.

Repo: https://github.com/houdemingfagewuzhigong/cursorrules-doctor

## X Short Post

Built cursorrules-doctor: audit `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, and Copilot instructions before Cursor/Claude/Codex-style agents obey them.

Flags skip-tests, force-push, secret reads, destructive shell, curl|bash. JSON + SARIF.

https://github.com/houdemingfagewuzhigong/cursorrules-doctor

## X Long Post

AI coding-agent instruction files are quietly becoming part of the codebase.

A bad `.cursorrules`, `CLAUDE.md`, or `AGENTS.md` can tell an agent to skip tests, read secrets, force push, or run destructive shell commands.

I built `cursorrules-doctor` to audit those files before Cursor/Claude Code/Codex/Copilot-style agents obey them.

Zero dependencies. Text, JSON, and SARIF output.

Repo: https://github.com/houdemingfagewuzhigong/cursorrules-doctor

## Naming Note

This is an unofficial compatibility/audit tool. Product names are used descriptively, not to imply affiliation or endorsement.
