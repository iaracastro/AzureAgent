import os
from typing import Optional
import pandas as pd
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

def build_message(data: list[str]) -> str:
    quotes = '"""'
    separator = f"\n{quotes}\n\n{quotes}\n"
    return quotes + "\n" + separator.join(data) + "\n" + quotes


def get_response(client: AgentsClient, thread_id: str) -> str:
    # Messages are listed from newest to oldest
    for message in client.messages.list(thread_id):
        if message.role == "assistant":
            return message.content[0].text.value
    
    raise RuntimeError("Could not find the assistant response message.")


def run_agent(
    data: list[str],
    agent_id: Optional[str] = None,
    project_endpoint: Optional[str] = None,
    temperature: float = 0.8,
) -> str:
    """Run the Azure Foundry agent with the provided list of texts and return its response.

    This function reads `AGENT_ID` and `PROJECT_ENDPOINT` from the environment if not provided.
    Raises ValueError when required configuration is missing, RuntimeError on auth or API failures.
    """
    # Load env again in case Streamlit changed it or user provided in UI
    load_dotenv(override=True)
    AGENT_ID = agent_id or os.getenv("AGENT_ID")
    PROJECT_ENDPOINT = project_endpoint or os.getenv("PROJECT_ENDPOINT")

    if not AGENT_ID or not PROJECT_ENDPOINT:
        raise ValueError("Missing AGENT_ID or PROJECT_ENDPOINT environment variables.")

    try:
        credential = DefaultAzureCredential()
        client = AgentsClient(PROJECT_ENDPOINT, credential)
    except Exception as exc:
        raise RuntimeError(f"Authentication failed: {exc}")

    message = build_message(data)

    try:
        response = client.create_thread_and_process_run(
            agent_id=AGENT_ID,
            thread={"messages": [{"role": "user", "content": message}]},
            temperature=temperature,
            polling_interval=1,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to send request to agent: {exc}")

    try:
        return get_response(client, response.thread_id)
    except Exception as exc:
        raise RuntimeError(f"Failed to get agent response: {exc}")

