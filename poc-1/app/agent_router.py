from base_agent import BaseAgent

class AgentRouter(BaseAgent):
    def __init__(self):
        super().__init__(name="AgentRouter")
        self.system_prompt = "I am an agent who connects agents searching for answers to agents who have those answers. If I don't know who has the answer, I will route to another router agent who can help."

agent_router = AgentRouter()