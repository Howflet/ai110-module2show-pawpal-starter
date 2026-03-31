# PawPal+ UML Class Diagram

```mermaid
classDiagram
    direction TB

    class Task {
        +str description
        +int duration_minutes
        +str priority
        +time due_time
        +str category
        +bool recurring
        +int recur_interval_days
        +bool completed
        --
        +mark_complete() None
        +priority_value() int
        +__repr__() str
    }

    class Pet {
        +str name
        +str species
        +int age
        +list~Task~ tasks
        --
        +add_task(task: Task) None
        +remove_task(task: Task) None
        +list_tasks() list~Task~
        +get_pending_tasks() list~Task~
        +get_completed_tasks() list~Task~
        +__repr__() str
    }

    class Owner {
        +str name
        +int available_minutes_per_day
        +list~Pet~ pets
        --
        +add_pet(pet: Pet) None
        +remove_pet(pet: Pet) None
        +list_pets() list~Pet~
        +get_all_tasks() list~tuple~
        +__repr__() str
    }

    class Scheduler {
        +Owner owner
        --
        +sort_tasks_by_priority(include_completed: bool) list~tuple~
        +filter_tasks_by_category(category: str) list~tuple~
        +detect_conflicts() list~tuple~
        +build_daily_schedule() list~tuple~
        +get_schedule_summary() str
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Task : has
    Scheduler "1" --> "1" Owner : manages
```

## Relationship notes

| Relationship | Type | Meaning |
|---|---|---|
| `Owner` → `Pet` | Composition (`*--`) | Pets belong to one Owner; Owner manages their lifecycle |
| `Pet` → `Task` | Composition (`*--`) | Tasks belong to one Pet; Pet manages their lifecycle |
| `Scheduler` → `Owner` | Association (`-->`) | Scheduler operates on an Owner but does not own it |
