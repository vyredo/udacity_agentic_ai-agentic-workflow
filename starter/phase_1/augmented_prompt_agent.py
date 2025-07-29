
import os

from dotenv import load_dotenv
from workflow_agents.base_agents import AugmentedPromptAgent

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY") or ""

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

# TODO: 2 - Instantiate an object of AugmentedPromptAgent with the required parameters
augmented_agent = AugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona
)

# TODO: 3 - Send the 'prompt' to the agent and store the response in a variable named 'augmented_agent_response'
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(augmented_agent_response)

# TODO: 4 - Add a comment explaining:
# - What knowledge the agent likely used to answer the prompt.
# - How the system prompt specifying the persona affected the agent's response.
"""
Knowledge Source Analysis:
- The agent likely used its training data containing geographical and political information
  to identify Paris as the capital of France. This is basic factual knowledge that would
  be present in the model's training corpus.

Persona Impact:
- The system prompt specifying the college professor persona affected the response by:
  1. Making the agent start with "Dear students," as instructed
  2. Potentially adopting a more educational/pedagogical tone
  3. The response may be more formal and explanatory compared to a generic response
  4. The agent explicitly forgot previous context and responded only based on the current
     interaction with the specified persona
"""
