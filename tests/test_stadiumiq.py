import os
import pytest
from pydantic import BaseModel, Field

# Ensure correct PYTHONPATH and system keys
from services.groq_client import GroqClient
from services.simulator import StadiumSimulator
from services.output_parser import OutputParser
from models.schemas import CrowdAnalysisResult

class MockResponseModel(BaseModel):
    test_key: str = Field(description="A mock verification parameter")
    status_score: int

def test_simulator_payloads() -> None:
    """Verifies that all simulator context databases yield correct structures."""
    st_context = StadiumSimulator.get_stadium_context()
    assert isinstance(st_context, str)
    assert "Gate Statuses" in st_context
    
    crowd_context = StadiumSimulator.get_crowd_context()
    assert isinstance(crowd_context, dict)
    assert "bottleneck_zones" in crowd_context
    assert crowd_context["risk_level"] == "Yellow"

    acc_context = StadiumSimulator.get_accessibility_context()
    assert isinstance(acc_context, dict)
    assert "sensory_quiet_lounges" in acc_context

    trans_context = StadiumSimulator.get_transport_context()
    assert "metro" in trans_context
    assert trans_context["rideshare"]["surge_pricing_multiplier"] == 1.8

    sust_context = StadiumSimulator.get_sustainability_context()
    assert sust_context["solar_generation_pct"] == 38.4

    ops_context = StadiumSimulator.get_operations_context()
    assert len(ops_context["active_incidents"]) == 3

def test_output_parser_json_extraction() -> None:
    """Verifies that output parser safely locates and parses embedded markdown JSON objects."""
    raw_markdown = (
        "Hello! Here is the operations report you requested:\n\n"
        "```json\n"
        "{\n"
        '  "test_key": "StadiumIQ OK",\n'
        '  "status_score": 98\n'
        "}\n"
        "```\n\n"
        "Let me know if you need physical volunteer dispatches."
    )
    
    parsed = OutputParser.parse_to_model(raw_markdown, MockResponseModel)
    assert parsed.test_key == "StadiumIQ OK"
    assert parsed.status_score == 98

def test_groq_client_init() -> None:
    """Validates that Groq client initializes safely under empty or active conditions."""
    client = GroqClient(api_key="gsk_test_fake_api_key_for_testing")
    assert client.api_key == "gsk_test_fake_api_key_for_testing"
    assert client.is_active is True

    # Test empty API key handling
    empty_client = GroqClient(api_key="")
    # It should fall back safely without throwing raw exceptions during initialization
    assert empty_client.is_active is (bool(os.getenv("GROQ_API_KEY")))
