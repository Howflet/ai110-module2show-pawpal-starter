"""
PawPal+ demo script.
Creates one Owner, two Pets, and several Tasks, then exercises the Scheduler.
Run: python main.py
"""

from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    print("=" * 50)
    print("  PawPal+ Demo")
    print("=" * 50)

    # ── Owner ──────────────────────────────────────
    owner = Owner("Jordan", available_minutes_per_day=90)

    # ── Pet 1: Mochi the dog ───────────────────────
    mochi = Pet("Mochi", "dog", age=3)
    mochi.add_task(Task("Morning walk",     30, priority="high",   due_time=time(7, 0),  category="walk"))
    mochi.add_task(Task("Breakfast",        10, priority="high",   due_time=time(7, 30), category="feeding", recurring=True))
    mochi.add_task(Task("Heartworm pill",    5, priority="high",   due_time=time(8, 0),  category="meds"))
    mochi.add_task(Task("Afternoon walk",   20, priority="medium", due_time=time(15, 0), category="walk"))
    mochi.add_task(Task("Brush coat",       15, priority="low",                          category="grooming"))

    # ── Pet 2: Luna the cat ────────────────────────
    luna = Pet("Luna", "cat", age=5)
    luna.add_task(Task("Breakfast",         5,  priority="high",   due_time=time(7, 30), category="feeding", recurring=True))
    luna.add_task(Task("Flea treatment",   10,  priority="high",   due_time=time(9, 0),  category="meds"))
    luna.add_task(Task("Enrichment play",  20,  priority="medium",                       category="enrichment"))
    luna.add_task(Task("Litter box clean", 10,  priority="medium",                       category="general"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    # ── Basic info ─────────────────────────────────
    print(f"\nOwner : {owner}")
    print(f"Pets  : {', '.join(p.name for p in owner.list_pets())}")

    print("\n--- All Tasks by Pet ---")
    for pet in owner.list_pets():
        print(f"\n  {pet.name} ({pet.species}, {pet.age}y):")
        for task in pet.list_tasks():
            print(f"    {task}")

    # -- Algorithmic Feature 1: Sort by priority --
    print("\n--- Feature 1: All Tasks Sorted by Priority (high -> low) ---")
    for pet, task in scheduler.sort_tasks_by_priority():
        print(f"  [{pet.name:6}] {task}")

    # -- Algorithmic Feature 2: Filter by category --
    print("\n--- Feature 2: Filter Tasks by Category 'meds' (all pets) ---")
    med_tasks = scheduler.filter_tasks_by_category("meds")
    if med_tasks:
        for pet, task in med_tasks:
            print(f"  [{pet.name}] {task}")
    else:
        print("  (none)")

    print("\n--- Feature 2b: Filter by Category 'feeding' (all pets) ---")
    for pet, task in scheduler.filter_tasks_by_category("feeding"):
        print(f"  [{pet.name}] {task}")

    # -- Algorithmic Feature 3: Conflict detection --
    print("\n--- Feature 3: Conflict Detection ---")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for pet_a, task_a, pet_b, task_b in conflicts:
            print(
                f"  CONFLICT: [{pet_a.name}] '{task_a.description}' "
                f"overlaps [{pet_b.name}] '{task_b.description}'"
            )
    else:
        print("  No scheduling conflicts detected.")

    # -- Algorithmic Feature 4: Daily schedule --
    print("\n--- Feature 4: Build Daily Schedule (greedy, priority-first) ---")
    print(scheduler.get_schedule_summary())

    # -- Task completion --
    print("\n--- Marking tasks complete ---")
    mochi.tasks[0].mark_complete()   # Morning walk
    luna.tasks[0].mark_complete()    # Breakfast
    print(f"  Marked '{mochi.tasks[0].description}' (Mochi) complete.")
    print(f"  Marked '{luna.tasks[0].description}' (Luna) complete.")
    print(f"\n  Mochi pending : {len(mochi.get_pending_tasks())} tasks")
    print(f"  Mochi done    : {len(mochi.get_completed_tasks())} tasks")
    print(f"  Luna  pending : {len(luna.get_pending_tasks())} tasks")
    print(f"  Luna  done    : {len(luna.get_completed_tasks())} tasks")

    print("\n--- Rebuilt Schedule After Completions ---")
    print(scheduler.get_schedule_summary())

    print("\n" + "=" * 50)
    print("  Demo complete.")
    print("=" * 50)


if __name__ == "__main__":
    main()
