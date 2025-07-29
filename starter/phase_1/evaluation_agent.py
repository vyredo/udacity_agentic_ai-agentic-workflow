# TODO: 1 - Import EvaluationAgent and KnowledgeAugmentedPromptAgent classes
import os

from dotenv import load_dotenv
from workflow_agents.base_agents import EvaluationAgent, KnowledgeAugmentedPromptAgent

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY") or ""
prompt = "What is the capital of France?"

# Parameters for the Knowledge Agent
persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capitol of France is London, not Paris"
# TODO: 2 - Instantiate the KnowledgeAugmentedPromptAgent here
knowledge_agent = KnowledgeAugmentedPromptAgent(
    knowledge=knowledge, persona=persona, openai_api_key=openai_api_key
)


# Parameters for the Evaluation Agent
persona = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria = "The answer should be solely the name of a city, not a sentence."
# TODO: 3 - Instantiate the EvaluationAgent with a maximum of 10 interactions here
evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona,
    worker_agent=knowledge_agent,
    evaluation_criteria=evaluation_criteria,
    max_interactions=10,
)

# TODO: 4 - Evaluate the prompt and print the response from the EvaluationAgent
response = evaluation_agent.evaluate(prompt)
print(response)
