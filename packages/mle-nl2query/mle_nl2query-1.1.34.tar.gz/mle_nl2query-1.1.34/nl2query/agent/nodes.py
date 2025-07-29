from loguru import logger

from nl2query.core.decorators import handle_exceptions


class StartNode:
    def __init__(self, config):
        self._config = config

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 0
            state["module_name"] = "start_node"
            state["conversation_messages"] = []
            state["errors"] = []
            state["query"] = state["query"]
            if not state["query"]:
                raise Exception("Error at StartNode: 'query'")

            state["user_message"] = []
            state["raw_messages"] = []
            state["messages"] = []
            state["config"] = {}
            state["info_message_to_user"] = {}
            state["proceed_to_query_reframer_yn"] = False
            state["metadata_json"] = {}
            state["regenerate_intent_yn"] = False
            state.update(self._config)
            return state
        except Exception as e:
            raise Exception(f"Error at StartNode: {e}")


class TableSelectorNode:
    def __init__(self, table_selector):
        self._table_selector = table_selector

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 1
            state["module_name"] = "table_selector_node"
            _, response = self._table_selector.run(state)
            state["selected_tables"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at TableSelectorNode: {e}")


class QueryReframerNode:
    def __init__(self, query_reframer):
        self._query_reframer = query_reframer

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 2
            state["module_name"] = "query_reframer_node"
            _, response = self._query_reframer.run(state)
            state["reframed_query"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryReframerNode: {e}")


class IntentEngineNode:
    def __init__(self, intent_engine):
        self._intent_engine = intent_engine

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 3
            state["module_name"] = "intent_engine_node"
            _, response = self._intent_engine.run(state)
            state["intent_json"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at IntentEngineNode: {e}")



class QueryBuilderNode:
    def __init__(self, query_builder):
        self._query_builder = query_builder

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 7
            state["module_name"] = "query_builder_node"
            state, response = self._query_builder.run(state)
            state["initial_query"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryBuilderNode: {e}")


class QueryValidatorNode:
    def __init__(self, query_validator):
        self._query_validator = query_validator

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 8
            state["module_name"] = "query_validator_node"
            _, response = self._query_validator.run(state)
            state["validated_query"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryValidatorNode: {e}")


class QueryExecutorNode:
    def __init__(self, query_executor):
        self._query_executor = query_executor

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 9
            state["module_name"] = "query_executor_node"
            _, response = self._query_executor.run(state)
            state["output_response"] = response
            return state
        except Exception as e:
            raise Exception(f"Error at QueryExecutorNode: {e}")


class UserFollowUpNode:
    def __init__(self):
        pass

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            state["state_id"] = 10
            state["module_name"] = "user_followup_query_node"
            state["proceed_to_query_builder_yn"] = False
            state["validated_query"] = None
            state["intent_json"] = None
            state["selected_tables"] = None
            return state
        except Exception as e:
            raise Exception(f"Error at UserFollowUpNode: {e}")


class LastNode:
    def __init__(self):
        pass

    @handle_exceptions
    def __call__(self, state, **kwargs):
        try:
            logger.info("I am here at last node.")
            state["state_id"] = -1
            state["module_name"] = "last_node"
            return state
        except Exception as e:
            raise Exception(f"Error at LastNode: {e}")
