"""workflow_mri.agents

Agent orchestration: ingest -> graph -> risk -> recommender -> simulate -> (enrich) ->
assemble -> critic. Runs as a LangGraph StateGraph when available, else a deterministic
sequential runner over the same nodes. Every node emits an AuditEvent.
"""

from workflow_mri.agents.orchestrator import orchestrate

__all__ = ["orchestrate"]
