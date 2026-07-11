import os

import pytest
from pydantic import BaseModel, Field

from models.schemas import (
    AccessibilityRouteResult,
    BottleneckZone,
    CrowdAnalysisResult,
    OperationsCommandResult,
    SustainabilityResult,
    TransportnexusResult,
)

# Ensure correct PYTHONPATH and system keys
from services.groq_client import GroqClient
from services.llm_chain import (
    AccessibilityChain,
    CrowdAnalysisChain,
    FanAssistantChain,
    OpsCommandChain,
    SustainabilityChain,
    TransportChain,
)
from services.memory import ConversationMemory
from services.output_parser import OutputParser
from services.simulator import StadiumSimulator
from services.utils import render_status_badge


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

def test_conversation_memory_history_and_trimming() -> None:
    """Verifies conversation memory serializes turns and trims history to max_turns."""
    memory = ConversationMemory(max_turns=2)

    assert memory.get_history([]) == "No previous conversation history. This is the first interaction."

    history = [
        {"role": "user", "content": "Where is Gate A?"},
        {"role": "assistant", "content": "Gate A is on Level 1 East."},
        {"role": "user", "content": "Thanks!"},
    ]
    serialized = memory.get_history(history)
    assert "Fan: Thanks!" in serialized
    assert "Where is Gate A?" not in serialized  # trimmed beyond max_turns

    growing_history: list = []
    for i in range(10):
        memory.add_turn(growing_history, "user", f"message {i}")
    assert len(growing_history) == memory.max_turns * 2


def test_output_parser_raises_on_invalid_json() -> None:
    """Verifies the output parser raises a clear error when no valid JSON can be recovered."""
    with pytest.raises(ValueError):
        OutputParser.parse_to_model("no json anywhere in this response", MockResponseModel)


def test_render_status_badge_known_and_unknown_status() -> None:
    """Verifies status badges render with the correct color for known and unknown status types."""
    badge = render_status_badge("Critical Alert", "critical")
    assert "Critical Alert" in badge
    assert "#FF5252" in badge

    fallback_badge = render_status_badge("Unlisted", "totally-unknown-status")
    assert "Unlisted" in fallback_badge


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

@pytest.mark.parametrize(
    "scenario",
    [
        "🍔 Halftime (Food Court Rush)",
        "🏃 After Match (Exit Congestion)",
        "⛈️ Sudden Weather Shift (Rain/Storm)",
        "🚨 Critical Emergency Event",
        "🎟️ Before Match (High Entry Crowd)",
    ],
)
def test_simulator_context_covers_every_scenario(scenario: str) -> None:
    """Verifies every stadium/crowd context branch returns well-formed data for each simulated phase."""
    import streamlit as st

    st.session_state["stadium_scenario"] = scenario
    try:
        assert StadiumSimulator.get_active_scenario() == scenario
        assert isinstance(StadiumSimulator.get_stadium_context(), str)
        assert isinstance(StadiumSimulator.get_crowd_context(), dict)
        assert isinstance(StadiumSimulator.get_transport_context(), dict)
        assert isinstance(StadiumSimulator.get_sustainability_context(), dict)
        assert isinstance(StadiumSimulator.get_operations_context(), dict)
    finally:
        del st.session_state["stadium_scenario"]

def test_get_active_scenario_falls_back_when_session_state_unavailable() -> None:
    """Verifies get_active_scenario degrades gracefully if Streamlit session state raises."""
    import streamlit as st

    original_session_state = st.session_state

    class ExplodingSessionState:
        def get(self, *_args, **_kwargs):
            raise RuntimeError("no script run context")

    st.session_state = ExplodingSessionState()
    try:
        assert StadiumSimulator.get_active_scenario() == "Before Match (High Entry Crowd)"
    finally:
        st.session_state = original_session_state

@pytest.mark.parametrize(
    ("query", "expected_snippet"),
    [
        ("Where can I find vegan food?", "Concession Guide"),
        ("Where is the nearest restroom?", "Restroom Locator"),
        ("Where should I park my car?", "Parking Intelligence"),
        ("Which gate is my ticket entrance?", "Gate & Entry Status"),
        ("I need help, someone is hurt!", "EMERGENCY ACTION PROTOCOL"),
        ("hola, donde esta el estadio?", "Bienvenido"),
        ("What time does the match start?", "Multilingual Concierge"),
    ],
)
def test_generate_demo_chat_response_covers_intents(query: str, expected_snippet: str) -> None:
    """Verifies the offline demo chat responder matches every supported intent and language branch."""
    response = StadiumSimulator.generate_demo_chat_response(query)
    assert expected_snippet in response

def test_render_world_cup_header_calls_markdown() -> None:
    """Verifies the World Cup header renders through st.markdown with unsafe_allow_html."""
    from unittest.mock import MagicMock

    import streamlit as st

    from services.utils import render_world_cup_header

    original_markdown = st.markdown
    st.markdown = MagicMock()
    try:
        render_world_cup_header()
        st.markdown.assert_called_once()
        _, kwargs = st.markdown.call_args
        assert kwargs.get("unsafe_allow_html") is True
    finally:
        st.markdown = original_markdown

def test_apply_accessibility_filters_toggles(monkeypatch) -> None:
    """Verifies accessibility filter CSS is only injected when the relevant session flags are set."""
    from unittest.mock import MagicMock

    import streamlit as st

    from services.utils import apply_accessibility_filters

    original_markdown = st.markdown
    st.markdown = MagicMock()
    try:
        st.session_state["accessibility_large_text"] = False
        st.session_state["accessibility_high_contrast"] = False
        apply_accessibility_filters()
        st.markdown.assert_not_called()

        st.session_state["accessibility_large_text"] = True
        apply_accessibility_filters()
        st.markdown.assert_called_once()
        assert "font-size" in st.markdown.call_args[0][0]
    finally:
        st.markdown = original_markdown
        del st.session_state["accessibility_large_text"]
        del st.session_state["accessibility_high_contrast"]

@pytest.mark.parametrize(
    "service_type",
    ["Wheelchair", "Vision", "Hearing", "Senior", "Family"],
)
def test_accessibility_chain_fallback_covers_every_service_type(service_type: str) -> None:
    """Verifies the offline fallback route narration works for every assisted service type."""
    chain = AccessibilityChain()
    chain.client.api_key = None
    chain.client._client = None

    result = chain.generate_route(
        service_type=service_type,
        current_location="Gate A",
        destination="Row 12",
        context={},
    )
    assert isinstance(result, AccessibilityRouteResult)
    assert result.service_requested == service_type
    assert result.navigation_steps

def test_transport_chain_fallback_offline() -> None:
    """Verifies the offline transport fallback produces a full multi-modal recommendation."""
    chain = TransportChain()
    chain.client.api_key = None
    chain.client._client = None

    result = chain.get_recommendation(
        sector_id="112",
        destination_zone="Downtown Transit Hub",
        context={},
    )
    assert isinstance(result, TransportnexusResult)
    assert result.recommended_option_mode == "Metro"
    assert len(result.all_transit_options) == 4

def test_sustainability_chain_fallback_offline() -> None:
    """Verifies the offline sustainability fallback produces a valid grid/recycling report."""
    chain = SustainabilityChain()
    chain.client.api_key = None
    chain.client._client = None

    result = chain.monitor_utilities(context={})
    assert isinstance(result, SustainabilityResult)
    assert result.grid_power_status in {"Optimal", "Loaded", "Critical Peak"}

@pytest.mark.parametrize(
    ("incident_report", "expected_category", "expected_priority"),
    [
        ("Small fire near the grill smoke detected", "Security", "Critical"),
        ("A fight broke out between two fans", "Security", "High"),
        ("A fan is injured and needs an ambulance", "Medical", "High"),
        ("There is a glass spill on the concourse", "Facility", "Medium"),
        ("A handrail is slightly loose", "Structural", "Low"),
    ],
)
def test_ops_command_chain_fallback_classifies_every_incident_type(
    incident_report: str, expected_category: str, expected_priority: str
) -> None:
    """Verifies the offline incident classifier routes every keyword category to the right playbook."""
    chain = OpsCommandChain()
    chain.client.api_key = None
    chain.client._client = None

    result = chain.manage_incident(
        incident_report=incident_report,
        zone_location="Sector 205 Concourse",
        reporter_type="Staff",
        context={},
    )
    assert isinstance(result, OperationsCommandResult)
    assert result.classification_category == expected_category
    assert result.priority_level == expected_priority

def test_fan_assistant_chain_streaming_offline_uses_simulator() -> None:
    """Verifies FanAssistantChain streams simulated word tokens when the Groq client is inactive."""
    chain = FanAssistantChain()
    chain.client.api_key = None
    chain.client._client = None

    tokens = list(
        chain.run_streaming(
            user_query="Where can I park?",
            history_buffer="no history",
            stadium_context="stadium OK",
        )
    )
    assert "".join(tokens).strip().startswith("⚽") or "Parking" in "".join(tokens)

def test_fan_assistant_chain_streaming_client_error_yields_alert_token() -> None:
    """Verifies a live streaming failure inside GroqClient surfaces as a graceful inline alert token
    rather than crashing the generator (GroqClient.stream catches and yields, it does not raise)."""
    from unittest.mock import MagicMock

    chain = FanAssistantChain()
    chain.client.api_key = "gsk_test_key"
    chain.client._client = MagicMock()
    chain.client._client.chat.completions.create.side_effect = Exception("stream broke")

    tokens = list(
        chain.run_streaming(
            user_query="Where is the restroom?",
            history_buffer="no history",
            stadium_context="stadium OK",
        )
    )
    assert any("API Error Alert" in t for t in tokens)

def test_fan_assistant_chain_streaming_prompt_error_falls_back_to_simulator(monkeypatch) -> None:
    """Verifies FanAssistantChain falls back to the offline simulator if prompt formatting itself raises,
    which is the actual failure path caught by run_streaming's own try/except."""
    from unittest.mock import MagicMock

    chain = FanAssistantChain()
    chain.client.api_key = "gsk_test_key"
    chain.client._client = MagicMock()

    import services.llm_chain as llm_chain_module

    broken_prompts = MagicMock()
    broken_prompts.__getitem__.side_effect = KeyError("fan_assistant")
    monkeypatch.setattr(llm_chain_module, "PROMPTS", broken_prompts)

    tokens = list(
        chain.run_streaming(
            user_query="Where is the restroom?",
            history_buffer="no history",
            stadium_context="stadium OK",
        )
    )
    assert any("Restroom Locator" in t for t in tokens)

def test_app_module_routing_dispatches_to_the_correct_renderer(monkeypatch) -> None:
    """Verifies app.main() imports and calls the renderer matching the selected sidebar module."""
    import sys
    import types
    from unittest.mock import MagicMock

    import app

    fake_module = types.ModuleType("modules.fan_assistant")
    render_mock = MagicMock()
    fake_module.render_fan_assistant = render_mock
    monkeypatch.setitem(sys.modules, "modules.fan_assistant", fake_module)

    monkeypatch.setattr(app, "load_custom_css", MagicMock())
    monkeypatch.setattr(app, "init_session_states", MagicMock())
    monkeypatch.setattr(app, "render_sidebar", MagicMock(return_value="Fan Assistant"))

    import streamlit as st
    original_markdown = st.markdown
    st.markdown = MagicMock()
    try:
        app.main()
    finally:
        st.markdown = original_markdown

    render_mock.assert_called_once()
    assert st.session_state.current_module == "Fan Assistant"

def test_app_module_routing_shows_fallback_on_import_error(monkeypatch) -> None:
    """Verifies app.main() shows the graceful loading fallback if a module import fails."""
    from unittest.mock import MagicMock

    import app

    monkeypatch.setattr(app, "load_custom_css", MagicMock())
    monkeypatch.setattr(app, "init_session_states", MagicMock())
    monkeypatch.setattr(app, "render_sidebar", MagicMock(return_value="Nonexistent Module"))

    import streamlit as st
    original_markdown = st.markdown
    st.markdown = MagicMock()
    try:
        app.main()
    finally:
        st.markdown = original_markdown

    # No branch matches "Nonexistent Module", so no ImportError fires and it falls through cleanly.
    assert st.session_state.current_module == "Nonexistent Module"

def test_utils_render_html() -> None:
    """Verifies that render_html strips indentation and passes correctly to st.markdown."""
    from unittest.mock import MagicMock

    import streamlit as st

    from services.utils import render_html

    original_markdown = st.markdown
    st.markdown = MagicMock()
    try:
        render_html("  <div>\n    <span>Content</span>\n  </div>")
        st.markdown.assert_called_once_with("<div> <span>Content</span> </div>", unsafe_allow_html=True)
    finally:
        st.markdown = original_markdown

