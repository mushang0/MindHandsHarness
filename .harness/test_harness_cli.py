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
    shutil.copytree(REPO_ROOT / ".harness", work / ".harness")
    shutil.copy2(REPO_ROOT / "AGENTS.md", work / "AGENTS.md")
    (work / "src").mkdir()
    (work / "src" / "app.py").write_text("print('hello')\n")
    return work


def run_cli(work, *args):
    return subprocess.run(
        [sys.executable, ".harness/bin/harness.py", *args],
        cwd=work,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path):
    return json.loads(path.read_text())


class HarnessV2CliTests(unittest.TestCase):
    def test_init_creates_v2_context_memory_policy_and_runtime_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))

            result = run_cli(work, "init")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((work / ".harness/context/boot.md").exists())
            self.assertTrue((work / ".harness/context/project-status.md").exists())
            self.assertTrue((work / ".harness/context/recent-summary.md").exists())
            self.assertTrue((work / ".harness/policies/context-loading.md").exists())
            self.assertTrue((work / ".harness/policies/rtk-policy.md").exists())
            self.assertTrue((work / ".harness/policies/memory-policy.md").exists())
            self.assertTrue((work / ".harness/roles/executor.md").exists())
            self.assertTrue((work / ".harness/runtime/state.json").exists())

    def test_start_and_context_boot_use_runtime_session_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)

            started = run_cli(work, "start", "Refactor skeleton")
            boot = run_cli(work, "context", "boot")

            self.assertEqual(started.returncode, 0, started.stderr)
            self.assertEqual(boot.returncode, 0, boot.stderr)
            state = read_json(work / ".harness/runtime/state.json")
            session_dir = work / ".harness/runtime/sessions" / state["active_session_id"]
            self.assertTrue(session_dir.exists())
            self.assertTrue((session_dir / "events.jsonl").exists())
            self.assertIn("Refactor skeleton", boot.stdout)
            self.assertIn("Coordinator decides. Executor acts.", boot.stdout)

    def test_map_init_and_update_create_incremental_project_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)

            initial = run_cli(work, "map", "init")
            (work / "src" / "feature.py").write_text("VALUE = 1\n")
            update = run_cli(work, "map", "update")
            show = run_cli(work, "map", "show")

            self.assertEqual(initial.returncode, 0, initial.stderr)
            self.assertEqual(update.returncode, 0, update.stderr)
            self.assertEqual(show.returncode, 0, show.stderr)
            index = read_json(work / ".harness/context/project-map.index.json")
            paths = {entry["path"] for entry in index["entries"]}
            self.assertIn("AGENTS.md", paths)
            self.assertIn("src/feature.py", paths)
            self.assertNotIn(".harness/runtime/state.json", paths)
            self.assertIn("src/feature.py", update.stdout)
            self.assertIn("Project Map", show.stdout)

    def test_task_new_dispatch_collect_executor_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)
            self.assertEqual(run_cli(work, "start", "Implement feature").returncode, 0)

            created = run_cli(
                work,
                "task",
                "new",
                "--title",
                "Edit app",
                "--objective",
                "Change app.py output",
                "--mode",
                "execute",
                "--allowed",
                "src/app.py",
                "--steps",
                "Edit src/app.py; run python src/app.py",
                "--validation",
                "python src/app.py",
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            task_id = created.stdout.strip().split()[-1]

            dispatched = run_cli(work, "task", "dispatch", "--task-id", task_id)
            self.assertEqual(dispatched.returncode, 0, dispatched.stderr)
            state = read_json(work / ".harness/runtime/state.json")
            task_dir = work / ".harness/runtime/sessions" / state["active_session_id"] / "tasks" / task_id
            prompt = task_dir / "executor_prompt.md"
            result = task_dir / "executor_result.md"
            self.assertTrue(prompt.exists())
            self.assertIn("Role: Executor", prompt.read_text())
            result.write_text("# Executor Result\n## Status\nsuccess\n")

            collected = run_cli(work, "task", "collect", "--task-id", task_id)
            self.assertEqual(collected.returncode, 0, collected.stderr)
            self.assertIn("success", collected.stdout)

            boot = run_cli(work, "context", "boot")
            self.assertIn(task_id, boot.stdout)
            self.assertIn("Suggested Next Action", boot.stdout)

    def test_context_probe_records_targeted_read_path_for_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)
            self.assertEqual(run_cli(work, "start", "Probe code").returncode, 0)
            created = run_cli(
                work,
                "task",
                "new",
                "--title",
                "Inspect app",
                "--objective",
                "Inspect app.py",
                "--mode",
                "inspect",
                "--allowed",
                "src/app.py",
            )
            task_id = created.stdout.strip().split()[-1]

            probe = run_cli(
                work,
                "context",
                "probe",
                "--task-id",
                task_id,
                "--purpose",
                "confirm entry point",
                "--method",
                "rtk_slice",
                "--source",
                "src/app.py",
                "--result",
                "line 1 prints hello",
            )

            self.assertEqual(probe.returncode, 0, probe.stderr)
            state = read_json(work / ".harness/runtime/state.json")
            probes = (
                work
                / ".harness/runtime/sessions"
                / state["active_session_id"]
                / "tasks"
                / task_id
                / "context-probes.md"
            ).read_text()
            self.assertIn("confirm entry point", probes)
            self.assertIn("rtk_slice", probes)
            self.assertIn("src/app.py", probes)

    def test_task_collect_extracts_memory_candidates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)
            self.assertEqual(run_cli(work, "start", "Collect memory").returncode, 0)
            created = run_cli(
                work,
                "task",
                "new",
                "--title",
                "Run tests",
                "--objective",
                "Collect validation command",
                "--mode",
                "verify",
            )
            task_id = created.stdout.strip().split()[-1]
            state = read_json(work / ".harness/runtime/state.json")
            task_dir = work / ".harness/runtime/sessions" / state["active_session_id"] / "tasks" / task_id
            (task_dir / "executor_result.md").write_text(
                "# Executor Result\n"
                "## Status\nsuccess\n\n"
                "## Memory Candidates\n"
                "- type: command\n"
                "  content: Use `python3 .harness/test_harness_cli.py` for CLI regression tests.\n"
                "  evidence: verification output passed.\n"
                "\n"
                "## Next Suggested Action\n- Apply command memory.\n"
            )

            collected = run_cli(work, "task", "collect", "--task-id", task_id)

            self.assertEqual(collected.returncode, 0, collected.stderr)
            candidates = task_dir / "memory_candidates.md"
            self.assertTrue(candidates.exists())
            self.assertIn("CLI regression tests", candidates.read_text())

    def test_memory_apply_updates_target_file_and_recent_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)

            result = run_cli(
                work,
                "memory",
                "apply",
                "--type",
                "decision",
                "--source",
                "manual",
                "--content",
                "Use Coordinator + Executor as the only standing roles.",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Coordinator + Executor", (work / ".harness/memory/decisions.md").read_text())
            self.assertIn("Coordinator + Executor", (work / ".harness/context/recent-summary.md").read_text())

    def test_memory_propose_apply_from_proposal_and_show_boot(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            self.assertEqual(run_cli(work, "init").returncode, 0)

            proposed = run_cli(
                work,
                "memory",
                "propose",
                "--type",
                "negative",
                "--source",
                "T-001",
                "--content",
                "Do not paste full command logs into Coordinator context.",
                "--evidence",
                "rtk policy requires bounded output.",
            )
            proposal_id = proposed.stdout.strip().split()[-1]
            applied = run_cli(work, "memory", "apply", "--proposal-id", proposal_id)
            boot = run_cli(work, "memory", "show-boot")

            self.assertEqual(proposed.returncode, 0, proposed.stderr)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertIn("full command logs", (work / ".harness/memory/negative.md").read_text())
            self.assertIn("full command logs", boot.stdout)

    def test_skills_scan_indexes_external_skill_locations_without_copying(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            skill_root = Path(tmp) / "external-skills"
            (skill_root / "demo").mkdir(parents=True)
            (skill_root / "demo" / "SKILL.md").write_text("---\nname: demo\n---\n# Demo\n")
            self.assertEqual(run_cli(work, "init").returncode, 0)

            scan = run_cli(work, "skills", "scan", "--path", str(skill_root))
            listed = run_cli(work, "skills", "list")

            self.assertEqual(scan.returncode, 0, scan.stderr)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            registry = read_json(work / ".harness/skills/registry.json")
            self.assertEqual(registry["skills"][0]["name"], "demo")
            self.assertEqual(registry["skills"][0]["location"], "external")
            self.assertFalse((work / ".harness/skills/demo/SKILL.md").exists())
            self.assertIn("demo", listed.stdout)

    def test_skills_register_and_resolve_single_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = prepare_harness(Path(tmp))
            skill_file = Path(tmp) / "external" / "rtk" / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("---\nname: rtk\n---\n# RTK\n")
            self.assertEqual(run_cli(work, "init").returncode, 0)

            registered = run_cli(
                work,
                "skills",
                "register",
                "--name",
                "rtk",
                "--path",
                str(skill_file),
                "--trigger",
                "large files,logs",
            )
            resolved = run_cli(work, "skills", "resolve", "rtk")

            self.assertEqual(registered.returncode, 0, registered.stderr)
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            self.assertIn(str(skill_file), resolved.stdout)
            self.assertFalse((work / ".harness/skills/rtk/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
