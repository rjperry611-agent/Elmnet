from base_agent import BaseAgent

class AgentRetriever(BaseAgent):
    def __init__(self):
        super().__init__(name="AgentRetriever")
        self.system_prompt = "I am an agent who represents a business owner, content creator, or any other person who wants to present public information to world. When someone requests information, I will look in the database and create a helpful response to the question."

agent_retriever = AgentRetriever()