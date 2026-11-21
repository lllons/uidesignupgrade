# Setup instructions for agents

You are a coding agent installing the **uidesignupgrade** skill for your user. Follow these steps in order. Install at **user level** so it works in every project, unless the user asked for this project only.

## 1. Work out which agent you are

Claude Code, Codex, Gemini CLI, GitHub Copilot, OpenCode, Cursor, or another agent that reads `SKILL.md` files.

## 2. Run the matching install

| Agent | Command |
|-------|---------|
| Claude Code | `claude plugin marketplace add lllons/uidesignupgrade` then `claude plugin install uidesignupgrade@lllons-plugins` |
| Gemini CLI | `gemini skills install https://github.com/lllons/uidesignupgrade.git --consent` |
| Codex, GitHub Copilot, OpenCode | `git clone https://github.com/lllons/uidesignupgrade "$HOME/.agents/skills/uidesignupgrade"` |
| Cursor or any other agent | `npx uidesignupgrade --agent all` (or `npx skills add lllons/uidesignupgrade -g`) |

For this project only (when the user asks): `npx uidesignupgrade --project`, or clone into the project's `.agents/skills/uidesignupgrade` (or `.claude/skills/uidesignupgrade` for Claude Code).

## 3. If the command isn't available

Clone the repo into your agent's personal skills folder instead:

| Agent | Folder |
|-------|--------|
| Claude Code | `~/.claude/skills/uidesignupgrade` |
| Codex, Gemini CLI, Copilot, OpenCode | `~/.agents/skills/uidesignupgrade` |
| Gemini CLI (alternative) | `~/.gemini/skills/uidesignupgrade` |
| GitHub Copilot (alternative) | `~/.copilot/skills/uidesignupgrade` |
| OpenCode (alternative) | `~/.config/opencode/skills/uidesignupgrade` |

```sh
git clone https://github.com/lllons/uidesignupgrade "<folder from the table>"
```

If the folder already exists, update it with `git pull` inside it instead of cloning again.

## 4. Verify

- `SKILL.md` exists in the installed folder.
- The `references/` folder exists next to it, with `motion.md`, `ux-laws.md`, `typography.md`, `color.md`, `unslop.md` and `patterns.md`.
- Reload skills if your agent needs it (for example `/skills reload` in Gemini CLI or Copilot), or tell the user to restart the agent.

## 5. Tell the user

- How to run it: `/uidesignupgrade` in Claude Code (`/uidesignupgrade:uidesignupgrade` when installed as a plugin), `$uidesignupgrade` in Codex, or simply ask the agent to "upgrade the UI design" in any agent.
- Then offer to run it on the current project.

## Rules

- Don't change the user's other skills, settings or config files while installing.
- If an install command fails, report the error and try the next option in step 3; don't retry the same command repeatedly.
- Never ask the user for passwords or tokens; this install needs none.
