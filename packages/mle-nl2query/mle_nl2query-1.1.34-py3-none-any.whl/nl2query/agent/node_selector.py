from nl2query.agent.state import State
from nl2query.core.decorators import wrap_state_transition


@wrap_state_transition
def select_next_node_after_tables_selector(state: State):
    """Select next node after tables selector."""
    return "query_reframer_node" if state["query_reframer_yn"] else "intent_engine_node"


@wrap_state_transition
def select_next_node_after_query_reframer(state: State):
    """Select next node after query reframer."""
    return "intent_engine_node" if state["intent_yn"] else "query_builder_node"


@wrap_state_transition
def select_next_node_after_intent_engine(state: State):
    """Select next node after intent engine."""
    if state.get("proceed_to_query_builder_yn"):
        return "query_builder_node"
    return "query_builder_node"


@wrap_state_transition
def select_next_node_after_query_builder(state: State):
    """Select next node after query builder."""
    return "query_validator_node"


@wrap_state_transition
def select_next_node_after_query_validator(state: State):
    """Select next node after query corrector."""
    if state["query_executor_yn"]:
        return "query_executor_node"
    else:
        return "user_followup_query_node"


@wrap_state_transition
def select_next_node_after_query_executor(state: State):
    """Select next node after query executor"""
    return "user_followup_query_node"


@wrap_state_transition
def select_next_node_after_followup_query(state: State):
    if state["tables_selector_yn"]:
        return "tables_selector_node"
    elif state["query_reframer_yn"]:
        return "query_reframer_node"
    elif state["intent_yn"]:
        return "intent_engine_node"
    else:
        return "query_builder_node"
