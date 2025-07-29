# TODO: 1 - Import the KnowledgeAugmentedPromptAgent and RoutingAgent
import os

from dotenv import load_dotenv
from workflow_agents.base_agents import (
    KnowledgeAugmentedPromptAgent,
    RoutingAgent,
    WorkerAgent,
)

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY") or ""

persona = "You are a college professor"

# TODO: 2 - Define the Texas Knowledge Augmented Prompt Agent
texasAgent = KnowledgeAugmentedPromptAgent(
    name="texas agent",
    description="Answer a question about Texas",
    openai_api_key=openai_api_key,
    persona=persona,
    knowledge="You know everything about Texas",
)

# TODO: 3 - Define the Europe Knowledge Augmented Prompt Agent
europeAgent = KnowledgeAugmentedPromptAgent(
    name="europe agent",
    description="Answer a question about Europe",
    openai_api_key=openai_api_key,
    persona=persona,
    knowledge="You know everything about Europe",
)


# TODO: 4 - Define the Math Knowledge Augmented Prompt Agent
mathAgent = KnowledgeAugmentedPromptAgent(
    name="math agent",
    description="When a prompt contains numbers, respond with a math formula",
    openai_api_key=openai_api_key,
    persona="You are a college math professor",
    knowledge="You know everything about math, you take prompts with numbers, extract math formulas, and show the answer without explanation",
)
agents: list[WorkerAgent] = [texasAgent, mathAgent, europeAgent]
routing_agent = RoutingAgent(
    openai_api_key,
    agents=agents,
)


routing_agent.agents = agents

# TODO: 8 - Print the RoutingAgent responses to the following prompts:
#           - "Tell me about the history of Rome, Texas"
#           - "Tell me about the history of Rome, Italy"
#           - "One story takes 2 days, and there are 20 stories"

prompts = [
    "Tell me about the history of Rome, Texas",
    "Tell me about the history of Rome, Italy",
    "One story takes 2 days, and there are 20 stories",
]

for p in prompts:
    print(f"prompt: {p}")
    print(routing_agent.route(p))
