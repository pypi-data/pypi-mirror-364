import langgraph.prebuilt

from ai_app.ai_utils import PreModelHook
from ai_app.config import get_sql_toolkit
from ai_app.core import State


class Bot:
    async def respond(
        self,
        model,
        model_input,
        state: State,
        connection_context_name: str,
    ) -> str:
        toolkit = get_sql_toolkit(connection_context_name)
        agent = langgraph.prebuilt.create_react_agent(
            model=model,
            pre_model_hook=PreModelHook(model),
            tools=toolkit.get_tools(),
            prompt=toolkit.prompt,
        )
        response: dict = await agent.ainvoke({"messages": model_input})
        response_message = response["messages"][-1].content
        return response_message
