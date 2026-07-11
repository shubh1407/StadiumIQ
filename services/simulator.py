import random
from typing import Dict, Any, List

class StadiumSimulator:
    """
    Simulates high-fidelity contextual data streams and generates fully synthetic,
    context-aware natural language answers for our Llama-3.3 fallback engine.
    """

    @staticmethod
    def get_stadium_context() -> str:
        """Generates real-time operational state metrics for MetLife Stadium."""
        return (
            "- Gate Statuses: Gate A (Stable queue, 4 mins), Gate B (Heavy queue, 18 mins), Gate C (Fast-track, 2 mins), Gate D (VIP Only, 1 min).\n"
            "- Restrooms: Level 1 Concourse East (Wait time 9 mins), Concourse West (Wait time 2 mins), Level 3 Upper Concourse (Wait time 12 mins).\n"
            "- Concessions: GreenBites Organic (Sector 114 - 3 mins), GrillMaster Burgers (Sector 201 - 15 mins), TacoExpress (Sector 304 - 6 mins).\n"
            "- Ticket Booths: Ticket booth B1 is open for digital credential re-verification. Main Booth is closed.\n"
            "- Matches: Match 14 (USA vs England) kicking off in 45 minutes. Stadium capacity is currently at 91.2%.\n"
            "- Weather: 72°F (22°C), Clear Skies, Wind 5mph North."
        )

    @staticmethod
    def get_crowd_context() -> Dict[str, Any]:
        """Generates structured crowd distribution and safety hazard tracking data."""
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
                {"timestamp": "T-180m", "density": 1.2},
                {"timestamp": "T-120m", "density": 3.4},
                {"timestamp": "T-60m", "density": 6.8},
                {"timestamp": "T-30m", "density": 8.1},
                {"timestamp": "Live", "density": 8.7},
            ]
        }

    @staticmethod
    def get_accessibility_context() -> Dict[str, Any]:
        """Provides status updates on ADA amenities and companions on-site."""
        return {
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

    @staticmethod
    def get_transport_context() -> Dict[str, Any]:
        """Tracks live status of subway rail systems, shuttle loops, parking and rideshares."""
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

    @staticmethod
    def get_sustainability_context() -> Dict[str, Any]:
        """Returns statistics on power consumption, recycling, and carbon emissions."""
        return {
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

    @staticmethod
    def get_operations_context() -> Dict[str, Any]:
        """Simulates active field logs for security and tactical operations dispatch."""
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

    @classmethod
    def generate_demo_chat_response(cls, query: str, history: List[Dict[str, str]] = None) -> str:
        """Generates structured natural chatbot responses matching various keywords."""
        q = query.lower()
        
        # Concessions, food, vegan, drink
        if any(w in q for w in ["food", "eat", "drink", "concession", "water", "beer", "vegan", "vegetarian", "burger", "taco"]):
            return (
                "🌭 **StadiumIQ Concession Guide**: Based on real-time conditions around MetLife Stadium:\n\n"
                "1. **Vegan & Vegetarian Options**: Try **GreenBites** inside Level 1 Concourse near **Gate B (Sector 114)**. Current wait time: < 3 mins. Highly recommended: Vegan Avocado Wraps!\n"
                "2. **Burgers & Classic Stadium Fare**: Head to **GrillMaster Burgers** at **Sector 201**. Queue is moderate (approx 15-minute wait).\n"
                "3. **Tacos & Nachos**: **TacoExpress** is located at **Sector 304** (6-minute wait time).\n\n"
                "💡 *Pro-tip: If you are sitting in the upper levels, ordering via the StadiumIQ mobile app allows quick express pickup at Concourse Level 3 counters!*"
            )
            
        # Restrooms, toilets, bathroom, wheelchair
        elif any(w in q for w in ["restroom", "toilet", "bathroom", "wc", "washroom"]):
            return (
                "🚽 **StadiumIQ Restroom Locator**:\n\n"
                "- **Level 1 Concourse East (Sector 108)**: Currently experiencing a peak wait time of **9 minutes**.\n"
                "- **Level 1 Concourse West (Sector 124)**: Highly optimized stream! Wait time is under **2 minutes**. Walking there will save you valuable match time!\n"
                "- **Level 3 Upper Concourse (Sector 312)**: Wait time is **12 minutes**.\n\n"
                "♿ *All ADA-accessible and family companion restrooms are fully open, clear, and equipped with automatic door assists. The nearest is at Sector 112.*"
            )

        # Parking, driving, garage, lots
        elif any(w in q for w in ["parking", "park", "car", "drive", "lot"]):
            return (
                "🚗 **StadiumIQ Parking Intelligence Alert**:\n\n"
                "- **Lot Green A (Closest to Gate A)**: Fully occupied (98% capacity). Turnstiles are crowded. Avoid driving here.\n"
                "- **Lot Gold VIP**: Reserved for ticket holders with pre-purchased VIP credentials. Active checkpoints at route entrances.\n"
                "- **Lot Blue Overflow (Recommended)**: Currently at only **42% capacity**. Rapid shuttle loops depart every 4 minutes directly to Gate C entrance. Parking fee is $25."
            )

        # Tickets, seat, gate, entry
        elif any(w in q for w in ["ticket", "seat", "gate", "entry", "entrance", "turnstile"]):
            return (
                "🎟️ **StadiumIQ Ticket & Gate Operations Summary**:\n\n"
                "- **Gate A Entrance**: Queue is smooth and fast-flowing (4-minute wait).\n"
                "- **Gate B Entrance**: Experiencing high congestion (**18-minute wait**) due to high volume scanning. We suggest diverting to **Gate C (2-minute wait)** which is a short 3-minute walk around the plaza.\n"
                "- **Digital Tickets**: Please ensure your FIFA World Cup mobile ticket is loaded in Google Wallet or Apple Wallet *before* approaching the scanner to prevent NFC lag."
            )

        # Emergency, police, security, help, accident
        elif any(w in q for w in ["emergency", "police", "security", "help", "hurt", "injured", "accident", "lost"]):
            return (
                "🚨 **EMERGENCY ACTION PROTOCOL**:\n\n"
                "**If you are witnessing an active physical threat or medical emergency, please stay calm and follow these options immediately:**\n\n"
                "1. **Call FIFA Emergency Line**: Dial **Ext 911** on any stadium hotline, or flag the nearest volunteer wearing a neon yellow jersey.\n"
                "2. **First Aid Station**: Main medical operations center is located at **Concourse Level 1, behind Sector 112**.\n"
                "3. **Lost & Found / Kids Registry**: Safe-haven registry and lost claims desk is situated at **Sector 135 Entrance Hub**.\n\n"
                "*Our on-field safety team is on active standby. GPS coordinates can be broadcasted via operations command center.*"
            )

        # Default fallback general response
        return (
            "⚽ Welcome to **StadiumIQ (FIFA World Cup 2026 AI Gateway)**!\n\n"
            "I can assist you with real-time stadium navigation, finding parking slots, food courts, wheelchair-accessible paths, metro schedules, and emergency alerts. "
            "How can I help you support your matchday experience today?"
        )
