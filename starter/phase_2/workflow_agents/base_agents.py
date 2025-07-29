import csv
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd
from openai import OpenAI


class WorkerAgent(Protocol):
    description: str
    name: str
    func: Callable[..., Any]

    def respond(self, input_text: str) -> str | None: ...


def noop(x: Any):
    return None


base_url = "https://openai.vocareum.com/v1"
model = "gpt-4o-mini"


@dataclass
class DirectPromptAgent:
    openai_api_key: str

    def respond(self, prompt: str) -> str | None:
        # Generate a response using the OpenAI API
        client = OpenAI(
            api_key=self.openai_api_key,
            base_url=base_url,
        )
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], temperature=0
        )
        content = response.choices[0].message.content
        if content is None:
            return ""
        return content


@dataclass
class AugmentedPromptAgent:
    openai_api_key: str
    persona: str

    def respond(self, input_text: str):
        """Generate a response using OpenAI API."""
        client = OpenAI(
            api_key=self.openai_api_key,
            base_url=base_url,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                # TODO: 3 - Add a system prompt instructing the agent to assume the defined persona and explicitly forget previous context.
                {"role": "user", "content": input_text},
                {
                    "role": "system",
                    "content": f"You are {self.persona}. Forget any previous conversation context and respond only based on this current interaction.",
                },
            ],
            temperature=0,
        )

        # TODO: 4 - Return only the textual content of the response, not the full JSON payload.
        return response.choices[0].message.content


@dataclass
class KnowledgeAugmentedPromptAgent(WorkerAgent):
    openai_api_key: str
    persona: str
    knowledge: str
    description: str = ""
    name: str = ""
    func: Callable[..., Any] = noop

    def __post_init__(self):
        self.func = self.respond

    def respond(self, input_text: str):
        """Generate a response using the OpenAI API."""
        client = OpenAI(base_url=base_url, api_key=self.openai_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                # TODO: 2 - Construct a system message including:
                #           - The persona with the following instruction:
                #             "You are _persona_ knowledge-based assistant. Forget all previous context."
                #           - The provided knowledge with this instruction:
                #             "Use only the following knowledge to answer, do not use your own knowledge: _knowledge_"
                #           - Final instruction:
                #             "Answer the prompt based on this knowledge, not your own."
                {
                    "role": "system",
                    "content": f"You are {self.persona} knowledge-based assistant. Forget all previous context. "
                    f"Use only the following knowledge to answer, do not use your own knowledge: {self.knowledge} "
                    f"Answer the prompt based on this knowledge, not your own.",
                },
                # TODO: 3 - Add the user's input prompt here as a user message.
                {"role": "user", "content": input_text},
            ],
            temperature=0,
        )
        return response.choices[0].message.content


# RAGKnowledgePromptAgent class definition
@dataclass
class RAGKnowledgePromptAgent:
    """
    An agent that uses Retrieval-Augmented Generation (RAG) to find knowledge from a large corpus
    and leverages embeddings to respond to prompts based solely on retrieved information.
    """

    openai_api_key: str
    persona: str
    chunk_size = 2000
    chunk_overlap = 100

    def __post_init__(self):
        self.unique_filename = (
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.csv"
        )

    def get_embedding(self, text: str):
        """
        Fetches the embedding vector for given text using OpenAI's embedding API.

        Parameters:
        text (str): Text to embed.

        Returns:
        list: The embedding vector.
        """
        client = OpenAI(
            base_url="https://openai.vocareum.com/v1", api_key=self.openai_api_key
        )
        response = client.embeddings.create(
            model="text-embedding-3-large", input=text, encoding_format="float"
        )
        return response.data[0].embedding

    def calculate_similarity(
        self, vector_one: npt.ArrayLike, vector_two: npt.ArrayLike
    ):
        """
        Calculates cosine similarity between two vectors.

        Parameters:
        vector_one (list): First embedding vector.
        vector_two (list): Second embedding vector.

        Returns:
        float: Cosine similarity between vectors.
        """
        vec1, vec2 = np.array(vector_one), np.array(vector_two)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def chunk_text(self, text: str) -> list[dict[str, int | str]]:
        """
        Splits text into manageable chunks, attempting natural breaks.

        Parameters:
        text (str): Text to split into chunks.

        Returns:
        list: List of dictionaries containing chunk metadata.
        """
        separator = "\n"
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) <= self.chunk_size:
            return [{"chunk_id": 0, "text": text, "chunk_size": len(text)}]

        start, chunk_id = 0, 0
        chunks: list[dict[str, int | str]] = []

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if separator in text[start:end]:
                end = start + text[start:end].rindex(separator) + len(separator)

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": text[start:end],
                    "chunk_size": end - start,
                    "start_char": start,
                    "end_char": end,
                }
            )

            start = end - self.chunk_overlap
            chunk_id += 1

        with open(
            f"chunks-{self.unique_filename}", "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["text", "chunk_size"])
            writer.writeheader()
            for chunk in chunks:
                writer.writerow({k: chunk[k] for k in ["text", "chunk_size"]})

        return chunks

    def calculate_embeddings(self):
        """
        Calculates embeddings for each chunk and stores them in a CSV file.

        Returns:
        DataFrame: DataFrame containing text chunks and their embeddings.
        """
        filename: str = f"chunks-{self.unique_filename}"
        df = pd.read_csv(filepath_or_buffer=filename, encoding="utf-8")  # pyright: ignore[reportUnknownMemberType]
        df["embeddings"] = df["text"].apply(self.get_embedding)  # pyright: ignore[reportUnknownMemberType]
        df.to_csv(f"embeddings-{self.unique_filename}", encoding="utf-8", index=False)
        return df

    def find_prompt_in_knowledge(self, prompt: str):
        """
        Finds and responds to a prompt based on similarity with embedded knowledge.

        Parameters:
        prompt (str): User input prompt.

        Returns:
        str: Response derived from the most similar chunk in knowledge.
        """
        prompt_embedding = self.get_embedding(prompt)
        df = pd.read_csv(f"embeddings-{self.unique_filename}", encoding="utf-8")  # pyright: ignore[reportUnknownMemberType]
        df["embeddings"] = df["embeddings"].apply(lambda x: np.array(eval(x)))  # type: ignore

        df["similarity"] = df["embeddings"].apply(  # type: ignore
            lambda emb: self.calculate_similarity(prompt_embedding, emb)  # type: ignore
        )

        best_chunk = df.loc[df["similarity"].idxmax(), "text"]

        client = OpenAI(
            base_url="https://openai.vocareum.com/v1", api_key=self.openai_api_key
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are {self.persona}, a knowledge-based assistant. Forget previous context.",
                },
                {
                    "role": "user",
                    "content": f"Answer based only on this information: {best_chunk}. Prompt: {prompt}",
                },
            ],
            temperature=0,
        )

        return response.choices[0].message.content


@dataclass
class EvaluationAgent:
    openai_api_key: str
    persona: str
    evaluation_criteria: str
    worker_agent: WorkerAgent
    max_interactions: int = 10

    def evaluate(self, initial_prompt: str) -> dict[str, Any] | None:
        # This method manages interactions between agents to achieve a solution.
        client = OpenAI(base_url=base_url, api_key=self.openai_api_key)
        prompt_to_evaluate = initial_prompt
        response_from_worker = ""
        evaluation = "No evaluation performed"
        i = -1  # Will be 0 after first iteration

        # TODO: 2 - Set loop to iterate up to the maximum number of interactions:
        for i in range(self.max_interactions):
            print(f"\n--- Interaction {i + 1} ---")

            print(" Step 1: Worker agent generates a response to the prompt")
            print(f"Prompt:\n{prompt_to_evaluate}")
            # TODO: 3 - Obtain a response from the worker agent
            response_from_worker = self.worker_agent.respond(prompt_to_evaluate)
            print(f"Worker Agent Response:\n{response_from_worker}")

            print(" Step 2: Evaluator agent judges the response")
            eval_prompt = (
                f"Does the following answer: {response_from_worker}\n"
                # TODO: 4 - Insert evaluation criteria here
                f"Meet this criteria: {self.evaluation_criteria}\n"
                f"Respond Yes or No, and the reason why it does or doesn't meet the criteria."
            )
            response = client.chat.completions.create(
                model=model,
                # TODO: 5 - Define the message structure sent to the LLM for evaluation (use temperature=0)
                messages=[
                    {"role": "system", "content": self.persona},
                    {"role": "user", "content": eval_prompt},
                ],
                temperature=0,
            )
            if response.choices[0].message.content is None:
                return None
            evaluation = response.choices[0].message.content.strip()
            print(f"Evaluator Agent Evaluation:\n{evaluation}")

            print(" Step 3: Check if evaluation is positive")
            if evaluation.lower().startswith("yes"):
                print("✅ Final solution accepted.")
                break
            else:
                print(" Step 4: Generate instructions to correct the response")
                instructions = f"Provide instructions to fix an answer based on these reasons why it is incorrect: {evaluation}"
                response = client.chat.completions.create(
                    model=model,
                    # TODO: 6 - Define the message structure sent to the LLM to generate correction instructions (use temperature=0)
                    messages=[
                        {"role": "system", "content": self.persona},
                        {"role": "user", "content": eval_prompt},
                    ],
                    temperature=0,
                )
                if response.choices[0].message.content is None:
                    return None
                evaluation = response.choices[0].message.content.strip()
                print(f"Instructions to fix:\n{instructions}")

                print(" Step 5: Send feedback to worker agent for refinement")
                prompt_to_evaluate = (
                    f"The original prompt was: {initial_prompt}\n"
                    f"The response to that prompt was: {response_from_worker}\n"
                    f"It has been evaluated as incorrect.\n"
                    f"Make only these corrections, do not alter content validity: {instructions}"
                )
            # TODO: 7 - Return a dictionary containing the final response, evaluation, and number of iterations
        return {
            "final_response": response_from_worker,
            "final_evaluation": evaluation,
            "iterations": i + 1,
            "success": evaluation.lower().startswith("yes"),
        }


@dataclass
class RoutingAgent:
    openai_api_key: str
    agents: list[WorkerAgent]

    def get_embedding(self, text: str) -> list[float] | None:
        """
        Fetches the embedding vector for given text using OpenAI's embedding API.

        Parameters:
        text (str): Text to embed.

        Returns:
        list: The embedding vector.
        """
        client = OpenAI(
            base_url="https://openai.vocareum.com/v1", api_key=self.openai_api_key
        )
        response = client.embeddings.create(
            model="text-embedding-3-large", input=text, encoding_format="float"
        )
        return response.data[0].embedding

    # TODO: 3 - Define a method to route user prompts to the appropriate agent
    def route(self, user_input: str) -> str:
        """Route user prompts to the appropriate agent based on semantic similarity."""
        # TODO: 4 - Compute the embedding of the user input prompt
        input_emb = self.get_embedding(user_input) or 0.0
        best_agent = None
        best_score = -1

        for agent in self.agents:
            agent_emb = self.get_embedding(agent.description)
            # TODO: 5 - Compute the embedding of the agent description
            if agent_emb is None:
                continue

            similarity = np.dot(input_emb, agent_emb) / (
                np.linalg.norm(input_emb) * np.linalg.norm(agent_emb)
            )
            print(f"{agent.name} = {similarity}")

            # TODO: 6 - Add logic to select the best agent based on the similarity score between the user prompt and the agent descriptions

            if similarity > best_score:  # Fixed: Added missing selection logic
                best_score = similarity
                best_agent = agent
        if best_agent is None:
            return "Sorry, no suitable agent could be selected."

        print(f"[Router] Best agent: {best_agent.name} (score={best_score:.3f})")
        return best_agent.func(user_input)


@dataclass
class ActionPlanningAgent:
    openai_api_key: str
    knowledge: str

    def extract_steps_from_prompt(self, prompt: str):
        # TODO: 2 - Instantiate the OpenAI client using the provided API key
        client = OpenAI(base_url=base_url, api_key=self.openai_api_key)
        # TODO: 3 - Call the OpenAI API to get a response from the "gpt-3.5-turbo" model.
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an action planning agent. Using your knowledge, you extract from the user prompt the steps requested to complete the action the user is asking for. You return the steps as a list. Only return the steps in your knowledge. Forget any previous context. This is your knowledge: {self.knowledge}",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        # Provide the following system prompt along with the user's prompt:
        # "You are an action planning agent. Using your knowledge, you extract from the user prompt the steps requested to complete the action the user is asking for. You return the steps as a list. Only return the steps in your knowledge. Forget any previous context. This is your knowledge: {pass the knowledge here}"

        # TODO: 4 - Extract the response text from the OpenAI API response
        response_text = response.choices[0].message.content or ""

        # TODO: 5 - Clean and format the extracted steps by removing empty lines and unwanted text
        steps = [step.strip() for step in response_text.split("\n") if step.strip()]

        return steps
