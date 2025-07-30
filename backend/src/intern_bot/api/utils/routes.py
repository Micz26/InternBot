import json
import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from intern_bot.data_manager import DataManager
from intern_bot.agent import agent
from intern_bot.api.utils.models import AgentInput


router = APIRouter()


@router.post('/agent/invoke')
async def aagent_invoke(payload: AgentInput):
    query = payload.query
    config = payload.config

    first_message = HumanMessage(query)

    result = await agent.ainvoke({"messages": [first_message]}, config=config)
    messages = result.get("messages", [])
    if messages:
        return messages
    else:
        raise Exception('NO MESSAGES')
    
@router.post('/agent/stream')
async def aagent_stream(payload: AgentInput):
    query = payload.query
    config = payload.config

    first_message = HumanMessage(query)

    async def event_generator():
        try:
            async for state_update in agent.astream({"messages": [first_message]}, config=config):
                messages = state_update.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    data = json.dumps({"content": last_message.content})
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0)
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")




