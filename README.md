# ClickUp Sprint Importer

A Python CLI that turns a JSON sprint definition into a fully-structured ClickUp board — Space → Folder → List → Tasks → Subtasks, all created in one run.

I built this because spinning up a new 2-week learning sprint in the ClickUp UI took 45+ minutes of repetitive clicking. Now it's `python clickup_importer.py` and done.

## What it does

Given a JSON file describing a sprint (task list with nested subtasks, statuses, priorities, descriptions), the importer:

1. Resolves the target **Space → Folder → List** by name via ClickUp's API v2.
2. Creates each top-level task in that list.
3. Creates subtasks underneath, linked by `parent` ID.
4. Reports per-row success/failure to stdout so failed creates are obvious.

Built around a personal use case: structured 14-day skill sprints (SQL, DSA, system design, etc.) where each day has measurable outcomes. See [`Sprint_1_ClickUp_Structure.md`](Sprint_1_ClickUp_Structure.md) for the source spec that drove the design.

## Tech stack

- **Python 3** — core
- **`requests`** — ClickUp REST API client
- **`python-dotenv`** — `.env`-based credential management (no secrets in code)
- **`pytest`** + `unittest.mock` — unit tests with mocked HTTP layer

## Quickstart

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Add credentials
cat > .env <<EOF
CLICKUP_API_TOKEN=pk_your_token_here
CLICKUP_TEAM_ID=your_team_id
EOF

# 3. Edit learning-sprint-1.json (or pass your own) — fill in space/folder/list names + task hierarchy
# 4. Run
python clickup_importer.py
```

The script will print each Space/Folder/List it resolves and each task it creates, then exit.

## JSON schema

See [`task-structure.json`](task-structure.json) for the schema. Minimal example:

```json
{
  "space": "Learning",
  "folder": "Sprint 1",
  "list": "Week 1 Tasks",
  "tasks": [
    {
      "name": "TASK 1: Complete SQL tutorial",
      "description": "Finish all 3 tiers on DataLemur",
      "status": "to do",
      "priority": 1,
      "subtasks": [
        { "name": "1.1 Beginner lessons 1-4", "description": "Day 1, 50 min" }
      ]
    }
  ]
}
```

## File map

| File | Purpose |
|------|---------|
| `clickup_importer.py` | Main script — API client + import driver |
| `test_clickup.py` | Unit tests (mocked `requests`) |
| `task-structure.json` | JSON schema reference |
| `learning-sprint-1.json` | Example sprint data |
| `Sprint_1_ClickUp_Structure.md` | Source spec the example was built from |
| `requirements.txt` | Pinned dependencies |

## Testing

```bash
pytest
```

Tests cover the name-to-ID resolver, the task creation payload, and the main-loop subtask traversal. No live API calls — all HTTP is mocked.

## Status

Working end-to-end for the sprint-import use case. Next improvements on the list: CLI flags for JSON path + dry-run mode, retry-on-429 for rate limits, and idempotent re-runs (skip tasks that already exist by name).
