# Same function, different answer

The [function mapping](matlab-vs-python.md) tells you which function replaces
which. It does not tell you whether the replacement returns the *same thing* —
and in a few places it does not.

This page collects the cases where the two implementations agree on the job but
differ in what they hand back, how they order it, or what they do to the model on
the way. It is deliberately short: a row is added only once the difference has
been confirmed in both sources, because a wrong entry here is worse than a
missing one.

!!! info "Not a complete list"
    Absence from this page is not a guarantee of identical behaviour. Where an
    exact answer matters — reproducing a published result, comparing two
    pipelines — see [what "identical results" means](parity.md).

## Duplicate reactions: gene associations are not merged

`contractModel` merges duplicate reactions **and their gene associations**: when
it collapses a set of duplicates it joins the distinct `grRules` with `or`, so
every gene that pointed at any of the duplicates still points at the survivor.

`remove_duplicate_reactions` keeps one reaction of each duplicate set and removes
the rest, without merging gene associations. A gene that was associated *only*
with a removed duplicate is no longer associated with anything.

The stoichiometric network is the same either way; the gene–reaction mapping is
not. If you are contracting a draft assembled from several templates — where the
same reaction commonly arrives with different gene associations — check the GPRs
of the survivors afterwards.

## Metabolic tasks: same verdicts, very different cost

`checkTasks` rebuilds the working model from the original for each task.
`check_tasks` instead applies each task's constraints to one model inside a
`with model:` block and reverts them afterwards, restoring by hand the one kind
of edit cobra's context manager does not track (direct mass-balance bound
changes).

The pass/fail verdicts are the same. The cost is not: at genome scale the copy
dominates the MATLAB runtime, which is why the Python version reuses a single
model. Worth knowing if you are comparing runtimes rather than results.

## Gap-filling: one function becomes three

`fillGaps` covers several jobs behind one interface. raven-toolbox splits them,
so porting a `fillGaps` call means choosing:

| What you were doing | Use |
|---|---|
| Connecting blocked reactions against template models | `connect_blocked_reactions` |
| Fast LP-based filling of a large candidate set | `fill_gaps_fast_lp` |
| MILP filling with explicit weights | `fill_gaps_kumar_milp` |
| Only *finding* the gaps (`canProduce`, `checkProduction`, `getAllSubGraphs`, `haveFlux`) | `analyse_topology` |

The choice changes both the reaction set added and the runtime — they are
different algorithms, not one algorithm behind three names.

## Anything solved by MILP

INIT and ftINIT extraction, gap-filling, and compartment assignment all solve
mixed-integer problems that routinely have **several optima of equal objective
value**. Two runs can return different reaction sets and both be correct — across
languages, across solvers, and in some configurations across runs of the same
solver.

Do not compare these outputs for identity. Compare them for overlap, and expect
a band rather than a number; see [parity](parity.md).

## A note on elemental balance

Both `getElementalBalance` and `get_elemental_balance` grade each reaction rather
than returning a bare balanced/unbalanced flag: a reaction whose metabolites lack
formulas is reported as *unknown*, not as balanced. The two agree.

The distinction matters when moving to plain cobrapy, whose `check_mass_balance`
does not make it — which is the reason raven-toolbox keeps its own function
instead of delegating.
