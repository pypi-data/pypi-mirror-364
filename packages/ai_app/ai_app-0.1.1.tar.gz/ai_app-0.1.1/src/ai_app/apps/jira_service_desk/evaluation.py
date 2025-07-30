import datetime
import random
import textwrap
import warnings

import langchain_core
import langsmith.evaluation
import langsmith.schemas
import numpy as np
import prefect
import pydantic
import tqdm.auto

from ai_app.ai_utils import to_json_llm_input
from ai_app.apps.jira_service_desk.backend import Bot, get_system_prompt
from ai_app.apps.jira_service_desk.data import (
    JiraRequest,
    JiraRequestPrimaryKey,
    ManualJiraRequestGuide,
    fetch_use_case_guides_for_requests,
    get_saved_request_type_primary_keys,
)
from ai_app.apps.jira_service_desk.preparation import generate_requests
from ai_app.config import get_ai_postgres_engine, get_chat_model, get_judge_model_names
from ai_app.core import Response
from ai_app.external.atlassian import build_issue_url
from ai_app.utils import wrap_with_xml_tag


class JiraServiceDeskBotEvaluationExample(pydantic.BaseModel):
    generated_user_query: str
    issue_url: str
    model_used_for_generation: str
    request_type_primary_key: JiraRequestPrimaryKey
    issue_key: str


def try_create_evaluation_example_from_latest_resolved_request(
    request_primary_key: JiraRequestPrimaryKey,
) -> JiraServiceDeskBotEvaluationExample | None:
    requests = list(generate_requests(**request_primary_key.model_dump(), limit_requests=1))
    if len(requests) != 1:
        warnings.warn(
            f"Failed to fetch a singular request for primary key {request_primary_key}, "
            f"instead fetched {len(requests)} requests"
        )
        return

    request = requests[0]
    issue_key = request["Issue key"]
    judge_model_name = random.choice(get_judge_model_names())
    model = get_chat_model(judge_model_name)
    system_prompt = textwrap.dedent("""
        We are evaluating a Jira service desk support bot designed to help users find the correct 
        request type and assist with creating and filling out Jira requests. To test the bot, we 
        need realistic synthetic user messages that could have been sent to the bot before a request
        was created.

        **Your task**:

        - Review the provided resolved Jira request in JSON format.
        - Generate a message that a user might have sent to the bot before submitting this request.
        - The message should be natural and reflect how real users communicate: it may contain 
            errors, typos, be brief or incomplete, and written in a hurry.
        - Assume the user knows they are chatting with a bot, so the message is likely direct and 
            to the point, not polite or formal.
        - The message should be in the same language as the request description or comments.
        
        **Produce a single, realistic user message that could have initiated the provided Jira 
        request.**
    """)
    response = model.invoke(
        [
            langchain_core.messages.SystemMessage(system_prompt),
            langchain_core.messages.HumanMessage(to_json_llm_input(request)),
        ]
    )
    example = JiraServiceDeskBotEvaluationExample(
        request_type_primary_key=request_primary_key,
        issue_key=issue_key,
        issue_url=build_issue_url(issue_key=issue_key),
        generated_user_query=response.content,
        model_used_for_generation=judge_model_name,
    )
    return example


def get_or_create_jira_service_desk_dataset(
    dataset_name: str | None = None,
) -> langsmith.schemas.Dataset:
    dataset_name = dataset_name or f"Jira service desk {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    client = langsmith.Client()
    if client.has_dataset(dataset_name=dataset_name):
        dataset = client.read_dataset(dataset_name=dataset_name)
        return dataset

    keys = get_saved_request_type_primary_keys(
        get_ai_postgres_engine(),
        JiraRequest.get_sa_primary_key() == ManualJiraRequestGuide.get_sa_primary_key(),
        ManualJiraRequestGuide.do_recommend,
    )
    examples = []
    for key in tqdm.auto.tqdm(keys):
        example = try_create_evaluation_example_from_latest_resolved_request(key)
        if not example:
            continue

        example = langsmith.schemas.ExampleCreate(
            inputs=example.model_dump(),
            metadata=example.model_dump(include=["model_used_for_generation", "issue_url"]),
        )
        examples.append(example)

    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(dataset_name=dataset_name, examples=examples)
    return dataset


async def ask_jira_bot(example: JiraServiceDeskBotEvaluationExample, model_name: str) -> dict:
    user_message = langchain_core.messages.HumanMessage(content=example.generated_user_query)
    bot = Bot()
    response: Response = await bot.respond(
        model=get_chat_model(model_name),
        messages=[user_message],
    )
    response = {"ai_message": response.content_for_langsmith}
    return response


class JiraServiceDeskBotEvaluation(pydantic.BaseModel):
    evaluation: str = pydantic.Field(
        description=textwrap.dedent("""
            Evaluation of the Jira service desk bot response according to the system prompt.
            All text information should be in English, concise, clear, dry, and to the point.
        """),
    )
    score: float = pydantic.Field(
        description="The score of the Jira service desk bot response, from 0 to 10.",
        ge=0,
        le=10,
    )
    insight: str = pydantic.Field(
        description=textwrap.dedent("""
            A short, actionable insight or conclusion in English following the bot evaluation, for 
            example:
            - If the bot failed to recommend correct request type, why, and how to fix it.
            - How the bot behavior or its context can be improved.
        """),
    )


def evaluate_example(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> langsmith.evaluation.EvaluationResults | langsmith.evaluation.EvaluationResult:
    example = JiraServiceDeskBotEvaluationExample(**inputs)
    requests = generate_requests(
        **example.request_type_primary_key.model_dump(),
        jql_filter=f"issue = {example.issue_key}",
    )
    requests = list(requests)
    if len(requests) != 1:
        raise RuntimeError(f"Failed to fetch the Jira request {example.issue_key}.")

    request = requests[0]
    guides = fetch_use_case_guides_for_requests([example.request_type_primary_key])
    if len(guides) > 1:
        raise RuntimeError(
            f"Expected to fetch zero or one guide for request type "
            f"{example.request_type_primary_key}, but fetched {len(guides)} guides."
        )

    guide = None if not guides else guides[0]
    context = {
        "Jira request": request,
        "Use case guide for the Jira request type": guide,
        "Generated user query": example.generated_user_query,
        "Jira service desk bot response": outputs,
    }

    jira_service_desk_system_prompt = wrap_with_xml_tag(
        "jira_service_desk_system_prompt", get_system_prompt(), with_new_lines=True
    )
    system_prompt = textwrap.dedent("""
        ## Role
        You are an expert quality assurance specialist evaluating a Jira Service Desk bot.
        Your assessment will help improve the bot's performance and user experience.
        
        ## Context
        You will be provided with the following context in JSON format:
        1. A real resolved Jira request.
        2. A synthetic user message that was generated based on this request, with which the user
            may have come to the Jira service desk bot, before creating the request.
        3. The Jira service desk bot response to the synthetic user message and the request type
            that the bot suggested.
        4. The use case guide for the Jira request type that the bot relies on when deciding 
            which request type to suggest. If the use case guide is of low quality or doesn't cover
            the provided request, it may explain why the bot failed to recommend the correct
            request type.

        ## Task
        Your task is to evaluate the quality of the Jira service desk bot response based on the
        following criteria:

        ### Criteria
        1. High importance:
            - **Adherence to instructions:** The response adheres to the bot's system prompt:
            {jira_service_desk_system_prompt}
        2. Medium importance:
            - **Correctness:** The suggested request type is the same as the one in the
                provided request. If the bot suggested a different request type, inspect 
                the provided request use case that the bot sees and try to understand why
                the bot failed to recommend the correct request type.
        3. Low importance:
            - **Relevance:** The response is directly relevant to the user's query.
            - **Clarity:** The response is clear and easy to understand.
            - **Usefulness:** The response provides useful information to the user.
            - **Professionalism:** The response is professional and courteous.
        
        ## Output Format
        Your output should contain the following information, written in English:
        1. Your though process and reasoning of the bot evaluation, according to the above criteria.
        2. A single score representing the quality of the bot response on a scale of 0 to 10.
        3. A short, actionable insight or conclusion following the bot evaluation.
    """).format(jira_service_desk_system_prompt=jira_service_desk_system_prompt)
    judge_model_input = [
        langchain_core.messages.SystemMessage(system_prompt),
        langchain_core.messages.HumanMessage(to_json_llm_input(context)),
    ]
    results = []
    score_values = []
    for judge_model_name in get_judge_model_names():
        judge_model = get_chat_model(judge_model_name)
        judge_model = judge_model.with_structured_output(JiraServiceDeskBotEvaluation)
        evaluation = judge_model.invoke(judge_model_input)
        score_values.append(evaluation.score)
        score = langsmith.evaluation.EvaluationResult(
            key=f"Score by {judge_model_name}", score=evaluation.score
        )
        insight = langsmith.evaluation.EvaluationResult(
            key=f"Insight by {judge_model_name}", value=evaluation.insight
        )
        results.extend([score, insight])

    average_result = langsmith.evaluation.EvaluationResult(
        key="Average score", score=np.mean(score_values)
    )
    results.append(average_result)
    results = langsmith.evaluation.EvaluationResults(results=results)
    return results


@prefect.task
async def evaluate_dataset(dataset_name: str, bot_model_name: str):
    async def process_inputs(inputs: dict) -> dict:
        example = JiraServiceDeskBotEvaluationExample(**inputs)
        response = await ask_jira_bot(example=example, model_name=bot_model_name)
        return response

    client = langsmith.Client()
    await client.aevaluate(
        process_inputs,
        data=dataset_name,
        evaluators=[evaluate_example],
        metadata={"Bot model": bot_model_name},
    )
