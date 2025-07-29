import time

from loguru import logger
from langchain_core.prompts import ChatPromptTemplate

from nl2query.core.base_module import BaseModule
from nl2query.query_validator.schema import QueryValidatorSchema
from nl2query.core.llm_models import get_llm
from nl2query.query_validator.prompts import get_query_validator_prompt


class QueryValidator(BaseModule):
    """Concrete implementation of BaseModule for intent detection"""

    def __init__(
        self,
        system_prompt: str = None,
        pydantic_class: QueryValidatorSchema = QueryValidatorSchema,
        prompt: str = None,
        examples: str = None,
        schema_mapping_path: str = "data/input/schema_mapping.json",
        *args,
        **kwargs,
    ):
        super().__init__(
            system_prompt=system_prompt,
            pydantic_class=pydantic_class,
            examples=examples,
            *args,
            **kwargs,
        )
        self.prompt = prompt
        self.examples = examples
        self.pydantic_class = pydantic_class
        self.schema_mapping_path = schema_mapping_path

        logger.info(f"Initialized IntentEngine with prompt: {system_prompt}")

    def run(self, state):
        """Process the state and return intent JSON"""
        try:
            start_time = time.time()
            model_type = state.get("model_type", "openai")
            model_name = state.get("model_name", "gpt-4o")
            temperature = state.get("temperature", 0.01)

            prompt = get_query_validator_prompt(self.prompt)

            prompt = ChatPromptTemplate.from_messages(
                [("system", prompt), ("human", "{initial_query}")]
            )

            llm = get_llm(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
            )
            structured_llm = llm.with_structured_output(self.pydantic_class)
            few_shot_structured_llm = prompt | structured_llm
            initial_query = state["initial_query"]
            response = few_shot_structured_llm.invoke({"initial_query": initial_query})
            validated_query = response.dict()["validated_query"]

            state["validated_query"] = validated_query

            logger.info(f"Query after validation: {validated_query}")
            state["raw_messages"].append(
                {"role": "validated_query", "content": response}
            )

            system_message = {"role": "ai", "content": validated_query}
            state["messages"].append(system_message)

            end_time = time.time()
            response_time = end_time - start_time
            state["query_validator_response_time"] = response_time
            logger.info(f"Query validator processing time: {response_time}")

            return state, validated_query

        except Exception as e:
            logger.error(f"Error processing intent: {e}")
            raise
