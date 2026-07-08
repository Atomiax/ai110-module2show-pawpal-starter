from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional

DAY_START_TIME = "08:00"


class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"
    VET_VISIT = "vet_visit"


class TimeSlot(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


@dataclass
class Constraint:
    """A restriction on the owner's day, e.g. blocked time or a pet-specific limit."""

    description: str
    affected_time_slot: TimeSlot
    blocked_minutes: int
    affected_pet: Optional["Pet"] = None


@dataclass
class Task:
    """A single pet care activity that can be completed and later reset for its next cycle."""

    name: str
    type: TaskType
    duration_minutes: int
    priority: int
    frequency: str
    preferred_time_of_day: TimeSlot
    pet: Optional["Pet"] = None
    is_completed: bool = False
    last_completed_date: Optional[str] = None

    def complete(self) -> None:
        """Mark this task done and stamp today's date as its last completion."""
        self.is_completed = True
        self.last_completed_date = date.today().isoformat()

    def reset(self) -> None:
        """Clear completion so a recurring task can be scheduled again."""
        self.is_completed = False


@dataclass
class Pet:
    """An owner's pet along with the list of care tasks assigned to it."""

    name: str
    species: str
    breed: str
    age: int
    health_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, _task: Task) -> None:
        """Attach a task to this pet, linking it back via Task.pet."""
        _task.pet = self
        self.tasks.append(_task)

    def get_pending_tasks(self) -> List[Task]:
        """Return the subset of this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.is_completed]


@dataclass
class ScheduledTask:
    task: Task
    pet: Pet
    scheduled_time: str
    is_completed: bool = False


@dataclass
class DailyPlan:
    """A single day's ordered schedule, with the reasoning behind its choices."""

    date: str
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    reasoning: str = ""

    @property
    def total_duration(self) -> int:
        """Sum of the durations of every task actually scheduled today."""
        return sum(st.task.duration_minutes for st in self.scheduled_tasks)

    def summarize(self) -> str:
        """Render the day's schedule as a human-readable, line-per-task string."""
        if not self.scheduled_tasks:
            return f"No tasks scheduled for {self.date}."

        lines = [f"Today's Schedule ({self.date}):"]
        for st in self.scheduled_tasks:
            lines.append(
                f"  {st.scheduled_time} - {st.task.name} for {st.pet.name} "
                f"({st.task.duration_minutes} min) [priority: {st.task.priority}]"
            )
        lines.append(f"Total scheduled time: {self.total_duration} min")
        return "\n".join(lines)


class Owner:
    def __init__(self, name: str, email: str, daily_time_available: int):
        self.name = name
        self.email = email
        self.daily_time_available = daily_time_available
        self.preferences: List[str] = []
        self.constraints: List[Constraint] = []
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def add_constraint(self, constraint: Constraint) -> None:
        """Register a new time/schedule constraint for this owner."""
        self.constraints.append(constraint)

    def get_available_minutes(self) -> int:
        """Return the owner's daily time budget minus all constraint-blocked minutes."""
        blocked = sum(c.blocked_minutes for c in self.constraints)
        return max(0, self.daily_time_available - blocked)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.current_plan: Optional[DailyPlan] = None

    def _get_all_pending_tasks(self) -> List[Task]:
        """Collect every pending task across all of the owner's pets."""
        tasks: List[Task] = []
        for pet in self.owner.pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks

    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Order tasks by highest priority first, then by shortest duration."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def generate_plan(self) -> DailyPlan:
        """Build and store today's schedule by greedily fitting prioritized tasks into available time."""
        available_minutes = self.owner.get_available_minutes()
        ordered_tasks = self.prioritize_tasks(self._get_all_pending_tasks())

        scheduled_tasks: List[ScheduledTask] = []
        reasoning_lines: List[str] = [
            f"Available time today: {available_minutes} minutes "
            f"(after subtracting {sum(c.blocked_minutes for c in self.owner.constraints)} "
            f"blocked minutes from constraints)."
        ]

        clock = datetime.strptime(DAY_START_TIME, "%H:%M")
        remaining_minutes = available_minutes

        for task in ordered_tasks:
            if task.duration_minutes > remaining_minutes:
                reasoning_lines.append(
                    f"Skipped '{task.name}' (priority {task.priority}): "
                    f"needs {task.duration_minutes} min but only {remaining_minutes} min remain."
                )
                continue

            scheduled_tasks.append(
                ScheduledTask(
                    task=task,
                    pet=task.pet,
                    scheduled_time=clock.strftime("%H:%M"),
                )
            )
            reasoning_lines.append(
                f"Scheduled '{task.name}' for {task.pet.name if task.pet else 'unknown pet'} "
                f"at {clock.strftime('%H:%M')} (priority {task.priority})."
            )
            clock += timedelta(minutes=task.duration_minutes)
            remaining_minutes -= task.duration_minutes

        plan = DailyPlan(
            date=date.today().isoformat(),
            scheduled_tasks=scheduled_tasks,
            reasoning="\n".join(reasoning_lines),
        )
        self.current_plan = plan
        return plan

    def explain_plan(self) -> str:
        """Return the reasoning behind the most recently generated plan."""
        if self.current_plan is None:
            return "No plan has been generated yet."
        return self.current_plan.reasoning

    def get_total_scheduled_time(self) -> int:
        """Return the total scheduled minutes from the most recently generated plan."""
        if self.current_plan is None:
            return 0
        return self.current_plan.total_duration
