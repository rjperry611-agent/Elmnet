from base_agent import BaseAgent

class AgentClient(BaseAgent):
    def __init__(self):
        super().__init__(name="AgentClient")
        self.system_prompt = "I am an agent who is helping a user find answers to a question. I will notify the user that I am going to use Elmnet to find their answer."

agent_client = AgentClient()