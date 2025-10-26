from typing import Annotated

from pydantic import BaseModel
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage

from langgraph.checkpoint.memory import InMemorySaver

from intern_bot.data_manager import DataManager
from intern_bot.settings import Settings

settings = Settings()

llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    model="gpt-4.1-mini",
    temperature=0,
    max_tokens=15000,
)

@tool
async def retrieve_offers(internship_info: str, company: str | None, limit: int = 5, offset: int = 0):
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
      specific company (e.g., Sii, Nokia); otherwise, leave it as None.
    - limit: Optional. The maximum number of offers to return (default = 5).  
      Use this parameter **only if the user explicitly specifies** how many offers 
      they want to see (e.g., "show me 10 offers").  
      Otherwise, do not include it in the call — the default value of 5 will be used automatically.
    - offset: Optional. Used to skip a given number of top-ranked results (default = 0).  
      Use this parameter **when the user asks for other or new offers** after already 
      receiving some (e.g., “show me different ones” or “what else do you have?”).  
      In such cases, pass an offset equal to the number of previously shown offers 
      (e.g., offset = 5 if the previous call returned 5 offers).

    Returns:
    - Ranked list of internship or apprenticeship offers from the vector database
      that are most semantically similar to the input description, optionally
      filtered by company.  
      The returned offer links can later be used with the `get_offer_details` tool
      to retrieve detailed information about each offer.
    """
    print('Querying with description:', internship_info, 'Company filter:', company, 'Limit:', limit, 'Offset:', offset)
    results = DataManager.similarity_search_cosine(query=internship_info, k=limit, offset=offset, filters={'company': company})
    print('Found results:', results)
    return results

@tool
async def get_offer_details(offer_link: str):
    """
    Retrieve all available information about a specific offer based on its link.

    This tool provides comprehensive details about a given internship or apprenticeship 
    offer using its unique offer link. It should be used whenever detailed information 
    about a specific offer (previously retrieved or recommended) is requested.

    This function works exclusively with offer links that were previously obtained 
    from the `retrieve_offers` tool. Using any other external or arbitrary links 
    will not return valid results.

    Parameters:
    - offer_link: The unique URL or identifier of the offer to retrieve details for.

    Returns:
    - All available metadata and structured information about the specified offer, 
      including description, requirements, location, company, and other relevant fields.
    """
    offer = DataManager.get_offer(offer_link)
    return offer

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

When recommending an offer, always include:
- Link to the offer in markdown format: [Offer title] (offer_link)  
  (If no title is available, use the company name instead.)
- Company name
- Short description of the offer (max 2-3 sentences)

If available, you may also include additional details:
- Location
- Contract type
- Date posted
- Closing date

When showing offer details, always include full information about the offer as returned by the tool.

Instructions:
- Always use the `retrieve_offers` tool when asked to find or recommend internship or apprenticeship offers.
- Always use the `get_offer_details` tool when asked to get details about an offer that was previously recommended.
- In all other cases, respond based on your knowledge without using any tools.
- When asked about salary, pay, or compensation (for any position, company, or offer), or when the user asks for the highest-paying or best-paid offers (either in general or in a specific company):
  * Do NOT use any tools.
  * Always respond that salary information is not available and that you do not have access to salary data.
  * Suggest instead that you can help find internship or apprenticeship offers that best match the user's skills, interests, or goals.
""")
)
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