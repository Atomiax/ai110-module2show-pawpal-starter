from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"
    VET_VISIT = "vet_visit"


@dataclass
class Constraint:
    description: str
    affected_time_slot: str
    blocked_minutes: int


@dataclass
class Task:
    name: str
    type: TaskType
    duration_minutes: int
    priority: int
    frequency: str
    preferred_time_of_day: str
    is_completed: bool = False

    def complete(self) -> None:
        pass

    def reset(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    health_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, _task: Task) -> None:
        pass

    def get_pending_tasks(self) -> List[Task]:
        pass


@dataclass
class ScheduledTask:
    task: Task
    pet: Pet
    scheduled_time: str
    is_completed: bool = False


@dataclass
class DailyPlan:
    date: str
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    reasoning: str = ""
    total_duration: int = 0

    def summarize(self) -> str:
        pass


class Owner:
    def __init__(self, name: str, email: str, daily_time_available: int):
        self.name = name
        self.email = email
        self.daily_time_available = daily_time_available
        self.preferences: List[str] = []
        self.constraints: List[Constraint] = []
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def add_constraint(self, constraint: Constraint) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan: List[ScheduledTask] = []

    def generate_plan(self) -> DailyPlan:
        pass

    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def get_total_scheduled_time(self) -> int:
        pass
