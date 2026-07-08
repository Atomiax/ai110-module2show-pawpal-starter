from pawpal_system import Owner, Pet, ScheduledTask, Task, TaskType, TimeSlot, Scheduler


def main():
    owner = Owner(name="Jordan", email="jordan@example.com", daily_time_available=90)

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(
        Task(
            name="Morning walk",
            type=TaskType.WALK,
            duration_minutes=30,
            priority=3,
            frequency="daily",
            preferred_time_of_day=TimeSlot.MORNING,
        )
    )
    biscuit.add_task(
        Task(
            name="Feeding",
            type=TaskType.FEEDING,
            duration_minutes=10,
            priority=3,
            frequency="daily",
            preferred_time_of_day=TimeSlot.MORNING,
        )
    )
    mochi.add_task(
        Task(
            name="Grooming",
            type=TaskType.GROOMING,
            duration_minutes=20,
            priority=1,
            frequency="weekly",
            preferred_time_of_day=TimeSlot.AFTERNOON,
        )
    )

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print(plan.summarize())
    print()
    print("Reasoning:")
    print(scheduler.explain_plan())

    # --- Sorting demo: feed scheduled tasks in out of order, sort them back ---
    print("\n--- Sorting demo (Scheduler.sort_by_time) ---")
    shuffled = [plan.scheduled_tasks[2], plan.scheduled_tasks[0], plan.scheduled_tasks[1]]
    print("Out of order:", [st.scheduled_time for st in shuffled])
    print("Sorted:      ", [st.scheduled_time for st in scheduler.sort_by_time(shuffled)])

    # --- Filtering demo: Scheduler.filter_tasks by pet / completion status ---
    print("\n--- Filtering demo (Scheduler.filter_tasks) ---")
    all_tasks = biscuit.tasks + mochi.tasks
    print("Biscuit's tasks:", [t.name for t in scheduler.filter_tasks(all_tasks, pet_name="Biscuit")])
    print("Incomplete tasks:", [t.name for t in scheduler.filter_tasks(all_tasks, is_completed=False)])

    # --- Recurring task demo: completing a daily task creates its next occurrence ---
    print("\n--- Recurring task demo (Pet.mark_task_complete) ---")
    walk = next(t for t in biscuit.tasks if t.name == "Morning walk")
    next_walk = biscuit.mark_task_complete(walk)
    print(f"Completed '{walk.name}' on {walk.last_completed_date}.")
    print(f"Next occurrence due {next_walk.due_date} (not scheduled again until then).")
    print("Biscuit's pending tasks now:", [t.name for t in biscuit.get_pending_tasks()])

    # --- Conflict detection demo: two tasks for the same pet at the same time ---
    print("\n--- Conflict detection demo (Scheduler.detect_conflicts) ---")
    grooming = next(t for t in mochi.tasks if t.name == "Grooming")
    extra_task = Task(
        name="Vet check-in call",
        type=TaskType.VET_VISIT,
        duration_minutes=15,
        priority=2,
        frequency="once",
        preferred_time_of_day=TimeSlot.AFTERNOON,
    )
    mochi.add_task(extra_task)
    conflicting_schedule = [
        ScheduledTask(task=grooming, pet=mochi, scheduled_time="08:40"),
        ScheduledTask(task=extra_task, pet=mochi, scheduled_time="08:40"),
    ]
    warnings = scheduler.detect_conflicts(conflicting_schedule)
    for warning in warnings:
        print(warning)


if __name__ == "__main__":
    main()
