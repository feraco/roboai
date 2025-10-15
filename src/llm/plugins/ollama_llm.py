import json
import logging
import os
import time
import typing as T

import aiohttp
from pydantic import BaseModel

from llm import LLM, LLMConfig
from llm.function_schemas import convert_function_calls_to_actions
from llm.output_model import CortexOutputModel
from providers.llm_history_manager import LLMHistoryManager

R = T.TypeVar("R", bound=BaseModel)


class OllamaLLM(LLM[R]):
    """
    An Ollama-based Language Learning Model implementation with function call support.

    This class implements the LLM interface for Ollama's local models, handling
    configuration and async API communication. It supports both traditional JSON 
    structured output and function calling.

    Parameters
    ----------
    config : LLMConfig
        Configuration object containing API settings. If not provided, defaults
        will be used.
    available_actions : list[AgentAction], optional
        List of available actions for function call generation. If provided,
        the LLM will use function calls instead of structured JSON output.
    """

    def __init__(
        self,
        config: LLMConfig = LLMConfig(),
        available_actions: T.Optional[T.List] = None,
    ):
        """
        Initialize the Ollama LLM instance.

        Parameters
        ----------
        config : LLMConfig, optional
            Configuration settings for the LLM.
        available_actions : list[AgentAction], optional
            List of available actions for function calling.
        """
        super().__init__(config, available_actions)

        # Get base URL from config or environment
        self.base_url = config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        if not config.model:
            self._config.model = "llama3"

        # Initialize session for HTTP requests
        self.session = None

        # Initialize history manager (simplified for Ollama)
        self.history_manager = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def ask(
        self, prompt: str, messages: T.List[T.Dict[str, T.Any]] = []
    ) -> R | None:
        """
        Send a prompt to the Ollama API and get a structured response.

        Parameters
        ----------
        prompt : str
            The input prompt to send to the model.
        messages : List[Dict[str, str]]
            List of message dictionaries to send to the model.

        Returns
        -------
        R or None
            Parsed response matching the output_model structure, or None if
            parsing fails.
        """
        try:
            logging.info(f"Ollama LLM input: {prompt}")
            logging.info(f"Ollama LLM messages: {messages}")

            self.io_provider.llm_start_time = time.time()
            self.io_provider.set_llm_prompt(prompt)

            # Format messages for Ollama
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Add the current prompt
            formatted_messages.append({"role": "user", "content": prompt})

            # Prepare the request payload
            payload = {
                "model": self._config.model or "llama3",
                "messages": formatted_messages,
                "stream": False,
                "format": "json" if not self.function_schemas else None,
            }

            # Add function calling support if available
            if self.function_schemas:
                # Convert function schemas to Ollama format
                tools_prompt = self._create_tools_prompt()
                payload["messages"][-1]["content"] = f"{prompt}\n\n{tools_prompt}"

            session = await self._get_session()
            
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self._config.timeout or 30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"Ollama API error {response.status}: {error_text}")
                    return None

                result = await response.json()
                
                self.io_provider.llm_end_time = time.time()

                # Extract the response content
                if "message" in result and "content" in result["message"]:
                    content = result["message"]["content"]
                    
                    # Try to parse function calls if function schemas are available
                    if self.function_schemas:
                        actions = self._parse_function_calls(content)
                        if actions:
                            result_obj = CortexOutputModel(actions=actions)
                            logging.info(f"Ollama LLM function call output: {result_obj}")
                            return T.cast(R, result_obj)
                    
                    # Try to parse as JSON for structured output
                    try:
                        json_content = json.loads(content)
                        if "actions" in json_content:
                            result_obj = CortexOutputModel(**json_content)
                            logging.info(f"Ollama LLM JSON output: {result_obj}")
                            return T.cast(R, result_obj)
                    except json.JSONDecodeError:
                        logging.warning(f"Could not parse Ollama response as JSON: {content}")

                return None

        except Exception as e:
            logging.error(f"Ollama API error: {e}")
            return None

    def _create_tools_prompt(self) -> str:
        """Create a prompt that describes available tools/functions."""
        if not self.function_schemas:
            return ""
        
        tools_desc = "You have access to the following functions. Respond with function calls in JSON format:\n\n"
        
        for schema in self.function_schemas:
            if "function" in schema:
                func = schema["function"]
                tools_desc += f"Function: {func['name']}\n"
                tools_desc += f"Description: {func.get('description', 'No description')}\n"
                if "parameters" in func:
                    tools_desc += f"Parameters: {json.dumps(func['parameters'], indent=2)}\n"
                tools_desc += "\n"
        
        tools_desc += "Respond with function calls in this format:\n"
        tools_desc += '{"function_calls": [{"function": {"name": "function_name", "arguments": "{\\"param\\": \\"value\\"}"}}]}\n'
        
        return tools_desc

    def _parse_function_calls(self, content: str) -> T.List:
        """Parse function calls from Ollama response."""
        try:
            # Try to extract JSON from the response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                parsed = json.loads(json_str)
                
                if "function_calls" in parsed:
                    return convert_function_calls_to_actions(parsed["function_calls"])
                    
        except Exception as e:
            logging.error(f"Error parsing function calls from Ollama: {e}")
        
        return []

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session and not self.session.closed:
            await self.session.close()