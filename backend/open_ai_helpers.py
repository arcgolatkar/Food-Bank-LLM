import os
from typing import List, Dict, Optional
import logging
from openai import OpenAI
from openai import OpenAIError

# Use the same logger from main.py
logger = logging.getLogger(__name__)

def initialize_openai_client(api_key: str):
    global openai_client
    if 'openai_client' not in globals():
        openai_client = OpenAI(api_key=api_key)
        logger.info("Initialized OpenAI client successfully.")
    return openai_client

def get_completion(
    key: str,
    prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    stop: Optional[List[str]] = None
) -> Dict:
    """
    Generates a completion response from OpenAI's ChatCompletion endpoint.
    """
    try:
        client = initialize_openai_client(api_key=key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        )

        logger.info(f"Successfully got completion from model: {model}")
        return response

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during completion: {str(e)}")
        raise
