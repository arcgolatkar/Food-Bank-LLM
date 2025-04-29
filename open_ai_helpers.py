import os
from typing import List, Dict, Optional, Union
import logging
from openai import OpenAI


# Configure logging
logger = logging.getLogger(__name__)

    
def get_completion(prompt: str,
                    model: str = "gpt-3.5-turbo", #
                    temperature: float = 0.7,
                    max_tokens: int = 1000,
                    top_p: float = 1.0,
                    frequency_penalty: float = 0.0,
                    presence_penalty: float = 0.0,
                    stop: Optional[List[str]] = None
                ) -> Dict:

    try:
        # print(prompt)
        client = OpenAI()

        response = client.responses.create(
                        model=model,
                        input=prompt
                    )
        # response = client.completions.create(
        #     model=model,
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=temperature,
        #     max_tokens=max_tokens,
        #     top_p=top_p,
        #     frequency_penalty=frequency_penalty,
        #     presence_penalty=presence_penalty,
        #     stop=stop
        # )
        
        print(f"Successfully got completion from {model}")
        return response.output_text
        
    except Exception as e:
        logger.error(f"Error getting completion: {str(e)}")
        print(f"Error getting completion: {str(e)}")
        raise
