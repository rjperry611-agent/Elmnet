import httpx

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def start(self):
        # Base startup tasks
        print(f"{self.name} started.")

    async def handle_request(self, query: str):
        # Logic for handling requests using Llama model
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://ollama:11400/api/generate",
                json={"model": "llama3.2", "prompt": "${self.system_prompt}. This is the query ${query}"}
            )
            result = response.json()
            return {"agent": self.name, "text": result.get("generated_text", "No response")}