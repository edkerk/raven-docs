# 13. Gap-filling

A draft model always has holes: reactions that cannot carry flux because
something upstream is missing, metabolites nothing produces, a biomass component
the network cannot make. Gap-filling adds reactions from a template until the
holes close — and the judgement is in deciding which holes are worth closing.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `gapReport` | `check_model`, `analyse_topology` | find the holes first |
| `fillGaps` | `connect_blocked_reactions` | add template reactions so blocked reactions can carry flux |
| `gapFillFastLP` | `fill_gaps_fast_lp` | the LP formulation (fastGapFill / swiftGapFill) |
| `gapFillMILP` | `fill_gaps_kumar_milp` | the MILP formulation, when the LP is not enough |
| `gapFillTopological` | `analyse_topology` | connectivity, without solving an LP |
| `fitTasks` | `fill_tasks` | fill until a task passes — see [12. Metabolic tasks](tasks.md) |

## Setup

A gap-filling example needs a draft with holes and a template to fill them from.
`smallYeast.yml` serves as both: open its medium, take a copy, and remove a
reaction. What gap-filling then puts back is checkable by eye — it should be the
reaction that was removed.

=== "MATLAB"

    ```matlab
    template = readYAMLmodel('smallYeast.yml');
    template = setParam(template, 'ub', {'glcIN', 'o2IN'}, [1 1000]);

    draft = removeReactions(template, {'ADH1'});   % alcohol dehydrogenase
    draft.id = 'draft';   % fillGaps refuses a template sharing the model's id
    fprintf('draft %d rxns, template %d rxns\n', numel(draft.rxns), numel(template.rxns));
    ```

    ```text title="Output"
    draft 52 rxns, template 53 rxns
    ```

=== "Python"

    ```python
    import cobra
    from raven_toolbox.io import read_yaml_model

    cobra.Configuration().processes = 1     # FVA below spawns workers otherwise

    template = read_yaml_model("smallYeast.yml")
    template.reactions.get_by_id("glcIN").upper_bound = 1.0
    template.reactions.get_by_id("o2IN").upper_bound = 1000.0

    draft = template.copy()
    draft.remove_reactions([draft.reactions.get_by_id("ADH1")])   # alcohol dehydrogenase
    print(f"draft {len(draft.reactions)} rxns, template {len(template.reactions)} rxns")
    ```

    ```text title="Output"
    draft 52 rxns, template 53 rxns
    ```

    Note the medium. Shipped shut, `smallYeast` has **51 of its 53 reactions
    blocked** — not because it has gaps, but because nothing can get in. Gap-fill
    a model in that state and you are asking the wrong question entirely.

## 13.1 Find the holes before filling them

Gap-filling without looking first is how a model acquires reactions nobody can
justify. Start from what cannot carry flux.

=== "MATLAB"

    ```matlab
    canCarry = haveFlux(draft);
    fprintf('%d of %d reactions can carry flux\n', sum(canCarry), numel(draft.rxns));
    ```

    ```text title="Output"
    50 of 52 reactions can carry flux
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import find_blocked_reactions

    blocked = find_blocked_reactions(draft)
    print(f"{len(blocked)} of {len(draft.reactions)} reactions are blocked")
    print(sorted(blocked)[:5])
    ```

    ```text title="Output"
    2 of 52 reactions are blocked
    ['ethIN', 'ethOUT']
    ```

## 13.2 Connectivity gap-filling

The question here is structural: which template reactions, added to the draft,
would let a blocked reaction carry flux at all? No objective, no growth — just
connectivity.

=== "MATLAB"

    <!-- run-examples: needs-gurobi -->

    ```matlab
    setRavenSolver('gurobi');   % fillGaps is a MILP
    [newConnected, cannotConnect, addedRxns] = fillGaps(draft, {template}, ...
        'allowNetProduction', true, 'useModelConstraints', false);
    fprintf('%d added: %s\n', numel(addedRxns), strjoin(addedRxns, ', '));
    ```

    ```text title="Output"
    1 added: ADH1
    ```

=== "Python"

    ```python
    from raven_toolbox.gapfilling import connect_blocked_reactions

    result = connect_blocked_reactions(draft, template, allow_net_production=True)
    print(f"{len(result.added_reactions)} added: "
          f"{', '.join(sorted(result.added_reactions))}")
    ```

    ```text title="Output"
    1 added: ADH1
    ```

    The reaction that comes back is the one that was taken out — in both
    toolboxes. That identity is the result worth reporting. `fillGaps` also
    returns counts of *newly connected* and *still unconnectable* reactions, and
    those are not stable: it solves a MILP, several solutions are equally
    optimal, and which one comes back can change with the machine or the thread
    count. Two CI runs on identical input reported 11 and 9 newly connected.

    **The two are not the same algorithm.** RAVEN's `fillGaps` solves a MILP, so
    it needs Gurobi and reports `glpk is not suitable for solving MILPs`
    otherwise. raven-toolbox's `connect_blocked_reactions` is an LP and runs on
    the GLPK that ships with cobrapy.

    `allow_net_production` decides how strict the test is. A reaction can be
    blocked because a substrate is unavailable *or* because a product has nowhere
    to go; with net production allowed, only the first counts. Turning it off asks
    the harder question and usually adds more reactions.

## 13.3 The LP formulation

Note the argument: `fillGaps` takes a **cell array** of template models, while
`gapFillFastLP` and `gapFillMILP` take a **single struct**. Passing a cell to
these two fails with `Dot indexing is not supported for variables of this
type`.

`fill_gaps_fast_lp` (fastGapFill, and its `swift` variant) solves one LP per
blocked reaction: activate this reaction using as few template reactions as
possible. It is the fast option, and the one to reach for on a genome-scale
draft.

=== "MATLAB"

    ```matlab
    [addedRxns, outModel] = gapFillFastLP(draft, template);
    fprintf('%d reactions added\n', numel(addedRxns));
    ```

    ```text title="Output"
    gapFillFastLP: 2 blocked reaction(s) found in draft model.
    gapFillFastLP: 1 reaction(s) cannot be rescued by the universal database.
    gapFillFastLP: 1/2 blocked reaction(s) are rescuable; running fast...
    gapFillFastLP: added 8 reaction(s) from universal database.
    8 reactions added
    ```

=== "Python"

    ```python
    from raven_toolbox.gapfilling import fill_gaps_fast_lp

    result = fill_gaps_fast_lp(draft, template, verbose=False)
    print(f"{len(result.added_reactions)} reactions added")
    ```

    ```text title="Output"
    1 reactions added
    ```

## 13.4 The MILP formulation

<!-- run-examples: needs-gurobi -->

When the LP relaxation adds too much — or you want the provably smallest set —
the mixed-integer formulation is the alternative. It needs a MILP solver, and it
is slower by a wide margin on anything genome-scale.

=== "MATLAB"

    ```matlab
    setRavenSolver('gurobi');
    params.OutputFlag = 0;   % the solver log is long, and machine-specific
    [addedRxns, reversedRxns, outModel] = gapFillMILP(draft, template, ...
        'params', params);
    fprintf('%d reactions added\n', numel(addedRxns));
    ```

    ```text title="Output"
    gapFillMILP: merged model has 52 mets, 105 rxns (52 draft, 52 universal).
    gapFillMILP: 35 reversal candidates, 52 database candidates.
    gapFillMILP: setting minGrowth = 0.02443 (10% of max 0.2443).
    gapFillMILP: solving MILP (192 vars, 87 binary, 192 constraints)...
    gapFillMILP: reversed 0 draft reaction(s), added 0 universal reaction(s).
    0 reactions added
    ```

=== "Python"

    ```python
    from raven_toolbox.gapfilling import fill_gaps_kumar_milp

    draft.solver = "gurobi"
    result = fill_gaps_kumar_milp(draft, template)
    print(f"{len(result.added_reactions)} reactions added")
    ```

    ```text title="Output"
    fill_gaps_kumar_milp: merged model has 53 reactions (52 draft, 1 template).
    fill_gaps_kumar_milp: setting min_growth = 0.01222 (10% of FBA max 0.1222).
    fill_gaps_kumar_milp: solving MILP (35 reversal, 1 database candidates)...
    fill_gaps_kumar_milp: reversed 0 reaction(s), added 0 template reaction(s).
    0 reactions added
    ```

## 13.5 Filling towards a task, not a hole

Connectivity gap-filling asks "can this reaction carry flux?". The other question
— "can the model still do *this*?" — is answered by filling against a task list,
which is usually what you actually want: a model that grows, or that produces a
particular compound.

=== "MATLAB"

    ```matlab
    tasks = parseTaskList('tasks.txt');
    [outModel, addedRxns] = fitTasks(draft, template, [], true, [], tasks);
    ```

    ```text title="Output"
    [Warning: Exchange metabolites should normally not be removed from the model when using checkTasks. Inputs and outputs are defined in the task file instead. Use importModel(file,false) to import a model with exchange metabolites remaining]
    [GROWTH] Growth on glucose: Added 0 reaction(s), 0 reactions added in total
    [Warning: "[LEAK] Biomass from nothing" is set as SHOULD FAIL. Such tasks cannot be modelled using this approach and the task is therefore ignored\n]
    ```

=== "Python"

    ```python
    from raven_toolbox.init import fill_tasks
    ```

    See [12. Metabolic tasks](tasks.md) for the task list itself, and
    [10. Context-specific models](init.md) for `fill_tasks` in its usual role —
    repairing a model that ftINIT has just cut down.

!!! warning "What can go wrong"
    - **Identifiers that do not line up.** Gap-filling can only add what it can
      match. Two models built from different databases share almost no metabolite
      ids, and the result is a gap-filler that adds nothing, or adds duplicates.
    - **Filling every gap.** Some blocked reactions are blocked because the
      organism genuinely cannot do them. Each addition is a claim about biology,
      and `fillGaps` will happily make hundreds of them.
    - **Net production hiding the problem.** `allowNetProduction` makes more
      reactions look connectable by ignoring where the products go. Useful early,
      misleading later.
    - **MILP on a genome-scale model.** Expect it to be slow, and give it a time
      limit — see [6. Solvers and configuration](solvers.md).

## See also

- [9. Quality control](quality-control.md) — finding the holes, and deciding
  which matter.
- [12. Metabolic tasks](tasks.md) — the other way to say what the model must do.
- [3. Reading and writing models](io.md) — saving the filled model with a record
  of what was added.
