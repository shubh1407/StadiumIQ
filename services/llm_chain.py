import os
import random
from collections.abc import Callable, Generator
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel

from models.schemas import (
    AccessibilityRouteResult,
    CrowdAnalysisResult,
    OperationsCommandResult,
    SustainabilityResult,
    TransportnexusResult,
)
from services.groq_client import GroqClient
from services.output_parser import OutputParser
from services.prompt_manager import PROMPTS
from services.simulator import StadiumSimulator

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
        formatting_args: dict[str, Any],
        schema_model: type[T],
        fallback_func: Callable[[], dict[str, Any]]
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

            yield from self.client.stream(messages=messages, temperature=0.5, max_tokens=800)

        except Exception as e:
            logger.error(f"FanAssistant stream error: {str(e)}. Defaulting to simulator static stream.")
            simulated_text = StadiumSimulator.generate_demo_chat_response(user_query)
            yield simulated_text


class CrowdAnalysisChain(BaseStadiumChain):
    """Orchestrates live camera/turnstile analytics, density profiling, and alert generation."""

    def analyze(self, crowd_context: dict[str, Any]) -> CrowdAnalysisResult:
        def fallback():
            scenario = StadiumSimulator.get_active_scenario()
            alerts = crowd_context.get("alerts", [])

            # Determine mock risk levels and alerts depending on active scenario
            if "Critical Emergency" in scenario:
                rec = "Evacuate Sector 205 Level 2 concourse foyer immediately. Divert all unassigned volunteers to assist ADA stairs."
                alt = "In case western exit corridor B is blocked, divert evacuation streams outwards to Sector 112 eastern ramp."
                reason_txt = "Active facility hazard detected. Evacuation of localized sectors initiated under emergency fire-safety protocols."
                conf = 99.5
                impact = "Guarantees rapid and safe crowd dispersion under 8 minutes."
            elif "Weather Shift" in scenario:
                rec = "Advise fans to remain inside covered concourse pods. Clear open plaza areas to prevent lightning exposure."
                alt = "Deploy facilities crews to disperse anti-slip carpets near slick ramp surfaces."
                reason_txt = "Heavy active lightning storms and slippery walkway conditions warrant covered shelter huddling."
                conf = 95.0
                impact = "Reduces slip-and-fall injuries by 85% and protects fans from thunderstorm hazards."
            elif "After Match" in scenario:
                rec = "Unlock all egress gates (Gate A to D) and route outgoing pedestrian flows toward Transit Plaza lanes."
                alt = "Provide priority boarding on Lot Blue shuttle loops to ease transit queue bottlenecks."
                reason_txt = "Match is concluded. Stadium is shifting entirely to egress mode for 80,000 departing fans."
                conf = 92.0
                impact = "Disfuses heavy plaza bottlenecks and drops general travel queue time by 15 mins."
            else:
                rec = "Divert incoming Sector 112 pedestrian traffic to the wide western gate ramps."
                alt = "Open overflow turnstiles at Gate C to offload Gate B heavy queues."
                reason_txt = "High entry crowd flows detected at main Gate B gates before kickoff."
                conf = 90.0
                impact = "Balances entry queue wait times across all stadium gates within 5 minutes."

            return {
                "overall_risk_level": crowd_context.get("risk_level", "Yellow"),
                "crowd_density_score": 8.7 if "Before Match" in scenario else (9.4 if "Halftime" in scenario else 5.2),
                "active_bottlenecks": [
                    {
                        "zone_id": b["zone_id"],
                        "density_index": b["density_index"],
                        "status": b["status"],
                        "flow_rate": b["flow_rate"]
                    } for b in crowd_context.get("bottleneck_zones", [])
                ],
                "system_alerts": alerts,
                "tactical_recommendations": [rec, "Deploy additional ticketing assistants.", "Deploy first-aid units near restrooms."],
                # New Explainable AI fields
                "reason": reason_txt,
                "confidence_score": conf,
                "expected_impact": impact,
                "alternative_recommendation": alt
            }

        return self._execute_structured_chain(
            prompt_key="crowd_intelligence",
            formatting_args={"crowd_context": str(crowd_context)},
            schema_model=CrowdAnalysisResult,
            fallback_func=fallback
        )


class AccessibilityChain(BaseStadiumChain):
    """Produces customized mobility route narrations and schedules helper assignments."""

    def generate_route(self, service_type: str, current_location: str, destination: str, context: dict[str, Any]) -> AccessibilityRouteResult:
        def fallback():
            scenario = StadiumSimulator.get_active_scenario()

            # Formulate route specifics tailored to service_type
            if "Wheelchair" in service_type:
                steps = [
                    {"instruction": f"Depart from current location: {current_location}.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": "Proceed 120m along North Ramp A (100% ADA step-free, no stairs).", "is_step_free": True, "sensory_rating": "Quiet"},
                    {"instruction": "Board Elevator #3 at Sector 112 to level 2 foyer.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": f"Arrive safely at seating Row {destination} with wheelchair companion seating.", "is_step_free": True, "sensory_rating": "Loud"}
                ]
                reason_txt = "Step-free route calculated prioritizing elevators and smooth-graded ramps."
                impact_txt = "Enables completely frictionless, strain-free physical transit for wheelchair visitors."
                alt_txt = "If Elevator #3 experiences a wait, companion crew can route you to western Elevator #4."
            elif "Vision" in service_type:
                steps = [
                    {"instruction": f"Depart {current_location}. Locate tactile paving strip on right side.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": "Follow the tactile floor guides 150m. An info kiosk with audio beacon is 20m ahead.", "is_step_free": True, "sensory_rating": "Quiet"},
                    {"instruction": "Ascend elevator #3 (automatic verbal level announcements active).", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": f"Arrive at destination {destination}. Row features bright visual warning indicators.", "is_step_free": True, "sensory_rating": "Loud"}
                ]
                reason_txt = "Tactile guide alignment mapped to assist vision-impaired fans using audio navigation."
                impact_txt = "Boosts self-navigation confidence and prevents physical collisions."
                alt_txt = "Request physical escort from companion team stationed 10 meters away."
            elif "Hearing" in service_type:
                steps = [
                    {"instruction": f"Depart {current_location}. Look for flashing LED beacon trackers.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": "Proceed to sector 112 concourse foyer where closed caption boards are active.", "is_step_free": True, "sensory_rating": "Quiet"},
                    {"instruction": f"Arrive at {destination}. Closed caption systems and FM channel support are available here.", "is_step_free": True, "sensory_rating": "Loud"}
                ]
                reason_txt = "Visual indicator route prioritized for visitors requesting high auditory assistance."
                impact_txt = "Connects visitor instantly with all stadium visual message systems."
                alt_txt = "Ask sector volunteer Elena G. for a physical copy of match-updates."
            elif "Senior" in service_type:
                steps = [
                    {"instruction": f"Depart {current_location}. Use the low-gradient easy-paced North Ramp.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": "Stop at the resting seat pod next to Sector 112 concessions (distance: 80m).", "is_step_free": True, "sensory_rating": "Quiet"},
                    {"instruction": "Board Elevator #3 to bypass all stair climb requirements.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": f"Arrive safely at seating row {destination}.", "is_step_free": True, "sensory_rating": "Loud"}
                ]
                reason_txt = "Low-strain pathway selected featuring resting spots and zero stair climb."
                impact_txt = "Reduces physical exhaustion and fatigue levels for senior citizens by 90%."
                alt_txt = "Our companion team can dispatch a buggy shuttle to pick you up directly."
            else:  # Children / Family
                steps = [
                    {"instruction": f"Depart {current_location}. Stroller-friendly wide corridor active.", "is_step_free": True, "sensory_rating": "Moderate"},
                    {"instruction": "Pass next to the diaper changing kiosk and family care room opposite Sector 112.", "is_step_free": True, "sensory_rating": "Quiet"},
                    {"instruction": f"Arrive at destination row {destination}.", "is_step_free": True, "sensory_rating": "Loud"}
                ]
                reason_txt = "Family-friendly route emphasizing close proximity to nursing rooms and quiet lounges."
                impact_txt = "Creates an eye-safe, tranquil, stress-free stadium experience for parents with children."
                alt_txt = "We can arrange a stroller-parking ticket validation opposite Gate A."

            return {
                "service_requested": service_type,
                "route_narration": (
                    f"Welcome to StadiumIQ inclusive navigation aid. Starting from '{current_location}', "
                    f"we have calculated a fully certified accessible pathway to seat '{destination}' "
                    f"under active conditions of '{scenario}'."
                ),
                "navigation_steps": steps,
                "nearby_ada_amenities": ["Wide Family Care restroom (Opposite Sector 112)", "Wheelchair charging point B1"],
                "companion_team_notified": True,
                # New Explainable AI fields
                "reason": reason_txt,
                "confidence_score": 96.0,
                "expected_impact": impact_txt,
                "alternative_recommendation": alt_txt
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

    def get_recommendation(self, sector_id: str, destination_zone: str, context: dict[str, Any]) -> TransportnexusResult:
        def fallback():
            scenario = StadiumSimulator.get_active_scenario()

            # Setup dynamic travel times depending on active scenario
            if "After Match" in scenario:
                metro_time, bus_time, taxi_time = 18, 35, 55
                metro_con, bus_con, taxi_con = "Medium", "High", "Critical"
                rec_mode = "Metro"
                reason_txt = "Metro trains are operating at maximum post-game frequency (every 2 mins) with a dedicated boarding queue."
                impact_txt = "Saves up to 35 minutes compared to rideshares experiencing extreme surge pricing and traffic locks."
                alt_txt = "Take the Blue Lot express shuttle loop which is operating at 95% efficiency."
            elif "Weather Shift" in scenario:
                metro_time, bus_time, taxi_time = 28, 45, 60
                metro_con, bus_con, taxi_con = "High", "High", "Critical"
                rec_mode = "Metro"
                reason_txt = "Public rail transit remains active under heavy rain protocols. Roads are severely delayed due to rain hazards."
                impact_txt = "Provides dry shelter transit and bypasses heavy surface road gridlock."
                alt_txt = "Huddle inside the covered Gate C taxi canopy until lightning storm warnings pass."
            else:
                metro_time, bus_time, taxi_time = 15, 22, 30
                metro_con, bus_con, taxi_con = "Low", "Medium", "Medium"
                rec_mode = "Metro"
                reason_txt = "Standard matchday transit lanes are clear. Red Line rail is the fastest and greenest option."
                impact_txt = "Guarantees match kickoff arrival under 18 minutes with zero carbon emissions."
                alt_txt = "Take the airport loop shuttle bus route A from plaza Gate C."

            return {
                "origin_sector": sector_id,
                "target_destination": destination_zone,
                "recommended_option_mode": rec_mode,
                "travel_time_summary": f"Estimated duration is {metro_time} minutes via Red Line Metro link.",
                "all_transit_options": [
                    {"mode": "Metro", "estimated_duration_mins": metro_time, "estimated_cost_usd": 2.75, "congestion_level": metro_con, "carbon_footprint_kg": 0.1},
                    {"mode": "Shuttle Bus", "estimated_duration_mins": bus_time, "estimated_cost_usd": 0.00, "congestion_level": bus_con, "carbon_footprint_kg": 0.3},
                    {"mode": "Taxi/Rideshare", "estimated_duration_mins": taxi_time, "estimated_cost_usd": 38.50, "congestion_level": taxi_con, "carbon_footprint_kg": 3.8},
                    {"mode": "Walking", "estimated_duration_mins": 55, "estimated_cost_usd": 0.00, "congestion_level": "Low", "carbon_footprint_kg": 0.0}
                ],
                "operator_guideline": f"Divert outgoing Sector {sector_id} fans towards exit doors Gate C to utilize direct rail bridges.",
                # New Explainable AI fields
                "reason": reason_txt,
                "confidence_score": 94.5,
                "expected_impact": impact_txt,
                "alternative_recommendation": alt_txt
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

    def monitor_utilities(self, context: dict[str, Any]) -> SustainabilityResult:
        def fallback():
            scenario = StadiumSimulator.get_active_scenario()

            # Dynamic solar generation and HVAC recommendations based on scenario
            if "Halftime" in scenario:
                grid = "Loaded"
                insight = "Concourse Level 1 concessions reaching peak loads. Increase HVAC setpoints to 75°F in VIP Suites to shed 400 kW."
                offset = 24.5
                reason_txt = "Peak game loads are active. Offsetting consumption through thermal load management."
                impact = "Bypasses utility demand charges and saves 15% grid cost."
                alt = "Switch on the standby micro-grid battery cells to supplement peak."
            elif "Weather Shift" in scenario:
                grid = "Critical Peak"
                insight = "Lightning storm active. Shut down outdoor decorative screens. Pre-heat indoor concourses to prevent HVAC spikes."
                offset = 12.1
                reason_txt = "Storm lighting needs and indoor fan clustering require critical safety load management."
                impact = "Prevents localized brownouts and protects sensitive electrical equipment."
                alt = "Route solar reserves into core emergency pathways."
            else:
                grid = "Optimal"
                insight = "Grid loads are stable. Solar generation is at peak (38%). Optimize lighting arrays in Sector 3."
                offset = 38.4
                reason_txt = "Stable daylight conditions and solar peaks offer high offset ratios."
                impact = "Maintains carbon-neutral footprint goals for Matchday 14."
                alt = "Feed excess solar generation back into local utility grids."

            return {
                "grid_power_status": grid,
                "carbon_offset_percentage": offset,
                "recycling_compliance_score": 88,
                "operator_grid_insight": insight,
                "fan_challenges": [
                    {"challenge_title": "Eco-Sort Champion (Sector 114)", "points_reward": 100, "instructions": "Deposit 3 aluminium beverage cans inside the smart bin opposite Gate B. Scan barcode to claim points."},
                    {"challenge_title": "Clean Concourse Supporter", "points_reward": 150, "instructions": "Take a photo of your sorted organic waste and upload to StadiumIQ to claim a gold star."}
                ],
                # New Explainable AI fields
                "reason": reason_txt,
                "confidence_score": 93.0,
                "expected_impact": impact,
                "alternative_recommendation": alt
            }

        return self._execute_structured_chain(
            prompt_key="sustainability_monitor",
            formatting_args={"sustainability_context": str(context)},
            schema_model=SustainabilityResult,
            fallback_func=fallback
        )


class OpsCommandChain(BaseStadiumChain):
    """Performs priority classification on logged incidents and creates shift briefings."""

    def manage_incident(self, incident_report: str, zone_location: str, reporter_type: str, context: dict[str, Any]) -> OperationsCommandResult:
        def fallback():
            # Determine priority classification and categories programmatically
            rep_lower = incident_report.lower()

            # Determine incident classification and priority level
            if any(w in rep_lower for w in ["fire", "smoke", "burn"]):
                cat = "Security"
                p_level = "Critical"
                playbook = "1. Evacuate Sector 205 immediately. 2. Dispatch safety crew. 3. Engage central alarm systems."
                code = "CODE-RED-SECURITY"
                impact = "Active building evacuation required. Safety threat is highly critical."
                medical_team = "EMS Squad 3 dispatched on standby at Sector 205 Gate B entrance."
                v_sector = "Sector 205 Security Team"
                res_time = "10 minutes"
                conf = 99.0
                exp_imp = "Secures localized perimeter and prevents fire/smoke exposure."
                alt_rec = "Direct unassigned sector 112 volunteers to guide fans to eastern Gate C."
            elif any(w in rep_lower for w in ["fight", "scuffle", "punch", "assault", "police"]):
                cat = "Security"
                p_level = "High"
                playbook = "1. Dispatch police patrol. 2. Inform shift chief. 3. Restrain active altercations."
                code = "CODE-ORANGE-SECURITY"
                impact = "Physical altercation poses immediate safety risk to nearby fans."
                medical_team = "First Aid team placed on standby."
                v_sector = "Security Patrol Sector 205"
                res_time = "5 minutes"
                conf = 95.0
                exp_imp = "Restores peace and order within Sector concourses."
                alt_rec = "Trigger secondary security loop from Gate A."
            elif any(w in rep_lower for w in ["hurt", "injured", "chest", "medical", "ambulance", "faint", "dehydration"]):
                cat = "Medical"
                p_level = "High"
                playbook = "1. Deploy closest paramedic unit. 2. Stations leads clear elevator pathways. 3. Track EMS timestamps."
                code = "CODE-RED-EMS"
                impact = "Physically distressed fan requires rapid on-site paramedic support."
                medical_team = "EMS Unit 1 dispatched from Sector 112 medical room."
                v_sector = "First Aid Sector 112"
                res_time = "6 minutes"
                conf = 98.0
                exp_imp = "Provides immediate stabilizing first-aid and medical care."
                alt_rec = "Divert on-call volunteer Elena G. with wheelchair en route."
            elif any(w in rep_lower for w in ["spill", "glass", "cleaning", "trash"]):
                cat = "Facility"
                p_level = "Medium"
                playbook = "1. Dispatch cleaning crews with wet-floor signages. 2. Divert traffic around spill. 3. Confirm dry."
                code = "CODE-BLUE-FACILITY"
                impact = "Slip risk on concourse floors. Needs localized cleaning."
                medical_team = "None required"
                v_sector = "Facilities Squad Level 2"
                res_time = "8 minutes"
                conf = 91.0
                exp_imp = "Eliminates concourse floor slippage hazards."
                alt_rec = "Divert sector 205 concourse volunteer to guard the spill spot."
            else:
                cat = "Structural"
                p_level = "Low"
                playbook = "1. Log ticket in facilities maintenance ledger. 2. Dispatch repair crew during shift break."
                code = "CODE-GREY-FACILITY"
                impact = "Minor structural or convenience issue. No physical safety hazard."
                medical_team = "None required"
                v_sector = "Facilities Care Team"
                res_time = "30 minutes"
                conf = 88.0
                exp_imp = "Restores comfort and long-term facility standard."
                alt_rec = "Provide fan with temporary seat assignment."

            return {
                "incident_id": "INC-" + str(os.getpid() % 1000 + random.randint(100, 999)),  # nosec B311 - cosmetic demo ID, not security-sensitive
                "classification_category": cat,
                "priority_level": p_level,
                "closest_volunteer_sector": v_sector,
                "dispatch_action_code": code,
                "incident_response_playbook": playbook,
                "shift_crew_briefing_bulletins": [
                    "USA vs England kickoff is in 45 mins. High crowd flow at Gate B entrance lanes.",
                    f"Active incident triage logged at {zone_location} (Code {code})."
                ],
                # New Real-Time Incident Management fields
                "impact_assessment": impact,
                "suggested_response": f"Dispatch closest {v_sector} to location {zone_location} to execute protocol {code}.",
                "nearest_volunteers_quadrant": "Quadrant North-East" if "Concourse" in zone_location else "Quadrant South-West",
                "medical_team_dispatch": medical_team,
                "estimated_resolution_time": res_time,
                # New Explainable AI fields
                "reason": f"Incident classified as {cat} with priority {p_level} based on keywords: '{incident_report[:40]}...'.",
                "confidence_score": conf,
                "expected_impact": exp_imp,
                "alternative_recommendation": alt_rec
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
