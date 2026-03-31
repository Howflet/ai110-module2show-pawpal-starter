# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

In my first UML sketch, there were four classes: Owner, Pet, Task, and Scheduler. From the beginning, I made sure that everyone knew what their job was. For example, Task holds all the information about one care activity, Pet owns a collection of tasks and knows how to query them, Owner owns a collection of pets and knows how much time they have each day, and Scheduler does all the algorithmic work between pets. The most important early choice was that Scheduler would not store any data itself. Instead, it would just get a Owner and work with what the owner already has.

**b. Design changes**

Moving get_all_tasks() from Scheduler to Owner was one significant change. Since it feels like a query, my initial thought was to put it in Scheduler. However, during implementation, it became apparent that an Owner should be able to respond to what are all my tasks? without requiring a Scheduler. As a result, Owner became more independent and Scheduler remained solely algorithmic. Adding the category and recurring fields to Task was a second modification. These werent in the original sketch, but they became essential when I started creating actual tasks and realized that walk and meds needed to be distinguishable for the filter feature.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

Two limitations are taken into account by the scheduler: the owner's daily time budget in minutes and the task priority (high / medium / low). No matter how much time is available, missing a grooming session is worse than missing a medication, so priority was considered the main constraint. The time budget was secondary because, after tasks are ranked, it decides which ones are actually included in the plan. Due time does not determine whether a task is added to the schedule; rather, it is used to detect conflicts and break ties in the sort.

**b. Tradeoffs**

The greedy method stops when the budget is full and strictly prioritizes the tasks. This means that even if the pet benefits more from the two smaller tasks combined, a 30-minute high-priority walk will always be preferred over two 10-minute medium-priority tasks. A much more difficult knapsack problem would need to be solved in order to find a true optimal solution. Because pet care priorities are typically clear (owners already know that medication outperforms enrichment) and the plan's simplicity makes its logic easy for the user to understand, the greedy approach is a reasonable trade-off in this situation.

---

## 3. AI Collaboration

**a. How you used AI**

I worked with Claude as a design partner to improve the logic and architecture of my pet care scheduler. In addition to establishing the mathematical basis for conflict detection using the interval overlap check start_a < end_b and start_b < end_a, this collaboration revealed important data attributes like category and recurring for task scheduling. Claude suggested a dict-based method for controlling Streamlit session state, which went beyond logic to direct the UI implementation. The best approach was to ask for intent rather than code; by outlining the intended result—for example, by asking the scheduler to defend its task choices—I was able to make the underlying logic clear and simpler to assess.

**b. Judgment and verification**

At first, Claude proposed using st.session_state to store live Pet and Task objects. At first, I was okay with this, but when I reran, the state became inconsistent and Streamlit issued serialization warnings. I rejected the method and substituted it with reconstructing domain objects each time the schedule is generated and storing plain dicts in session state. By adding pets and tasks, clicking Build Daily Schedule several times, and making sure the output remained consistent throughout reruns and after marking tasks completed, I was able to confirm the fix.

---

## 4. Testing and Verification

**a. What you tested**

Task.mark_complete() and priority_value(), Pet task management (add, remove, pending/completed filtering), Owner.get_all_tasks() returning tasks from all pets, Scheduler.sort_tasks_by_priority() ordering and cross-pet coverage, Scheduler.filter_tasks_by_category() correctness and cross-pet coverage, Scheduler.detect_conflicts() overlap detection and no-conflict cases, and Scheduler are all included in the test suite.build_daily_schedule() cross-pet coverage, empty-result edge case, priority preference, and time-budget enforcement.
These tests are important because the schedulers' value is totally dependent on their accuracy; if sorting or filtering silently yields incorrect results, the owner will receive a poor plan with no error message.

**b. Confidence**

I'm sure that the four algorithmic features are right for the cases that were tested. The 28 passing tests cover the main behaviors, including edge cases like finishing all tasks and having a budget that is too small for any task. There is a lot of uncertainty about how to find conflicts when tasks go past midnight or when some but not all tasks for the same pet are missing their due time. These are the edge cases that aren't tested. I'd also test that build_daily_schedule always breaks ties when two tasks have the same priority and due time if I had more time.

---

## 5. Reflection

**a. What went well**

The four classes' separation of concerns worked well throughout the project. I could write and test the scheduling logic without having to worry about the Streamlit UI because Scheduler only needs the Owner interface. When I linked them in app.py, the core classes didn't need to change much. That's what you get for spending time on the design before writing code.

**b. What you would improve**

The Streamlit UI keeps tasks as simple dictionaries and builds domain objects again every time a button is pressed. This works, but it feels fragile. If someone added a new Task attribute, they would have to change the dict schema and the app's reconstruction code.py. In the next version, I would look into using Streamlit's newer session state patterns or a lightweight serialization layer so that the UI always works directly with Task and Pet objects.

**c. Key takeaway**

Before I could write any logic, I had to design the class boundaries, which made me ask, "Who is responsible for this?" for each technique. Which class should be responsible for this behavior? proved to be more valuable than any single algorithm. All of Scheduler's methods became simpler when get_all_tasks() was transferred from Scheduler to Owner. Well-defined boundaries are more valuable than clever code.
