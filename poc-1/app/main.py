from fastapi import FastAPI
from pydantic import BaseModel
import random
import uvicorn
import requests
import sys
import os
import time
from orchestrator import orchestrator
from agent_client import agent_client

app = FastAPI()

# In-memory set of known peers
peer_list = set()

class PeerInfo(BaseModel):
    node_url: str

@app.post("/query-peers")
async def query_peers(peer_info: PeerInfo):
    # Add the caller's node URL to peer_list
    peer_list.add(peer_info.node_url)
    print(f"Added new peer: {peer_info.node_url}")
    # Return about 5 random peers from peer_list
    peers = list(peer_list)
    random_peers = random.sample(peers, min(len(peers), 5))
    print(f"Providing peers: {random_peers}")
    return {"peers": random_peers}

def connect_to_bootstrap_node(bootstrap_url, node_url):
    # Send a request to the bootstrap node's /query-peers endpoint
    try:
        response = requests.post(
            f"{bootstrap_url}/query-peers",
            json={"node_url": node_url}
        )
        if response.status_code == 200:
            data = response.json()
            new_peers = data.get("peers", [])
            peer_list.update(new_peers)
            print(f"Received peers from bootstrap node: {new_peers}")
        else:
            print(f"Failed to query peers from bootstrap node: {bootstrap_url}")
    except Exception as e:
        print(f"Error connecting to bootstrap node: {e}")

# Define main endpoints
@app.get("/internal")
async def query_internal(query: str):
    # Route request using router agent
    response = await orchestrator.orchestrate_request(True, query)
    return response

# @app.get("/external")
async def query_external(query: str):
    # Route request using router agent
    response = await orchestrator.orchestrate_request(False, query)
    return response

def main():
    orchestrator.start()
    agent_client.start()

    # Get the bootstrap URL from command line arguments, if any
    whoami = os.environ.get('WHOAMI')
    bootstrap_url = os.environ.get('BOOTSTRAP_URL')
    if whoami and bootstrap_url:
        print(f"{whoami} connecting to bootstrap node at {bootstrap_url}")
        # Wait a bit to ensure the bootstrap node is up
        time.sleep(2)
        # Connect to bootstrap node
        connect_to_bootstrap_node(bootstrap_url, whoami)
        # Add bootstrap node to peer list
        peer_list.add(bootstrap_url)
    elif whoami:
        print(f"No bootstrap URL provided. {whoami} will be the first node in the network.")
    else:
        print(f"Running in single node mode")
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()