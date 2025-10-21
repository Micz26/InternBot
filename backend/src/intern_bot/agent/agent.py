from typing import Annotated

from pydantic import BaseModel
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
from langsmith import traceable

from langgraph.checkpoint.memory import InMemorySaver

from intern_bot.data_manager import DataManager
from intern_bot.settings import Settings

settings = Settings()

llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    model="gpt-4.1-nano",
    temperature=0,
    max_tokens=15000,
)

@tool
@traceable
async def retrieve_offers(internship_info: str, company: str | None):
    """
    Retrieve internship and apprenticeship offers based on semantic similarity.

    This tool searches a vector database containing internship and apprenticeship
    offers. It should always be used whenever a recommendation of relevant offers
    is requested.

    Parameters:
    - internship_info: Free-text input describing an internship or apprenticeship,
      similar in style to a job posting (e.g., required skills, role, responsibilities).
      The tool will use this description to find semantically matching offers
      from the indexed dataset.
    - company: Optional. The name of the company for which to retrieve offers.
      Only provide this parameter if the user explicitly requests offers from a
      specific company (eg. Sii, Nokia); otherwise, leave it as None.

    Returns:
    - Ranked list of internship or apprenticeship offers from the vector database
      that are most semantically similar to the input description, optionally
      filtered by company.
    """
    print('Querying with description:', internship_info, 'Company filter:', company)
    results = DataManager.similarity_search_cosine(internship_info, filters={'company': company})
    print('Found results:', results)
    return results


tools = [retrieve_offers]

tools_map = {tool.name: tool for tool in tools}

llm_w_tools = llm.bind_tools(tools)

class GraphInputState(BaseModel):
    query: str

class GraphState(GraphInputState):
    messages: Annotated[list, add_messages]

async def chatbot(state: GraphState, config):
    MAX_ITERATIONS = 3

    messages = state.messages
    query = state.query

    if len(messages) == 0:
        messages.append(SystemMessage(content="""
You are a helpful assistant whose goal is to find the best internship or apprenticeship offers for the user. 
Always use the `retrieve_offers` tool when asked to find offers. 

When recommending an offer, always include:
- Link to the offer
- Company name
- Short description of the offer

If available, you may also include additional details:
- Location
- Contract type
- Date posted
- Closing date
"""))
    messages.append(HumanMessage(query))


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
    GraphState, input=GraphInputState, output=GraphState
)


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge("__start__", "chatbot")
graph_builder.add_edge("chatbot", "__end__")

checkpointer = InMemorySaver()
agent = graph_builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    import asyncio
    async def main():
        config = {"configurable": {"thread_id": "123"}}
        initial_state = {
            "messages": [HumanMessage(content="Find me internships related to software engineering in Nokia")]
        }

        # Invoke the graph once and get the final state
        result = await agent.ainvoke(initial_state, config=config)
        messages = result.get("messages", [])
        if messages:
            print(f"Assistant: {messages[-1].content}")

        initial_state = {
            "messages": [HumanMessage(content="Now me internships related to software engineering in Sii")]
        }

        result = await agent.ainvoke(initial_state, config=config)
        messages = result.get("messages", [])
        if messages:
            print(f"Assistant: {messages[-1].content}")

    asyncio.run(main())