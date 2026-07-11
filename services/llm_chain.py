import os
from typing import Generator, Dict, Any, List, Type, TypeVar
from pydantic import BaseModel
from loguru import logger

from services.groq_client import GroqClient
from services.prompt_manager import PROMPTS
from services.output_parser import OutputParser
from services.simulator import StadiumSimulator

from models.schemas import (
    CrowdAnalysisResult,
    AccessibilityRouteResult,
    TransportnexusResult,
    SustainabilityResult,
    OperationsCommandResult
)

T = TypeVar("T", bound=BaseModel)

class BaseStadiumChain:
    """
    Base operational chain that coordinates prompt retrieval, context injection,
    Groq interaction, and fallback orchestration.
    """
    def __init__(self) -> None:
        self.client = GroqClient()

    def _execute_structured_chain(
        self,
        prompt_key: str,
        formatting_args: Dict[str, Any],
        schema_model: Type[T],
        fallback_func: Any
    ) -> T:
        """
        Coordinates standard prompting, JSON generation, output parsing, and resilient fallbacks.
        """
        if not self.client.is_active:
            logger.warning(f"Groq API client is inactive. Triggering fast simulator fallback for chain: {prompt_key}")
            return schema_model.model_validate(fallback_func())

        try:
            # Load template and construct prompts
            template = PROMPTS[prompt_key]
            user_prompt = template.format(**formatting_args)
            
            # Inject structured formatting constraints
            system_prompt_with_format = (
                f"{template.system_prompt}\n\n"
                f"Mandatory: Return the result strictly as a valid JSON object matching this schema definition:\n"
                f"{schema_model.model_json_schema()}"
            )
            
            messages = [
                {"role": "system", "content": system_prompt_with_format},
                {"role": "user", "content": user_prompt}
            ]
            
            raw_response = self.client.generate(
                messages=messages,
                temperature=0.1,  # Low temperature for highly deterministic JSON mapping
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Parse response into target Pydantic model
            return OutputParser.parse_to_model(raw_response, schema_model)

        except Exception as e:
            logger.critical(f"Chain exception on key '{prompt_key}': {str(e)}. Triggering simulator fallback.")
            try:
                return schema_model.model_validate(fallback_func())
            except Exception as fe:
                logger.error(f"Simulator validation crash: {str(fe)}")
                raise fe


# ==============================================================================
# Dedicated Specific Chains for Modules
# ==============================================================================

class FanAssistantChain(BaseStadiumChain):
    """Handles fan chatbot conversations with history context and token streaming support."""
    
    def run_streaming(
        self,
        user_query: str,
        history_buffer: str,
        stadium_context: str
    ) -> Generator[str, None, None]:
        """Streams chatbot tokens with automatic fallback to high-fidelity simulated tokens."""
        if not self.client.is_active:
            logger.warning("Groq API client inactive. Streaming simulated response tokens.")
            simulated_text = StadiumSimulator.generate_demo_chat_response(user_query)
            # Yield simulated words slowly to emulate AI streams
            import time
            for word in simulated_text.split(" "):
                yield word + " "
                time.sleep(0.04)
            return

        try:
            template = PROMPTS["fan_assistant"]
            user_prompt = template.format(
                user_query=user_query,
                history=history_buffer,
                stadium_context=stadium_context
            )
            
            messages = [
                {"role": "system", "content": template.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            for chunk in self.client.stream(messages=messages, temperature=0.5, max_tokens=800):
                yield chunk
                
        except Exception as e:
            logger.error(f"FanAssistant stream error: {str(e)}. Defaulting to simulator static stream.")
            simulated_text = StadiumSimulator.generate_demo_chat_response(user_query)
            yield simulated_text


class CrowdAnalysisChain(BaseStadiumChain):
    """Orchestrates live camera/turnstile analytics, density profiling, and alert generation."""
    
    def analyze(self, crowd_context: Dict[str, Any]) -> CrowdAnalysisResult:
        return self._execute_structured_chain(
            prompt_key="crowd_intelligence",
            formatting_args={"crowd_context": str(crowd_context)},
            schema_model=CrowdAnalysisResult,
            fallback_func=StadiumSimulator.get_crowd_context
        )


class AccessibilityChain(BaseStadiumChain):
    """Produces customized mobility route narrations and schedules helper assignments."""
    
    def generate_route(self, service_type: str, current_location: str, destination: str, context: Dict[str, Any]) -> AccessibilityRouteResult:
        # Mock companion dispatch logic embedded directly
        def fallback():
            # Inject dynamic values into fallback template matching inputs
            return {
                "service_requested": service_type,
                "route_narration": (
                    f"Welcome to StadiumIQ Mobility assistance. Starting from your current coordinate '{current_location}', "
                    f"we have mapped a fully step-free route to your seat at '{destination}'. "
                    "Please proceed down North Ramp A with tactile pavement, pass the food courts, and board Elevator #3 at Sector 112. "
                    "Our companion team has been alerted to stand by near your zone."
                ),
                "navigation_steps": [
                    {"instruction": f"Depart from current location: {current_location}.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": "Proceed 100 meters along the wide step-free North Ramp A.", "is_step_free": True, "sensory_rating": "Quiet"},
                    {"instruction": "Take Elevator #3 near Sector 112 to Concourse Level 2.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": f"Arrive comfortably at target Seat {destination}.", "is_step_free": True, "sensory_rating": "Loud"}
                ],
                "nearby_ada_amenities": ["Wide Wheelchair ADA Restroom (Opposite Sector 112)", "Tactile Floor Guides (Entrance A)"],
                "companion_team_notified": True
            }

        return self._execute_structured_chain(
            prompt_key="accessibility_hub",
            formatting_args={
                "service_type": service_type,
                "current_location": current_location,
                "destination": destination,
                "accessibility_context": str(context)
            },
            schema_model=AccessibilityRouteResult,
            fallback_func=fallback
        )


class TransportChain(BaseStadiumChain):
    """Determines multi-modal transit recommendation schedules to dispatch matchday traffic."""
    
    def get_recommendation(self, sector_id: str, destination_zone: str, context: Dict[str, Any]) -> TransportnexusResult:
        def fallback():
            return {
                "origin_sector": sector_id,
                "target_destination": destination_zone,
                "recommended_option_mode": "Metro",
                "travel_time_summary": "Estimated travel duration to Central Hub is 18 minutes via Red Line Metro link.",
                "all_transit_options": [
                    {"mode": "Metro", "estimated_duration_mins": 18, "estimated_cost_usd": 2.75, "congestion_level": "Medium", "carbon_footprint_kg": 0.12},
                    {"mode": "Shuttle Bus", "estimated_duration_mins": 25, "estimated_cost_usd": 0.00, "congestion_level": "High", "carbon_footprint_kg": 0.35},
                    {"mode": "Rideshare", "estimated_duration_mins": 35, "estimated_cost_usd": 42.50, "congestion_level": "High", "carbon_footprint_kg": 4.10},
                    {"mode": "Walking", "estimated_duration_mins": 55, "estimated_cost_usd": 0.00, "congestion_level": "Low", "carbon_footprint_kg": 0.00},
                ],
                "operator_guideline": f"Divert fans leaving Sector {sector_id} towards the western transit terminal to ease Metro bottlenecking."
            }

        return self._execute_structured_chain(
            prompt_key="transport_nexus",
            formatting_args={
                "sector_id": sector_id,
                "destination_zone": destination_zone,
                "transport_context": str(context)
            },
            schema_model=TransportnexusResult,
            fallback_func=fallback
        )


class SustainabilityChain(BaseStadiumChain):
    """Incentivizes fan-recycling and optimizes general operator power grids."""
    
    def monitor_utilities(self, context: Dict[str, Any]) -> SustainabilityResult:
        def fallback():
            return {
                "grid_power_status": "Optimal",
                "carbon_offset_percentage": 38.4,
                "recycling_compliance_score": 88,
                "operator_grid_insight": "Solar batteries are fully charged (38%). Optimize Concourse Level 3 air conditioning setpoints to 74°F.",
                "fan_challenges": [
                    {"challenge_title": "Nalgene Refill Cup Champion", "points_reward": 100, "instructions": "Refill your reusable water bottle at any water station. Snap ticket barcodes to claim points."},
                    {"challenge_title": "Sector 114 Sorting King", "points_reward": 150, "instructions": "Deposit 3 aluminum beverage cans into the smart sorting bin near Sector 114."}
                ]
            }

        return self._execute_structured_chain(
            prompt_key="sustainability_monitor",
            formatting_args={"sustainability_context": str(context)},
            schema_model=SustainabilityResult,
            fallback_func=fallback
        )


class OpsCommandChain(BaseStadiumChain):
    """Performs priority classification on logged incidents and creates shift briefings."""
    
    def manage_incident(self, incident_report: str, zone_location: str, reporter_type: str, context: Dict[str, Any]) -> OperationsCommandResult:
        def fallback():
            # Classify priority and actions programmatically inside fallback logic
            p_map = "High" if any(w in incident_report.lower() for w in ["fire", "blood", "medical", "hurt", "injured", "fight", "weapon", "faint"]) else "Medium"
            return {
                "incident_id": "INC-" + str(os.getpid() % 1000),
                "classification_category": "Medical" if "dehydration" in incident_report.lower() or "hurt" in incident_report.lower() else "Facility",
                "priority_level": p_map,
                "closest_volunteer_sector": "Sector 205",
                "dispatch_action_code": "CODE-YELLOW-EMS" if p_map == "High" else "CODE-BLUE-FACILITY",
                "incident_response_playbook": "1. Deploy closest paramedic unit from Gate B. 2. Station lead to coordinate step-free access path clearing. 3. Security logs incident timestamps.",
                "shift_crew_briefing_bulletins": [
                    "USA vs England kickoff is in 45 mins. High crowd flow at Gate B entrance lanes.",
                    "Active incident triage: Medical dispatched to Sector 205 Seat Row L."
                ]
            }

        return self._execute_structured_chain(
            prompt_key="operations_command",
            formatting_args={
                "incident_report": incident_report,
                "zone_location": zone_location,
                "reporter_type": reporter_type,
                "security_context": str(context)
            },
            schema_model=OperationsCommandResult,
            fallback_func=fallback
        )
