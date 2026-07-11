import os
import pytest
from pydantic import BaseModel, Field

# Ensure correct PYTHONPATH and system keys
from services.groq_client import GroqClient
from services.simulator import StadiumSimulator
from services.output_parser import OutputParser
from services.memory import ConversationMemory
from services.utils import render_status_badge
from services.llm_chain import (
    FanAssistantChain,
    CrowdAnalysisChain,
    AccessibilityChain,
    TransportChain,
    SustainabilityChain,
    OpsCommandChain
)
from models.schemas import (
    CrowdAnalysisResult,
    AccessibilityRouteResult,
    TransportnexusResult,
    SustainabilityResult,
    OperationsCommandResult,
    BottleneckZone
)

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
    assert empty_client.is_active is (bool(os.getenv("GROQ_API_KEY")))

def test_fan_assistant_chain_fallback() -> None:
    """Verifies that the fan assistant chain streams properly when Groq client is inactive."""
    chain = FanAssistantChain()
    # Force client to be inactive to test the high-fidelity simulator fallback path by setting _client = None
    chain.client._client = None
    
    stream_generator = chain.run_streaming(
        user_query="vegan food",
        history_buffer="No previous history",
        stadium_context="Sample context"
    )
    
    tokens = list(stream_generator)
    assert len(tokens) > 0
    full_text = "".join(tokens)
    assert "GreenBites" in full_text
    assert "Gate B" in full_text

def test_crowd_analysis_chain_fallback() -> None:
    """Verifies that the crowd analysis chain returns a valid CrowdAnalysisResult model in fallback mode."""
    chain = CrowdAnalysisChain()
    chain.client._client = None
    
    raw_context = StadiumSimulator.get_crowd_context()
    result = chain.analyze(raw_context)
    
    assert isinstance(result, CrowdAnalysisResult)
    # The simulator mock data should have overall risk level Yellow
    assert result.overall_risk_level == "Yellow"
    assert result.crowd_density_score == 8.7
    assert len(result.active_bottlenecks) == 3
    assert "Gate-D-Ingress" in [b.zone_id for b in result.active_bottlenecks]

def test_accessibility_chain_fallback() -> None:
    """Verifies that the accessibility chain produces a custom AccessibilityRouteResult model in fallback mode."""
    chain = AccessibilityChain()
    chain.client._client = None
    
    raw_context = StadiumSimulator.get_accessibility_context()
    result = chain.generate_route(
        service_type="♿ Wheelchair Step-Free Guide",
        current_location="Entrance Plaza A",
        destination="Sector 112 Row K Seat 14",
        context=raw_context
    )
    
    assert isinstance(result, AccessibilityRouteResult)
    assert result.service_requested == "♿ Wheelchair Step-Free Guide"
    assert any("Elevator #3" in s.instruction for s in result.navigation_steps)
    assert len(result.navigation_steps) == 4
    assert result.navigation_steps[0].is_step_free is True
    assert result.companion_team_notified is True

def test_transport_chain_fallback() -> None:
    """Verifies that the transport chain computes transit schedules correctly in fallback mode."""
    chain = TransportChain()
    chain.client._client = None
    
    raw_context = StadiumSimulator.get_transport_context()
    result = chain.get_recommendation(
        sector_id="Sector 108",
        destination_zone="Central Hub",
        context=raw_context
    )
    
    assert isinstance(result, TransportnexusResult)
    assert result.origin_sector == "Sector 108"
    assert result.target_destination == "Central Hub"
    assert result.recommended_option_mode == "Metro"
    assert len(result.all_transit_options) == 4
    assert result.all_transit_options[0].mode == "Metro"
    assert result.all_transit_options[0].estimated_duration_mins in [15, 18, 28]

def test_sustainability_chain_fallback() -> None:
    """Verifies that the sustainability chain maps power grid states and metrics in fallback mode."""
    chain = SustainabilityChain()
    chain.client._client = None
    
    raw_context = StadiumSimulator.get_sustainability_context()
    result = chain.monitor_utilities(raw_context)
    
    assert isinstance(result, SustainabilityResult)
    assert result.grid_power_status == "Optimal"
    assert result.carbon_offset_percentage == 38.4
    assert result.recycling_compliance_score == 88
    assert len(result.fan_challenges) == 2

def test_operations_command_chain_fallback() -> None:
    """Verifies that the operations chain prioritizes reports and produces crew briefings in fallback mode."""
    chain = OpsCommandChain()
    chain.client._client = None
    
    raw_context = StadiumSimulator.get_operations_context()
    
    # Test high priority mapping (due to medical dehydrated keywords)
    result_high = chain.manage_incident(
        incident_report="Faint fan dehydration issue",
        zone_location="Sector 205",
        reporter_type="Volunteer",
        context=raw_context
    )
    assert isinstance(result_high, OperationsCommandResult)
    assert result_high.priority_level == "High"
    assert result_high.dispatch_action_code == "CODE-RED-EMS"
    
    # Test lower priority mapping
    result_med = chain.manage_incident(
        incident_report="Paper towels needed in restroom Level 1 East",
        zone_location="Sector 108",
        reporter_type="Fan",
        context=raw_context
    )
    assert result_med.priority_level == "Low"
    assert result_med.dispatch_action_code == "CODE-GREY-FACILITY"

def test_conversation_memory() -> None:
    """Verifies that ConversationMemory serializes and manages chat history buffer correctly."""
    mem = ConversationMemory(max_turns=3)
    
    history = []
    assert mem.get_history(history) == "No previous conversation history. This is the first interaction."
    
    mem.add_turn(history, "user", "Hello there")
    mem.add_turn(history, "assistant", "Hi, how can I help you?")
    
    serialized = mem.get_history(history)
    assert "Fan: Hello there" in serialized
    assert "Assistant: Hi, how can I help you?" in serialized
    
    # Exceed limit to test trim-down
    mem.add_turn(history, "user", "Query 2")
    mem.add_turn(history, "assistant", "Answer 2")
    mem.add_turn(history, "user", "Query 3")
    mem.add_turn(history, "assistant", "Answer 3")
    mem.add_turn(history, "user", "Query 4")
    mem.add_turn(history, "assistant", "Answer 4")
    
    # History list should keep at most max_turns * 2 (which is 6 items)
    assert len(history) <= 6

def test_pydantic_invalid_data() -> None:
    """Ensures that invalid data throws clear validation errors for our models."""
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        # BottleneckZone density_index must be float, but let's try sending list
        BottleneckZone(zone_id="ZoneA", density_index=[1.2], status="Stable", flow_rate="10 people/min")

def test_utils_render_helpers() -> None:
    """Verifies HTML status badge helper output structure."""
    badge_html = render_status_badge("Critical Warning", "critical")
    assert "background-color: rgba(244, 67, 54, 0.15)" in badge_html
    assert "#FF5252" in badge_html
    assert "Critical Warning" in badge_html

def test_groq_client_health() -> None:
    """Verifies the GroqClient.health checks mock connectivity successfully."""
    from unittest.mock import MagicMock
    client = GroqClient(api_key="gsk_test_key")
    assert client.is_active is True
    
    # Mock chat completion return
    mock_completion = MagicMock()
    client._client.chat.completions.create = MagicMock(return_value=mock_completion)
    
    assert client.health() is True
    client._client.chat.completions.create.assert_called_once()

def test_groq_client_generate() -> None:
    """Verifies the GroqClient.generate creates messages and returns text successfully."""
    from unittest.mock import MagicMock
    client = GroqClient(api_key="gsk_test_key")
    
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked Response Text"
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    client._client.chat.completions.create = MagicMock(return_value=mock_completion)
    
    res = client.generate(messages=[{"role": "user", "content": "Hello"}])
    assert res == "Mocked Response Text"

def test_base_stadium_chain_success_path() -> None:
    """Verifies that the base chain successfully queries the active Groq client and parses JSON."""
    from unittest.mock import MagicMock
    chain = CrowdAnalysisChain()
    chain.client.api_key = "gsk_test_key"
    chain.client._client = MagicMock()
    
    # Mock response containing structured JSON conforming to CrowdAnalysisResult
    mock_choice = MagicMock()
    mock_choice.message.content = (
        "```json\n"
        "{\n"
        '  "overall_risk_level": "Green",\n'
        '  "crowd_density_score": 2.3,\n'
        '  "active_bottlenecks": [],\n'
        '  "system_alerts": ["All gates clear"],\n'
        '  "tactical_recommendations": ["No actions required"],\n'
        '  "reason": "Clear gate flow indices",\n'
        '  "confidence_score": 98.0,\n'
        '  "expected_impact": "Zero bottlenecks during pre-game",\n'
        '  "alternative_recommendation": "Maintain baseline security level"\n'
        "}\n"
        "```"
    )
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    chain.client._client.chat.completions.create = MagicMock(return_value=mock_completion)
    
    result = chain.analyze(crowd_context={})
    assert isinstance(result, CrowdAnalysisResult)
    assert result.overall_risk_level == "Green"
    assert result.crowd_density_score == 2.3
    assert "All gates clear" in result.system_alerts

def test_base_stadium_chain_exception_path() -> None:
    """Verifies that the base chain falls back to simulator when Groq client raises an Exception."""
    from unittest.mock import MagicMock
    chain = CrowdAnalysisChain()
    chain.client.api_key = "gsk_test_key"
    chain.client._client = MagicMock()
    
    # Force exception during create call
    chain.client._client.chat.completions.create.side_effect = Exception("Groq connection timeout")
    
    # Should fall back to the fallback_func gracefully
    result = chain.analyze(crowd_context={})
    assert isinstance(result, CrowdAnalysisResult)
    # Simulator overall risk level defaults to Yellow
    assert result.overall_risk_level == "Yellow"

def test_fan_assistant_chain_streaming_active() -> None:
    """Verifies that FanAssistantChain streams tokens when the client is active."""
    from unittest.mock import MagicMock
    chain = FanAssistantChain()
    chain.client.api_key = "gsk_test_key"
    chain.client._client = MagicMock()
    
    # Mock chunks
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = "Hello "
    
    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = "world!"
    
    chain.client._client.chat.completions.create = MagicMock(return_value=[mock_chunk1, mock_chunk2])
    
    tokens = list(chain.run_streaming(
        user_query="hi",
        history_buffer="no history",
        stadium_context="stadium OK"
    ))
    
    assert tokens == ["Hello ", "world!"]

def test_utils_render_html() -> None:
    """Verifies that render_html strips indentation and passes correctly to st.markdown."""
    from services.utils import render_html
    import streamlit as st
    from unittest.mock import MagicMock
    
    original_markdown = st.markdown
    st.markdown = MagicMock()
    try:
        render_html("  <div>\n    <span>Content</span>\n  </div>")
        st.markdown.assert_called_once_with("<div> <span>Content</span> </div>", unsafe_allow_html=True)
    finally:
        st.markdown = original_markdown

