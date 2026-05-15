import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def prepare_harness(tmp_path):
    work = tmp_path / "work"
    harness = work / ".harness"
    harness.mkdir(parents=True)
    for name in ["bin", "roles", "protocols", "memory"]:
        shutil.copytree(REPO_ROOT / ".harness" / name, harness / name)
    shutil.copy2(REPO_ROOT / ".harness" / "worker_bootstrap.md", harness / "worker_bootstrap.md")
    shutil.copy2(REPO_ROOT / ".harness" / "config.yaml", harness / "config.yaml")
    return work


def run_cli(work, *args):
    result = subprocess.run(
        [sys.executable, ".harness/bin/harness.py", *args],
        cwd=work,
        text=True,
        capture_output=True,
        check=False,
    )
    return result


def events(work, session_id):
    log_path = work / ".harness" / "sessions" / f"{session_id}.jsonl"
    return [json.loads(line) for line in log_path.read_text().splitlines()]


def state(work):
    return json.loads((work / ".harness" / "state.json").read_text())


def write_result(work, role, text):
    slot = state(work)["role_slots"][role]
    result_path = work / slot["result_path"]
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(text)


class HarnessCliTests(unittest.TestCase):
    def test_dispatch_uses_unique_task_ids_and_preserves_same_role_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))

            self.assertEqual(run_cli(work, "start", "Mission").returncode, 0)
            first = run_cli(
                work,
                "dispatch-role",
                "--role",
                "Reader",
                "--objective",
                "Find facts",
                "--questions",
                "Q1?",
            )
            self.assertEqual(first.returncode, 0)
            first_slot = state(work)["role_slots"]["reader"]
            write_result(work, "reader", "- **Role**: reader\n- **Status**: Success\n")
            self.assertEqual(run_cli(work, "collect-role", "--role", "Reader").returncode, 0)

            second = run_cli(
                work,
                "dispatch-role",
                "--role",
                "Reader",
                "--objective",
                "Find more facts",
                "--questions",
                "Q2?",
            )
            self.assertEqual(second.returncode, 0)
            second_slot = state(work)["role_slots"]["reader"]

            self.assertNotEqual(first_slot["task_id"], second_slot["task_id"])
            self.assertTrue((work / first_slot["task_path"]).exists())
            self.assertTrue((work / first_slot["prompt_path"]).exists())
            self.assertTrue((work / first_slot["result_path"]).exists())
            self.assertTrue((work / second_slot["task_path"]).exists())
            self.assertTrue((work / second_slot["prompt_path"]).exists())


    def test_spec_check_creates_versioned_snapshot_and_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))

            self.assertEqual(run_cli(work, "start", "Mission").returncode, 0)
            session_id = state(work)["active_session_id"]
            self.assertEqual(run_cli(work, "write-spec").returncode, 0)
            spec_path = work / ".harness" / "runtime" / "current" / "implementation_spec.md"
            spec_path.write_text(
                "# Implementation Spec\n\n"
                "## Objective\nShip feature\n\n"
                "## Scope\n- Files Allowed:\n\n"
                "## Required Changes\nChange code\n\n"
                "## Evidence References\n- file.py:1\n\n"
                "## Allowed Autonomy\nNames only\n\n"
                "## Must Not Decide\nDefaults\n\n"
                "## Stop Conditions\nMissing evidence\n"
            )

            result = run_cli(work, "spec-check")

            self.assertEqual(result.returncode, 0)
            current_state = state(work)
            self.assertEqual(current_state["spec"]["status"], "ready")
            self.assertEqual(current_state["spec"]["version"], 1)
            snapshot = work / current_state["spec"]["snapshot_path"]
            self.assertTrue(snapshot.exists())
            self.assertEqual(snapshot.read_text(), spec_path.read_text())
            self.assertTrue(any(event["event_type"] == "SPEC_READY" for event in events(work, session_id)))


    def test_archive_current_preserves_task_tree_and_emits_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))

            self.assertEqual(run_cli(work, "start", "Mission").returncode, 0)
            mission_id = state(work)["active_mission_id"]
            session_id = state(work)["active_session_id"]
            self.assertEqual(
                run_cli(
                    work,
                    "dispatch-role",
                    "--role",
                    "Reader",
                    "--objective",
                    "Find facts",
                    "--questions",
                    "Q1?",
                ).returncode,
                0,
            )
            slot = state(work)["role_slots"]["reader"]
            write_result(work, "reader", "- **Role**: reader\n- **Status**: Success\n")

            result = run_cli(work, "archive-current")

            self.assertEqual(result.returncode, 0)
            archive = work / ".harness" / "tasks" / "archive" / mission_id
            self.assertTrue((archive / "mission_state.json").exists())
            self.assertTrue((archive / "tasks" / slot["task_id"] / "reader.task.md").exists())
            self.assertTrue((archive / "tasks" / slot["task_id"] / "reader.prompt.md").exists())
            self.assertTrue((archive / "tasks" / slot["task_id"] / "reader.result.md").exists())
            self.assertTrue(any(event["event_type"] == "MISSION_ARCHIVE" for event in events(work, session_id)))


    def test_start_auto_archive_writes_state_and_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))

            self.assertEqual(run_cli(work, "start", "First mission").returncode, 0)
            first_mission = state(work)["active_mission_id"]
            first_session = state(work)["active_session_id"]
            self.assertEqual(
                run_cli(
                    work,
                    "dispatch-role",
                    "--role",
                    "Reader",
                    "--objective",
                    "Find facts",
                    "--questions",
                    "Q1?",
                ).returncode,
                0,
            )

            self.assertEqual(run_cli(work, "start", "Second mission").returncode, 0)

            archive = work / ".harness" / "tasks" / "archive" / first_mission
            self.assertTrue((archive / "mission_state.json").exists())
            self.assertTrue(any(event["event_type"] == "AUTO_ARCHIVE" for event in events(work, first_session)))

    def test_doctor_reports_duplicate_task_ids_in_session_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))

            self.assertEqual(run_cli(work, "start", "Mission").returncode, 0)
            session_id = state(work)["active_session_id"]
            log_path = work / ".harness" / "sessions" / f"{session_id}.jsonl"
            with log_path.open("a") as f:
                f.write(json.dumps({
                    "timestamp": "2026-05-15T00:00:00",
                    "session_id": session_id,
                    "event_type": "TASK_DISPATCH",
                    "actor": "coordinator",
                    "summary": "duplicate one",
                    "task_id": "T-20260515-999",
                }) + "\n")
                f.write(json.dumps({
                    "timestamp": "2026-05-15T00:00:01",
                    "session_id": session_id,
                    "event_type": "TASK_DISPATCH",
                    "actor": "coordinator",
                    "summary": "duplicate two",
                    "task_id": "T-20260515-999",
                }) + "\n")

            result = run_cli(work, "doctor")

            self.assertIn("Duplicate task_id", result.stdout)
            self.assertIn("Found 1 potential issue", result.stdout)


if __name__ == "__main__":
    unittest.main()
