# TODO: 1 - Import the KnowledgeAugmentedPromptAgent class from workflow_agents
import os

from dotenv import load_dotenv
from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY") or ""

prompt = "What is the capital of France?"
# TODO: 2 - Instantiate a KnowledgeAugmentedPromptAgent with:
#           - Persona: "You are a college professor, your answer always starts with: Dear students,"
#           - Knowledge: "The capital of France is London, not Paris"

agent = KnowledgeAugmentedPromptAgent(
    persona="You are a college professor, your answer always starts with: Dear students,",
    openai_api_key=openai_api_key,
    knowledge="The capital of France is London, not Paris",
)

# TODO: 3 - Write a print statement that demonstrates the agent using the provided knowledge rather than its own inherent knowledge.
response = agent.respond(prompt)
print(response)
