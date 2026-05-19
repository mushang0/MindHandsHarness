#!/usr/bin/env python3
"""MindHandsHarness v2 runtime CLI.

The v2 harness has one standing decision role, one standing action role, and
script-managed state. The CLI owns project maps, task packets, memory writes,
skill indexes, session events, and boot-context rendering.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path


HARNESS = Path(".harness")
CONTEXT = HARNESS / "context"
MEMORY = HARNESS / "memory"
POLICIES = HARNESS / "policies"
ROLES = HARNESS / "roles"
RUNTIME = HARNESS / "runtime"
SESSIONS = RUNTIME / "sessions"
MEMORY_PROPOSALS = RUNTIME / "memory-proposals"
SKILLS = HARNESS / "skills"
TEMPLATES = HARNESS / "templates"
STATE = RUNTIME / "state.json"
MAP_MD = CONTEXT / "project-map.md"
MAP_INDEX = CONTEXT / "project-map.index.json"
MAP_DIFF = CONTEXT / "map-update-report.md"

EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}


def now():
    return dt.datetime.now().replace(microsecond=0).isoformat()


def today():
    return dt.datetime.now().strftime("%Y-%m-%d")


def compact_date():
    return dt.datetime.now().strftime("%Y%m%d")


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def read_text(path, default=""):
    if not path.exists():
        return default
    return path.read_text()


def write_text(path, text):
    ensure_dir(path.parent)
    path.write_text(text)


def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path, data):
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def next_id(prefix, parent):
    ensure_dir(parent)
    stem = f"{prefix}-{compact_date()}-"
    existing = []
    for path in parent.iterdir():
        if path.name.startswith(stem):
            try:
                existing.append(int(path.name.split("-")[-1]))
            except ValueError:
                pass
    return f"{stem}{(max(existing) + 1 if existing else 1):03d}"


def default_state():
    return {
        "version": 2,
        "active_session_id": None,
        "active_task_id": None,
        "mode": "coordinator_executor",
        "last_context_refresh": None,
    }


def load_state():
    state = read_json(STATE, default_state())
    for key, value in default_state().items():
        state.setdefault(key, value)
    return state


def save_state(state):
    write_json(STATE, state)


def active_session_dir(state=None):
    state = state or load_state()
    session_id = state.get("active_session_id")
    if not session_id:
        return None
    return SESSIONS / session_id


def emit_event(event_type, actor, summary, task_id=None, details_ref=None, artifacts=None):
    state = load_state()
    session_dir = active_session_dir(state)
    if not session_dir:
        return
    ensure_dir(session_dir)
    event = {
        "time": now(),
        "type": event_type,
        "actor": actor,
        "summary": summary,
    }
    if task_id:
        event["task_id"] = task_id
    if details_ref:
        event["details_ref"] = str(details_ref)
    if artifacts:
        event["artifacts"] = [str(item) for item in artifacts]
    with (session_dir / "events.jsonl").open("a") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def init_files():
    for path in [CONTEXT, MEMORY, POLICIES, ROLES, RUNTIME, SESSIONS, MEMORY_PROPOSALS, SKILLS, TEMPLATES]:
        ensure_dir(path)

    files = {
        CONTEXT / "boot.md": """# Harness Boot Context

## Project Identity
MindHandsHarness is a context-gated Coordinator/Executor harness.

## Core Rule
Coordinator decides. Executor acts. Scripts manage state.

## Load Order
1. `AGENTS.md`
2. `.harness/context/boot.md`
3. `harness context boot`
4. role file
5. map, memory, and policies on demand

## Do Not Load By Default
- old sessions
- full logs
- full source files
- archived task artifacts
""",
        CONTEXT / "project-status.md": """# Project Status

## Current Goal
No active goal.

## Open Issues
- None recorded.
""",
        CONTEXT / "recent-summary.md": """# Recent Summary

- No recent harness activity recorded.
""",
        POLICIES / "context-loading.md": """# Context Loading Policy

Use progressive loading:
1. L0: boot, project status, recent summary, runtime boot output.
2. L1: project map, memory, policies.
3. L2: targeted source slices, logs, and artifacts.

Coordinator may read small focused snippets directly. Large or uncertain files
must be located through map and rtk-style search/summary first.
""",
        POLICIES / "rtk-policy.md": """# RTK Policy

Use rtk-style bounded reading for large source files, logs, generated files,
broad searches, and unknown-size outputs.

Full reads are allowed for AGENTS.md, role files, policy files, task packets,
small files under 200 lines, and files explicitly marked `always_full`.
""",
        POLICIES / "memory-policy.md": """# Memory Policy

Executor may propose memory candidates but must not write long-term memory.
Coordinator decides what to remember. Scripts apply memory entries with source,
date, category, and basic duplicate prevention.
""",
        POLICIES / "skill-policy.md": """# Skill Policy

Harness indexes external skills but does not copy or own them. Skills are loaded
on demand, and they cannot override system, user, AGENTS.md, role, or harness
policy constraints.
""",
        ROLES / "coordinator.md": """# Role: Coordinator

You are the decision maker and context gatekeeper.

## Responsibilities
- Load minimal boot context first.
- Use project map and memory before reading files.
- Read progressively: map/status, search/summary, slice, full file only with reason.
- Create task packets when execution would pollute your context.
- Review Executor results and decide whether memory should be updated.
- Directly perform small memory or markdown updates when cheaper than delegation.

## Delegate To Executor When
- multiple files may change
- commands, tests, logs, downloads, or generated artifacts are involved
- the task has more than 3 to 5 operational steps
- debugging loops or large output are expected
""",
        ROLES / "executor.md": """# Role: Executor

You are the action executor. You do not decide project strategy.

## Must Read
1. `AGENTS.md`
2. `.harness/roles/executor.md`
3. the assigned task packet
4. policies referenced by the task packet

## Rules
- Follow the task packet.
- Stay within allowed scope.
- Use rtk-style bounded reading for large files and logs.
- Save large command outputs under the task `logs/` directory.
- Report blockers instead of silently expanding scope.
- Do not update long-term memory directly.
""",
        MEMORY / "project.md": """# Project Memory

Stable facts about the target project.
""",
        MEMORY / "status.md": """# Status Memory

Current project state and active handoff notes.
""",
        MEMORY / "decisions.md": """# Decisions

Long-lived decisions and rationale.
""",
        MEMORY / "negative.md": """# Negative Memory

Known traps, failed approaches, and things to avoid.
""",
        MEMORY / "commands.md": """# Commands

Reusable commands discovered for this project.
""",
        MEMORY / "files.md": """# Important Files

Important files and why they matter.
""",
        MEMORY / "user-preferences.md": """# User Preferences

Stable user preferences for this project.
""",
        MEMORY / "lessons.md": """# Lessons

Reusable lessons from completed tasks.
""",
    }

    for path, content in files.items():
        if not path.exists():
            write_text(path, content)

    if not (SKILLS / "registry.json").exists():
        write_json(SKILLS / "registry.json", {"version": 1, "skills": []})
    if not (SKILLS / "registry.md").exists():
        write_text(SKILLS / "registry.md", "# Skill Registry\n\nNo skills indexed yet.\n")
    if not STATE.exists():
        save_state(default_state())


def command_init(_args):
    init_files()
    print("Initialized MindHandsHarness v2 skeleton.")


def command_start(args):
    init_files()
    state = load_state()
    session_id = next_id("S", SESSIONS)
    session_dir = SESSIONS / session_id
    ensure_dir(session_dir / "tasks")
    write_json(
        session_dir / "session.json",
        {
            "session_id": session_id,
            "objective": args.objective,
            "created_at": now(),
            "status": "active",
        },
    )
    state["active_session_id"] = session_id
    state["active_task_id"] = None
    state["last_context_refresh"] = now()
    save_state(state)
    emit_event("SESSION_START", "user", args.objective)
    write_text(
        CONTEXT / "project-status.md",
        f"# Project Status\n\n## Current Goal\n{args.objective}\n\n## Active Session\n{session_id}\n\n## Open Issues\n- None recorded.\n",
    )
    write_text(CONTEXT / "recent-summary.md", f"# Recent Summary\n\n- {today()}: Started `{session_id}` for {args.objective}.\n")
    print(f"Started session {session_id}")


def command_context_boot(_args):
    init_files()
    state = load_state()
    status = read_text(CONTEXT / "project-status.md").strip()
    recent = read_text(CONTEXT / "recent-summary.md").strip()
    recent_tasks = recent_session_tasks(state)
    print("# Boot Context")
    print()
    print("## Runtime")
    print(f"- mode: {state.get('mode')}")
    print(f"- active_session_id: {state.get('active_session_id')}")
    print(f"- active_task_id: {state.get('active_task_id')}")
    print()
    print("## Core Rule")
    print("Coordinator decides. Executor acts. Scripts manage state.")
    print()
    print("## Project Status")
    print(status)
    print()
    print("## Recent Summary")
    print(recent)
    print()
    print("## Recent Tasks")
    if recent_tasks:
        for task in recent_tasks:
            print(f"- {task['task_id']}: {task['summary']} ({task['type']})")
    else:
        print("- None recorded.")
    print()
    print("## Important Constraints")
    print("- Coordinator decides. Executor acts.")
    print("- Scripts manage maps, tasks, memory, skills, and session state.")
    print("- Use rtk-style bounded reads for large files, logs, searches, and command outputs.")
    print()
    print("## Suggested Next Action")
    if state.get("active_task_id"):
        print(f"- Continue or collect active task `{state['active_task_id']}`.")
    elif state.get("active_session_id"):
        print("- Create the next task packet or update memory/status.")
    else:
        print("- Start a session with `python3 .harness/bin/harness.py start \"<objective>\"`.")


def recent_session_tasks(state, limit=5):
    session_dir = active_session_dir(state)
    if not session_dir:
        return []
    event_path = session_dir / "events.jsonl"
    if not event_path.exists():
        return []
    tasks = []
    for line in event_path.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("task_id") and event.get("type") in {"TASK_CREATED", "EXECUTOR_DISPATCHED", "EXECUTOR_RESULT"}:
            tasks.append(
                {
                    "task_id": event["task_id"],
                    "type": event.get("type", ""),
                    "summary": event.get("summary", ""),
                }
            )
    return tasks[-limit:]


def command_context_probe(args):
    init_files()
    state, session_dir = require_session()
    task_id = args.task_id or state.get("active_task_id")
    task_dir = session_dir / "tasks" / task_id
    if not task_dir.exists():
        raise SystemExit(f"Error: task not found: {task_id}")
    probe_path = task_dir / "context-probes.md"
    current = read_text(probe_path, "# Context Probes\n")
    count = current.count("## Probe") + 1
    entry = f"""
## Probe {count}
- purpose: {args.purpose}
- method: {args.method}
- source: {args.source}
- result: {args.result}
- time: {now()}
"""
    write_text(probe_path, current.rstrip() + "\n" + entry)
    emit_event("CONTEXT_PROBE", "coordinator", args.purpose, task_id=task_id, details_ref=probe_path)
    print(f"Recorded probe for {task_id}")


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_skip(path):
    parts = set(path.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if path.is_dir():
        return True
    if path == MAP_INDEX or path == MAP_MD or path == MAP_DIFF:
        return True
    if path.as_posix().startswith(".harness/runtime/"):
        return True
    return False


def load_policy_for(path, line_count):
    if path.as_posix() in {"AGENTS.md"}:
        return "always_full"
    if path.as_posix().startswith(".harness/roles/") or path.as_posix().startswith(".harness/policies/"):
        return "always_full"
    if line_count <= 200:
        return "full_allowed"
    return "rtk_summary_first"


def scan_project():
    entries = []
    for path in sorted(Path(".").rglob("*")):
        if should_skip(path):
            continue
        rel = path.as_posix()[2:] if path.as_posix().startswith("./") else path.as_posix()
        try:
            text = path.read_text(errors="ignore")
            line_count = len(text.splitlines())
        except OSError:
            line_count = 0
        stat = path.stat()
        entries.append(
            {
                "path": rel,
                "type": "file",
                "size": stat.st_size,
                "hash": file_hash(path),
                "line_count": line_count,
                "load_policy": load_policy_for(Path(rel), line_count),
                "summary": summarize_path(rel),
            }
        )
    return entries


def summarize_path(path):
    if path == "AGENTS.md":
        return "Universal router and manifest."
    if path.startswith(".harness/roles/"):
        return "Role definition."
    if path.startswith(".harness/policies/"):
        return "Harness policy."
    if path.startswith(".harness/context/"):
        return "Project context artifact."
    if path.startswith(".harness/memory/"):
        return "Long-term memory file."
    if path.startswith(".harness/bin/"):
        return "Runtime CLI script."
    return "Project file."


def write_project_map(entries):
    lines = [
        "# Project Map",
        "",
        "## Project Purpose",
        "MindHandsHarness is a context-gated Coordinator/Executor harness.",
        "",
        "## Important Files",
    ]
    for entry in entries:
        if entry["path"] in {"AGENTS.md", ".harness/bin/harness.py"} or entry["path"].startswith(".harness/roles/"):
            lines.append(f"- `{entry['path']}`: {entry['summary']} ({entry['load_policy']})")
    lines.extend(["", "## Indexed Files"])
    for entry in entries:
        lines.append(f"- `{entry['path']}`: {entry['summary']}")
    lines.extend(["", f"## Last Updated\n{today()}", ""])
    write_text(MAP_MD, "\n".join(lines))
    write_json(MAP_INDEX, {"version": 1, "last_updated": now(), "entries": entries})


def command_map(args):
    init_files()
    old_entries = {item["path"]: item for item in read_json(MAP_INDEX, {"entries": []}).get("entries", [])}
    entries = scan_project()
    new_entries = {item["path"]: item for item in entries}

    if args.map_command in ["init", "update"]:
        added = sorted(set(new_entries) - set(old_entries))
        removed = sorted(set(old_entries) - set(new_entries))
        changed = sorted(
            path for path in set(new_entries) & set(old_entries)
            if new_entries[path]["hash"] != old_entries[path]["hash"]
        )
        write_project_map(entries)
        report = ["# Map Update Report", ""]
        report.append("## Added")
        report.extend([f"- {path}" for path in added] or ["- None"])
        report.append("")
        report.append("## Changed")
        report.extend([f"- {path}" for path in changed] or ["- None"])
        report.append("")
        report.append("## Removed")
        report.extend([f"- {path}" for path in removed] or ["- None"])
        write_text(MAP_DIFF, "\n".join(report) + "\n")
        print("\n".join(added + changed + removed) if added or changed or removed else "Map is current.")
    elif args.map_command == "show":
        print(read_text(MAP_MD, "# Project Map\n\nNo map generated. Run `harness map init`.\n"))
    elif args.map_command == "diff":
        print(read_text(MAP_DIFF, "No map diff recorded.\n"))


def require_session():
    state = load_state()
    session_dir = active_session_dir(state)
    if not session_dir:
        raise SystemExit("Error: no active session. Run `harness start \"<objective>\"` first.")
    ensure_dir(session_dir / "tasks")
    return state, session_dir


def command_task(args):
    init_files()
    if args.task_command == "new":
        state, session_dir = require_session()
        task_id = next_id("T", session_dir / "tasks")
        task_dir = session_dir / "tasks" / task_id
        ensure_dir(task_dir / "logs")
        ensure_dir(task_dir / "artifacts")
        task = f"""# Task Packet

## Task ID
{task_id}

## Title
{args.title}

## Mode
{args.mode}

## Objective
{args.objective}

## Background
Use the boot context, project map, memory, and policies only as needed.

## Allowed Scope
{args.allowed or "- Not specified. Ask Coordinator before changing files."}

## Forbidden Scope
{args.forbidden or "- Do not broaden scope silently."}

## Steps
{format_semicolon_list(args.steps)}

## Tool Policy
- Use rtk-style bounded reads for large files, logs, generated files, and broad searches.
- Save large outputs under `{task_dir / "logs"}`.

## Validation
{args.validation or "- Not specified."}

## Output Required
- `executor_result.md` with Status, Changed Files, Commands Run, Validation, Issues, Tool Policy Compliance, Memory Candidates, Next Suggested Action.
"""
        write_text(task_dir / "task.md", task)
        write_text(task_dir / "context-probes.md", "# Context Probes\n\n- None recorded yet.\n")
        state["active_task_id"] = task_id
        save_state(state)
        emit_event("TASK_CREATED", "coordinator", args.title, task_id=task_id, details_ref=task_dir / "task.md")
        print(f"Created task {task_id}")
    elif args.task_command == "dispatch":
        state, session_dir = require_session()
        task_id = args.task_id or state.get("active_task_id")
        task_dir = session_dir / "tasks" / task_id
        task_path = task_dir / "task.md"
        if not task_path.exists():
            raise SystemExit(f"Error: task not found: {task_id}")
        prompt = "\n\n".join(
            [
                "# Executor Prompt",
                read_text(ROLES / "executor.md"),
                "# Context Loading Policy",
                read_text(POLICIES / "context-loading.md"),
                "# RTK Policy",
                read_text(POLICIES / "rtk-policy.md"),
                "# Assigned Task Packet",
                read_text(task_path),
                "# Result Path",
                f"Write the result to `{task_dir / 'executor_result.md'}`.",
            ]
        )
        write_text(task_dir / "executor_prompt.md", prompt)
        emit_event("EXECUTOR_DISPATCHED", "coordinator", f"Dispatched {task_id}", task_id=task_id)
        print(f"Rendered executor prompt for {task_id}")
    elif args.task_command == "collect":
        state, session_dir = require_session()
        task_id = args.task_id or state.get("active_task_id")
        task_dir = session_dir / "tasks" / task_id
        result_path = task_dir / "executor_result.md"
        if not result_path.exists():
            raise SystemExit(f"Error: result not found: {result_path}")
        result = read_text(result_path)
        candidates = extract_markdown_section(result, "Memory Candidates")
        if candidates:
            write_text(task_dir / "memory_candidates.md", "# Memory Candidates\n\n" + candidates.strip() + "\n")
        emit_event("EXECUTOR_RESULT", "executor", f"Collected {task_id}", task_id=task_id, details_ref=result_path)
        print(result)


def format_semicolon_list(value):
    if not value:
        return "- Not specified."
    items = [item.strip() for item in value.split(";") if item.strip()]
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))


def extract_markdown_section(content, section_name):
    lines = content.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == f"## {section_name}".lower():
            start = idx + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start, len(lines)):
        line = lines[idx]
        if line.startswith("## ") and line.strip().lower() != f"## {section_name}".lower():
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def command_memory(args):
    init_files()
    if args.memory_command == "propose":
        proposal_id = next_id("P", MEMORY_PROPOSALS)
        proposal = {
            "proposal_id": proposal_id,
            "type": args.type,
            "source": args.source,
            "content": args.content,
            "evidence": args.evidence,
            "created_at": now(),
            "status": "pending",
        }
        write_json(MEMORY_PROPOSALS / f"{proposal_id}.json", proposal)
        write_text(
            MEMORY_PROPOSALS / f"{proposal_id}.md",
            f"""# Memory Proposal {proposal_id}

## Type
{args.type}

## Source
{args.source}

## Content
{args.content}

## Evidence
{args.evidence}

## Status
pending
""",
        )
        emit_event("MEMORY_PROPOSED", "coordinator", args.content, details_ref=MEMORY_PROPOSALS / f"{proposal_id}.md")
        print(f"Created proposal {proposal_id}")
        return

    if args.memory_command == "show-boot":
        print("# Memory Boot")
        for name, path in memory_targets().items():
            text = read_text(path).strip()
            if not text:
                continue
            lines = [line for line in text.splitlines() if line.strip()]
            preview_lines = lines[:8]
            tail_lines = lines[-6:]
            if tail_lines != preview_lines[-6:]:
                preview_lines = preview_lines + ["..."] + tail_lines
            preview = "\n".join(preview_lines)
            print()
            print(f"## {name}")
            print(preview)
        return

    if args.memory_command == "compact":
        lines = ["# Recent Summary", ""]
        for proposal_path in sorted(MEMORY_PROPOSALS.glob("*.json"))[-5:]:
            proposal = read_json(proposal_path, {})
            lines.append(f"- {proposal.get('created_at')}: proposal `{proposal.get('proposal_id')}` {proposal.get('type')}: {proposal.get('content')}")
        state = load_state()
        for task in recent_session_tasks(state):
            lines.append(f"- {task['task_id']}: {task['summary']} ({task['type']})")
        if len(lines) == 2:
            lines.append("- No recent harness activity recorded.")
        write_text(CONTEXT / "recent-summary.md", "\n".join(lines) + "\n")
        print("Compacted recent summary.")
        return

    proposal = None
    if args.proposal_id:
        proposal = read_json(MEMORY_PROPOSALS / f"{args.proposal_id}.json", None)
        if not proposal:
            raise SystemExit(f"Error: proposal not found: {args.proposal_id}")
        args.type = proposal["type"]
        args.source = proposal["source"]
        args.content = proposal["content"]

    target = {
        "project": MEMORY / "project.md",
        "status": MEMORY / "status.md",
        "decision": MEMORY / "decisions.md",
        "negative": MEMORY / "negative.md",
        "command": MEMORY / "commands.md",
        "file": MEMORY / "files.md",
        "preference": MEMORY / "user-preferences.md",
        "lesson": MEMORY / "lessons.md",
    }.get(args.type)
    if args.memory_command != "apply":
        raise SystemExit("Error: unsupported memory command.")
    if not target:
        raise SystemExit(f"Error: unsupported memory type: {args.type}")
    current = read_text(target)
    if args.content not in current:
        entry = f"\n## {today()} - {args.source}\n- {args.content}\n"
        write_text(target, current.rstrip() + "\n" + entry)
    recent = read_text(CONTEXT / "recent-summary.md")
    line = f"- {today()}: Memory `{args.type}` updated from `{args.source}`: {args.content}\n"
    if args.content not in recent:
        write_text(CONTEXT / "recent-summary.md", recent.rstrip() + "\n" + line)
    emit_event("MEMORY_UPDATED", "coordinator", args.content, details_ref=target)
    if proposal:
        proposal["status"] = "applied"
        proposal["applied_at"] = now()
        write_json(MEMORY_PROPOSALS / f"{proposal['proposal_id']}.json", proposal)
    print(f"Updated {target}")


def memory_targets():
    return {
        "project": MEMORY / "project.md",
        "status": MEMORY / "status.md",
        "decision": MEMORY / "decisions.md",
        "negative": MEMORY / "negative.md",
        "command": MEMORY / "commands.md",
        "file": MEMORY / "files.md",
        "preference": MEMORY / "user-preferences.md",
        "lesson": MEMORY / "lessons.md",
    }


def parse_skill_name(skill_file):
    text = read_text(skill_file)
    for line in text.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return skill_file.parent.name


def command_skills(args):
    init_files()
    if args.skills_command == "scan":
        root = Path(args.path).expanduser()
        found = []
        if root.exists():
            for skill_file in sorted(root.rglob("SKILL.md")):
                found.append(
                    {
                        "name": parse_skill_name(skill_file),
                        "location": "external",
                        "path_hint": str(skill_file),
                        "trigger": [],
                        "load_policy": "on_demand",
                        "conflict_policy": "harness_priority",
                    }
                )
        write_json(SKILLS / "registry.json", {"version": 1, "skills": found})
        lines = ["# Skill Registry", ""]
        lines.extend([f"- `{item['name']}`: {item['path_hint']}" for item in found] or ["No skills indexed."])
        write_text(SKILLS / "registry.md", "\n".join(lines) + "\n")
        print(f"Indexed {len(found)} skill(s).")
    elif args.skills_command == "list":
        registry = read_json(SKILLS / "registry.json", {"skills": []})
        for item in registry.get("skills", []):
            print(f"{item['name']}\t{item['path_hint']}")
    elif args.skills_command == "register":
        registry = read_json(SKILLS / "registry.json", {"version": 1, "skills": []})
        skills = [item for item in registry.get("skills", []) if item.get("name") != args.name]
        skills.append(
            {
                "name": args.name,
                "location": "external",
                "path_hint": str(Path(args.path).expanduser()),
                "trigger": split_csv(args.trigger),
                "load_policy": "on_demand",
                "conflict_policy": "harness_priority",
            }
        )
        write_skill_registry(skills)
        print(f"Registered skill {args.name}")
    elif args.skills_command == "resolve":
        registry = read_json(SKILLS / "registry.json", {"skills": []})
        for item in registry.get("skills", []):
            if item.get("name") == args.name:
                print(json.dumps(item, indent=2, ensure_ascii=False))
                return
        raise SystemExit(f"Error: skill not found: {args.name}")


def split_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def write_skill_registry(skills):
    write_json(SKILLS / "registry.json", {"version": 1, "skills": skills})
    lines = ["# Skill Registry", ""]
    lines.extend([f"- `{item['name']}`: {item['path_hint']}" for item in skills] or ["No skills indexed."])
    write_text(SKILLS / "registry.md", "\n".join(lines) + "\n")


def command_status(_args):
    init_files()
    state = load_state()
    print("# Harness Status")
    print(f"- version: {state.get('version')}")
    print(f"- mode: {state.get('mode')}")
    print(f"- active_session_id: {state.get('active_session_id')}")
    print(f"- active_task_id: {state.get('active_task_id')}")


def command_doctor(_args):
    init_files()
    issues = []
    for path in [CONTEXT / "boot.md", ROLES / "coordinator.md", ROLES / "executor.md", STATE]:
        if not path.exists():
            issues.append(f"Missing {path}")
    if issues:
        print("# Harness Doctor")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("OK")


def build_parser():
    parser = argparse.ArgumentParser(description="MindHandsHarness v2 runtime CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create v2 skeleton files").set_defaults(func=command_init)

    start = sub.add_parser("start", help="Start a new Coordinator/Executor session")
    start.add_argument("objective")
    start.set_defaults(func=command_start)

    context = sub.add_parser("context", help="Render context artifacts")
    context_sub = context.add_subparsers(dest="context_command", required=True)
    context_sub.add_parser("boot").set_defaults(func=command_context_boot)
    probe = context_sub.add_parser("probe")
    probe.add_argument("--task-id", default="")
    probe.add_argument("--purpose", required=True)
    probe.add_argument("--method", required=True)
    probe.add_argument("--source", required=True)
    probe.add_argument("--result", required=True)
    probe.set_defaults(func=command_context_probe)

    map_parser = sub.add_parser("map", help="Manage project map")
    map_sub = map_parser.add_subparsers(dest="map_command", required=True)
    for name in ["init", "update", "show", "diff"]:
        map_sub.add_parser(name).set_defaults(func=command_map)

    task = sub.add_parser("task", help="Manage Executor task packets")
    task_sub = task.add_subparsers(dest="task_command", required=True)
    new_task = task_sub.add_parser("new")
    new_task.add_argument("--title", required=True)
    new_task.add_argument("--objective", required=True)
    new_task.add_argument("--mode", choices=["inspect", "execute", "verify", "review"], default="execute")
    new_task.add_argument("--allowed", default="")
    new_task.add_argument("--forbidden", default="")
    new_task.add_argument("--steps", default="")
    new_task.add_argument("--validation", default="")
    new_task.set_defaults(func=command_task)
    dispatch = task_sub.add_parser("dispatch")
    dispatch.add_argument("--task-id", default="")
    dispatch.set_defaults(func=command_task)
    collect = task_sub.add_parser("collect")
    collect.add_argument("--task-id", default="")
    collect.set_defaults(func=command_task)

    memory = sub.add_parser("memory", help="Apply approved memory updates")
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)
    propose_memory = memory_sub.add_parser("propose")
    propose_memory.add_argument("--type", required=True)
    propose_memory.add_argument("--source", required=True)
    propose_memory.add_argument("--content", required=True)
    propose_memory.add_argument("--evidence", default="")
    propose_memory.set_defaults(func=command_memory)
    apply_memory = memory_sub.add_parser("apply")
    apply_memory.add_argument("--type", default="")
    apply_memory.add_argument("--source", default="")
    apply_memory.add_argument("--content", default="")
    apply_memory.add_argument("--proposal-id", default="")
    apply_memory.set_defaults(func=command_memory)
    memory_sub.add_parser("show-boot").set_defaults(func=command_memory)
    memory_sub.add_parser("compact").set_defaults(func=command_memory)

    skills = sub.add_parser("skills", help="Index external skills")
    skills_sub = skills.add_subparsers(dest="skills_command", required=True)
    scan = skills_sub.add_parser("scan")
    scan.add_argument("--path", required=True)
    scan.set_defaults(func=command_skills)
    skills_sub.add_parser("list").set_defaults(func=command_skills)
    register = skills_sub.add_parser("register")
    register.add_argument("--name", required=True)
    register.add_argument("--path", required=True)
    register.add_argument("--trigger", default="")
    register.set_defaults(func=command_skills)
    resolve = skills_sub.add_parser("resolve")
    resolve.add_argument("name")
    resolve.set_defaults(func=command_skills)

    sub.add_parser("status").set_defaults(func=command_status)
    sub.add_parser("doctor").set_defaults(func=command_doctor)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
