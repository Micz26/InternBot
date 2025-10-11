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


router = APIRouter()


def process_source(source: str):
    """Process a single source: scrape offers, update database"""
    try:
        current_offers = DataManager.get_current_offers_links(source)
        
        new_offers = DataScraper.scrape_offers(source)
        print(f"SCRAPED {source}:", new_offers)
        
        to_add, to_remove = DataManager.diff_offers(current_offers, new_offers)
        print(f"TO ADD {source}:", to_add)
        to_add = to_add
        
        DataManager.remove_offers(to_remove)
        
        detailed_offers = DataScraper.scrape_offers_details(source, to_add)
        DataManager.add_offers(detailed_offers)
        print(f"ADDED {source}:", detailed_offers)
        
        return {"source": source, "status": "success", "added": len(detailed_offers)}
    except Exception as e:
        print(f"Error processing {source}: {e}")
        return {"source": source, "status": "error", "error": str(e)}


@router.post('/scrape/data')
async def aagent_stream():
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




