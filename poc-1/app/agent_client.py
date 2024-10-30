from base_agent import BaseAgent

class AgentClient(BaseAgent):
    def __init__(self):
        super().__init__(name="AgentClient")
        self.system_prompt = "I am an agent who is helping a user find answers to a question. I will talk to nodes on the Elmnet until I can find the answer to their question."

agent_client = AgentClient()