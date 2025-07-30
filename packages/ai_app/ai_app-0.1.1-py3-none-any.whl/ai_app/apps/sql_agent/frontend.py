import gradio as gr

from ai_app.config import get_config
from ai_app.core import BaseApp
from ai_app.frontend import build_model_choice_dropdown

from .backend import Bot


class App(BaseApp):
    name = "SQL agent"
    requires_auth = True

    def __init__(self):
        self.bot = Bot()
        self.respond = self.bot.respond

    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks(fill_height=True) as app:
            # SQL queries are hard, need a powerful model.
            model_choice = model_choice or build_model_choice_dropdown(models=["gpt-4.1"])
            connection_context_choice = gr.Dropdown(
                choices=sorted(get_config().sql_connection_contexts),
                label="Connection",
            )
            self.build_gradio_chat_interface(
                model_choice=model_choice,
                additional_inputs=[connection_context_choice],
                description=(
                    "The chatbot will help you with SQL queries. Note that due to difficulty of the task, "
                    "it is recommended to use a powerful model."
                ),
                examples=[  # Todo: set connection context for each example.
                    [
                        "What kind of tables do you see?",
                    ],
                    [
                        "Provide details about which structures are struggling with budget, and which ones have a surplus."
                    ],
                    [
                        "Describe average employee tenure by tribe.",
                    ],
                ],
            )

        return app
