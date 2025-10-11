from typing import Annotated

from pydantic import BaseModel
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

from intern_bot.data_manager import DataManager
from intern_bot.settings import Settings

settings = Settings()


llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    model="gpt-4o-mini",
    temperature=0,
)

@tool
async def retrieve_offers(internship_info: str):
    # , title: str | None, company: str | None, location: str | None
    """
    Search internship offers using semantic similarity over indexed descriptions.

    Parameters:
    - offer_description: Free‑text description that serves as the semantic query.

    Returns:
    - Ranked results from the data store matching the query and applied filters.
    """
    print('DESC', internship_info)
    results = DataManager.similarity_search_cosine(internship_info)
    print(results)
    return results

tools = [retrieve_offers]

tools_map = {tool.name: tool for tool in tools}

llm_w_tools = llm.bind_tools(tools)

class GraphState(BaseModel):
    messages: Annotated[list, add_messages]

async def chatbot(state: GraphState, config):
    MAX_ITERATIONS = 3

    messages = state.messages

    for i in range(1, MAX_ITERATIONS+1):
        if i == MAX_ITERATIONS:
            response = await llm.ainvoke(messages, config={**config})
            messages.append(response)

        response = await llm_w_tools.ainvoke(messages, config={**config})
        messages.append(response)

        if tool_calls:=response.tool_calls:
            for tool_call in tool_calls:
                tool = tools_map.get(tool_call["name"]) 
                try:
                    tool_message = await tool.ainvoke(tool_call, config={**config})
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
    print('MESSAGES', messages)

    return {"messages": messages}


graph_builder = StateGraph(
    GraphState, input=GraphState, output=GraphState
)


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge("__start__", "chatbot")
graph_builder.add_edge("chatbot", "__end__")

agent = graph_builder.compile()


if __name__ == "__main__":
    import asyncio
    from langchain_core.messages import HumanMessage
    async def main():
        initial_state = {
            "messages": [HumanMessage(content="Find me internships related to software engineering in Poland")]
        }
        config = {}

        # Invoke the graph once and get the final state
        result = await agent.ainvoke(initial_state, config=config)
        messages = result.get("messages", [])
        if messages:
            print(f"Assistant: {messages[-1].content}")

    asyncio.run(main())