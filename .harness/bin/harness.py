#!/usr/bin/env python3
import os
import json
import argparse
import sys
import datetime
import shutil
import re

def get_markdown_section(content, section_name, level=2):
    """Extract content under a specific header."""
    header_prefix = "#" * level
    escaped_name = re.escape(section_name)
    # Stop at the next header of the SAME level that looks like a new section (e.g. ## 2.) 
    # or a level 1 header.
    pattern = rf"(?:^|\n){header_prefix}\s+{escaped_name}.*?\n(.*?)(?=\n{header_prefix}\s+\d+\.|\n#\s|$)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def get_task_type_boundary(content, task_type):
    """Extract specific boundary from task-packet.md."""
    pattern = rf"^- \*\*`{re.escape(task_type)}`.*$"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.group(0).strip()
    return None

BIN_DIR = ".harness/bin"
STATE_FILE = ".harness/state.json"
SESSIONS_DIR = ".harness/sessions"
TASKS_DIR = ".harness/tasks"
ARCHIVE_DIR = ".harness/tasks/archive"
RUNTIME_DIR = ".harness/runtime/current"
RUNTIME_TASKS_DIR = ".harness/runtime/current/tasks"
RUNTIME_SPECS_DIR = ".harness/runtime/current/specs"
ROLES_DIR = ".harness/roles"
PROTOCOLS_DIR = ".harness/protocols"
MEMORY_DIR = ".harness/memory"

def load_state():
    default_state = {
        "active_session_id": None, 
        "active_mission_id": None, 
        "active_stage": "investigation", 
        "spec": {
            "path": ".harness/runtime/current/implementation_spec.md",
            "meta_path": ".harness/runtime/current/implementation_spec.meta.json",
            "status": "missing",
            "mission_id": None,
            "evidence_checked": False,
            "approved": False,
            "version": 0,
            "snapshot_path": None
        },
        "role_slots": {}
    }
    if not os.path.exists(STATE_FILE):
        return default_state
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
        if "spec" not in state:
            state["spec"] = default_state["spec"]
        else:
            for k, v in default_state["spec"].items():
                state["spec"].setdefault(k, v)
        return state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def emit_event(session_id, event_type, actor, summary, task_id=None, details_ref=None, artifacts=None):
    if not session_id: return
    log_path = os.path.join(SESSIONS_DIR, f"{session_id}.jsonl")
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id,
        "event_type": event_type,
        "actor": actor,
        "summary": summary
    }
    if task_id:
        event["task_id"] = task_id
    if details_ref:
        event["details_ref"] = details_ref
    if artifacts:
        event["artifacts"] = artifacts
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")

def ensure_runtime_dirs():
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    os.makedirs(RUNTIME_TASKS_DIR, exist_ok=True)
    os.makedirs(RUNTIME_SPECS_DIR, exist_ok=True)

def runtime_has_contents():
    if not os.path.exists(RUNTIME_DIR):
        return False
    for dirpath, dirnames, filenames in os.walk(RUNTIME_DIR):
        if filenames:
            return True
    return False

def task_id_index():
    ids = set()
    pattern = re.compile(r"T-\d{8}-(\d{3})")
    search_roots = [TASKS_DIR, RUNTIME_DIR]
    for root in search_roots:
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            for name in dirnames + filenames:
                match = pattern.search(name)
                if match:
                    ids.add(match.group(0))
    if os.path.exists(SESSIONS_DIR):
        for name in os.listdir(SESSIONS_DIR):
            if not name.endswith(".jsonl"):
                continue
            with open(os.path.join(SESSIONS_DIR, name), "r") as f:
                for line in f:
                    for match in pattern.finditer(line):
                        ids.add(match.group(0))
    return ids

def get_next_id(prefix, directory, ext):
    today = datetime.datetime.now().strftime("%Y%m%d")
    os.makedirs(directory, exist_ok=True)
    existing = [f for f in os.listdir(directory) if f.startswith(f"{prefix}-{today}-") and (not ext or f.endswith(ext))]
    if not existing:
        return f"{prefix}-{today}-001"
    indices = []
    for f in existing:
        parts = f.split("-")
        if len(parts) >= 3:
            try:
                indices.append(int(parts[2].split(".")[0]))
            except ValueError:
                continue
    if not indices:
        return f"{prefix}-{today}-001"
    next_idx = max(indices) + 1
    return f"{prefix}-{today}-{next_idx:03d}"

def generate_task_id():
    today = datetime.datetime.now().strftime("%Y%m%d")
    ids = task_id_index()
    indices = []
    for task_id in ids:
        parts = task_id.split("-")
        if len(parts) == 3 and parts[1] == today:
            try:
                indices.append(int(parts[2]))
            except ValueError:
                continue
    next_idx = max(indices) + 1 if indices else 1
    return f"T-{today}-{next_idx:03d}"

def generate_session_id():
    return get_next_id("S", SESSIONS_DIR, ".jsonl")

def generate_mission_id():
    # Misson IDs are just logical, we can track them in a mission dir or just use a counter based on tasks archive
    return get_next_id("M", ARCHIVE_DIR, "")

def archive_runtime(state, archive_event_type, summary):
    mission_id = state.get("active_mission_id")
    if not mission_id:
        archive_dir_path = os.path.join(ARCHIVE_DIR, f"orphan-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    else:
        archive_dir_path = os.path.join(ARCHIVE_DIR, mission_id)
    os.makedirs(archive_dir_path, exist_ok=True)
    if os.path.exists(RUNTIME_DIR):
        for f in os.listdir(RUNTIME_DIR):
            src = os.path.join(RUNTIME_DIR, f)
            dst = os.path.join(archive_dir_path, f)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            shutil.move(src, dst)
    with open(os.path.join(archive_dir_path, "mission_state.json"), "w") as f:
        json.dump(state, f, indent=2)
    emit_event(
        state.get("active_session_id"),
        archive_event_type,
        "coordinator",
        summary,
        details_ref=os.path.join(archive_dir_path, "mission_state.json"),
    )
    ensure_runtime_dirs()
    return archive_dir_path

def next_spec_version():
    os.makedirs(RUNTIME_SPECS_DIR, exist_ok=True)
    pattern = re.compile(r"implementation_spec\.v(\d{3})\.md$")
    versions = []
    for name in os.listdir(RUNTIME_SPECS_DIR):
        match = pattern.match(name)
        if match:
            versions.append(int(match.group(1)))
    return max(versions) + 1 if versions else 1

def main():
    parser = argparse.ArgumentParser(
        description="Unified Managed Agent Harness CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Recommended coordinator cycle:\n"
            "  start -> dispatch-role Reader -> worker-instructions -> collect-role Reader\n"
            "  -> write-spec -> edit implementation_spec.md -> spec-check\n"
            "  -> dispatch-role Coder -> worker-instructions -> collect-role Coder\n"
            "  -> dispatch-role Tester/Reviewer when risk warrants -> archive-current\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start", help="Start a new session and mission")
    start_parser.add_argument("objective", help="Session objective")

    dispatch_parser = subparsers.add_parser("dispatch-role", help="Dispatch a task to a role slot")
    dispatch_parser.add_argument("--role", required=True, help="Worker role (e.g. reader, coder, tester, reviewer)")
    dispatch_parser.add_argument("--objective", required=True, help="Task objective")
    dispatch_parser.add_argument("--scope", default="", help="Task scope")
    dispatch_parser.add_argument("--constraints", default="", help="Task constraints")
    dispatch_parser.add_argument("--questions", default="", help="Specific questions for Reader to answer")
    dispatch_parser.add_argument("--task-type", default="", choices=["investigation", "implementation", "verification", "review", "memory-curation", ""], help="Task boundary classification")
    dispatch_parser.add_argument("--force", action="store_true", help="Force overwrite if slot is unconsumed")

    subparsers.add_parser("worker-instructions", help="Print instructions for opening worker agents")

    collect_parser = subparsers.add_parser("collect-role", help="Collect results from a worker role")
    collect_parser.add_argument("--role", required=True, help="Worker role")
    collect_parser.add_argument("--full", action="store_true", help="Print full result even if it is long")

    subparsers.add_parser("write-spec", help="Initialize the implementation_spec.md template")
    subparsers.add_parser("spec-check", help="Validate implementation_spec.md against completeness rules")

    subparsers.add_parser("collect-all", help="Collect results from all completed worker roles")

    subparsers.add_parser("archive-current", help="Archive current mission")

    subparsers.add_parser("status", help="Print the current status of the mission and active roles")
    subparsers.add_parser("doctor", help="Perform a static health check on the harness state")

    args = parser.parse_args()
    state = load_state()

    ensure_runtime_dirs()

    if args.command == "start":
        if runtime_has_contents():
            archive_runtime(state, "AUTO_ARCHIVE", "Archived previous runtime before starting a new mission")

        session_id = generate_session_id()
        mission_id = generate_mission_id()
        
        state["active_session_id"] = session_id
        state["active_mission_id"] = mission_id
        state["active_stage"] = "investigation"
        state["spec"]["status"] = "missing"
        state["spec"]["mission_id"] = None
        state["spec"]["evidence_checked"] = False
        state["spec"]["approved"] = False
        state["spec"]["version"] = 0
        state["spec"]["snapshot_path"] = None
        state["role_slots"] = {}
        save_state(state)
        
        mission_meta = {
            "mission_id": mission_id,
            "session_id": session_id,
            "objective": args.objective,
            "created_at": datetime.datetime.now().isoformat(),
            "stage": "investigation",
            "status": "active"
        }
        with open(os.path.join(RUNTIME_DIR, "mission.json"), "w") as f:
            json.dump(mission_meta, f, indent=2)

        emit_event(session_id, "SESSION_START", "user", f"New session: {args.objective}")
        emit_event(session_id, "MISSION_START", "user", f"New mission: {args.objective}")
        print(f"Created session: {session_id}")
        print(f"Created mission: {mission_id}")

    elif args.command == "write-spec":
        ensure_runtime_dirs()
        spec_path = os.path.join(RUNTIME_DIR, "implementation_spec.md")
        meta_path = os.path.join(RUNTIME_DIR, "implementation_spec.meta.json")
        if os.path.exists(spec_path):
            print(f"File {spec_path} already exists. Please edit it directly.")
            return
            
        mission_id = state.get("active_mission_id")
        if not mission_id:
            print("Error: No active mission. Run 'start' first.")
            return
            
        template = """# Implementation Spec\n\n## Objective\n[Clear goal]\n\n## Scope\n- Files Allowed:\n- Files Forbidden:\n\n## Required Changes\n[Exact insertion points and required logic modifications]\n\n## Evidence References\n[File paths and line numbers from Reader findings backing up this plan]\n\n## Allowed Autonomy\n[What the Coder CAN decide, e.g., local variable names]\n\n## Must Not Decide\n[What the Coder CANNOT decide, e.g., changing default behavior, adding dependencies]\n\n## Stop Conditions\n[Exact scenarios where the Coder must halt and report blocked]\n"""
        with open(spec_path, "w") as f:
            f.write(template)
            
        meta_data = {
            "mission_id": mission_id,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        with open(meta_path, "w") as f:
            json.dump(meta_data, f, indent=2)
            
        state["spec"]["status"] = "draft"
        state["spec"]["mission_id"] = mission_id
        state["spec"]["version"] = 0
        state["spec"]["snapshot_path"] = None
        state["active_stage"] = "spec_draft"
        save_state(state)
        emit_event(
            state.get("active_session_id"),
            "SPEC_CREATED",
            "coordinator",
            "Created implementation spec draft",
            details_ref=spec_path,
        )
        
        print(f"Created Implementation Spec template at {spec_path}")

    elif args.command == "spec-check":
        mission_id = state.get("active_mission_id")
        if not mission_id:
            print("Error: No active mission.")
            return
            
        spec_path = os.path.join(RUNTIME_DIR, "implementation_spec.md")
        meta_path = os.path.join(RUNTIME_DIR, "implementation_spec.meta.json")
        
        if not os.path.exists(spec_path):
            print("Error: implementation_spec.md does not exist.")
            return
        if not os.path.exists(meta_path):
            print("Error: implementation_spec.meta.json does not exist. Did you use 'write-spec'?")
            return
            
        with open(meta_path, "r") as f:
            meta = json.load(f)
            
        if meta.get("mission_id") != mission_id:
            print(f"Error: Spec is bound to mission {meta.get('mission_id')}, but active mission is {mission_id}.")
            return
            
        with open(spec_path, "r") as f:
            content = f.read()
            
        required_sections = ["## Objective", "## Required Changes", "## Evidence References", "## Allowed Autonomy", "## Must Not Decide", "## Stop Conditions"]
        missing = [sec for sec in required_sections if sec not in content]
        if missing:
            print(f"Error: Spec is missing required sections: {', '.join(missing)}")
            return
            
        ev_start = content.find("## Evidence References")
        if ev_start != -1:
            ev_end = content.find("##", ev_start + 1)
            ev_content = content[ev_start:ev_end] if ev_end != -1 else content[ev_start:]
            ev_content = ev_content.replace("## Evidence References", "").strip()
            if not ev_content or ev_content == "[File paths and line numbers from Reader findings backing up this plan]":
                print("Error: Evidence References section is empty or still contains the placeholder.")
                return
        
        version = next_spec_version()
        snapshot_path = os.path.join(RUNTIME_SPECS_DIR, f"implementation_spec.v{version:03d}.md")
        shutil.copy2(spec_path, snapshot_path)
        meta["updated_at"] = datetime.datetime.now().isoformat()
        meta["spec_version"] = version
        meta["snapshot_path"] = snapshot_path
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        
        state["spec"]["status"] = "ready"
        state["spec"]["version"] = version
        state["spec"]["snapshot_path"] = snapshot_path
        state["active_stage"] = "spec_ready"
        save_state(state)
        emit_event(
            state.get("active_session_id"),
            "SPEC_READY",
            "coordinator",
            f"Implementation spec v{version:03d} passed checks",
            details_ref=snapshot_path,
        )
        print(f"Success: Implementation Spec passed all checks and is marked as 'ready' (v{version:03d}).")

    elif args.command == "dispatch-role":
        if not state.get("active_session_id"):
            print("Error: No active session. Run 'start' first.")
            return
        role = args.role.lower()
        
        slot = state.get("role_slots", {}).get(role)
        if slot and slot["status"] in ["dispatched", "running", "completed"] and not args.force:
            print(f"Error: Role slot '{role}' has unconsumed status: {slot['status']}")
            print("Please run 'collect-role' or 'archive-current' first, or pass '--force' to overwrite.")
            return

        task_type = args.task_type
        if not task_type:
            role_to_task_type = {
                "reader": "investigation",
                "coder": "implementation",
                "tester": "verification",
                "reviewer": "review",
                "memory-curator": "memory-curation"
            }
            task_type = role_to_task_type.get(role, "implementation")
            
        spec_file = os.path.join(RUNTIME_DIR, "implementation_spec.md")
        meta_file = os.path.join(RUNTIME_DIR, "implementation_spec.meta.json")
        if role in ["coder", "tester", "reviewer"]:
            if not os.path.exists(spec_file) or not os.path.exists(meta_file):
                print(f"Error: Refusing to dispatch '{role}'. The file implementation_spec.md or its meta does not exist.")
                print("Coordinator MUST perform Evidence Sufficiency Check and write the Implementation Spec first.")
                return
                
            with open(meta_file, "r") as f:
                meta = json.load(f)
            
            mission_id = state.get("active_mission_id")
            if meta.get("mission_id") != mission_id:
                print(f"Error: Spec mission_id ({meta.get('mission_id')}) does not match active mission_id ({mission_id}).")
                print("This is likely a stale spec from a previous mission.")
                return
                
            spec_status = state.get("spec", {}).get("status")
            if spec_status not in ["ready", "approved"]:
                print(f"Error: Spec status is '{spec_status}', but must be 'ready' or 'approved' to dispatch '{role}'.")
                print("Please run 'spec-check' to validate the spec first.")
                return

        task_id = generate_task_id()
        
        task_dir = os.path.join(RUNTIME_TASKS_DIR, task_id)
        os.makedirs(task_dir, exist_ok=False)
        task_path = os.path.join(task_dir, f"{role}.task.md")
        prompt_path = os.path.join(task_dir, f"{role}.prompt.md")
        result_path = os.path.join(task_dir, f"{role}.result.md")
        current_prompt_path = os.path.join(RUNTIME_DIR, f"{role}.prompt.md")
        legacy_result_path = os.path.join(RUNTIME_DIR, f"{role}.result.md")
        
        # Build Task Packet
        task_content = f"# Task Packet: {task_id}\n"
        task_content += f"- **Role**: {role}\n"
        task_content += f"- **Task Type**: {task_type}\n"
        task_content += f"- **Objective**: {args.objective}\n"
        if args.scope: task_content += f"- **Scope**: {args.scope}\n"
        if args.constraints: task_content += f"- **Constraints**: {args.constraints}\n"
        if args.questions: task_content += f"- **Questions to Answer**:\n{args.questions}\n"
        
        with open(task_path, "w") as f:
            f.write(task_content)
        
        # Render Prompt
        prompt = ["# INSTRUCTIONS", "You are acting as a specialized worker in a Managed Agent Harness.", 
                  f"Your role is '{role}'. Read your ROLE below.",
                  "Follow the TASK PACKET strictly. When finished, provide your output using the WORKER RESULT template.",
                  f"Write your result to `{result_path}`. Do not write the result to chat.", ""]
        
        role_file = os.path.join(ROLES_DIR, f"{role}.md")
        if os.path.exists(role_file):
            prompt.append("# ROLE")
            with open(role_file, "r") as f: prompt.append(f.read())
            prompt.append("")
            
        proj_mem = os.path.join(MEMORY_DIR, "project.md")
        if os.path.exists(proj_mem):
            prompt.append("# PROJECT CONTEXT")
            with open(proj_mem, "r") as f: prompt.append(f.read())
            prompt.append("")
            
        spec_file = os.path.join(RUNTIME_DIR, "implementation_spec.md")
        if role in ["coder", "tester", "reviewer"] and os.path.exists(spec_file):
            prompt.append("# IMPLEMENTATION SPEC")
            prompt.append("This is the strict specification generated by the Coordinator Brain. You MUST follow it.")
            with open(spec_file, "r") as f: prompt.append(f.read())
            prompt.append("")
            
        task_pkt_file = os.path.join(PROTOCOLS_DIR, "task-packet.md")
        if os.path.exists(task_pkt_file):
            with open(task_pkt_file, "r") as f:
                pkt_protocol = f.read()
            boundary = get_task_type_boundary(pkt_protocol, task_type)
            if boundary:
                prompt.append("# TASK TYPE BOUNDARY")
                prompt.append(f"Your task type is '{task_type}'. Boundary constraint:")
                prompt.append(boundary)
                prompt.append("")
            
        prompt.append("# TASK PACKET")
        prompt.append(task_content)
        prompt.append("")
        
        prompt.append("# OUTPUT FORMAT (WORKER RESULT)")
        worker_res_file = os.path.join(PROTOCOLS_DIR, "worker-result.md")
        if os.path.exists(worker_res_file):
            with open(worker_res_file, "r") as f:
                res_protocol = f.read()
            
            common = get_markdown_section(res_protocol, "Common Metadata")
            if common:
                prompt.append("## Common Metadata")
                prompt.append(common)
                prompt.append("")

            role_to_section = {
                "reader": "1. Reader Result",
                "coder": "2. Coder Result",
                "tester": "3. Tester Result",
                "reviewer": "4. Reviewer Result",
                "memory-curator": "5. Memory Curator Result"
            }
            section_name = role_to_section.get(role)
            if section_name:
                section_content = get_markdown_section(res_protocol, section_name)
                if section_content:
                    prompt.append(f"## {section_name}")
                    prompt.append(section_content)
        else:
            prompt.append("Provide a concise summary of findings, code changes, or test results.")
            prompt.append("Include any risks or proposed memory updates.")
        
        with open(prompt_path, "w") as f:
            f.write("\n".join(prompt))
        shutil.copy2(prompt_path, current_prompt_path)
            
        # Clear only the role entry result used by older bootstrap instructions. The
        # canonical per-task result path is never reused.
        if os.path.exists(legacy_result_path):
            os.remove(legacy_result_path)
            
        state.setdefault("role_slots", {})[role] = {
            "status": "dispatched",
            "task_id": task_id,
            "task_dir": task_dir,
            "task_path": task_path,
            "prompt_path": prompt_path,
            "result_path": result_path,
            "current_prompt_path": current_prompt_path,
            "legacy_result_path": legacy_result_path
        }
        save_state(state)
        
        emit_event(
            state["active_session_id"],
            "TASK_DISPATCH",
            "coordinator",
            f"Dispatched {role}: {args.objective}",
            task_id,
            details_ref=task_path,
            artifacts=[task_path, prompt_path],
        )
        print(f"Dispatched {role} (Task {task_id})")

    elif args.command == "worker-instructions":
        slots = state.get("role_slots", {})
        active_roles = [r for r, d in slots.items() if d["status"] in ["dispatched", "pending", "running"]]
        if not active_roles:
            print("No active roles dispatched.")
            return
        print("Please ask the user to open a new sub-agent window and send this instruction:\n")
        print("```text")
        for role in active_roles:
            role_cap = role.capitalize()
            print(f"请读取 .harness/worker_bootstrap.md，并以 {role_cap} 身份执行当前任务。完成后只回复完成或失败。")
        print("```")

    elif args.command == "collect-role":
        role = args.role.lower()
        slot = state.get("role_slots", {}).get(role)
        if not slot:
            print(f"Error: Role {role} not in active slots.")
            return
        
        result_path = slot["result_path"]
        legacy_result_path = slot.get("legacy_result_path", os.path.join(RUNTIME_DIR, f"{role}.result.md"))
        if not os.path.exists(result_path) and os.path.exists(legacy_result_path):
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            shutil.copy2(legacy_result_path, result_path)
        if not os.path.exists(result_path):
            print(f"Error: Result file {result_path} not found.")
            return
            
        with open(result_path, "r") as f:
            result_content = f.read()
            
        print(f"--- {role.upper()} RESULT SUMMARY ---")
        if len(result_content) > 2000 and not args.full:
            print(result_content[:2000])
            print(f"\n... [RESULT TRUNCATED DUE TO LENGTH ({len(result_content)} chars)] ...")
            print(f"To see the full result, view {result_path} or run 'collect-role --role {role} --full'")
        else:
            print(result_content)
        print("---------------------------------")
        
        slot["status"] = "consumed"
        save_state(state)
        emit_event(
            state["active_session_id"],
            "WORKER_RESULT",
            role,
            f"Collected result for {role}",
            slot["task_id"],
            details_ref=result_path,
        )

    elif args.command == "collect-all":
        for role, slot in state.get("role_slots", {}).items():
            if slot["status"] == "dispatched": # In reality we assume they are done if result exists
                if os.path.exists(slot["result_path"]):
                    print(f"\nCollecting {role}:")
                    os.system(f"{sys.executable} {__file__} collect-role --role {role}")

    elif args.command == "archive-current":
        mission_id = state.get("active_mission_id")
        if not mission_id:
            print("No active mission to archive.")
            return
        archive_path = archive_runtime(state, "MISSION_ARCHIVE", f"Archived mission {mission_id}")
            
        state["active_mission_id"] = None
        state["role_slots"] = {}
        state["active_stage"] = "archived"
        state["spec"]["status"] = "missing"
        state["spec"]["mission_id"] = None
        state["spec"]["evidence_checked"] = False
        state["spec"]["approved"] = False
        state["spec"]["version"] = 0
        state["spec"]["snapshot_path"] = None
        save_state(state)
        print(f"Archived mission to {archive_path}")

    elif args.command == "status":
        print(f"--- HARNESS STATUS ---")
        print(f"Active Session: {state.get('active_session_id')}")
        print(f"Active Mission: {state.get('active_mission_id')}")
        print(f"Active Stage:   {state.get('active_stage')}")
        
        spec = state.get("spec", {})
        print(f"Spec Status:    {spec.get('status')} (Mission: {spec.get('mission_id')})")
        
        slots = state.get("role_slots", {})
        print("\n--- ROLE SLOTS ---")
        if not slots:
            print("No active roles.")
        else:
            for r, d in slots.items():
                print(f"  {r.capitalize()}: {d['status']} (Task: {d['task_id']})")
                
        print("\n--- RUNTIME/CURRENT ---")
        if os.path.exists(RUNTIME_DIR):
            files = os.listdir(RUNTIME_DIR)
            for f in sorted(files):
                print(f"  {f}")
        else:
            print("  (Empty)")

        unconsumed = [r for r, d in slots.items() if d['status'] in ["dispatched", "running", "completed"]]
        if unconsumed:
            print("\nUnconsumed Results:")
            for r in unconsumed:
                print(f"  Role '{r}' needs to be collected.")
        
        print("\n--- NEXT STEP HINT ---")
        if not state.get("active_session_id"):
            print("Run: start \"<mission objective>\"")
        elif not state.get("active_mission_id"):
            print("Run: start \"<next mission objective>\"")
        elif unconsumed:
            print("Ask the worker to finish, then run: collect-role --role <role>")
        elif spec.get("status") == "missing":
            if any(d.get("status") == "consumed" for d in slots.values()):
                print("If evidence is sufficient, run: write-spec. Otherwise dispatch another Reader.")
            else:
                print("Dispatch a Reader with narrow questions.")
        elif spec.get("status") == "draft":
            print("Edit implementation_spec.md, then run: spec-check")
        elif spec.get("status") in ["ready", "approved"]:
            print("Dispatch Coder, Tester, or Reviewer as appropriate; archive when done.")
        else:
            print("Run: doctor")
        print("----------------------")

    elif args.command == "doctor":
        print("--- HARNESS DOCTOR ---")
        issues = 0
        task_dispatch_counts = {}
        if os.path.exists(SESSIONS_DIR):
            for name in os.listdir(SESSIONS_DIR):
                if not name.endswith(".jsonl"):
                    continue
                with open(os.path.join(SESSIONS_DIR, name), "r") as f:
                    for line_no, line in enumerate(f, start=1):
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            print(f"[!] Invalid JSON in {name}:{line_no}.")
                            issues += 1
                            continue
                        if event.get("event_type") == "TASK_DISPATCH" and event.get("task_id"):
                            task_dispatch_counts.setdefault(event["task_id"], []).append(f"{name}:{line_no}")
        for task_id, refs in sorted(task_dispatch_counts.items()):
            if len(refs) > 1:
                print(f"[!] Duplicate task_id {task_id} appears in TASK_DISPATCH events: {', '.join(refs)}")
                issues += 1
        
        mission_id = state.get("active_mission_id")
        if mission_id:
            mission_file = os.path.join(RUNTIME_DIR, "mission.json")
            if not os.path.exists(mission_file):
                print("[!] mission.json is missing.")
                issues += 1
            else:
                with open(mission_file, "r") as f:
                    try:
                        m = json.load(f)
                        if m.get("mission_id") != mission_id:
                            print(f"[!] mission.json ID ({m.get('mission_id')}) != state ID ({mission_id})")
                            issues += 1
                    except:
                        print("[!] mission.json is corrupted.")
                        issues += 1
                        
            spec_file = os.path.join(RUNTIME_DIR, "implementation_spec.md")
            meta_file = os.path.join(RUNTIME_DIR, "implementation_spec.meta.json")
            
            if state.get("spec", {}).get("status") in ["ready", "approved"]:
                if not os.path.exists(spec_file):
                    print("[!] Spec is ready but implementation_spec.md is missing.")
                    issues += 1
                if not os.path.exists(meta_file):
                    print("[!] Spec is ready but implementation_spec.meta.json is missing.")
                    issues += 1
                else:
                    with open(meta_file, "r") as f:
                        try:
                            meta = json.load(f)
                            if meta.get("mission_id") != mission_id:
                                print(f"[!] Spec meta mission_id ({meta.get('mission_id')}) != state ID ({mission_id})")
                                issues += 1
                        except:
                            print("[!] implementation_spec.meta.json is corrupted.")
                            issues += 1
                snapshot_path = state.get("spec", {}).get("snapshot_path")
                if not snapshot_path:
                    print("[!] Spec is ready but snapshot_path is missing.")
                    issues += 1
                elif not os.path.exists(snapshot_path):
                    print(f"[!] Spec snapshot is missing: {snapshot_path}")
                    issues += 1
                            
        for r, d in state.get("role_slots", {}).items():
            if not os.path.exists(d.get("task_path", "")):
                print(f"[!] Role '{r}' task file is missing: {d.get('task_path')}")
                issues += 1
            if not os.path.exists(d.get("prompt_path", "")):
                print(f"[!] Role '{r}' prompt file is missing: {d.get('prompt_path')}")
                issues += 1
            if d["status"] in ["dispatched", "running", "completed"]:
                if os.path.exists(d.get("result_path", "")) and d["status"] == "dispatched":
                    print(f"[i] Role '{r}' has a result but status is still 'dispatched'.")
                legacy_result = d.get("legacy_result_path")
                if legacy_result and os.path.exists(legacy_result) and not os.path.exists(d.get("result_path", "")):
                    print(f"[i] Role '{r}' has a legacy result pending collection: {legacy_result}")
                    
        if os.path.exists(ARCHIVE_DIR):
            for name in sorted(os.listdir(ARCHIVE_DIR)):
                archive_path = os.path.join(ARCHIVE_DIR, name)
                if not os.path.isdir(archive_path) or name.startswith("orphan-"):
                    continue
                if not os.path.exists(os.path.join(archive_path, "mission_state.json")):
                    print(f"[!] Archive {name} is missing mission_state.json.")
                    issues += 1
                    
        if issues == 0:
            print("OK! All checks passed.")
        else:
            print(f"Found {issues} potential issue(s).")
        print("----------------------")

if __name__ == "__main__":
    main()
