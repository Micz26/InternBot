
from pydantic import BaseModel, Field
from langchain_core.prompt_values import StringPromptValue, ChatPromptValue
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage,
    ToolMessage,
    BaseMessage,
)
from typing import Literal, Annotated
from enum import Enum
from collections.abc import Sequence
from operator import add
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
import requests
import httpx

# LANGCHAIN UTILS

from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables.utils import Input, Output
from operator import itemgetter

# LANGSERVE UTILS

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from langserve import add_routes
from pydantic import BaseModel, Field

# COMMON UTILS

import os
import sys
import json
from typing import Any, Dict
from dotenv import load_dotenv
load_dotenv()

# IN/OUT BLOCKS PARSERS

from langchain_core.documents import Document
from langchain_core.prompt_values import StringPromptValue
from typing import List
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()


def docs_list_to_str(docs_list: List[Document] , with_metadata=True):
    docs_str = ''
    for idx, doc in enumerate(docs_list):
        docs_str += f'## {idx}. DOCUMENT\n'
        docs_str += '### CONTENT:\n'
        docs_str += f'{doc.page_content.strip()}\n'
        if with_metadata:
            docs_str += '### METADATA:\n'
            docs_str += f'{doc.metadata}\n'
    return docs_str

def prompt_val_to_str(prompt_val: StringPromptValue) -> str:
    return prompt_val.text

def if_dict_parse_to_str(named_element):
    if isinstance(named_element, dict):
        if len(named_element) != 1:
            raise ValueError(f'Expected string or dict of length=1.Found dict  of len {len(named_element)}')
        elif isinstance(named_element.values().__iter__().__next__(), dict):
            return if_dict_parse_to_str(named_element.values().__iter__().__next__())
        else:
            named_element = named_element.values().__iter__().__next__()
    
    if isinstance(named_element, AIMessage):
        return named_element.content
    elif isinstance(named_element, list) and len(named_element) >= 1 and isinstance(named_element[-1], AIMessage):
        return named_element[-1]
    
    return named_element

# LANGSERVE PER REQUEST MODIFIER

async def get_openid(request: Request):
    """Get the openid from either from Authorization header or from cookies"""
    token = request.headers.get("Authorization", "")
    if token and token.startswith("Bearer "):
        token = token[len("Bearer ") :]
    else:
        token = request.cookies.get("openid")
        
    return token


async def _per_request_config_modifier(
    config: dict[str, Any], request: Request
) -> dict[str, Any]:
    """Set configurables based on pipeline request data"""
    token = await get_openid(request)
    body = await request.body()
    body = json.loads(body.decode('utf-8'))
    configurable = body.get("config", {}).get('configurable', {})
    metadata = body.get("config", {}).get("metadata", {})
    config['configurable'] = configurable
    config['configurable']['user_id'] = metadata.get('user_id', None)
    config["configurable"]["__openid"] = token
    return config

# INITIALIZED BLOCKS


tools = [
    remote_tool_15
    ]

tools_map = {tool.name: tool for tool in tools}


llm_w_tools = gateway_llms_4.bind_tools(tools, tool_choice="auto")


class GraphInputState(BaseModel):
    input: (
        str
        | StringPromptValue
        | ChatPromptValue
        | SystemMessage
        | AIMessage
        | HumanMessage
        | ToolMessage
        | List[BaseMessage]
    )


class GraphOutputState(BaseModel):
    messages: Annotated[Sequence, add_messages] = Field(default_factory=list)


class GraphState(GraphInputState, GraphOutputState):
    pass


def parse_to_messages(state: GraphState, config):
    graph_input = state.input

    if isinstance(graph_input, str):
        messages = [HumanMessage(content=graph_input)]
    elif isinstance(graph_input, StringPromptValue):
        messages = [HumanMessage(content=graph_input.text)]
    elif isinstance(graph_input, ChatPromptValue):
        if len(messages) > 0:
            new_messages = graph_input.messages
            messages = [m for m in new_messages if not isinstance(m, SystemMessage)]
        else:
            messages = graph_input.messages
            system_msg = next(
                (m for m in messages if isinstance(m, SystemMessage)), None
            )
            non_system_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
            messages = [system_msg] if system_msg else []
            messages.extend(non_system_msgs)
    elif isinstance(
        graph_input, (SystemMessage, HumanMessage, ToolMessage)
    ):
        messages = [graph_input]
    elif isinstance(graph_input, AIMessage):
        messages = [HumanMessage(content=graph_input.content)]
    elif isinstance(graph_input, List[BaseMessage]):
        messages = graph_input

    return {'messages': messages}


async def call(state: GraphState, config):
    messages = state.messages

    i = 0
    while True:
        i += 1
        if i > 10:
            response = await gateway_llms_4.ainvoke(messages, config={**config})
            messages.append(response)
            break

        response = await llm_w_tools.ainvoke(messages, config={**config})
        messages.append(response)

        if tool_calls:=response.tool_calls:
            for tool_call in tool_calls:
                tool = tools_map.get(tool_call["name"]) 
               
                try:
                    tool_message = await tool.ainvoke(tool_call, config={**config})
                except requests.exceptions.HTTPError as e:
                    tool_message = ToolMessage(
                        content=f"Couldn't use tool: {tool_call['name']}, because of requests.exceptions.HTTPError: {e}. Explain the error to the user",
                        tool_call_id=tool_call.get("id"),
                    )
                except requests.exceptions.ConnectionError as e:
                    tool_message = ToolMessage(
                        content=f"Couldn't use tool: {tool_call['name']}, because of requests.exceptions.ConnectionError: {e}. Explain the error to the user",
                        tool_call_id=tool_call.get("id"),
                    )
                except httpx.HTTPStatusError as e:
                    tool_message = ToolMessage(
                        content=f"Couldn't use tool: {tool_call['name']}, because of httpx.HTTPStatusError: {e}. Explain the error to the user",
                        tool_call_id=tool_call.get("id"),
                    )
                except Exception as e:
                    tool_message = ToolMessage(
                        content=f"Couldn't use tool: {tool_call['name']}, because of {e}. Explain the error to the user",
                        tool_call_id=tool_call.get("id"),
                    )

                if not tool_message.content:
                    tool_message.content = ""
                messages.append(tool_message)
        else:
            break

    return {"messages": messages}



workflow = StateGraph(
    GraphState, input=GraphInputState, output=GraphOutputState
)

workflow.add_node("parse_to_messages", parse_to_messages)
workflow.add_node("call", call)

workflow.add_edge("__start__", "parse_to_messages")
workflow.add_edge("parse_to_messages", "call")
workflow.add_edge("call", "__end__")

agent_block_1 = workflow.compile()



# INPUT MODEL

class InputModel(BaseModel):
    """
    This is an agent, which has an expert to the telecom to[ics in a tool.
    """
    
    query: str = Field(..., description="user's query")

# LANGSERVE SERVE CHAIN

app=FastAPI()
