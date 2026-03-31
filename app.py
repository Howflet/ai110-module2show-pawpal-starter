"""
PawPal+ Streamlit app — connected to the pawpal_system backend.
Run: streamlit run app.py
"""

import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Daily pet care planner")

# ── Session state setup ───────────────────────────────────────────────────────

if "tasks_by_pet" not in st.session_state:
    st.session_state.tasks_by_pet = {}   # {pet_name: [task_dict, ...]}

if "pets" not in st.session_state:
    st.session_state.pets = []   # list of {name, species, age}

# ── Owner + pet setup ─────────────────────────────────────────────────────────

st.header("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input(
        "Available minutes per day", min_value=10, max_value=480, value=90
    )

st.header("Pets")
with st.expander("Add a pet", expanded=not st.session_state.pets):
    pc1, pc2, pc3, pc4 = st.columns([2, 2, 1, 1])
    with pc1:
        new_pet_name = st.text_input("Pet name", key="new_pet_name")
    with pc2:
        new_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"], key="new_species")
    with pc3:
        new_age = st.number_input("Age", min_value=0, max_value=30, value=2, key="new_age")
    with pc4:
        st.write("")
        st.write("")
        if st.button("Add pet"):
            if new_pet_name and new_pet_name not in [p["name"] for p in st.session_state.pets]:
                st.session_state.pets.append(
                    {"name": new_pet_name, "species": new_species, "age": int(new_age)}
                )
                st.session_state.tasks_by_pet[new_pet_name] = []
                st.rerun()

if st.session_state.pets:
    st.write("**Registered pets:**", ", ".join(p["name"] for p in st.session_state.pets))
else:
    st.info("Add at least one pet above to get started.")

# ── Task entry ────────────────────────────────────────────────────────────────

st.header("Tasks")

if st.session_state.pets:
    pet_names = [p["name"] for p in st.session_state.pets]

    with st.expander("Add a task", expanded=True):
        tc1, tc2 = st.columns(2)
        with tc1:
            task_pet = st.selectbox("For pet", pet_names, key="task_pet")
            task_title = st.text_input("Task description", value="Morning walk", key="task_title")
            task_category = st.selectbox(
                "Category",
                ["walk", "feeding", "meds", "grooming", "enrichment", "general"],
                key="task_category",
            )
        with tc2:
            task_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration"
            )
            task_priority = st.selectbox(
                "Priority", ["low", "medium", "high"], index=2, key="task_priority"
            )
            task_use_time = st.checkbox("Set a due time?", key="task_use_time")
            task_due_time = None
            if task_use_time:
                task_due_time = st.time_input("Due time", value=time(8, 0), key="task_due_time")
            task_recurring = st.checkbox("Recurring daily?", key="task_recurring")

        if st.button("Add task"):
            entry = {
                "description": task_title,
                "duration_minutes": int(task_duration),
                "priority": task_priority,
                "category": task_category,
                "due_time": str(task_due_time) if task_due_time else None,
                "recurring": task_recurring,
                "completed": False,
            }
            st.session_state.tasks_by_pet.setdefault(task_pet, []).append(entry)
            st.rerun()

    # Display current tasks per pet
    for pet_name in pet_names:
        tasks = st.session_state.tasks_by_pet.get(pet_name, [])
        if tasks:
            st.subheader(f"{pet_name}'s tasks")
            for i, t in enumerate(tasks):
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    status = "✓" if t["completed"] else "○"
                    time_str = f" @{t['due_time']}" if t.get("due_time") else ""
                    st.write(
                        f"[{status}] **{t['description']}** — {t['duration_minutes']}min, "
                        f"{t['priority']}, {t['category']}{time_str}"
                    )
                with col_b:
                    if not t["completed"] and st.button("Done", key=f"done_{pet_name}_{i}"):
                        st.session_state.tasks_by_pet[pet_name][i]["completed"] = True
                        st.rerun()
else:
    st.info("Add pets first to manage tasks.")

# ── Scheduler ─────────────────────────────────────────────────────────────────

st.header("Generate Schedule")

if st.button("Build Daily Schedule", type="primary"):
    if not st.session_state.pets:
        st.warning("Add at least one pet first.")
    else:
        # Reconstruct domain objects from session state
        owner = Owner(owner_name, available_minutes_per_day=int(available_minutes))
        for pet_info in st.session_state.pets:
            pet = Pet(pet_info["name"], pet_info["species"], age=pet_info["age"])
            for t in st.session_state.tasks_by_pet.get(pet_info["name"], []):
                due = None
                if t.get("due_time"):
                    h, m = map(int, t["due_time"].split(":")[:2])
                    due = time(h, m)
                task = Task(
                    description=t["description"],
                    duration_minutes=t["duration_minutes"],
                    priority=t["priority"],
                    due_time=due,
                    category=t["category"],
                    recurring=t["recurring"],
                )
                if t["completed"]:
                    task.mark_complete()
                pet.add_task(task)
            owner.add_pet(pet)

        scheduler = Scheduler(owner)

        # ── Daily schedule ─────────────────────────────────────
        st.subheader("Daily Schedule")
        schedule = scheduler.build_daily_schedule()
        if schedule:
            total_min = sum(t.duration_minutes for _, t in schedule)
            st.success(
                f"Scheduled {len(schedule)} tasks — {total_min} of {available_minutes} minutes used."
            )
            rows = []
            for pet, task in schedule:
                rows.append({
                    "Pet": pet.name,
                    "Task": task.description,
                    "Priority": task.priority,
                    "Duration (min)": task.duration_minutes,
                    "Category": task.category,
                    "Due time": task.due_time.strftime("%H:%M") if task.due_time else "—",
                })
            st.table(rows)
            st.caption(
                "Why this plan? Tasks were selected highest-priority first until the daily "
                "time budget was reached. Lower-priority tasks were deferred."
            )
        else:
            st.info("No pending tasks to schedule.")

        # ── Conflicts ──────────────────────────────────────────
        st.subheader("Conflict Check")
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning(f"{len(conflicts)} scheduling conflict(s) detected:")
            for pet_a, task_a, pet_b, task_b in conflicts:
                st.write(
                    f"- **[{pet_a.name}] {task_a.description}** overlaps with "
                    f"**[{pet_b.name}] {task_b.description}**"
                )
        else:
            st.success("No scheduling conflicts.")

        # ── Priority-sorted task list ──────────────────────────
        with st.expander("All pending tasks sorted by priority"):
            sorted_tasks = scheduler.sort_tasks_by_priority()
            for pet, task in sorted_tasks:
                time_str = f" @{task.due_time.strftime('%H:%M')}" if task.due_time else ""
                st.write(
                    f"[{pet.name}] **{task.description}** — {task.priority}, "
                    f"{task.duration_minutes}min{time_str}"
                )
