# agentic_workflow.py

# TODO: 1 - Import the following agents: ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent from the workflow_agents.base_agents module
import os
from typing import Any, TypedDict

from dotenv import load_dotenv
from workflow_agents.base_agents import (
    ActionPlanningAgent,
    EvaluationAgent,
    KnowledgeAugmentedPromptAgent,
    RoutingAgent,
)

# TODO: 2 - Load the OpenAI key into a variable called openai_api_key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY") or ""

# load the product spec
# TODO: 3 - Load the product spec document Product-Spec-Email-Router.txt into a variable called product_spec
current_dir = os.path.dirname(os.path.abspath(__file__))
product_spec_path = os.path.join(current_dir, "Product-Spec-Email-Router.txt")
try:
    with open(product_spec_path, encoding="utf-8") as file:
        product_spec = file.read() or ""
except Exception as e:
    print(f"Warning: Could not load Product-Spec-Email-Router.txt. Error: {e}")
    product_spec = ""

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
# TODO: 4 - Instantiate an action_planning_agent using the 'knowledge_action_planning'
action_planning_agent = ActionPlanningAgent(
    openai_api_key=openai_api_key, knowledge=knowledge_action_planning
)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    # TODO: 5 - Complete this knowledge string by appending the product_spec loaded in TODO 3
    f"\n\nProduct Specification:\n{product_spec}"
)

# TODO: 6 - Instantiate a product_manager_knowledge_agent using 'persona_product_manager' and the completed 'knowledge_product_manager'
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    name="Product Manager",
    description="Defines user stories for a product based on product specifications",
    openai_api_key=openai_api_key,
    persona="You are an evaluation agent that checks the answers of other worker agents",
    knowledge=knowledge_product_manager,
)


# Product Manager - Evaluation Agent
# TODO: 7 - Define the persona and evaluation criteria for a Product Manager evaluation agent and instantiate it as product_manager_evaluation_agent.
# This agent will evaluate the product_manager_knowledge_agent.
# The evaluation_criteria should specify the expected structure for user stories (e.g., "As a [type of user], I want [an action or feature] so that [benefit/value].").
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager,
    evaluation_criteria="As a [type of user], I want [an action or feature] so that [benefit/value].",
    worker_agent=product_manager_knowledge_agent,
    max_interactions=10,
)
# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
# (This is a necessary step before TODO 8. Students should add the instantiation code here.)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    name="Program Manager",
    description="Defines features by organizing similar user stories into cohesive groups",
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager,
)

# Program Manager - Evaluation Agent

# TODO: 8 - Instantiate a program_manager_evaluation_agent using 'persona_program_manager_eval' and the evaluation criteria below.
#                      "The answer should be product features that follow the following structure: " \
#                      "Feature Name: A clear, concise title that identifies the capability\n" \
#                      "Description: A brief explanation of what the feature does and its purpose\n" \
#                      "Key Functionality: The specific capabilities or actions the feature provides\n" \
#                      "User Benefit: How this feature creates value for the user"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.

persona_program_manager_eval = (
    "You are an evaluation agent that checks the answers of other worker agents."
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria="The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user",
    worker_agent=program_manager_knowledge_agent,
    max_interactions=10,
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    name="Development Engineer",
    description="Defines development tasks needed to implement each user story",
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer,
)

# Development Engineer - Evaluation Agent
# TODO: 9 - Instantiate a development_engineer_evaluation_agent using 'persona_dev_engineer_eval' and the evaluation criteria below.
#                      "The answer should be tasks following this exact structure: " \
#                      "Task ID: A unique identifier for tracking purposes\n" \
#                      "Task Title: Brief description of the specific development work\n" \
#                      "Related User Story: Reference to the parent user story\n" \
#                      "Description: Detailed explanation of the technical work required\n" \
#                      "Acceptance Criteria: Specific requirements that must be met for completion\n" \
#                      "Estimated Effort: Time or complexity estimation\n" \
#                      "Dependencies: Any tasks that must be completed first"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.

persona_dev_engineer_eval = (
    "You are an evaluation agent that checks the answers of other worker agents."
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    worker_agent=development_engineer_knowledge_agent,
    evaluation_criteria="The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first",
    max_interactions=10,
)

# Routing Agent
# TODO: 10 - Instantiate a routing_agent. You will need to define a list of agent dictionaries (routes) for Product Manager, Program Manager, and Development Engineer.
# Each dictionary should contain 'name', 'description', and 'func' (linking to a support function).
# Assign this list to the routing_agent's 'agents' attribute.
routing_agent = RoutingAgent(
    openai_api_key=openai_api_key,
    agents=[
        development_engineer_knowledge_agent,
        product_manager_knowledge_agent,
        program_manager_knowledge_agent,
    ],
)

# Job function persona support functions
# TODO: 11 - Define the support functions for the routes of the routing agent (e.g., product_manager_support_function, program_manager_support_function, development_engineer_support_function).
# Each support function should:
#   1. Take the input query (e.g., a step from the action plan).
#   2. Get a response from the respective Knowledge Augmented Prompt Agent.
#   3. Have the response evaluated by the corresponding Evaluation Agent.
#   4. Return the final validated response.


def product_manager_support_function(query: str):
    """Support function for Product Manager agent"""
    # Get response from knowledge agent
    response = product_manager_knowledge_agent.respond(query)
    if response is None:
        return ""

    # Evaluate the response
    evaluated_response = product_manager_evaluation_agent.evaluate(response)
    return evaluated_response['final_response'] 


def program_manager_support_function(query: str):
    """Support function for Program Manager agent"""
    # Get response from knowledge agent
    response = program_manager_knowledge_agent.respond(query)
    if response is None:
        return ""
    # Evaluate the response
    evaluated_response = program_manager_evaluation_agent.evaluate(response)
    return evaluated_response['final_response'] 


def development_engineer_support_function(query: str):
    """Support function for Development Engineer agent"""
    # Get response from knowledge agent
    response = development_engineer_knowledge_agent.respond(query)
    if response is None:
        return ""

    # Evaluate the response
    evaluated_response = development_engineer_evaluation_agent.evaluate(response)
    return evaluated_response['final_response'] 


# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# TODO: 12 - Implement the workflow.
#   1. Use the 'action_planning_agent' to extract steps from the 'workflow_prompt'.
#   2. Initialize an empty list to store 'completed_steps'.
#   3. Loop through the extracted workflow steps:
#      a. For each step, use the 'routing_agent' to route the step to the appropriate support function.
#      b. Append the result to 'completed_steps'.
#      c. Print information about the step being executed and its result.
#   4. After the loop, print the final output of the workflow (the last completed step).

workflow_steps_response = action_planning_agent.extract_steps_from_prompt(
    workflow_prompt
)
print(f"Action planning response: {workflow_steps_response}")

workflow_steps = (
    workflow_steps_response.split("\n")
    if isinstance(workflow_steps_response, str)
    else workflow_steps_response
)

# Filter out empty lines and clean up the steps
workflow_steps = [step.strip() for step in workflow_steps if step.strip()]


print(f"\nExtracted workflow steps: {len(workflow_steps)} steps")
for i, step in enumerate(workflow_steps, 1):
    print(f"  {i}. {step}")


class StepResult(TypedDict):
    step_number: int
    step_description: str
    result: Any  # Replace 'Any' with the actual type of step_result if known


completed_steps: list[StepResult] = []

print("\n --- Executing Workflow Steps ---")
for i, step in enumerate(workflow_steps, 1):
    print(f"\n=== Executing Step {i}: {step} ===")

    try:
        step_result = routing_agent.route(step)

        completed_steps.append(
            {"step_number": i, "step_description": step, "result": step_result}
        )

        print(f"Step {i} completed successfully:")
        print(f"Result: {step_result}")
        print("-" * 50)

    except Exception as e:
        print(f"Error executing step {i}: {e}")
        completed_steps.append(
            {"step_number": i, "step_description": step, "result": f"Error: {e}"}
        )


print("\n" + "=" * 60)
print("WORKFLOW EXECUTION COMPLETE")
print("=" * 60)

if completed_steps:
    print(f"\nTotal steps completed: {len(completed_steps)}")

    print("\n--- FINAL WORKFLOW OUTPUT ---")
    final_step = completed_steps[-1]
    print(f"Final Step ({final_step['step_number']}): {final_step['step_description']}")
    print(f"Final Result: {final_step['result']}")

    print("\n--- COMPLETE WORKFLOW SUMMARY ---")
    for step in completed_steps:
        print(f"Step {step['step_number']}: {step['step_description']}")
        print(
            f"  Result: {step['result'][:1000]}{'...' if len(str(step['result'])) > 100 else ''}"
        )
        print()
else:
    print("No steps were completed.")

print("\n*** Workflow execution finished ***")
