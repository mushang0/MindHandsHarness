#!/usr/bin/env python3
import os
import json
import argparse
import sys
import datetime
import shutil

BIN_DIR = ".harness/bin"
STATE_FILE = ".harness/state.json"
SESSIONS_DIR = ".harness/sessions"
TASKS_DIR = ".harness/tasks"
ARCHIVE_DIR = ".harness/tasks/archive"
RUNTIME_DIR = ".harness/runtime/current"
ROLES_DIR = ".harness/roles"
PROTOCOLS_DIR = ".harness/protocols"
MEMORY_DIR = ".harness/memory"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"active_session_id": None, "active_mission_id": None, "active_stage": None, "role_slots": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def emit_event(session_id, event_type, actor, summary, task_id=None):
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
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")

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
    return get_next_id("T", TASKS_DIR, ".md")

def generate_session_id():
    return get_next_id("S", SESSIONS_DIR, ".jsonl")

def generate_mission_id():
    # Misson IDs are just logical, we can track them in a mission dir or just use a counter based on tasks archive
    return get_next_id("M", ARCHIVE_DIR, "")

def main():
    parser = argparse.ArgumentParser(description="Unified Managed Agent Harness CLI")
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser("start", help="Start a new session and mission")
    start_parser.add_argument("objective", help="Session objective")

    dispatch_parser = subparsers.add_parser("dispatch-role", help="Dispatch a task to a role slot")
    dispatch_parser.add_argument("--role", required=True, help="Worker role (e.g. reader, coder, tester, reviewer)")
    dispatch_parser.add_argument("--objective", required=True, help="Task objective")
    dispatch_parser.add_argument("--scope", default="", help="Task scope")
    dispatch_parser.add_argument("--constraints", default="", help="Task constraints")

    subparsers.add_parser("worker-instructions", help="Print instructions for opening worker agents")

    collect_parser = subparsers.add_parser("collect-role", help="Collect results from a worker role")
    collect_parser.add_argument("--role", required=True, help="Worker role")

    subparsers.add_parser("collect-all", help="Collect results from all completed worker roles")

    subparsers.add_parser("archive-current", help="Archive current mission")

    args = parser.parse_args()
    state = load_state()

    os.makedirs(RUNTIME_DIR, exist_ok=True)

    if args.command == "start":
        session_id = generate_session_id()
        mission_id = generate_mission_id()
        state["active_session_id"] = session_id
        state["active_mission_id"] = mission_id
        state["role_slots"] = {}
        save_state(state)
        emit_event(session_id, "SESSION_START", "user", f"New session: {args.objective}")
        emit_event(session_id, "MISSION_START", "user", f"New mission: {args.objective}")
        print(f"Created session: {session_id}")
        print(f"Created mission: {mission_id}")

    elif args.command == "dispatch-role":
        if not state.get("active_session_id"):
            print("Error: No active session. Run 'start' first.")
            return
        role = args.role.lower()
        task_id = generate_task_id()
        
        task_path = os.path.join(RUNTIME_DIR, f"{role}.task.md")
        prompt_path = os.path.join(RUNTIME_DIR, f"{role}.prompt.md")
        result_path = os.path.join(RUNTIME_DIR, f"{role}.result.md")
        
        # Build Task Packet
        task_content = f"# Task Packet: {task_id}\n"
        task_content += f"- **Role**: {role}\n"
        task_content += f"- **Objective**: {args.objective}\n"
        if args.scope: task_content += f"- **Scope**: {args.scope}\n"
        if args.constraints: task_content += f"- **Constraints**: {args.constraints}\n"
        
        with open(task_path, "w") as f:
            f.write(task_content)
        
        # Render Prompt
        prompt = ["# INSTRUCTIONS", "You are acting as a specialized worker in a Managed Agent Harness.", 
                  f"Your role is '{role}'. Read your ROLE below.",
                  "Follow the TASK PACKET strictly. When finished, provide your output using the WORKER RESULT template.", ""]
        
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
            
        prompt.append("# TASK PACKET")
        prompt.append(task_content)
        prompt.append("")
        
        prompt.append("# OUTPUT FORMAT (WORKER RESULT)")
        prompt.append("Provide a concise summary of findings, code changes, or test results.")
        prompt.append("Include any risks or proposed memory updates.")
        
        with open(prompt_path, "w") as f:
            f.write("\n".join(prompt))
            
        # Clear old result if exists
        if os.path.exists(result_path):
            os.remove(result_path)
            
        state.setdefault("role_slots", {})[role] = {
            "status": "dispatched",
            "task_id": task_id,
            "task_path": task_path,
            "prompt_path": prompt_path,
            "result_path": result_path
        }
        save_state(state)
        
        emit_event(state["active_session_id"], "TASK_DISPATCH", "coordinator", f"Dispatched {role}: {args.objective}", task_id)
        print(f"Dispatched {role} (Task {task_id})")

    elif args.command == "worker-instructions":
        slots = state.get("role_slots", {})
        active_roles = [r for r, d in slots.items() if d["status"] in ["dispatched", "pending", "running"]]
        if not active_roles:
            print("No active roles dispatched.")
            return
        print("请打开以下子 agent：\n")
        for role in active_roles:
            role_cap = role.capitalize()
            print(f"{role_cap} 子 agent：")
            print(f"请读取 .harness/worker_bootstrap.md，并以 {role_cap} 身份执行当前任务。完成后只回复完成或失败。\n")

    elif args.command == "collect-role":
        role = args.role.lower()
        slot = state.get("role_slots", {}).get(role)
        if not slot:
            print(f"Error: Role {role} not in active slots.")
            return
        
        result_path = slot["result_path"]
        if not os.path.exists(result_path):
            print(f"Error: Result file {result_path} not found.")
            return
            
        with open(result_path, "r") as f:
            result_content = f.read()
            
        print(f"--- {role.upper()} RESULT SUMMARY ---")
        # Print a short summary of the result content for the coordinator
        lines = result_content.split('\n')
        summary = "\n".join(lines[:15])
        if len(lines) > 15: summary += "\n...(truncated)..."
        print(summary)
        print("---------------------------------")
        
        slot["status"] = "consumed"
        save_state(state)
        emit_event(state["active_session_id"], "WORKER_RESULT", role, f"Collected result for {role}", slot["task_id"])

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
        archive_path = os.path.join(ARCHIVE_DIR, mission_id)
        os.makedirs(archive_path, exist_ok=True)
        
        for f in os.listdir(RUNTIME_DIR):
            src = os.path.join(RUNTIME_DIR, f)
            if os.path.isfile(src):
                shutil.move(src, os.path.join(archive_path, f))
                
        # Also copy mission.json context if needed, and save state snippet
        with open(os.path.join(archive_path, "mission_state.json"), "w") as f:
            json.dump(state, f, indent=2)
            
        state["active_mission_id"] = None
        state["role_slots"] = {}
        save_state(state)
        print(f"Archived mission to {archive_path}")

if __name__ == "__main__":
    main()
