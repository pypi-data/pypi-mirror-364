import textwrap
from typing import Iterable, override

import langchain.chat_models
import langchain.hub
import langchain.tools
import langchain_community.agent_toolkits.sql.toolkit
import langchain_community.utilities
import sqlalchemy as sa

from .base import BaseToolkit


class SqlToolkit(BaseToolkit):
    def __init__(
        self,
        engine: sa.Engine,
        schema: str | None = None,
        include_tables: Iterable[str] | None = None,
        sql_checker_model: langchain.chat_models.base.BaseChatModel | None = None,
        top_k_query_rows: int = 20,
        prompt: str | None = None,
    ):
        self.database = langchain_community.utilities.SQLDatabase(
            engine=engine,
            schema=schema,
            include_tables=include_tables,
            sample_rows_in_table_info=top_k_query_rows,
            lazy_table_reflection=True,
        )
        if sql_checker_model:
            self.toolkit = langchain_community.agent_toolkits.sql.toolkit.SQLDatabaseToolkit(
                db=self.database,
                llm=sql_checker_model,
            )
        else:
            self.toolkit = None

        if not prompt:
            # prompt_template = langchain.hub.pull("langchain-ai/sql-agent-system-prompt")
            # prompt = prompt_template.format(dialect=self.database.dialect, top_k=top_k_query_rows)
            prompt = f"""
                You are an agent designed to interact with a SQL database.
                Given an input question, create a syntactically correct {self.database.dialect} query to run, then look 
                at the results of the query and return the answer.
                Unless the user specifies a specific number of examples they wish to obtain, always limit your query to 
                at most {top_k_query_rows} results.
                You can order the results by a relevant column to return the most interesting examples in the database.
                Never query for all the columns from a specific table, only ask for the relevant columns given the question.
                You have access to tools for interacting with the database.
                Only use the below tools. Only use the information returned by the below tools to construct your final answer.
                You MUST double check your query before executing it. If you get an error while executing a query, rewrite 
                the query and try again.

                DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

                To start you should ALWAYS look at the tables in the database to see what you can query.
                Do NOT skip this step.
                Then you should query the schema of the most relevant tables.

                When referring to table columns, always quote them with double quotes, like "Metric" or "Date".
            """  # noqa: E501

        self.prompt = textwrap.dedent(prompt)

    @override
    def get_tools(
        self, sql_checker_model: langchain.chat_models.base.BaseChatModel | None = None
    ) -> list[langchain.tools.BaseTool]:
        if sql_checker_model:
            toolkit = langchain_community.agent_toolkits.sql.toolkit.SQLDatabaseToolkit(
                db=self.database,
                llm=sql_checker_model,
            )
        else:
            toolkit = self.toolkit

        if not toolkit:
            raise ValueError(
                "An SQL checker model should be provided either during toolkit initialization "
                "or get_tools call."
            )

        tools = toolkit.get_tools()
        return tools
