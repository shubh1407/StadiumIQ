import re
import json
import orjson
from typing import Type, TypeVar
from pydantic import BaseModel
from loguru import logger

T = TypeVar("T", bound=BaseModel)

class OutputParser:
    """
    Safely extracts, deserializes, and validates JSON strings from raw LLM completions.
    Maps results directly to target Pydantic models.
    """

    @staticmethod
    def extract_json_block(text: str) -> str:
        """
        Locates the first JSON object or markdown codeblock inside a raw text string.
        """
        text = text.strip()
        
        # Regex to locate markdown JSON or raw JSON blocks
        json_pattern = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)
        match = json_pattern.search(text)
        
        if match:
            return match.group(1).strip()
            
        # Fallback: Look for the first occurrence of '{' and last occurrence of '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end+1].strip()
            
        return text

    @classmethod
    def parse_to_model(cls, text: str, model_class: Type[T]) -> T:
        """
        Parses raw text into the requested Pydantic model. If validation fails,
        attempts a defensive reconstruction before raising a clear JSON error.
        """
        cleaned_json = cls.extract_json_block(text)
        
        try:
            # High speed orjson parsing
            data = orjson.loads(cleaned_json)
            logger.info(f"Successfully deserialized raw text to schema class {model_class.__name__}")
            return model_class.model_validate(data)
            
        except (orjson.JSONDecodeError, json.JSONDecodeError) as je:
            logger.warning(f"Fast orjson parser failed. Retrying with default json parser: {str(je)}")
            try:
                data = json.loads(cleaned_json)
                return model_class.model_validate(data)
            except Exception as e:
                logger.error(f"Total failure parsing json block into Pydantic schema: {str(e)}")
                raise ValueError(f"Could not parse valid JSON for model {model_class.__name__}. Raw block was: {cleaned_json}")
                
        except Exception as ve:
            logger.error(f"Pydantic schema validation error: {str(ve)}")
            raise ve
