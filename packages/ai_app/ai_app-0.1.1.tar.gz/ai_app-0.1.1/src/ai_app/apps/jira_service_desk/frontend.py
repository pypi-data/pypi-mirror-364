from typing import override

import gradio as gr
import langchain_core.language_models
import langchain_core.messages

from ai_app.apps.jira_service_desk.backend import Bot
from ai_app.config import get_config
from ai_app.core import BaseApp, Response, State
from ai_app.frontend import build_model_choice_dropdown


class App(BaseApp):
    name = "Jira service desk"
    requires_auth = False

    def __init__(self):
        self.bot = Bot()

    async def astream(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
    ):
        messages = state.messages + [message]
        async for response in self.bot.astream(model, messages, state=state):
            yield response

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks() as app:
            model_choice = model_choice or build_model_choice_dropdown()
            self.build_gradio_chat_interface(
                model_choice=model_choice,
                description="The chatbot will help the user find appropriate Jira request type.",
                examples=(
                    None
                    if get_config().is_prod
                    else [
                        ["I want to change my password"],
                        ["I need access to a database"],
                        ["I received a phishing email"],
                        ["A system requires additional processing resources"],
                    ]
                ),
            )

        return app
