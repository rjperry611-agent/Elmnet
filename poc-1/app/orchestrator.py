from base_agent import BaseAgent
from agent_client import agent_client
from agent_storer import agent_storer
from agent_retriever import agent_retriever
from agent_router import agent_router

class Orchestrator(BaseAgent):
    def __init__(self):
        super().__init__(name="Orchestrator")
        # internal agents are the agents that will serve the owner of this node
        self.internal_agents = {
            "agent_client": agent_client,
            "agent_storer": agent_storer,
        }
        # external agents will deal with requests coming from outside of this node
        self.external_agents = {
            "agent_retriever": agent_retriever,
            "agent_router": agent_router,
        }

    async def orchestrate_request(self, internal, query: str):
        if internal:
            # Compile the system prompts from all agents
            agent_descriptions = "\n".join(
                [f"{agent_name}: {agent.system_prompt}" for agent_name, agent in self.internal_agents.items()]
            )

            # Create a prompt that allows the LLM to select the best agent
            prompt = f"""
            Below are descriptions of different agents and their capabilities:
            {agent_descriptions}

            Given the user query: "{query}", determine which agent is best suited to handle it. Respond with the agent's name.
            """

            # Use Llama to determine the best agent
            response = await self.handle_request(prompt)
            best_agent_name = response.text.strip()

            # Route the query to the appropriate agent
            if best_agent_name in self.internal_agents:
                return await self.internal_agents[best_agent_name].handle_request(query)
            else:
                return {"error": "Unable to determine the best agent for the query."}
        else:
            # Does this request have to do with this node's hosted content or does it need router knowledge?
            prompt = f"""
            Does this user's query pertain to this user's hosted information or should I seek out other nodes that would have this information.
            Respond "yes" if it's related to this user's hosted information and "no" otherwise"
            Query: {query}
            """

            response = await agent_retriever.handle_request(prompt)
            answer = response.text.strip()
            if "yes" in answer:
                return agent_retriever.handle_request(query)
            if "no" in answer:
                return agent_router.handle_request(query)

orchestrator = Orchestrator()