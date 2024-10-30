from base_agent import BaseAgent

class AgentStorer(BaseAgent):
    def __init__(self):
        super().__init__(name="AgentStorer")
        self.system_prompt = "I am an agent who stores information for a business owner, content creator, or any other person who wants to present information to world. They will provide the information to me and I will store it in a database and keep it organized."

agent_storer = AgentStorer()