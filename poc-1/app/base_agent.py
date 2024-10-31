from langchain_ollama import ChatOllama

class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.system_prompt = ""
        self.llm = ChatOllama(
            model="llama3.2",
            temperature=0,
            # other params...
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