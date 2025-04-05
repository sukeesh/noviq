from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import json
import asyncio
from .research import ResearchSession

app = FastAPI(title="Noviq Research API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active research sessions
sessions = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_message(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

# API Models
class UserIntent(BaseModel):
    intent: str
    model_name: str

class QAPair(BaseModel):
    question: str
    answer: str

class QAPairs(BaseModel):
    qa_pairs: List[QAPair]
    session_id: str

# API Routes
@app.get("/")
async def root():
    return {"message": "Noviq Research API"}

@app.get("/models")
async def get_models():
    """Get available Ollama models"""
    try:
        # Create a temporary session just to get models
        session = ResearchSession()
        models = session.get_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@app.post("/sessions")
async def create_session(user_intent: UserIntent):
    """Create a new research session"""
    try:
        # Create a new session with selected model
        session = ResearchSession(model_name=user_intent.model_name)
        session.set_user_intent(user_intent.intent)
        
        # Generate a session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Store the session
        sessions[session_id] = session
        
        return {
            "session_id": session_id,
            "status": "created",
            "model": user_intent.model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.get("/sessions/{session_id}/questions")
async def get_clarifying_questions(session_id: str):
    """Get clarifying questions for the session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        questions = session.generate_clarifying_questions()
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@app.post("/sessions/{session_id}/answers")
async def submit_answers(session_id: str, qa_pairs: QAPairs):
    """Submit answers to clarifying questions"""
    if session_id != qa_pairs.session_id:
        raise HTTPException(status_code=400, detail="Session ID mismatch")
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        # Convert from model to tuple format
        qa_tuples = [(qa.question, qa.answer) for qa in qa_pairs.qa_pairs]
        session.set_qa_pairs(qa_tuples)
        return {"status": "answers_submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting answers: {str(e)}")

@app.get("/sessions/{session_id}/plan")
async def get_research_plan(session_id: str):
    """Get the research plan for the session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        plan = session.generate_research_plan()
        return {"plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating research plan: {str(e)}")

@app.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get the current status of the session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        return {
            "status": session.current_step,
            "has_intent": session.user_intent is not None,
            "has_qa_pairs": len(session.qa_pairs) > 0,
            "has_plan": len(session.research_plan) > 0,
            "has_report": session.research_report is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session status: {str(e)}")

@app.get("/sessions/{session_id}/report")
async def get_research_report(session_id: str, generate: bool = False):
    """Get the research report for the session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        # If report exists or generate flag is set
        if session.research_report or generate:
            if generate and not session.research_report:
                # This is blocking and might take a while - in a real app, consider
                # using background tasks or WebSockets for this
                session.generate_final_report()
            
            return {"report": session.research_report}
        else:
            raise HTTPException(status_code=400, detail="Report not generated yet. Set generate=true to generate.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting research report: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates during research"""
    if session_id not in sessions:
        await websocket.close(code=1008)  # Policy violation (session doesn't exist)
        return
    
    session = sessions[session_id]
    await manager.connect(websocket, session_id)
    
    try:
        # Send initial state
        await manager.send_message(session_id, {
            "type": "status_update",
            "status": session.current_step
        })
        
        # Start execution in background
        execution_task = asyncio.create_task(execute_research(session_id))
        
        # Keep connection open for status updates
        while True:
            data = await websocket.receive_text()
            # Process any commands from client
            try:
                msg = json.loads(data)
                if msg.get("action") == "cancel":
                    execution_task.cancel()
                    await manager.send_message(session_id, {
                        "type": "status_update",
                        "status": "cancelled"
                    })
            except json.JSONDecodeError:
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error",
            "message": str(e)
        })
        manager.disconnect(session_id)

async def execute_research(session_id: str):
    """Execute the research workflow and send updates via WebSocket"""
    if session_id not in sessions:
        return
    
    session = sessions[session_id]
    
    try:
        # First check if we have the necessary data to proceed
        if not session.user_intent:
            await manager.send_message(session_id, {
                "type": "error",
                "message": "Research intent is missing. Please provide a research topic."
            })
            return
            
        if not session.qa_pairs or len(session.qa_pairs) == 0:
            await manager.send_message(session_id, {
                "type": "error",
                "message": "Please answer the clarifying questions to continue with the research."
            })
            return

        # Generate research plan if not already done
        if not session.research_plan:
            await manager.send_message(session_id, {
                "type": "status_update", 
                "status": "generating_plan"
            })
            try:
                plan = session.generate_research_plan()
                await manager.send_message(session_id, {
                    "type": "plan_generated", 
                    "plan": plan
                })
            except Exception as e:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": str(e)
                })
                return
        
        # For each step in the research plan
        for step_idx, step in enumerate(session.research_plan):
            await manager.send_message(session_id, {
                "type": "step_started", 
                "step_index": step_idx,
                "step": step
            })
            
            # Generate search queries
            await manager.send_message(session_id, {
                "type": "status_update", 
                "status": f"generating_queries_for_step_{step_idx}"
            })
            queries = session.generate_search_queries_for_step(step_idx)
            
            await manager.send_message(session_id, {
                "type": "queries_generated", 
                "step_index": step_idx,
                "queries": queries
            })
            
            # Execute searches
            for query_idx, query in enumerate(queries):
                await manager.send_message(session_id, {
                    "type": "executing_search", 
                    "query": query,
                    "query_index": query_idx
                })
                
                results = session.execute_search_for_query(query)
                
                await manager.send_message(session_id, {
                    "type": "search_results", 
                    "query": query,
                    "results": [{"title": title, "url": url} for title, url in results]
                })
                
                # Process first result
                if results:
                    title, url = results[0]
                    session.add_sources(title, url)
                    
                    await manager.send_message(session_id, {
                        "type": "processing_url", 
                        "url": url,
                        "title": title
                    })
                    
                    result = session.scrape_and_process_url(url)
                    
                    await manager.send_message(session_id, {
                        "type": "url_processed", 
                        "url": url,
                        "title": title,
                        "category": result.get("category", "Unknown")
                    })
            
            await manager.send_message(session_id, {
                "type": "step_completed", 
                "step_index": step_idx
            })
        
        # Generate final report
        await manager.send_message(session_id, {
            "type": "status_update", 
            "status": "generating_report"
        })
        
        report = session.generate_final_report()
        
        # Save report to file
        filename = session.save_report_to_file()
        
        await manager.send_message(session_id, {
            "type": "report_generated", 
            "filename": filename
        })
        
        # Complete
        await manager.send_message(session_id, {
            "type": "status_update", 
            "status": "completed"
        })
        
    except asyncio.CancelledError:
        await manager.send_message(session_id, {
            "type": "status_update", 
            "status": "cancelled"
        })
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error", 
            "message": str(e)
        })

# For direct execution with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 