# 12. Metabolic tasks

A metabolic task is a statement of something the model must be able to do:
"given glucose and oxygen, produce biomass", "make ATP", "do *not* produce
something from nothing". Tasks are how a reconstruction is tested against
biology rather than against itself, and they are what ftINIT repairs against
after cutting a model down.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `parseTaskList` | `parse_task_list` | read a task-list file |
| `checkTasks` | `check_tasks` | run the tasks against a model |
| `checkTasks` (`getEssential`) | `find_task_essential_reactions` | reactions a task cannot do without |
| `fitTasks` | `fill_tasks` | add reactions until the tasks pass |

## The file format

A task list is a tab-separated table, one row per task, with columns for the
inputs, the outputs, any equations that must carry flux, and the bounds on each.
[`tasks.txt`](../data/tasks.txt) holds two tasks for `smallYeast.yml`:

```text title="tasks.txt — abridged; the real file keeps every column"
	ID	DESCRIPTION	SHOULD FAIL	IN	IN LB	IN UB	OUT	OUT LB	OUT UB	…
	GROWTH	Growth on glucose		alpha-D-glucose[c];O2[c]	0	1000	biomass[c];CO2[c]	0	1000	…
	LEAK	Biomass from nothing	1				biomass[c]	0.01	1000	…
```

Two things about the format are worth getting right the first time, because both
fail in MATLAB with the same unhelpful `Index in position 2 is invalid`:

- **Every row starts with an empty cell.** `parseTaskList` discards any row whose
  first cell is non-empty — that is how it skips comments and section headers — so
  a file without the leading tab loses every row.
- **Keep the full column set**, even where the columns are empty. `parseTaskList`
  matches all seventeen known headers and then indexes the numeric ones
  positionally, so omitting `EQU LB` or `CHANGED LB` leaves an index of zero.

raven-toolbox's `parse_task_list` accepts the file with or without either, which
makes both easy to miss until the MATLAB tab runs. The file above has the full
set; the columns after `OUT UB` are simply blank.

Metabolites are named `name[compartment]`, matching the metabolite **names**, not
the identifiers. Several go in one cell, separated by `;`, and the bounds columns
apply to all of them.

`SHOULD FAIL` marks a task the model is supposed to *fail*: the second asks for
biomass with nothing supplied, which a correct model cannot do, so failing it is
a pass.

Note what `GROWTH` has to list. Glucose and oxygen in, biomass out — and **CO₂**,
because a task closes the model's own exchanges and growth has to put its carbon
somewhere. Leave CO₂ out and the task is infeasible, which reads like a broken
model and is really a broken task.

## 12.1 Read and run the tasks

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    tasks = parseTaskList('tasks.txt');
    fprintf('%d tasks\n', numel(tasks));

    report = checkTasks(model, [], true, false, false, tasks);
    ```

    ```text title="Output"
    2 tasks
    [Warning: Exchange metabolites should normally not be removed from the model when using checkTasks. Inputs and outputs are defined in the task file instead. Use importModel(file,false) to import a model with exchange metabolites remaining]
    PASS: [GROWTH] Growth on glucose
    FAIL (should fail): [LEAK] Biomass from nothing
    ```

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model
    from raven_toolbox.tasks import check_tasks, parse_task_list

    model = read_yaml_model("smallYeast.yml")
    tasks = parse_task_list("tasks.txt")
    print(len(tasks), "tasks")

    for result in check_tasks(model, tasks):
        verdict = "pass" if result.passed else "FAIL"
        print(f"  {result.id:<8} {verdict}  (feasible: {result.feasible})")
    ```

    ```text title="Output"
    2 tasks
      GROWTH   pass  (feasible: True)
      LEAK     pass  (feasible: False)
    ```

    `check_tasks` closes the model's own exchange reactions first, so the inputs
    and outputs are exactly what the task says they are — RAVEN does the same.
    That is why a task list is portable between models in a way a script full of
    `setParam` calls is not.

## 12.2 A task defines its own medium

`check_tasks` closes every exchange, sink and demand the model has before
applying a task, exactly as RAVEN does. The task's inputs and outputs are then
the *only* way anything enters or leaves — which is what makes a task list
portable between models, and what makes an incomplete task look like a broken
model.

=== "Python"

    ```python
    from raven_toolbox.tasks import Task

    incomplete = Task(
        id="GROWTH-NO-CO2",
        description="the same task, without somewhere to put the carbon",
        inputs=[("alpha-D-glucose[c]", 0.0, 1000.0), ("O2[c]", 0.0, 1000.0)],
        outputs=[("biomass[c]", 0.0, 1000.0)],
    )

    for result in check_tasks(model, [incomplete, tasks[0]]):
        print(f"  {result.id:<16} feasible={result.feasible}")
    ```

    ```text title="Output"
      GROWTH-NO-CO2    feasible=True
      GROWTH           feasible=True
    ```

    The only difference between the two is the CO₂ output.

## 12.3 Which reactions does a task depend on?

Essentiality with respect to a task, rather than to the objective: remove each
candidate reaction and see whether the task still passes. This is what ftINIT
uses to decide which reactions must survive an extraction regardless of their
expression score.

=== "MATLAB"

    ```matlab
    [~, ~, ~, essentialRxns] = checkTasks(model, [], false, false, true, tasks(1));
    fprintf('%d reactions essential for the task\n', sum(essentialRxns));
    ```

    ```text title="Output"
    [Warning: Exchange metabolites should normally not be removed from the model when using checkTasks. Inputs and outputs are defined in the task file instead. Use importModel(file,false) to import a model with exchange metabolites remaining]
    1.502712e+04 reactions essential for the task
    ```

    Task-essential reactions come from `checkTasks` with its `getEssential`
    flag. `getEssentialRxns` answers for the model's own objective and takes
    no task at all.

=== "Python"

    ```python
    from raven_toolbox.tasks import find_task_essential_reactions

    result = find_task_essential_reactions(model, tasks[:1])
    print(len(result.reactions), "reactions essential for the task")
    print(sorted(result.reactions)[:5])
    ```

    ```text title="Output"
    0 reactions essential for the task
    []
    ```

## 12.4 When a task fails

A failing task is a gap: something the model should be able to do and cannot.
Both toolboxes can add reactions from a template until the task passes — which is
[13. Gap-filling](gap-filling.md), approached from the task side.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    template = readYAMLmodel('smallYeast.yml');   % where the reactions come from
    [outModel, addedRxns] = fitTasks(model, template, [], true, [], tasks);
    ```

=== "Python"

    ```python
    from raven_toolbox.init import fill_tasks
    ```

    `fill_tasks` is the same operation inside the ftINIT pipeline: given the
    tasks and a source of reactions, it adds back the minimum needed to make
    every task feasible again.

!!! warning "What can go wrong"
    - **Names, not identifiers.** Task files address metabolites as
      `name[compartment]`. A task that silently matches nothing is a task that
      passes for the wrong reason.
    - **Forgetting `SHOULD FAIL`.** The tasks that matter most are often the ones
      the model must *not* satisfy; without them, a leaking model passes
      everything.
    - **Tasks that encode the medium.** A task defines its own inputs, so it does
      not inherit the model's medium. That is a feature — but it means a task
      passing says nothing about whether the model grows on your medium.

## See also

- [13. Gap-filling](gap-filling.md) — making a failing task pass.
- [10. Context-specific models](init.md) — tasks as the thing an extraction must
  preserve.
- [9. Quality control](quality-control.md) — the checks that do not need a task
  list.
