import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType, TimeSlot

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+, a pet care planning assistant. Set up your owner profile,
add pets and tasks, then generate a daily schedule.
"""
)

# --- Phase 2: session-state "memory" -----------------------------------
# Streamlit reruns this whole script on every interaction, so anything we
# want to survive a click (the Owner and its pets/tasks) must live in
# st.session_state instead of a plain local variable.
if "owner" not in st.session_state:
    st.session_state.owner = None

st.divider()
st.subheader("1. Owner Profile")

if st.session_state.owner is None:
    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value="Jordan")
        owner_email = st.text_input("Email", value="jordan@example.com")
        daily_time_available = st.number_input(
            "Daily time available (minutes)", min_value=1, max_value=1440, value=90
        )
        if st.form_submit_button("Create owner"):
            st.session_state.owner = Owner(
                name=owner_name,
                email=owner_email,
                daily_time_available=int(daily_time_available),
            )
            st.rerun()
else:
    owner = st.session_state.owner
    st.success(f"Owner: {owner.name} ({owner.email}) — {owner.daily_time_available} min/day available")

st.divider()
st.subheader("2. Pets")

owner = st.session_state.owner

if owner is None:
    st.info("Create an owner above before adding pets.")
else:
    with st.form("pet_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_name = st.text_input("Pet name", value="Mochi")
        with col2:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        with col3:
            breed = st.text_input("Breed", value="")
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
        if st.form_submit_button("Add pet"):
            # Owner.add_pet() is the single place that knows how a pet joins
            # a household, so the UI just calls it instead of touching
            # owner.pets directly.
            owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
            st.rerun()

    if owner.pets:
        st.write("Current pets:")
        st.table(
            [
                {"name": p.name, "species": p.species, "breed": p.breed, "age": p.age, "tasks": len(p.tasks)}
                for p in owner.pets
            ]
        )
    else:
        st.info("No pets yet. Add one above.")

st.divider()
st.subheader("3. Tasks")

if owner is None or not owner.pets:
    st.info("Add an owner and at least one pet before adding tasks.")
else:
    with st.form("task_form", clear_on_submit=True):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Pet", pet_names)

        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        col4, col5 = st.columns(2)
        with col4:
            task_type = st.selectbox("Type", [t.value for t in TaskType])
        with col5:
            preferred_time = st.selectbox("Preferred time of day", [t.value for t in TimeSlot])

        frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

        if st.form_submit_button("Add task"):
            priority_map = {"low": 1, "medium": 2, "high": 3}
            # Find the Pet object matching the selected name so we can call
            # Pet.add_task(), which also links the task back to its pet.
            selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            selected_pet.add_task(
                Task(
                    name=task_title,
                    type=TaskType(task_type),
                    duration_minutes=int(duration),
                    priority=priority_map[priority_label],
                    frequency=frequency,
                    preferred_time_of_day=TimeSlot(preferred_time),
                )
            )
            st.rerun()

    all_tasks = [t for p in owner.pets for t in p.tasks]
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "pet": t.pet.name if t.pet else "",
                    "title": t.name,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "preferred_time": t.preferred_time_of_day.value,
                    "completed": t.is_completed,
                }
                for t in all_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("4. Build Schedule")

if owner is None or not any(p.tasks for p in owner.pets):
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        # A fresh Scheduler per click is fine: all persistent state (the
        # owner, pets, tasks) already lives in st.session_state.owner.
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()

        st.markdown(f"**{plan.date} — total scheduled time: {plan.total_duration} min**")
        for st_task in plan.scheduled_tasks:
            st.write(
                f"{st_task.scheduled_time} — {st_task.task.name} for {st_task.pet.name} "
                f"({st_task.task.duration_minutes} min) [priority: {st_task.task.priority}]"
            )

        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan())
