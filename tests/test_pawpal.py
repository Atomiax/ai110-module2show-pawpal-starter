from datetime import date, timedelta

from pawpal_system import Owner, Pet, ScheduledTask, Scheduler, Task, TaskType, TimeSlot


def make_task(name, duration=10, priority=3, frequency="daily", time_of_day=TimeSlot.MORNING):
    return Task(
        name=name,
        type=TaskType.WALK,
        duration_minutes=duration,
        priority=priority,
        frequency=frequency,
        preferred_time_of_day=time_of_day,
    )


def test_task_completion_changes_status():
    task = Task(
        name="Morning walk",
        type=TaskType.WALK,
        duration_minutes=30,
        priority=3,
        frequency="daily",
        preferred_time_of_day=TimeSlot.MORNING,
    )

    assert task.is_completed is False

    task.complete()

    assert task.is_completed is True
    assert task.last_completed_date is not None


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    task = Task(
        name="Feeding",
        type=TaskType.FEEDING,
        duration_minutes=10,
        priority=3,
        frequency="daily",
        preferred_time_of_day=TimeSlot.MORNING,
    )

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] is task
    assert task.pet is pet


def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Jordan", email="jordan@example.com", daily_time_available=120)
    scheduler = Scheduler(owner)
    pet = Pet(name="Biscuit", species="dog", breed="Mixed", age=2)

    shuffled = [
        ScheduledTask(task=make_task("Grooming"), pet=pet, scheduled_time="14:00"),
        ScheduledTask(task=make_task("Feeding"), pet=pet, scheduled_time="08:00"),
        ScheduledTask(task=make_task("Walk"), pet=pet, scheduled_time="09:30"),
    ]

    sorted_tasks = scheduler.sort_by_time(shuffled)

    assert [st.scheduled_time for st in sorted_tasks] == ["08:00", "09:30", "14:00"]


def test_marking_daily_task_complete_creates_next_occurrence():
    pet = Pet(name="Biscuit", species="dog", breed="Mixed", age=2)
    task = make_task("Morning walk", frequency="daily")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task)

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.name == task.name
    assert next_task.due_date == (date.today() + timedelta(days=1)).isoformat()
    # The new occurrence is a separate instance already attached to the pet.
    assert next_task in pet.tasks
    assert next_task is not task


def test_detect_conflicts_flags_duplicate_times():
    owner = Owner(name="Jordan", email="jordan@example.com", daily_time_available=120)
    scheduler = Scheduler(owner)
    pet = Pet(name="Mochi", species="cat", breed="Tabby", age=1)

    scheduled = [
        ScheduledTask(task=make_task("Grooming"), pet=pet, scheduled_time="08:40"),
        ScheduledTask(task=make_task("Vet call"), pet=pet, scheduled_time="08:40"),
    ]

    warnings = scheduler.detect_conflicts(scheduled)

    assert len(warnings) == 1
    assert "Mochi" in warnings[0]
    assert "08:40" in warnings[0]


def test_pet_with_no_tasks_has_no_pending_tasks():
    pet = Pet(name="Ghost", species="dog", breed="Unknown", age=0)

    assert pet.get_pending_tasks() == []
