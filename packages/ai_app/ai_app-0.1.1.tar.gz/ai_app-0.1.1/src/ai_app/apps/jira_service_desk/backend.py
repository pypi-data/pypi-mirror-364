import inspect
import textwrap

import cachetools.func
import langchain_core.messages
import langgraph.prebuilt
import pydantic

from ai_app.ai_utils import PreModelHook, astream_response_messages
from ai_app.apps.jira_service_desk.data import (
    JiraRequestPrimaryKey,
    get_saved_request_type_primary_keys,
)
from ai_app.apps.jira_service_desk.tools import (
    build_url_for_jira_request_type,
    fetch_detailed_jira_request_type_guide,
    fetch_jira_request_type_guides_closest_to_user_query,
)
from ai_app.config import get_ai_postgres_engine
from ai_app.core import Response, State
from ai_app.frontend import get_generating_text_span
from ai_app.tools import (
    InfoSecUserReminder,
    build_structured_response_tool,
    extract_tool_artifacts_from_agent_response,
    get_structured_output_from_agent_response,
    report_disclosure_of_sensitive_information,
    report_feedback,
)


def get_system_prompt() -> str:
    system_prompt = textwrap.dedent(f"""
        ### Role
        You are a Jira service desk expert in a bank. Your goal is to help employees find the most 
        appropriate Jira request type for their problem.

        ### Language instruction
        - Your primary instruction, above all else, is to detect the language of the user's very 
        last message (Azerbaijani, English, or Russian) and ALWAYS respond in that exact language.
        - DO NOT deviate from this rule, even if other context suggests a different language might be helpful.

        ### Steps
        - Use the RAG retriever "{fetch_jira_request_type_guides_closest_to_user_query.name}" tool to find relevant 
        Jira request types.
        - If there is an appropriate request type among those fetched based on the user's problem and use case,
        use the "{fetch_detailed_jira_request_type_guide.name}" tool to get more information about it.
        - If based on the retrieved information the request type is highly relevant to the user's problem:
            - Provide the non-prefilled request type URL from the "{fetch_detailed_jira_request_type_guide.name}" tool output.
            - Briefly explain why the request type fits the user's situation and how the request type is usually handled.
            - Explain how the user may try to resolve the issue by themselves.
            - What information is needed to create the request.
        If the request type is not sufficiently relevant, ask clarifying questions to understand the user's problem 
        and rerun the "{fetch_jira_request_type_guides_closest_to_user_query.name}" tool based on the gathered 
        information.
        - After finding a relevant request type, collect from the user the information needed to create 
        a prefilled URL for the suggested request type  via the "{build_url_for_jira_request_type.name}" 
        tool and provide it to the user. Focus on required fields that can be passed as URL parameters.

        ### Notes
        - Proactively ask for user's feedback and use the "{report_feedback.name}" tool to report it.
        - Use the "{build_structured_response_tool(None).name}" tool to generate the message for the user.
    """)  # noqa: E501
    return system_prompt


def build_prompts() -> list[langchain_core.messages.BaseMessage]:
    system_prompt = get_system_prompt()
    prompts = [
        langchain_core.messages.SystemMessage(system_prompt),
    ]
    return prompts


class BotResponse(pydantic.BaseModel):
    last_user_message_language: str = pydantic.Field(
        description=inspect.cleandoc("""
            The language of the last user message, which the bot should also use for its own 
            response.
        """),
    )
    content: str = pydantic.Field(description="The message content that the user will see.")


@cachetools.func.ttl_cache(ttl=60)
def get_cached_saved_request_type_primary_keys() -> set[JiraRequestPrimaryKey]:
    return get_saved_request_type_primary_keys(get_ai_postgres_engine())


class Bot:
    async def astream(self, model, messages, state: State | None = None):
        agent = langgraph.prebuilt.create_react_agent(
            model,
            prompt=get_system_prompt(),
            pre_model_hook=PreModelHook(model=model),
            tools=[
                fetch_jira_request_type_guides_closest_to_user_query,
                fetch_detailed_jira_request_type_guide,
                build_url_for_jira_request_type,
                # report_disclosure_of_sensitive_information,
                report_feedback,
                build_structured_response_tool(BotResponse),
            ],
            response_format=BotResponse,
        )
        response = None
        async for response in astream_response_messages(
            agent, messages, stream_ai_tokens=True, with_spinner=False
        ):
            yield Response(
                content=response.formatted_response + get_generating_text_span(),
                messages=response.state["messages"],
            )

        if not response:
            return

        bot_response = get_structured_output_from_agent_response(response.state)
        yield Response(
            content=response.formatted_response + bot_response.content,
            messages=response.state["messages"],
            content_for_langsmith=bot_response.content,
        )

    async def respond(self, model, messages, state: State | None = None) -> Response:
        response = Response(content="")
        async for response in self.astream(model, messages, state):
            pass

        return response
