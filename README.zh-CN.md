# cursorrules-doctor

[English README](README.md)

在 Cursor、Claude Code、Codex 或其他 AI coding agent 执行之前，先审计你的 `.cursorrules`、`CLAUDE.md`、`AGENTS.md` 和 Copilot instructions。

`cursorrules-doctor` 是一个零依赖 CLI，用来发现危险的 agent 指令：跳过测试、绕过安全限制、破坏性 shell 命令、`curl | bash`、读取 secret、强制推送、生产环境删除或迁移等。

> 非官方项目。本仓库与 Cursor、Anthropic、OpenAI、GitHub 或 Microsoft 没有关联。相关产品名称仅用于说明兼容场景。

## Demo

![cursorrules-doctor demo](demo/demo.svg)

## 快速开始

```bash
python3 cursorrules_doctor.py .
```

生成 GitHub code scanning 可用的 SARIF：

```bash
python3 cursorrules_doctor.py . --sarif cursorrules-doctor.sarif
```

输出 JSON：

```bash
python3 cursorrules_doctor.py . --json
```

## 为什么有用

现在很多仓库都会放 agent instruction 文件。一个写坏的 `.cursorrules` 或 `CLAUDE.md`，可能会悄悄告诉 agent 跳过测试、强制推送、读取密钥，甚至执行破坏性命令。这个工具会在 agent 真正照做之前，先给这些指令文件做一次安全体检。

## 会扫描哪些文件

- `.cursorrules`
- `.cursor/rules/*`
- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`

## GitHub Actions 集成

```yaml
name: Agent Instruction Doctor

on:
  pull_request:

jobs:
  doctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Audit agent instructions
        run: python3 cursorrules_doctor.py . --sarif cursorrules-doctor.sarif
```

## 输出格式

- 终端文本输出：适合本地快速检查
- JSON：适合自动化脚本读取
- SARIF：适合接入 GitHub code scanning

## 路线图

- 自动修复建议
- 面向 Cursor、Claude Code、Codex、Copilot 团队的规则包
- 已接受风险的 baseline 文件
- Markdown 报告输出

## License

MIT
