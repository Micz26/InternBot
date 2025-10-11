import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from intern_bot.data_scraper import DataScraper
from intern_bot.data_manager import DataManager
from intern_bot.agent import agent
from intern_bot.api.utils.models import AgentInput
from intern_bot.api.utils.scheduler import scheduler
from intern_bot.api.utils.scheduler import process_source, run_daily_scraping


router = APIRouter()


@router.post('/scrape/data')
async def scrape_data():
    try:
        DataManager.create_vector_index()

        sources = ['Nokia', 'PWR', 'Sii']
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all source processing tasks
            future_to_source = {
                executor.submit(process_source, source): source 
                for source in sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing {source}: {e}")
                    results.append({"source": source, "status": "error", "error": str(e)})
        
        outdated = DataManager.get_outdated_offers()
        DataManager.remove_offers(outdated)
        
        return JSONResponse(content={
            "message": "Data scraped successfully", 
            "results": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/scrape/data/test')
async def test_scraping():
    """Test endpoint to manually trigger the scraping job"""
    try:
        run_daily_scraping()
        return JSONResponse(content={"message": "Test scraping completed successfully"})
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




