from langchain_ollama import ChatOllama
import requests

class BaseAgent:

    print("Pulling llama3.2")
    response = requests.post("http://ollama:11434/api/pull", json={
        "name": "llama3.2"
    })
    print("Finished pulling llama3.2")

    def __init__(self, name):
        self.name = name
        self.system_prompt = ""
        self.llm = ChatOllama(
            model="llama3.2",
            temperature=0,
            base_url="http://ollama:11434"
        )

    def start(self):
        # Base startup tasks
        print(f"{self.name} started.")

    def handle_request(self, query: str):
        # Logic for handling requests using Llama model
        messages = [
            ("system", self.system_prompt),
            ("human", query)
        ]
        print(f"Asking {self.name}: {self.system_prompt} | {query}")
        response = self.llm.invoke(messages).content
        print(f"Response from {self.name} is: {response}")
        return response
