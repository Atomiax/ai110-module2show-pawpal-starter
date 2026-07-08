# PawPal+ Project Reflection

## 1. System Design

**Core Actions**
- Add your pet
- Add Issues you have (whether for the pet, or constraints that interfere with caring for the pet)
- Create Plan

**a. Initial design**

- Briefly describe your initial UML design.

Owner has pets and constraints, and the Scheduler holds one Owner and works over that Owner's tasks to build a plan. Pretty flat: Owner → Pet → Task, plus Constraint hanging off Owner, and Scheduler sitting on top producing a DailyPlan.

- What classes did you include, and what responsibilities did you assign to each?

I started with Owner, Task, Pet, and Scheduler as the core four, then added Constraint (for things that eat into the Owner's time), DailyPlan and ScheduledTask (so a "plan" is its own object instead of just a list Scheduler mutates), and two enums, TaskType and TimeSlot, once I noticed I was about to represent both task category and time-of-day as loose strings.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, in a few ways. The biggest one: my first skeleton had `Pet.tasks` as a one-way list — a Task didn't know which Pet it belonged to. That was fine until I started writing `Scheduler.generate_plan()`, which needs to flatten every pet's tasks into one list to prioritize and schedule them. Without a `Task.pet` back-reference, I'd have had to carry `(task, pet)` tuples around by hand, and nothing would stop a task from accidentally getting paired with the wrong pet when building a `ScheduledTask`. So I added `Task.pet` and had `Pet.add_task()` set it automatically.

Second change: I originally had `DailyPlan.total_duration` as a plain stored field you set by hand. That's a bug waiting to happen — nothing forces it to stay equal to the sum of the scheduled tasks' durations if the list changes later. I turned it into a computed `@property` instead, so it can't drift out of sync.

Third: `Scheduler` originally kept its own `daily_plan: List[ScheduledTask]`, which duplicated the list already living inside the `DailyPlan` object returned by `generate_plan()`. Two sources of truth for "the current schedule" is exactly the kind of thing that causes a bug where one gets updated and the other doesn't, so I collapsed it down to a single `current_plan: DailyPlan`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler works off the Owner's `daily_time_available` minus whatever `Constraint.blocked_minutes` add up to (via `Owner.get_available_minutes()`), and then orders tasks by `priority` (highest first) and `duration_minutes` (shortest first as a tiebreaker) before greedily fitting them into whatever time is left. I leaned on priority as the primary signal because that's the thing an owner would actually want respected first — a high-priority medication task shouldn't get bumped by three low-priority grooming tasks just because they were added earlier.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`Scheduler.detect_conflicts()` only flags two tasks for the same pet that share the *exact* `scheduled_time` string (e.g. both at "08:40"). It does not check whether one task's duration overlaps into another task's start time (e.g. a 30-minute walk at 08:00 running into a 08:20 feeding). This is reasonable for PawPal+ because `generate_plan()` already assigns times sequentially with no gaps or overlaps by construction, so exact-match conflicts only show up when a user (or the Streamlit UI) manually schedules tasks outside that flow. Catching true interval overlaps would need an interval-overlap check (comparing start/end ranges) instead of a simple dictionary lookup, which is more correct but adds complexity that isn't needed yet given how plans are actually generated today.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI at basically every phase, but for different jobs each time. Early on it was design review — I asked it to look at my class skeleton and point out missing relationships or logic bottlenecks before I wrote any real logic, which is how I caught the missing `Task.pet` back-reference and the duplicate "current plan" state. Later it was implementation — turning stubbed methods into working code, writing the Streamlit wiring, and drafting test cases. The most useful prompts were the specific, "why" ones rather than generic ones: asking "how should the Scheduler retrieve all tasks from the Owner's pets" got a much more useful answer than "write the Scheduler class," because it forced a discussion of the Owner → Pet → Task path instead of just handing me code I'd have to reverse-engineer.

Keeping a separate chat session for the algorithmic-layer work (Phase 4) versus the earlier design work also helped more than I expected. It meant I could hand the AI just the current state of `pawpal_system.py` and a narrow question ("what's a lightweight conflict detection strategy that warns instead of crashing?") without dragging along the entire design-review conversation, which kept its answers focused on the actual code instead of re-litigating earlier decisions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked about conflict detection, a natural next step would've been full interval-overlap checking (comparing start/end time ranges instead of exact-time string matches) — genuinely the more "correct" version. I decided against implementing that version for now, because the way `generate_plan()` actually builds a schedule, tasks are already placed back-to-back with no overlaps, so an interval check would be solving a problem that can't currently happen. I verified this by tracing through `generate_plan()`'s clock-increment logic myself rather than taking the suggestion on faith, and instead of quietly dropping the idea, I wrote the tradeoff into this file (§2b) and the README so it's a documented decision, not a silent gap.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

`tests/test_pawpal.py` covers: task completion (`complete()` flips `is_completed` and stamps a date), task addition (`Pet.add_task()` grows the pet's list and links the task back), sorting correctness (`Scheduler.sort_by_time()` returns scheduled tasks in chronological order regardless of the order they were passed in), recurrence logic (completing a daily task spawns a new `Task` due the next day, via `timedelta`), conflict detection (two tasks for the same pet at the same time produce a warning), and one edge case — a pet with no tasks returns an empty pending list instead of erroring. These matter because they're exactly the behaviors a bug would hide in silently: a sorting bug wouldn't crash, it would just quietly show an owner their tasks in the wrong order; a recurrence bug could either spam duplicate tasks or lose a recurring task entirely.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'd put myself at 4 out of 5 stars. The core paths are tested and I've also run them by hand through `main.py`, so I trust the sorting, filtering, recurrence, and conflict-warning behavior. What I haven't tested yet: `Owner.get_available_minutes()` with several overlapping constraints stacked on top of each other, and a case where `generate_plan()` has to actually skip a low-priority task because higher-priority tasks used up all the available time — I've seen that logic work in the reasoning output, but I don't have an automated test pinning it down yet.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Splitting the scheduling logic into small, single-purpose methods (`prioritize_tasks`, `sort_by_time`, `filter_tasks`, `detect_conflicts`, `get_available_minutes`) instead of cramming everything into one big `generate_plan()`. It made each piece independently testable and meant that when Phase 4 asked for sorting/filtering/conflict detection, I was extending the design rather than untangling one giant method.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd revisit the exact-time-only conflict detection and build the real interval-overlap version, plus let the scheduler actually use `preferred_time_of_day` when placing tasks instead of just packing everything back-to-back starting at 8:00am. Right now a task's preferred time slot is stored but not really honored by `generate_plan()`.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Getting the relationships right in the skeleton — the back-references, the single source of truth for shared state — mattered more than any of the actual algorithm work that came later. Every bug-shaped risk I ran into in Phase 4 and 5 traced back to a structural gap from Phase 1 (the missing `Task.pet` link, the duplicate plan state). On the AI side: it's a much better design reviewer and implementer than it is a final decision-maker — it's good at surfacing options and tradeoffs quickly, but I still had to be the one tracing through the actual scheduling logic to decide which tradeoff was actually reasonable for this app, and documenting *why*, instead of just accepting whichever answer sounded more sophisticated.
