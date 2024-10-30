from fastapi import FastAPI
from orchestrator import orchestrator
from agent_client import agent_client

app = FastAPI()

# Instantiate agents
@app.on_event("startup")
async def startup_event():
    orchestrator.start()
    agent_client.start()

# Define main endpoints
@app.get("/internal")
async def query_internal(query: str):
    # Route request using router agent
    response = await orchestrator.orchestrate_request(True, query)
    return response

@app.get("/external")
async def query_external(query: str):
    # Route request using router agent
    response = await orchestrator.orchestrate_request(False, query)
    return response