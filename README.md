# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## ✨ Features

- **Owner & pet profiles** — create an `Owner` with a daily time budget, and attach any number of `Pet`s to them.
- **Task tracking** — add care tasks (walk, feeding, medication, grooming, etc.) to a pet with a duration, priority, and preferred time of day.
- **Priority-based scheduling** — `Scheduler.generate_plan()` greedily fits the highest-priority, then shortest, tasks into the owner's available minutes, skipping and explaining any that don't fit.
- **Sorting by time** — `Scheduler.sort_by_time()` puts a day's scheduled tasks back into chronological order regardless of the order they were generated in.
- **Filtering** — `Scheduler.filter_tasks()` narrows a task list down to one pet and/or a completion status, used to drive the filter dropdowns in the Streamlit UI.
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags two tasks booked for the same pet at the same time and returns a plain-language warning instead of crashing.
- **Daily recurrence** — completing a `daily`/`weekly`/`monthly` task via `Pet.mark_task_complete()` automatically creates its next occurrence, due on the correct future date.

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule (2026-07-07):
  08:00 - Feeding for Biscuit (10 min) [priority: 3]
  08:10 - Morning walk for Biscuit (30 min) [priority: 3]
  08:40 - Grooming for Mochi (20 min) [priority: 1]
Total scheduled time: 60 min

Reasoning:
Available time today: 90 minutes (after subtracting 0 blocked minutes from constraints).
Scheduled 'Feeding' for Biscuit at 08:00 (priority 3).
Scheduled 'Morning walk' for Biscuit at 08:10 (priority 3).
Scheduled 'Grooming' for Mochi at 08:40 (priority 1).
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

`tests/test_pawpal.py` covers:
- **Task completion** — `complete()` flips `is_completed` and stamps `last_completed_date`.
- **Task addition** — `Pet.add_task()` grows the pet's task list and links `Task.pet` back.
- **Sorting correctness** — `Scheduler.sort_by_time()` returns scheduled tasks in chronological order.
- **Recurrence logic** — completing a daily task via `Pet.mark_task_complete()` creates a new `Task` instance due the next day.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags two tasks for the same pet at the exact same time.
- **Edge case** — a pet with no tasks returns an empty pending-tasks list instead of erroring.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\ousma\Downloads\ai110-module2show-pawpal-starter-main\ai110-module2show-pawpal-starter-main
plugins: anyio-4.14.1
collected 6 items

tests\test_pawpal.py ......                                              [100%]

============================== 6 passed in 0.26s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — the core sorting, filtering, recurrence, and conflict-detection behaviors are covered and passing. What would push this to 5/5: tests around `Owner.get_available_minutes()` with multiple overlapping constraints, and a case where `generate_plan()` has to skip a low-priority task because higher-priority tasks used up all the available time.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts `ScheduledTask`s chronologically by their `HH:MM` `scheduled_time`. |
| Filtering | `Scheduler.filter_tasks()` | Filters a task list by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags any two scheduled tasks for the same pet at the exact same time and returns warning messages instead of crashing. See the tradeoff noted in `reflection.md` (exact time match only, not full interval overlap). |
| Recurring tasks | `Task.create_next_occurrence()`, `Pet.mark_task_complete()` | Completing a `daily`/`weekly`/`monthly` task stamps `last_completed_date` and spawns a new `Task` instance due on the next occurrence (via `timedelta`), which `Pet.get_pending_tasks()` excludes until its `due_date` arrives. |

## 📸 Demo Walkthrough

**UI features:**
- A one-time owner setup form (name, email, daily time available in minutes).
- A pet form that adds `Pet`s to the owner's household and lists them in a table.
- A task form scoped to a chosen pet, with dropdowns for task type, priority, frequency, and preferred time of day.
- A live-filterable task table (by pet, by pending/completed).
- A "Generate schedule" button that produces the day's plan, conflict warnings, and a reasoning expander.

**Example workflow:**
1. Run `streamlit run app.py`.
2. Fill out the owner form (e.g. "Jordan", 90 minutes/day) and submit.
3. Add a pet (e.g. "Biscuit", a dog) using the pet form.
4. Add a task to Biscuit — e.g. "Morning walk", 30 minutes, high priority, morning.
5. Add a second task, then use the pet/status filters to check the task table narrows correctly.
6. Click "Generate schedule" to view today's plan.

**Key Scheduler behaviors shown in the UI:**
- The schedule table is always in time order, because it's rendered from `scheduler.sort_by_time()`.
- If two tasks land on the same pet and time, a `st.warning` banner appears above the table instead of the app crashing; a clean day shows a `st.success` banner instead.
- The "Why this plan?" expander prints `scheduler.explain_plan()`, so an owner can see exactly why each task was scheduled (or skipped for lack of time).

**CLI output** (from `python main.py`, which exercises sorting, filtering, recurrence, and conflict detection end-to-end):

```
Today's Schedule (2026-07-07):
  08:00 - Feeding for Biscuit (10 min) [priority: 3]
  08:10 - Morning walk for Biscuit (30 min) [priority: 3]
  08:40 - Grooming for Mochi (20 min) [priority: 1]
Total scheduled time: 60 min

Reasoning:
Available time today: 90 minutes (after subtracting 0 blocked minutes from constraints).
Scheduled 'Feeding' for Biscuit at 08:00 (priority 3).
Scheduled 'Morning walk' for Biscuit at 08:10 (priority 3).
Scheduled 'Grooming' for Mochi at 08:40 (priority 1).

--- Sorting demo (Scheduler.sort_by_time) ---
Out of order: ['08:40', '08:00', '08:10']
Sorted:       ['08:00', '08:10', '08:40']

--- Filtering demo (Scheduler.filter_tasks) ---
Biscuit's tasks: ['Morning walk', 'Feeding']
Incomplete tasks: ['Morning walk', 'Feeding', 'Grooming']

--- Recurring task demo (Pet.mark_task_complete) ---
Completed 'Morning walk' on 2026-07-07.
Next occurrence due 2026-07-08 (not scheduled again until then).
Biscuit's pending tasks now: ['Feeding']

--- Conflict detection demo (Scheduler.detect_conflicts) ---
Conflict: 'Grooming' and 'Vet check-in call' are both scheduled for Mochi at 08:40.
```
