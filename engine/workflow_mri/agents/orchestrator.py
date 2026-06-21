"""Agent orchestration.

Wires the stage nodes (+ critic) into a graph and runs them. Uses LangGraph's StateGraph
when it's installed; otherwise a deterministic sequential runner executes the exact same
nodes. Either way the result is identical and the audit trail is populated — so the pipeline
stays offline-reproducible (no LangGraph, no LLM required) while presenting a real
multi-agent structure when the dependency is present.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from workflow_mri.agents.critic import critic_node
from workflow_mri.agents.nodes import (
    assemble_node,
    enrich_node,
    graph_node,
    ingest_node,
    recommend_node,
    risk_node,
    simulate_node,
)
from workflow_mri.schema import Bundle

State = dict[str, Any]

# ordered pipeline of (name, fn)
PIPELINE: list[tuple[str, Callable[[State], State]]] = [
    ("ingest", ingest_node),
    ("graph", graph_node),
    ("risk", risk_node),
    ("recommend", recommend_node),
    ("simulate", simulate_node),
    ("enrich", enrich_node),
    ("assemble", assemble_node),
    ("critic", critic_node),
]


def _run_sequential(state: State) -> State:
    """Deterministic fallback runner — last-write-wins state, same as LangGraph here."""
    for _name, fn in PIPELINE:
        state = {**state, **fn(state)}
    return state


def _run_langgraph(state: State) -> State:
    """Real LangGraph StateGraph over the same nodes; only used if langgraph is importable."""
    from langgraph.graph import END, START, StateGraph  # type: ignore

    g: StateGraph = StateGraph(dict)
    for name, fn in PIPELINE:
        # return the full merged state so untyped-dict channels keep keys a node didn't write
        g.add_node(name, (lambda s, _fn=fn: {**s, **_fn(s)}))
    g.add_edge(START, PIPELINE[0][0])
    for (prev, _), (nxt, _) in zip(PIPELINE, PIPELINE[1:]):
        g.add_edge(prev, nxt)
    g.add_edge(PIPELINE[-1][0], END)
    return g.compile().invoke(state)


def orchestrate(
    samples_dir: Path,
    *,
    run_id: str,
    enrich: bool = False,
    llm_backend: str | None = None,
    use_langgraph: bool | None = None,
) -> Bundle:
    state: State = {
        "samples_dir": samples_dir,
        "run_id": run_id,
        "enrich": enrich,
        "llm_backend": llm_backend or "ollama",
        "now": datetime.now().astimezone().replace(microsecond=0),
        "audit": [],
    }

    want_lg = use_langgraph
    if want_lg is None:
        try:
            import langgraph  # noqa: F401
            want_lg = True
        except ImportError:
            want_lg = False

    final = _run_langgraph(state) if want_lg else _run_sequential(state)
    return final["bundle"]
