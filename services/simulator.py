from typing import Any


class StadiumSimulator:
    """
    Simulates high-fidelity contextual data streams and generates synthetic,
    context-aware responses matching stadium scenarios: Before Match, Halftime,
    After Match, Weather Shift, and Emergency.
    """

    @staticmethod
    def get_active_scenario() -> str:
        """Retrieves the active simulation scenario from Streamlit session state safely."""
        import streamlit as st
        try:
            return st.session_state.get("stadium_scenario", "Before Match (High Entry Crowd)")
        except Exception:
            return "Before Match (High Entry Crowd)"

    @classmethod
    def get_stadium_context(cls) -> str:
        """Generates real-time operational state metrics for MetLife Stadium based on active scenario."""
        scenario = cls.get_active_scenario()

        if "Before Match" in scenario:
            return (
                "- Gate Statuses: Gate A (Stable queue, 4 mins), Gate B (Heavy queue, 18 mins), Gate C (Fast-track, 2 mins), Gate D (VIP Only, 1 min).\n"
                "- Restrooms: Level 1 Concourse East (Wait time 9 mins), Concourse West (Wait time 2 mins), Level 3 Upper Concourse (Wait time 12 mins).\n"
                "- Concessions: GreenBites Organic (Sector 114 - 3 mins), GrillMaster Burgers (Sector 201 - 15 mins), TacoExpress (Sector 304 - 6 mins).\n"
                "- Ticket Booths: Ticket booth B1 is open for digital credential re-verification. Main Booth is closed.\n"
                "- Matches: Match 14 (USA vs England) kicking off in 45 minutes. Stadium capacity is currently at 91.2%.\n"
                "- Weather: 72°F (22°C), Clear Skies, Wind 5mph North."
            )
        elif "Halftime" in scenario:
            return (
                "- Gate Statuses: All gates are wide clear (less than 1 min wait) as fans are seated.\n"
                "- Restrooms: Level 1 Concourse East (Extreme queue, 14 mins), Concourse West (Wait time 8 mins), Level 3 Upper Concourse (Wait time 15 mins).\n"
                "- Concessions: GreenBites Organic (Sector 114 - 18 mins), GrillMaster Burgers (Sector 201 - 25 mins), TacoExpress (Sector 304 - 19 mins).\n"
                "- Ticket Booths: All ticketing booths are closed for halftime shift transition.\n"
                "- Matches: Halftime (USA 1 - 1 England). Stadium capacity is at 97.8%.\n"
                "- Weather: 70°F (21°C), Cool Breeze, Sunset."
            )
        elif "After Match" in scenario:
            return (
                "- Gate Statuses: Ingress turnstiles closed. All egress doors Gate A, B, C, D are open at full capacity (dispersion mode).\n"
                "- Restrooms: Level 1 Concourse East (Wait time 3 mins), Concourse West (Wait time 1 min), Level 3 Upper Concourse (Wait time 4 mins).\n"
                "- Concessions: Most concession stands closing. Only Express Grab-and-Go is open near exit paths.\n"
                "- Ticket Booths: All ticket booths closed.\n"
                "- Matches: Final whistle (USA 2 - 2 England). Rapid fan egress in progress. Current stadium load: 62.4%.\n"
                "- Weather: 64°F (18°C), Clear Skies, Wind 8mph NW."
            )
        elif "Weather Shift" in scenario:
            return (
                "- Gate Statuses: Gate A (Stable, 3 mins), Gate B (Heavy congestion, 22 mins as fans huddle under canopy), Gate C (Wet surface, 5 mins).\n"
                "- Restrooms: Level 1 Concourse East (Wait time 10 mins), Concourse West (Wait time 5 mins).\n"
                "- Concessions: Food courts heavily crowded as outdoor plazas are evacuated due to lightning hazard.\n"
                "- Ticket Booths: Closed. All staff directed to support interior shelter coordination.\n"
                "- Matches: 2nd half, 68th minute. Match paused due to lightning proximity. Capacity inside concourse: 100%.\n"
                "- Weather: 58°F (14°C), Heavy Rain, Active Lightning Storm, Wind 24mph East."
            )
        elif "Critical Emergency" in scenario:
            return (
                "- Gate Statuses: Emergency egress doors unlocked. Gate B turnstiles paused. Gate A/C operating under warden directions.\n"
                "- Restrooms: All restrooms cleared of occupants by security wardens.\n"
                "- Concessions: All concession power grid sectors shut down as safety precaution.\n"
                "- Ticket Booths: Closed. Staff stationed at nearest evacuation pathways.\n"
                "- Matches: Match suspended. Evacuation directives active for Sector 205 concourse due to isolated facility incident.\n"
                "- Weather: 72°F (22°C), Clear Skies, Wind Calm."
            )
        return "- Stadium operational status stable."

    @classmethod
    def get_crowd_context(cls) -> dict[str, Any]:
        """Generates structured crowd distribution and safety hazard tracking data based on active scenario."""
        scenario = cls.get_active_scenario()

        if "Before Match" in scenario:
            return {
                "overall_occupancy_pct": 91.2,
                "total_fans_in_stadium": 75240,
                "risk_level": "Yellow",
                "bottleneck_zones": [
                    {"zone_id": "Concourse-B-East", "density_index": 8.7, "status": "Critical", "flow_rate": "15 people/min"},
                    {"zone_id": "Gate-D-Ingress", "density_index": 6.4, "status": "Warning", "flow_rate": "42 people/min"},
                    {"zone_id": "Plaza-North-Food-Court", "density_index": 4.1, "status": "Stable", "flow_rate": "85 people/min"},
                ],
                "alerts": [
                    "⚠️ Slow ingress detected at Gate B outer turnstiles due to scanner recalibrations.",
                    "⚠️ Crowd congestion forming near Sector 112 elevator foyer. Directing fans to western ramp."
                ],
                "historical_trends": [
                    {"timestamp": "T-120m", "density": 1.2},
                    {"timestamp": "T-60m", "density": 4.1},
                    {"timestamp": "T-30m", "density": 7.8},
                    {"timestamp": "Live Ingress", "density": 8.7}
                ]
            }
        elif "Halftime" in scenario:
            return {
                "overall_occupancy_pct": 97.8,
                "total_fans_in_stadium": 80685,
                "risk_level": "Yellow",
                "bottleneck_zones": [
                    {"zone_id": "Sector-114-Concourse", "density_index": 9.4, "status": "Critical", "flow_rate": "5 people/min"},
                    {"zone_id": "Concourse-Level-1-Toilets", "density_index": 9.1, "status": "Critical", "flow_rate": "12 people/min"},
                    {"zone_id": "Gate-B-Turnstiles", "density_index": 1.1, "status": "Stable", "flow_rate": "150 people/min"},
                ],
                "alerts": [
                    "⚠️ Food court and concourse concessions near Sector 114 reaching maximum capacity.",
                    "⚠️ Long bathroom lines. Recommending concourse Level 2 toilet blocks with low waiting times."
                ],
                "historical_trends": [
                    {"timestamp": "T-30m", "density": 7.8},
                    {"timestamp": "T-10m", "density": 8.2},
                    {"timestamp": "Kickoff", "density": 2.1},
                    {"timestamp": "Halftime Rush", "density": 9.4}
                ]
            }
        elif "After Match" in scenario:
            return {
                "overall_occupancy_pct": 62.4,
                "total_fans_in_stadium": 51480,
                "risk_level": "Yellow",
                "bottleneck_zones": [
                    {"zone_id": "Transit-Plaza-Egress", "density_index": 9.2, "status": "Critical", "flow_rate": "220 people/min"},
                    {"zone_id": "Gate-C-Egress", "density_index": 7.8, "status": "Warning", "flow_rate": "180 people/min"},
                    {"zone_id": "Concourse-East", "density_index": 3.4, "status": "Stable", "flow_rate": "90 people/min"},
                ],
                "alerts": [
                    "⚠️ Major pedestrian congestion at the East Transit Plaza. Recommending Blue Lot bus shuttle loop.",
                    "⚠️ All egress doors are unlocked. Heavy flow on western ramp staircases."
                ],
                "historical_trends": [
                    {"timestamp": "80th Min", "density": 3.4},
                    {"timestamp": "85th Min", "density": 4.2},
                    {"timestamp": "Final Whistle", "density": 9.1},
                    {"timestamp": "Egress Live", "density": 9.2}
                ]
            }
        elif "Weather Shift" in scenario:
            return {
                "overall_occupancy_pct": 97.8,
                "total_fans_in_stadium": 80685,
                "risk_level": "Yellow",
                "bottleneck_zones": [
                    {"zone_id": "Covered-Concourse-B", "density_index": 9.7, "status": "Critical", "flow_rate": "2 people/min"},
                    {"zone_id": "North-Ramp-Slippery", "density_index": 6.8, "status": "Warning", "flow_rate": "30 people/min"},
                    {"zone_id": "Plaza-North-Evac", "density_index": 1.2, "status": "Stable", "flow_rate": "100 people/min"},
                ],
                "alerts": [
                    "⚠️ Outdoor plazas evacuated. Extreme crowd density in covered concourses as fans seek shelter.",
                    "⚠️ Wet surfaces reported on North Ramp. Directing facilities to distribute anti-slip mats."
                ],
                "historical_trends": [
                    {"timestamp": "1st Half", "density": 2.5},
                    {"timestamp": "Storm Warning", "density": 5.4},
                    {"timestamp": "Match Pause", "density": 9.5},
                    {"timestamp": "Shelter Live", "density": 9.7}
                ]
            }
        elif "Critical Emergency" in scenario:
            return {
                "overall_occupancy_pct": 89.1,
                "total_fans_in_stadium": 73507,
                "risk_level": "Red",
                "bottleneck_zones": [
                    {"zone_id": "Sector-205-Foyer", "density_index": 9.9, "status": "Critical", "flow_rate": "0 people/min"},
                    {"zone_id": "Gate-B-Exit-Corridor", "density_index": 8.4, "status": "Critical", "flow_rate": "40 people/min"},
                    {"zone_id": "Sector-112-Evac-Ramp", "density_index": 4.5, "status": "Stable", "flow_rate": "120 people/min"},
                ],
                "alerts": [
                    "🚨 CRITICAL FIRE ALARM ACTIVE NEAR SECTOR 205 CONCOURSE LEVEL 2.",
                    "🚨 SUSPENDING ALL TRANSIT INGRESS. REDIRECTING ENTIRE STAFF FOR SECTOR 205 EVACUATION PATHWAY PREPARATION."
                ],
                "historical_trends": [
                    {"timestamp": "Normal", "density": 4.1},
                    {"timestamp": "Alarm T+1m", "density": 8.9},
                    {"timestamp": "Evacuation Start", "density": 9.9},
                    {"timestamp": "Evacuation T+5m", "density": 9.9}
                ]
            }
        return {"overall_occupancy_pct": 50.0, "total_fans_in_stadium": 40000, "risk_level": "Green", "bottleneck_zones": [], "alerts": [], "historical_trends": []}

    @classmethod
    def get_accessibility_context(cls) -> dict[str, Any]:
        """Provides status updates on ADA amenities and companions on-site based on scenario."""
        scenario = cls.get_active_scenario()

        base_context = {
            "wheelchair_ramps": "Ramp 1 (North-East) and Ramp 4 (South-West) are fully clear and step-free.",
            "elevators": "Elevator #3 (Sector 112) is fully operational. Elevator #7 (Sector 240) has a 4-minute queue.",
            "companion_volunteers_available": 14,
            "sensory_quiet_lounges": [
                {"lounge_id": "Lounge-Alpha-Sector-102", "availability": "Vacant (Quiet)", "amenities": "Weighted blankets, noise-canceling headphones"},
                {"lounge_id": "Lounge-Beta-Sector-311", "availability": "4 spots open", "amenities": "Dimmed lighting, tactile stimulators"}
            ],
            "visual_beacons_active": True,
            "audio_descriptions_channel": "FM 88.5 (Delay: 0.1s)"
        }

        if "Weather Shift" in scenario:
            base_context["wheelchair_ramps"] = "Ramp 1 (North-East) is slippery due to rain. Wheelchairs must use South-West Ramp 4 under canopy."
            base_context["companion_volunteers_available"] = 8
        elif "Critical Emergency" in scenario:
            base_context["elevators"] = "Elevator #3 (Sector 112) restricted to emergency services only. Please use Ramp 1 or Companion assist."
            base_context["companion_volunteers_available"] = 22
            base_context["sensory_quiet_lounges"][0]["availability"] = "Temporary safety check shelter"

        return base_context

    @classmethod
    def get_transport_context(cls) -> dict[str, Any]:
        """Tracks live status of subway rail systems, shuttle loops, parking and rideshares."""
        scenario = cls.get_active_scenario()

        if "Before Match" in scenario:
            return {
                "metro": {
                    "line_name": "MetLife Stadium Express (Red Line)",
                    "frequency_mins": 3,
                    "status": "Running - Extra Trains Added",
                    "estimated_delay_mins": 0,
                    "current_load_pct": 84
                },
                "shuttle_bus": {
                    "route_a_airport": {"wait_time_mins": 8, "load": "Medium", "buses_active": 12},
                    "route_b_downtown": {"wait_time_mins": 15, "load": "High", "buses_active": 8}
                },
                "parking_lots": [
                    {"lot_id": "Lot Green A", "occupancy_pct": 98, "recommendation": "DO NOT ROUTE - FULL"},
                    {"lot_id": "Lot Gold VIP", "occupancy_pct": 74, "recommendation": "Credentials check mandatory"},
                    {"lot_id": "Lot Blue Overflow", "occupancy_pct": 42, "recommendation": "HIGHLY RECOMMENDED - Shuttles running"}
                ],
                "rideshare": {
                    "surge_pricing_multiplier": 1.8,
                    "average_pickup_wait_mins": 14,
                    "designated_zone": "Gate C Outer Ring - Lane 4"
                }
            }
        elif "Halftime" in scenario:
            return {
                "metro": {
                    "line_name": "MetLife Stadium Express (Red Line)",
                    "frequency_mins": 10,
                    "status": "Idle / Standby",
                    "estimated_delay_mins": 0,
                    "current_load_pct": 10
                },
                "shuttle_bus": {
                    "route_a_airport": {"wait_time_mins": 4, "load": "Low", "buses_active": 6},
                    "route_b_downtown": {"wait_time_mins": 5, "load": "Low", "buses_active": 4}
                },
                "parking_lots": [
                    {"lot_id": "Lot Green A", "occupancy_pct": 100, "recommendation": "FULL - CLOSED"},
                    {"lot_id": "Lot Gold VIP", "occupancy_pct": 88, "recommendation": "No entry allowed"},
                    {"lot_id": "Lot Blue Overflow", "occupancy_pct": 51, "recommendation": "Spaces available - Gate closed"}
                ],
                "rideshare": {
                    "surge_pricing_multiplier": 1.0,
                    "average_pickup_wait_mins": 5,
                    "designated_zone": "Gate C Outer Ring - Lane 4"
                }
            }
        elif "After Match" in scenario:
            return {
                "metro": {
                    "line_name": "MetLife Stadium Express (Red Line)",
                    "frequency_mins": 2,
                    "status": "Running - Maximized Frequency (Egress mode)",
                    "estimated_delay_mins": 0,
                    "current_load_pct": 99
                },
                "shuttle_bus": {
                    "route_a_airport": {"wait_time_mins": 25, "load": "Critical Peak", "buses_active": 24},
                    "route_b_downtown": {"wait_time_mins": 35, "load": "Critical Peak", "buses_active": 18}
                },
                "parking_lots": [
                    {"lot_id": "Lot Green A", "occupancy_pct": 99, "recommendation": "EGRESS ONLY - Severe delay"},
                    {"lot_id": "Lot Gold VIP", "occupancy_pct": 84, "recommendation": "VIP prioritized departure lane active"},
                    {"lot_id": "Lot Blue Overflow", "occupancy_pct": 30, "recommendation": "FAST DISPERSION - Rapid shuttles active"}
                ],
                "rideshare": {
                    "surge_pricing_multiplier": 3.2,
                    "average_pickup_wait_mins": 40,
                    "designated_zone": "Gate C Outer Ring - Lanes 1-6"
                }
            }
        elif "Weather Shift" in scenario:
            return {
                "metro": {
                    "line_name": "MetLife Stadium Express (Red Line)",
                    "frequency_mins": 5,
                    "status": "Slowing down due to track slippery hazards",
                    "estimated_delay_mins": 8,
                    "current_load_pct": 90
                },
                "shuttle_bus": {
                    "route_a_airport": {"wait_time_mins": 18, "load": "High", "buses_active": 12},
                    "route_b_downtown": {"wait_time_mins": 22, "load": "High", "buses_active": 8}
                },
                "parking_lots": [
                    {"lot_id": "Lot Green A", "occupancy_pct": 98, "recommendation": "Wet surface risk - speed limit 5mph"},
                    {"lot_id": "Lot Gold VIP", "occupancy_pct": 74, "recommendation": "Warden assistance on site"},
                    {"lot_id": "Lot Blue Overflow", "occupancy_pct": 42, "recommendation": "Buses running under severe weather protocols"}
                ],
                "rideshare": {
                    "surge_pricing_multiplier": 2.5,
                    "average_pickup_wait_mins": 28,
                    "designated_zone": "Gate C Covered Canopy Zone"
                }
            }
        elif "Critical Emergency" in scenario:
            return {
                "metro": {
                    "line_name": "MetLife Stadium Express (Red Line)",
                    "frequency_mins": 1,
                    "status": "EMERGENCY DIRECT DISPERSION INITIATED",
                    "estimated_delay_mins": 0,
                    "current_load_pct": 100
                },
                "shuttle_bus": {
                    "route_a_airport": {"wait_time_mins": 5, "load": "Emergency Egress", "buses_active": 30},
                    "route_b_downtown": {"wait_time_mins": 5, "load": "Emergency Egress", "buses_active": 25}
                },
                "parking_lots": [
                    {"lot_id": "Lot Green A", "occupancy_pct": 98, "recommendation": "EMERGENCY EVACUATION EXIT LANES OPEN"},
                    {"lot_id": "Lot Gold VIP", "occupancy_pct": 74, "recommendation": "VIP checkpoints bypassed"},
                    {"lot_id": "Lot Blue Overflow", "occupancy_pct": 42, "recommendation": "ALL ROADS LEADING OUTWARD ONLY"}
                ],
                "rideshare": {
                    "surge_pricing_multiplier": 1.0,
                    "average_pickup_wait_mins": 50,
                    "designated_zone": "SUSPENDED - Use Public Transit or Shuttle Services"
                }
            }

        return {}

    @classmethod
    def get_sustainability_context(cls) -> dict[str, Any]:
        """Returns statistics on power consumption, recycling, and carbon emissions based on scenario."""
        scenario = cls.get_active_scenario()

        base_sust = {
            "power_grid_load_kw": 4820,
            "solar_generation_pct": 38.4,
            "water_recycled_liters": 142000,
            "waste_segregation": {
                "organic_kg": 2400,
                "recyclable_plastic_kg": 5800,
                "landfill_kg": 950
            },
            "carbon_offset_tons": 18.4,
            "active_eco_leaderboard": [
                {"group_id": "Sector 114 Fans", "points": 1450, "recycled_bottles": 720},
                {"group_id": "Sector 202 Volunteers", "points": 1390, "recycled_bottles": 690},
                {"group_id": "VIP Suite Crew B", "points": 1120, "recycled_bottles": 560}
            ]
        }

        if "Halftime" in scenario:
            base_sust["power_grid_load_kw"] = 5980
            base_sust["solar_generation_pct"] = 12.5  # Solar drops after sunset
            base_sust["waste_segregation"]["organic_kg"] = 5200  # Massive consumption waste
            base_sust["waste_segregation"]["recyclable_plastic_kg"] = 12400
        elif "After Match" in scenario:
            base_sust["power_grid_load_kw"] = 3100  # Load begins dropping
            base_sust["solar_generation_pct"] = 0.0
            base_sust["waste_segregation"]["organic_kg"] = 6800
            base_sust["waste_segregation"]["recyclable_plastic_kg"] = 18900
        elif "Weather Shift" in scenario:
            base_sust["power_grid_load_kw"] = 6200  # Heavy HVAC/Heating/Lights load
            base_sust["solar_generation_pct"] = 2.1
        elif "Critical Emergency" in scenario:
            base_sust["power_grid_load_kw"] = 1800  # Core auxiliary systems only
            base_sust["solar_generation_pct"] = 10.0

        return base_sust

    @classmethod
    def get_operations_context(cls) -> dict[str, Any]:
        """Simulates active field logs for security and tactical operations dispatch."""
        scenario = cls.get_active_scenario()

        if "Before Match" in scenario:
            return {
                "active_incidents": [
                    {"id": "INC-881", "type": "Minor Spill", "priority": "Low", "location": "Sector 114 Concourse", "status": "Dispatched"},
                    {"id": "INC-882", "type": "Gate Turnstile Jam", "priority": "Medium", "location": "Gate B Entrance 3", "status": "In Progress"},
                    {"id": "INC-883", "type": "Faint Fan (Dehydration)", "priority": "High", "location": "Sector 205 Seat Row L", "status": "Dispatched"}
                ],
                "volunteers_on_duty": 420,
                "volunteers_unassigned": 38,
                "security_teams_active": 45,
                "tactical_channels": "UHF Channel 4 & 9 active"
            }
        elif "Halftime" in scenario:
            return {
                "active_incidents": [
                    {"id": "INC-901", "type": "Food Court Altercation", "priority": "High", "location": "Plaza North Concessions", "status": "In Progress"},
                    {"id": "INC-882", "type": "Gate Turnstile Jam", "priority": "Low", "location": "Gate B Entrance 3", "status": "Resolved"},
                    {"id": "INC-905", "type": "Trash Bin Overflow", "priority": "Low", "location": "Sector 315 Concourse", "status": "Dispatched"}
                ],
                "volunteers_on_duty": 420,
                "volunteers_unassigned": 12,
                "security_teams_active": 50,
                "tactical_channels": "UHF Channel 2 & 4 active"
            }
        elif "After Match" in scenario:
            return {
                "active_incidents": [
                    {"id": "INC-940", "type": "Lost Child", "priority": "High", "location": "Sector 124 Main Exit", "status": "In Progress"},
                    {"id": "INC-945", "type": "Fender Bender", "priority": "Medium", "location": "Lot Green A Exit 2", "status": "Dispatched"}
                ],
                "volunteers_on_duty": 420,
                "volunteers_unassigned": 88,  # Volunteers freed up from gates
                "security_teams_active": 45,
                "tactical_channels": "UHF Channel 1 & 9 active"
            }
        elif "Weather Shift" in scenario:
            return {
                "active_incidents": [
                    {"id": "INC-961", "type": "Slippery Walkway Slip", "priority": "Medium", "location": "North Ramp A Upper", "status": "Dispatched"},
                    {"id": "INC-965", "type": "Lightning Alert Evacuation", "priority": "Critical", "location": "Open Fan Zone East", "status": "In Progress"}
                ],
                "volunteers_on_duty": 420,
                "volunteers_unassigned": 5,
                "security_teams_active": 60,
                "tactical_channels": "UHF Channel 3 & 4 active"
            }
        elif "Critical Emergency" in scenario:
            return {
                "active_incidents": [
                    {"id": "INC-991", "type": "Concourse Facility Alert", "priority": "Critical", "location": "Sector 205 Level 2", "status": "Active Rescue"}
                ],
                "volunteers_on_duty": 420,
                "volunteers_unassigned": 0,
                "security_teams_active": 85,
                "tactical_channels": "ALL OPERATIONS RE-TUNED TO DISPATCH CHANNEL 1"
            }

        return {}

    @classmethod
    def generate_demo_chat_response(cls, query: str, history: list[dict[str, str]] = None) -> str:
        """Generates synthetic, highly natural chat responses matching search keywords and selected scenarios."""
        q = query.lower()
        scenario = cls.get_active_scenario()

        # Check user language
        language_greeting = "⚽ Welcome to **StadiumIQ (FIFA World Cup 2026 AI Gateway)**!\n\n"
        if any(w in q for w in ["hola", "buenos", "gracias", "donde", "estadio"]):
            language_greeting = "🏟️ ¡Bienvenido a **StadiumIQ (Portal de Inteligencia Artificial para la Copa Mundial de la FIFA 2026)**!\n\n"
        elif any(w in q for w in ["bonjour", "salut", "merci", "où", "stade"]):
            language_greeting = "🏟️ Bienvenue sur **StadiumIQ (Portail d'intelligence IA de la Coupe du Monde de la FIFA 2026)**!\n\n"
        elif any(w in q for w in ["namaste", "aap", "kaise", "dhanyawad", "idhar"]):
            language_greeting = "🏟️ **StadiumIQ (फीफा विश्व कप 2026 एआई गेटवे)** में आपका स्वागत है!\n\n"

        # Concessions, food, vegan, drink
        if any(w in q for w in ["food", "eat", "drink", "concession", "water", "beer", "vegan", "vegetarian", "burger", "taco", "khana", "comida", "nourriture"]):
            wait_time_bites = "18 mins (Peak Halftime Rush)" if "Halftime" in scenario else "3 mins (Fast Inflow)"
            wait_master = "25 mins" if "Halftime" in scenario else "15 mins"
            return (
                f"{language_greeting}"
                "🌭 **StadiumIQ Concession Guide**: Based on live conditions under the **" + scenario + "** phase:\n\n"
                f"1. **Vegan & Vegetarian**: Try **GreenBites** inside Level 1 Concourse near **Gate B (Sector 114)**. Current wait time: **{wait_time_bites}**. Highly recommended: Vegan Avocado Wraps!\n"
                f"2. **Burgers & Classics**: **GrillMaster Burgers** at **Sector 201**. Current wait time: **{wait_master}**.\n"
                "3. **Tacos & Nachos**: **TacoExpress** at **Sector 304** (6-minute wait).\n\n"
                "💡 *Pro-tip: Order ahead on the StadiumIQ mobile app for express counter pick-up!*"
            )

        # Restrooms, toilets, bathroom, wheelchair
        elif any(w in q for w in ["restroom", "toilet", "bathroom", "wc", "washroom", "shauchalay", "baño", "toilette"]):
            wait_east = "14 minutes (Extremely Congested)" if "Halftime" in scenario else "9 minutes"
            wait_west = "8 minutes" if "Halftime" in scenario else "under 2 minutes (Highly Recommended)"
            return (
                f"{language_greeting}"
                f"🚽 **StadiumIQ Restroom Locator** (Active Phase: **{scenario}**):\n\n"
                f"- **Level 1 Concourse East (Sector 108)**: Wait time is **{wait_east}**.\n"
                f"- **Level 1 Concourse West (Sector 124)**: Wait time is **{wait_west}**.\n"
                "- **Level 3 Upper Concourse (Sector 312)**: Wait time is **12 minutes**.\n\n"
                "♿ *ADA step-free wide-door companion restrooms are located at Sectors 112, 124, 205, and 315.*"
            )

        # Parking, driving, garage, lots
        elif any(w in q for w in ["parking", "park", "car", "drive", "lot", "gaadi", "estacionamiento", "parking"]):
            rec_lot = "CLOSED - EXITS ONLY" if "After Match" in scenario else "FULL (98% capacity). Use Blue Lot."
            return (
                f"{language_greeting}"
                f"🚗 **StadiumIQ Parking Intelligence Alert** (Current: **{scenario}**):\n\n"
                f"- **Lot Green A (East Gate)**: Currently **{rec_lot}**.\n"
                "- **Lot Gold VIP**: Credentials checkpoint active. Evacuation priority lane enabled in emergency/after-match phases.\n"
                "- **Lot Blue Overflow (Recommended)**: Spaces available (42% full). Free express electric shuttles running directly to Gate C every 4 minutes."
            )

        # Tickets, seat, gate, entry
        elif any(w in q for w in ["ticket", "seat", "gate", "entry", "entrance", "turnstile", "gate B", "gate A"]):
            gate_b_time = "CLOSED FOR INGRESS" if "After Match" in scenario else ("22 mins (Heavy Storm Shelter Congestion)" if "Weather Shift" in scenario else "18 mins (Heavy Turnstile Queue)")
            return (
                f"{language_greeting}"
                f"🎟️ **StadiumIQ Gate & Entry Status Tracker**:\n\n"
                f"- **Gate A Turnstiles**: Queue is flowing smoothly (4-minute wait time).\n"
                f"- **Gate B Entrance**: Wait time is **{gate_b_time}**. Suggest rerouting to **Gate C** which is clear.\n"
                "- **Mobile Tickets**: Please open tickets in Google/Apple wallets before scanner check-ins to bypass cellular latency."
            )

        # Emergency, police, security, help, accident
        elif any(w in q for w in ["emergency", "police", "security", "help", "hurt", "injured", "accident", "lost", "bachao", "fight", "maramari"]):
            return (
                f"{language_greeting}"
                "🚨 **EMERGENCY ACTION PROTOCOL ACTIVATED**:\n\n"
                "**If there is an active medical event, physical threat, or structural hazard, please proceed with the following immediate options:**\n\n"
                "1. **Urgently contact Command**: Dial **Ext 911** on any stadium hotline, or alert the nearest volunteer wearing a neon yellow jersey.\n"
                "2. **First Aid Command**: Located behind Concourse Level 1, directly at **Sector 112**.\n"
                "3. **Evacuation and Assistance**: In case of evacuation, follow flashing directional LED floor tracks and warden voice directories.\n\n"
                "*Our medical responders and tactical security units have been placed on high alert.*"
            )

        # Default fallback general response
        return (
            f"{language_greeting}"
            "⚽ I am the **StadiumIQ AI Multilingual Concierge** for the FIFA World Cup 2026.\n\n"
            f"Currently simulated under the **{scenario}** operational phase. "
            "Ask me anything about wheelchair routing, concession waiting times, emergency alerts, taxi/metro schedules, and recycling points!"
        )
