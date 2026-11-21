#!/usr/bin/env node
// npx uidesignupgrade [--project] [--agent claude|agents|gemini|copilot|opencode|cursor|all]
const fs = require("fs");
const os = require("os");
const path = require("path");

const SRC = path.join(__dirname, "..");
const FILES = ["SKILL.md", "references", "LICENSE"];
const NAME = "uidesignupgrade";
// user-level skill folders; "agents" (~/.agents/skills) is read by Codex, Gemini CLI, Copilot and OpenCode
const USER = {
  claude: ".claude/skills", agents: ".agents/skills", gemini: ".gemini/skills",
  copilot: ".copilot/skills", opencode: ".config/opencode/skills", cursor: ".cursor/skills",
};
const PROJECT = { claude: ".claude/skills", agents: ".agents/skills" };

const args = process.argv.slice(2);
if (args.includes("-h") || args.includes("--help")) {
  console.log(`Usage: npx ${NAME} [--project] [--agent <${Object.keys(USER).join("|")}|all>]...
Default: installs for Claude Code (~/.claude/skills) and Codex, Gemini CLI, Copilot, OpenCode (~/.agents/skills).
--project  install into the current project (.claude/skills and .agents/skills) instead of your home folder.`);
  process.exit(0);
}
const project = args.includes("--project");
const table = project ? PROJECT : USER;
let agents = args.flatMap((a, i) => (a === "--agent" || a === "-a") && args[i + 1] ? [args[i + 1]] : []);
if (agents.includes("all")) agents = Object.keys(table);
if (!agents.length) agents = ["claude", "agents"];
const unknown = agents.filter((a) => !table[a]);
if (unknown.length) {
  console.error(`Unknown agent: ${unknown.join(", ")}. Choose from: ${Object.keys(table).join(", ")}, all`);
  process.exit(1);
}

const base = project ? process.cwd() : os.homedir();
for (const agent of agents) {
  const dest = path.join(base, table[agent], NAME);
  if (path.resolve(dest) === path.resolve(SRC)) continue; // running from an installed copy
  fs.rmSync(dest, { recursive: true, force: true }); // replace an older version cleanly
  fs.mkdirSync(dest, { recursive: true });
  for (const f of FILES) fs.cpSync(path.join(SRC, f), path.join(dest, f), { recursive: true });
  console.log(`Installed for ${agent}: ${dest}`);
}
console.log(`\nDone. Restart or reload skills in your agent, then run /${NAME} (Claude Code) or ask it to upgrade your UI.`);
