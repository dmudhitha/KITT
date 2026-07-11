"""
AI Integration Module for VANGUARD Assistant.
Handles connections to OpenAI and local LLM providers (Ollama/LM Studio) with stream support.
"""
import logging
import threading
from typing import Callable, List, Dict, Any, Optional
from openai import OpenAI, APIError, APIConnectionError, AuthenticationError

logger = logging.getLogger("vanguard.ai")


class AIEngine:
    """Manages AI conversation context, LLM client connections, and streaming responses."""

    def __init__(self, config_manager, db_manager):
        self.config = config_manager
        self.db = db_manager
        self.client: Optional[OpenAI] = None
        self.provider = "openai"
        self.model = "gpt-4-turbo"
        self.system_prompt = ""
        
        self.refresh_client()

    def refresh_client(self) -> None:
        """Reloads client configuration from settings.json."""
        self.provider = self.config.get("api", "provider", "openai")
        self.system_prompt = self.config.get(
            "api", "system_prompt",
            "You are VANGUARD, a sophisticated onboard AI desktop assistant. Analytical and professional."
        )

        try:
            if self.provider == "openai":
                import os
                api_key = self.config.get("api", "openai_api_key", "")
                if not api_key:
                    api_key = os.getenv("OPENAI_API_KEY", "")
                if not api_key:
                    api_key = "missing-key-placeholder"
                self.model = self.config.get("api", "openai_model", "gpt-4-turbo")
                # Instantiate standard OpenAI client
                self.client = OpenAI(api_key=api_key)
                logger.info(f"AI Client configured for OpenAI (Model: {self.model})")
            elif self.provider == "local":
                base_url = self.config.get("api", "local_url", "http://localhost:11434/v1")
                self.model = self.config.get("api", "local_model", "llama3")
                # Local provider uses standard client mapped to local server
                self.client = OpenAI(api_key="local-placeholder", base_url=base_url)
                logger.info(f"AI Client configured for Local LLM (URL: {base_url}, Model: {self.model})")
            else:
                logger.error(f"Unknown API provider: {self.provider}")
                self.client = None
        except Exception as e:
            logger.critical(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def send_message_stream(
        self,
        user_message: str,
        chunk_callback: Callable[[str], None],
        complete_callback: Callable[[str], None],
        error_callback: Callable[[str], None]
    ) -> None:
        """
        Sends a query to the LLM in a background thread and streams response chunks.
        Non-blocking to ensure UI responsiveness.
        """
        # Hot-reload configuration changes at runtime
        self.refresh_client()

        if self.provider == "openai":
            key = self.config.get("api", "openai_api_key", "")
            import os
            if not key and not os.getenv("OPENAI_API_KEY"):
                error_callback("AI client not initialized. OpenAI API key is missing. Add your API key in config/settings.json or set provider to 'local' for Ollama.")
                return

        if not self.client:
            error_callback("AI client not initialized. Check configurations.")
            return

        # Start thread
        worker = threading.Thread(
            target=self._stream_worker,
            args=(user_message, chunk_callback, complete_callback, error_callback),
            daemon=True
        )
        worker.start()

    def _stream_worker(
        self,
        user_message: str,
        chunk_callback: Callable[[str], None],
        complete_callback: Callable[[str], None],
        error_callback: Callable[[str], None]
    ) -> None:
        """Background thread worker for streaming completion."""
        try:
            # 1. Fetch conversation history from SQLite
            history_rows = self.db.get_recent_history(limit=10)
            
            # 2. Build completion messages payload
            messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
            
            for row in history_rows:
                # SQLite stores role as 'user'/'assistant'/'system'
                messages.append({"role": row["role"], "content": row["message"]})
            
            # Append current prompt (already committed to DB in UI layer)
            messages.append({"role": "user", "content": user_message})

            # 3. Create stream request
            logger.debug(f"Sending LLM request to provider: {self.provider} ({self.model})")
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                timeout=15.0
            )

            full_response = ""
            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    chunk_callback(token)

            # 4. Trigger completion callback with full aggregated text
            complete_callback(full_response)

        except AuthenticationError as e:
            logger.error(f"API Authentication Error: {e}")
            error_callback("DIALOG FAILURE: API Authentication failed. Verify your API key.")
        except APIConnectionError as e:
            logger.error(f"API Connection Error: {e}")
            error_callback("DIALOG FAILURE: Connection refused. Verify internet connection or local server status.")
        except APIError as e:
            logger.error(f"API General Error: {e}")
            error_callback(f"DIALOG FAILURE: LLM core returned an error: {e.message}")
        except Exception as e:
            logger.error(f"Unhandled exception in LLM worker: {e}")
            error_callback("DIALOG FAILURE: Unhandled exception in AI core router.")
