import json
import asyncio
from datetime import date, datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from intern_bot.data_manager import DataManager
from intern_bot.agent import agent
from intern_bot.api.utils.models import AgentInput
from intern_bot.api.utils.scheduler import scheduler
from intern_bot.api.utils.scheduler import run_daily_scraping


def serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="ignore")
    return obj

router = APIRouter()

@router.post('/scrape/data')
async def scrape_data():
    """Test endpoint to manually trigger the scraping job"""
    try:
        run_daily_scraping()
        return JSONResponse(content={"message": "Test scraping completed successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/data/info')
async def data_info():
    """Get the current status of the data"""
    try:
        data_info = DataManager.get_data_info()
        return JSONResponse(content={"message": data_info})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/data/current_offers')
async def current_offers():
    """Get the current offers"""
    try:
        current_offers = DataManager.get_current_offers()
        serialized = [
            {k: serialize(v) for k, v in offer.items()}
            for offer in current_offers
        ]
        return JSONResponse(content={"message": serialized})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/scheduler/status')
async def get_scheduler_status():
    """Get the current status of the scheduler"""
    try:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return JSONResponse(content={
            "scheduler_running": scheduler.running,
            "jobs": jobs
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/agent/invoke')
async def aagent_invoke(payload: AgentInput):
    query = payload.query
    config = payload.config.dict()

    result = await agent.ainvoke({"query": query}, config=config)
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




