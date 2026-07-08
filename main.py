from pawpal_system import Owner, Pet, Task, TaskType, TimeSlot, Scheduler


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


if __name__ == "__main__":
    main()
