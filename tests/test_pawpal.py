from pawpal_system import Pet, Task, TaskType, TimeSlot


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
