import os
import sys
import time
from typing import Generator, Optional, Dict, Any
from groq import Groq, APIError, APITimeoutError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger

# Configure Loguru logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
)

class GroqClient:
    """
    Enterprise-grade gateway client for the Groq API.
    Utilizes tenacity for exponential backoff retries, loguru for observability,
    and supports synchronous/streaming generations under 'llama-3.3-70b-versatile'.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initializes the Groq client. Never hardcodes secrets; prioritizes env variables.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = "llama-3.3-70b-versatile"
        self._client: Optional[Groq] = None

        if self.api_key:
            try:
                self._client = Groq(api_key=self.api_key)
                logger.info("Successfully initialized Groq API gateway.")
            except Exception as e:
                logger.error(f"Error instantiating Groq client SDK: {str(e)}")
        else:
            logger.warning("GROQ_API_KEY env variable missing. Operating exclusively in High-Fidelity Demo Mode.")

    @property
    def is_active(self) -> bool:
        """Returns True if the underlying client is initialized with credentials."""
        return self._client is not None

    def health(self) -> bool:
        """
        Checks connectivity with the Groq service by running a fast, low-cost verification call.
        """
        if not self.is_active:
            return False
        try:
            # Low latency, zero cost health trigger
            self._client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Ping"}],
                max_tokens=1
            )
            logger.info("Groq API health check passed.")
            return True
        except Exception as e:
            logger.error(f"Groq API health check failed: {str(e)}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"API warning: Retry attempt {retry_state.attempt_number} due to rate-limiting or network timeout."
        )
    )
    def generate(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates a completed response using Llama-3.3-70b-versatile.
        Leverages retry mechanisms for high operational reliability.
        """
        if not self.is_active:
            raise ValueError("Groq client not initialized. Ensure GROQ_API_KEY is supplied.")

        logger.info(f"Dispatching generation request to Groq (temperature={temperature}, max_tokens={max_tokens})")
        start_time = time.perf_counter()

        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                params["response_format"] = response_format

            response = self._client.chat.completions.create(**params)
            latency = time.perf_counter() - start_time
            logger.info(f"Generation response received in {latency:.4f} seconds.")
            return response.choices[0].message.content or ""

        except RateLimitError as rle:
            logger.error(f"Groq rate limit exceeded: {str(rle)}")
            raise rle
        except APITimeoutError as te:
            logger.error(f"Groq gateway network timeout: {str(te)}")
            raise te
        except APIError as ae:
            logger.error(f"Groq API generic failure: {str(ae)}")
            raise ae
        except Exception as e:
            logger.critical(f"Unexpected JSON, payload, or execution crash: {str(e)}")
            raise e

    def stream(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1000
    ) -> Generator[str, None, None]:
        """
        Streams generated completion tokens continuously to provide responsive UX.
        Does not use automatic retry loops to prevent token stream fragmentation;
        errors are captured and logged gracefully.
        """
        if not self.is_active:
            raise ValueError("Groq client not initialized. Ensure GROQ_API_KEY is supplied.")

        logger.info(f"Initiating completion stream (temperature={temperature}, max_tokens={max_tokens})")
        
        try:
            stream_obj = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream_obj:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
                    
        except RateLimitError as rle:
            logger.error(f"RateLimitError encountered in token stream: {str(rle)}")
            yield f"\n\n⚠️ **[Rate Limit Alert]**: {str(rle)}"
        except APITimeoutError as te:
            logger.error(f"Network timeout in token stream: {str(te)}")
            yield f"\n\n⚠️ **[Network Timeout Alert]**: {str(te)}"
        except Exception as e:
            logger.error(f"Unknown stream token crash: {str(e)}")
            yield f"\n\n⚠️ **[API Error Alert]**: {str(e)}"
