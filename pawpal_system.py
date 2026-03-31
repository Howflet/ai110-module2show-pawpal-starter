"""
PawPal+ core classes: Task, Pet, Owner, Scheduler.
"""

from datetime import time
from typing import Optional


class Task:
    """Represents a single pet care task."""

    PRIORITY_VALUES = {"low": 1, "medium": 2, "high": 3}

    def __init__(
        self,
        description: str,
        duration_minutes: int,
        priority: str = "medium",
        due_time: Optional[time] = None,
        category: str = "general",
        recurring: bool = False,
        recur_interval_days: int = 1,
    ):
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low", "medium", or "high"
        self.due_time = due_time          # datetime.time or None
        self.category = category          # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
        self.recurring = recurring
        self.recur_interval_days = recur_interval_days
        self.completed = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def priority_value(self) -> int:
        """Return a numeric priority (high=3, medium=2, low=1)."""
        return self.PRIORITY_VALUES.get(self.priority, 0)

    def __repr__(self) -> str:
        status = "[done]" if self.completed else "[    ]"
        time_str = f" @{self.due_time.strftime('%H:%M')}" if self.due_time else ""
        recurring_str = " (recurring)" if self.recurring else ""
        return (
            f"[{status}] {self.description} "
            f"({self.priority}, {self.duration_minutes}min{time_str}{recurring_str})"
        )


class Pet:
    """Represents a pet owned by an Owner, holding that pet's tasks."""

    def __init__(self, name: str, species: str, age: int = 0):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def list_tasks(self) -> list[Task]:
        """Return a copy of all tasks for this pet."""
        return list(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all completed tasks."""
        return [t for t in self.tasks if t.completed]

    def __repr__(self) -> str:
        return f"Pet({self.name}, {self.species}, {len(self.tasks)} tasks)"


class Owner:
    """Represents the pet owner, holding their pets and daily time budget."""

    def __init__(self, name: str, available_minutes_per_day: int = 120):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet from this owner's pet list."""
        self.pets.remove(pet)

    def list_pets(self) -> list[Pet]:
        """Return a copy of all pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every pet."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet, task))
        return result

    def __repr__(self) -> str:
        return f"Owner({self.name}, {len(self.pets)} pets, {self.available_minutes_per_day}min/day)"


class Scheduler:
    """
    Retrieves and organizes tasks across all of an owner's pets.

    Algorithmic features:
      1. sort_tasks_by_priority  — sort all pending tasks high→low, then by due_time
      2. filter_tasks_by_category — filter across all pets by a task category
      3. detect_conflicts         — find overlapping time windows across all pets
      4. build_daily_schedule     — greedy knapsack: fit high-priority tasks within time budget
    """

    def __init__(self, owner: Owner):
        self.owner = owner

    # ── Algorithmic Feature 1 ──────────────────────────────────────────────
    def sort_tasks_by_priority(
        self, include_completed: bool = False
    ) -> list[tuple[Pet, Task]]:
        """
        Return all tasks across all pets sorted by priority (high first),
        then by due_time (earliest first), then by duration (shortest first).
        Excludes completed tasks by default.
        """
        pairs = self.owner.get_all_tasks()
        if not include_completed:
            pairs = [(p, t) for p, t in pairs if not t.completed]

        def sort_key(pair: tuple[Pet, Task]):
            _, task = pair
            priority_order = -task.priority_value()           # negate so high sorts first
            time_order = task.due_time if task.due_time else time(23, 59)
            return (priority_order, time_order, task.duration_minutes)

        return sorted(pairs, key=sort_key)

    # ── Algorithmic Feature 2 ──────────────────────────────────────────────
    def filter_tasks_by_category(self, category: str) -> list[tuple[Pet, Task]]:
        """
        Return all (pet, task) pairs across all pets where task.category matches.
        Operates across multiple pets.
        """
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.category == category
        ]

    # ── Algorithmic Feature 3 ──────────────────────────────────────────────
    def detect_conflicts(self) -> list[tuple[Pet, Task, Pet, Task]]:
        """
        Detect scheduling conflicts: any two tasks whose time windows overlap.
        Only tasks with a due_time are considered.
        Operates across multiple pets.
        """
        timed_tasks = [
            (p, t) for p, t in self.owner.get_all_tasks() if t.due_time is not None
        ]
        conflicts = []
        for i in range(len(timed_tasks)):
            for j in range(i + 1, len(timed_tasks)):
                pet_a, task_a = timed_tasks[i]
                pet_b, task_b = timed_tasks[j]
                start_a = task_a.due_time.hour * 60 + task_a.due_time.minute
                end_a = start_a + task_a.duration_minutes
                start_b = task_b.due_time.hour * 60 + task_b.due_time.minute
                end_b = start_b + task_b.duration_minutes
                if start_a < end_b and start_b < end_a:
                    conflicts.append((pet_a, task_a, pet_b, task_b))
        return conflicts

    # ── Algorithmic Feature 4 ──────────────────────────────────────────────
    def build_daily_schedule(self) -> list[tuple[Pet, Task]]:
        """
        Greedy scheduler: pick tasks in priority order until the owner's daily
        time budget is exhausted.  Skips already-completed tasks.
        Operates across multiple pets.
        """
        sorted_pairs = self.sort_tasks_by_priority(include_completed=False)
        schedule: list[tuple[Pet, Task]] = []
        time_used = 0
        for pet, task in sorted_pairs:
            if time_used + task.duration_minutes <= self.owner.available_minutes_per_day:
                schedule.append((pet, task))
                time_used += task.duration_minutes
        return schedule

    def get_schedule_summary(self) -> str:
        """Return a human-readable summary of the daily schedule with reasoning."""
        schedule = self.build_daily_schedule()
        if not schedule:
            return "No tasks could be scheduled (budget exhausted or no pending tasks)."

        lines = [
            f"Daily Schedule for {self.owner.name}",
            f"Time budget: {self.owner.available_minutes_per_day} minutes",
            "-" * 44,
        ]
        total_time = 0
        for pet, task in schedule:
            time_str = f" (due {task.due_time.strftime('%H:%M')})" if task.due_time else ""
            recurring_str = " [recurring]" if task.recurring else ""
            lines.append(
                f"  [{pet.name}] {task.description}"
                f" - {task.duration_minutes}min, {task.priority}{time_str}{recurring_str}"
            )
            total_time += task.duration_minutes
        lines.append("-" * 44)
        lines.append(f"Total scheduled: {total_time} min  |  Remaining: {self.owner.available_minutes_per_day - total_time} min")
        lines.append("")
        lines.append("Why this plan? Tasks were selected highest-priority first until the")
        lines.append("daily time budget was reached. Lower-priority tasks were deferred.")
        return "\n".join(lines)
