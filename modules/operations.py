import streamlit as st
import time
from services.llm_chain import OpsCommandChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html
from models.schemas import OperationsCommandResult

def render_operations_command() -> None:
    """Renders the Operations Command control board & Real-Time AI Situation Room."""
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">🛡️ Operations Command & Situation Room</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Live multi-system tactical overlays, high-frequency security dispatch loops, and AI-powered executive briefing compilers.
            </p>
        </div>
        """
    )
    
    # Fetch active simulation context
    active_scenario = StadiumSimulator.get_active_scenario()
    ops_context = StadiumSimulator.get_operations_context()
    crowd_context = StadiumSimulator.get_crowd_context()
    trans_context = StadiumSimulator.get_transport_context()
    eco_context = StadiumSimulator.get_sustainability_context()
    ada_context = StadiumSimulator.get_accessibility_context()
    
    # Initialize active logged incidents database if empty
    if "incident_database" not in st.session_state:
        st.session_state.incident_database = list(ops_context.get("active_incidents", []))
        
    # Create the beautiful dual-tab structure
    tab1, tab2 = st.tabs(["📊 Real-Time AI Situation Room", "🛡️ Incident Dispatch & Log Center"])
    
    # ==========================================================================
    # TAB 1: REAL-TIME AI SITUATION ROOM (8 Core Parameters)
    # ==========================================================================
    with tab1:
        st.markdown("### 📡 Live Multi-System Tactical Matrix")
        st.caption(f"Continuous high-frequency synchronization with MetLife Stadium sensors under the **{active_scenario}** phase:")
        
        # Formulate dynamic indicators depending on the scenario
        # 1. Crowd
        if "Before Match" in active_scenario:
            crowd_val, crowd_badge, crowd_desc = "8.7 / 10 Index", "Yellow", "Heavy Gate B ingress flow"
        elif "Halftime" in active_scenario:
            crowd_val, crowd_badge, crowd_desc = "9.4 / 10 Index", "Yellow", "Extreme Concourse Food Court clustering"
        elif "After Match" in active_scenario:
            crowd_val, crowd_badge, crowd_desc = "9.2 / 10 Index", "Yellow", "Egress dispersion active"
        elif "Weather Shift" in active_scenario:
            crowd_val, crowd_badge, crowd_desc = "9.7 / 10 Index", "Red", "Covered concourse pod overcrowding"
        else: # Emergency
            crowd_val, crowd_badge, crowd_desc = "9.9 / 10 Index", "Red", "Local Sector 205 evacuation in progress"
            
        # 2. Transport
        if "Before Match" in active_scenario:
            trans_val, trans_badge, trans_desc = "3m Red Line Frequency", "Green", "Extra transit trains running smoothly"
        elif "Halftime" in active_scenario:
            trans_val, trans_badge, trans_desc = "10m Idle standby", "Green", "Transit load stable"
        elif "After Match" in active_scenario:
            trans_val, trans_badge, trans_desc = "2m Peak frequency", "Green", "Metro operating at full post-game frequency"
        elif "Weather Shift" in active_scenario:
            trans_val, trans_badge, trans_desc = "5m Weather frequency", "Yellow", "Slippery tracks, speed cap active"
        else: # Emergency
            trans_val, trans_badge, trans_desc = "1m Emergency dispatch", "Red", "Emergency dispersion mode activated"

        # 3. Parking
        if "Before Match" in active_scenario:
            park_val, park_badge, park_desc = "Lot Green A: 98% (FULL)", "Red", "Direct new arrivals to Lot Blue Overflow"
        elif "Halftime" in active_scenario:
            park_val, park_badge, park_desc = "Lot Green A: 100% (FULL)", "Red", "Gates locked. No entry permitted"
        elif "After Match" in active_scenario:
            park_val, park_badge, park_desc = "Lot Green A: Egress-only", "Yellow", "Evacuation departure corridor active"
        elif "Weather Shift" in active_scenario:
            park_val, park_badge, park_desc = "Lot Green A: 98% (Wet)", "Yellow", "Slippery asphalt, speed cap 5mph"
        else: # Emergency
            park_val, park_badge, park_desc = "Lot Green A: Evacuation Mode", "Green", "VIP check gates bypassed"

        # 4. Medical
        if "Before Match" in active_scenario:
            med_val, med_badge, med_desc = "EMS Units Standby", "Green", "1 active heat-exhaustion case under triage"
        elif "Halftime" in active_scenario:
            med_val, med_badge, med_desc = "Concourse Patrol Active", "Green", "First aid standby near main food court"
        elif "After Match" in active_scenario:
            med_val, med_badge, med_desc = "Egress Escort Duty", "Green", "Paramedic units posted near transit terminals"
        elif "Weather Shift" in active_scenario:
            med_val, med_badge, med_desc = "Trauma Unit Mobilized", "Yellow", "Slip injury dispatch crew active on North Ramp"
        else: # Emergency
            med_val, med_badge, med_desc = "CODE-RED medical dispatch", "Red", "EMS units focused near Sector 205 foyer"

        # 5. Security
        if "Before Match" in active_scenario:
            sec_val, sec_badge, sec_desc = "3 Active Incidents", "Yellow", "Gate B turnstile jam triage in progress"
        elif "Halftime" in active_scenario:
            sec_val, sec_badge, sec_desc = "2 Active Incidents", "Yellow", "Food court verbal dispute monitored"
        elif "After Match" in active_scenario:
            sec_val, sec_badge, sec_desc = "2 Active Incidents", "Yellow", "Lost child reported near Sector 124 exit"
        elif "Weather Shift" in active_scenario:
            sec_val, sec_badge, sec_desc = "2 Active Incidents", "Red", "Lightning hazard zone clearance active"
        else: # Emergency
            sec_val, sec_badge, sec_desc = "1 Critical Emergency", "Red", "Facility fire alarm active at Sector 205 L2"

        # 6. Weather
        if "Weather Shift" in active_scenario:
            wea_val, wea_badge, wea_desc = "58°F / Thunderstorm", "Red", "Active lightning storm warning. Paused match"
        elif "After Match" in active_scenario:
            wea_val, wea_badge, wea_desc = "64°F / Clear Night", "Green", "Stable ambient night dispersion conditions"
        elif "Halftime" in active_scenario:
            wea_val, wea_badge, wea_desc = "70°F / Cool Breeze", "Green", "Sunset conditions stable"
        else:
            wea_val, wea_badge, wea_desc = "72°F / Clear Skies", "Green", "Mild matchday wind (5mph North)"

        # 7. Waste
        if "Before Match" in active_scenario:
            was_val, was_badge, was_desc = "Compliance Index: 86%", "Green", "Organic recycling sorting stable"
        elif "Halftime" in active_scenario:
            was_val, was_badge, was_desc = "Compliance Index: 92%", "Green", "Heavy food court concession cup waste sorting"
        elif "After Match" in active_scenario:
            was_val, was_badge, was_desc = "Compliance Index: 88%", "Green", "Post-match clean up teams deploying"
        elif "Weather Shift" in active_scenario:
            was_val, was_badge, was_desc = "Compliance Index: 74%", "Yellow", "Outdoor trash units flooded by heavy rain"
        else: # Emergency
            was_val, was_badge, was_desc = "Compliance: Suspended", "Yellow", "Waste teams diverted to safety roles"

        # 8. Energy
        if "Before Match" in active_scenario:
            ene_val, ene_badge, ene_desc = "4,820 kW Load", "Green", "Solar arrays generating at peak (38% offset)"
        elif "Halftime" in active_scenario:
            ene_val, ene_badge, ene_desc = "5,980 kW Load", "Yellow", "HVAC / Floodlight load peaking. Solar drops"
        elif "After Match" in active_scenario:
            ene_val, ene_badge, ene_desc = "3,100 kW Load", "Green", "Concession grid power-shedding initiated"
        elif "Weather Shift" in active_scenario:
            ene_val, ene_badge, ene_desc = "6,200 kW Load", "Red", "Peak heating/lighting grids loaded under storm"
        else: # Emergency
            ene_val, ene_badge, ene_desc = "1,800 kW Load", "Green", "Main grids shed, auxiliary safety line active only"

        # Build the HTML 4x2 GRID
        grid_html = f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px;">
            <!-- CARD 1: CROWD -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">👥 Crowd Logistics</span>
                    {render_status_badge(crowd_badge, crowd_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{crowd_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{crowd_desc}</div>
            </div>
            
            <!-- CARD 2: TRANSPORT -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">🚌 Regional Transit</span>
                    {render_status_badge(trans_badge, trans_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{trans_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{trans_desc}</div>
            </div>

            <!-- CARD 3: PARKING -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">🅿️ Parking & Roads</span>
                    {render_status_badge(park_badge, park_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{park_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{park_desc}</div>
            </div>

            <!-- CARD 4: MEDICAL -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">🏥 Medical Care</span>
                    {render_status_badge(med_badge, med_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{med_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{med_desc}</div>
            </div>

            <!-- CARD 5: SECURITY -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">🛡️ Security Triage</span>
                    {render_status_badge(sec_badge, sec_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{sec_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{sec_desc}</div>
            </div>

            <!-- CARD 6: WEATHER -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">⛈️ Weather Sensors</span>
                    {render_status_badge(wea_badge, wea_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{wea_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{wea_desc}</div>
            </div>

            <!-- CARD 7: WASTE -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">♻️ Green Compliance</span>
                    {render_status_badge(was_badge, was_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{was_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{was_desc}</div>
            </div>

            <!-- CARD 8: ENERGY -->
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; transition: all 0.25s;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase; font-weight: bold;">⚡ micro-grid Load</span>
                    {render_status_badge(ene_badge, ene_badge.lower())}
                </div>
                <div style="font-size: 1.25rem; font-weight: bold; color: #FFFFFF; margin-bottom: 4px;">{ene_val}</div>
                <div style="font-size: 0.75rem; color: #E0E1DD; line-height: 1.3;">{ene_desc}</div>
            </div>
        </div>
        """
        render_html(grid_html)
        
        # AI Executive Tactical Summary
        st.markdown("### 📋 AI Executive Tactical Command Briefing")
        st.caption("Synthesized general operational directive compiled across all eight systems:")
        
        if "Before Match" in active_scenario:
            brief_text = (
                "**INBOUND CONGESTION WARNING**: Gates turnstiles are highly loaded due to fan arrivals. Gate B represents the primary bottleneck at 72% current and 96% projected 15m density. "
                "Regional transit is operating on maximum Red Line frequency (every 3m) to dispense rail arrivals. Parking Lot Green A is full; redirect traffic outward to Blue Lot. "
                "Power grids are fully supported by auxiliary solar arrays. Sector coordinators are advised to clear Sector 112 corridors to prepare for incoming ADA accessibility dispatches."
            )
        elif "Halftime" in active_scenario:
            brief_text = (
                "**CONCOURSE RUSH DETECTED**: Gates are clear, but concourse sectors (especially Sector 114 concessions and toilets) are experiencing massive halftime queues. Restroom wait times are up to 14 minutes. "
                "Grid HVAC load is peaking at 5,980 kW. Micro-grids have shed 400 kW of auxiliary suite lighting to keep peak rates optimal. Security is actively monitoring a verbal dispute at North Plaza food court."
            )
        elif "After Match" in active_scenario:
            brief_text = (
                "**EGRESS DEPLOYMENT ACTIVE**: Regional metro has transitioned to maximum 2-minute dispersion mode. Shuttles are operating at critical peak capacity. All gates (A to D) are fully unlocked. "
                "Power load has successfully been shed down to 3,100 kW. Medical crews are on standby near exit terminals. Sorting bins are deployed across concourses; waste teams are active."
            )
        elif "Weather Shift" in active_scenario:
            brief_text = (
                "**WEATHER EMERGENCY SENSORS ACTIVE**: Severe thunderstorm and active lightning proximity warning has paused the match. Outdoors zones are evacuated; fans are heavily huddled inside covered concourses (Index 9.7). "
                "Ramps are slick (Ramp A North); anti-slip mats must be distributed immediately. Transit is slowing down to 5-minute intervals. Auxiliary power lines are initialized."
            )
        else: # Emergency
            brief_text = (
                "**CRITICAL SECURITY RESPONSE**: Fire alarm triggered at Sector 205 Level 2 concourse foyer. Evacuation protocols are active for this sector; redirect all available sector 112 hosts to support. "
                "Gates are bypassed; Metro Red Line has shifted to 1m rapid emergency extraction. All concession power has been shed to protect infrastructure. EMS is focused at the Sector 205 evacuation point."
            )
            
        render_html(
            f"""
            <div style="background: rgba(0, 255, 204, 0.05); border-left: 4px solid #00FFCC; border-radius: 8px; padding: 18px; line-height: 1.5; font-size: 0.9rem; color: #E0E1DD; margin-bottom: 20px;">
                {brief_text}
            </div>
            """
        )
        
        # Button to re-verify systems
        if st.button("🩺 Trigger Complete Multi-System Self-Check", use_container_width=True):
            with st.spinner("Pinging stadium IoT nodes, cameras, and grid relays..."):
                time.sleep(1.2)
                st.toast("Self-check completed. All 842 IoT grid relays online.", icon="✅")

    # ==========================================================================
    # TAB 2: INCIDENT DISPATCH & LOG CENTER
    # ==========================================================================
    with tab2:
        col1, col2 = st.columns([1.2, 1.8], gap="medium")
        
        with col1:
            st.markdown("### 📝 Log New Stadium Incident")
            st.caption("Submit active field reports for instant AI triage and dispatch:")
            
            reporter_type = st.selectbox(
                "Reporter Personnel:",
                ["Field Volunteer (Neon Jersey)", "Stadium Security Patrol", "Gate Scanner Operator", "General Fan Report"]
            )
            
            zone_location = st.text_input("Coordinates / Zone Location:", value="Sector 205 Concourse Level 2")
            
            incident_report = st.text_area(
                "Incident Description:",
                placeholder="e.g. Broken glass spill blocking step-free corridor, need immediate cleaning dispatch."
            )
            
            submit_incident = st.button("🚀 Dispatch AI Emergency Response", type="primary", use_container_width=True)
            
            if submit_incident:
                if not incident_report.strip():
                    st.error("Please enter descriptive incident details before dispatch.")
                else:
                    # Trigger Operations chain
                    chain = OpsCommandChain()
                    with st.spinner("Analyzing threat levels and locating closest volunteers..."):
                        result: OperationsCommandResult = chain.manage_incident(
                            incident_report=incident_report,
                            zone_location=zone_location,
                            reporter_type=reporter_type,
                            context=ops_context
                        )
                    
                    # Append incident log to our persistent session-state database
                    st.session_state.incident_database.insert(0, {
                        "id": result.incident_id,
                        "type": result.classification_category,
                        "priority": result.priority_level,
                        "location": zone_location,
                        "status": "Assigned"
                    })
                    
                    # Show beautiful fully enriched dispatch card
                    st.markdown("---")
                    st.markdown("### 📡 Active AI Dispatch & Triage Directive")
                    priority_badge_type = result.priority_level.lower()
                    render_html(
                        f"""
                        <div style="background: rgba(255, 152, 0, 0.05); border: 2px solid #FF9800; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong style="color: #FF9800; font-size: 0.9rem;">CODE: {result.dispatch_action_code}</strong>
                                {render_status_badge(result.priority_level + ' Priority', priority_badge_type)}
                            </div>
                            <p style="color: #FFFFFF; font-size: 0.85rem; font-weight: 600; margin: 5px 0;">
                                📍 Category: {result.classification_category} Incident logged at {zone_location}
                            </p>
                            
                            <!-- Real-Time Incident Triage Parameters -->
                            <div style="background: rgba(0,0,0,0.25); border-radius: 6px; padding: 10px; margin: 10px 0; font-size: 0.8rem; line-height: 1.5; color: #E0E1DD;">
                                <strong>Impact Assessment:</strong> {result.impact_assessment}<br/>
                                <strong style="color: #00E5FF;">Suggested Response:</strong> {result.suggested_response}<br/>
                                <strong>Standby Volunteers Quadrant:</strong> {result.nearest_volunteers_quadrant}<br/>
                                <strong style="color: #FF5252;">Medical Allocation:</strong> {result.medical_team_dispatch}<br/>
                                <strong>Est. Resolution Time:</strong> <span style="color: #FFEE58; font-weight: bold;">{result.estimated_resolution_time}</span>
                            </div>
                            
                            <p style="color: #E0E1DD; font-size: 0.8rem; margin: 10px 0 0 0; line-height: 1.4;">
                                <strong>Playbook Directives:</strong> {result.incident_response_playbook}
                            </p>
                            <p style="color: #00FFCC; font-size: 0.8rem; margin-top: 10px; font-weight: bold;">
                                Assigned Responder: {result.closest_volunteer_sector}
                            </p>
                        </div>
                        """
                    )
                    
                    # Explainable AI on Incident Logging
                    render_html(
                        f"""
                        <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.06); padding: 12px; border-radius: 8px; font-size: 0.75rem; margin-bottom: 20px;">
                            <strong style="color: #00FFCC; font-size: 0.8rem;">🎯 Security Dispatch Explainability</strong>
                            <p style="color: #A0C4FF; margin: 4px 0 0 0; line-height: 1.3;">
                                <strong>Rationale:</strong> {result.reason}<br/>
                                <strong>Calculated Severity Confidence:</strong> {result.confidence_score}% • 
                                <strong>Expected Mitigation Impact:</strong> {result.expected_impact}<br/>
                                <strong style="color: #FFEE58;">Alternate Response Unit:</strong> {result.alternative_recommendation}
                            </p>
                        </div>
                        """
                    )
                    st.toast("AI Dispatch command issued successfully!", icon="🛡️")

        with col2:
            st.markdown("### 📋 Active Incident Monitoring Queue")
            st.caption("Live ticket triage backlog from command control:")
            
            # Draw current incidents list
            for inc in st.session_state.incident_database:
                p_badge = "critical" if inc["priority"] in ["High", "Critical"] else ("warning" if inc["priority"] == "Medium" else "low")
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #FFFFFF; font-size: 0.85rem;">{inc['id']}: {inc['type']}</strong>
                            <div style="font-size: 0.75rem; color: #A0C4FF; margin-top: 2px;">Zone: {inc['location']} • Status: <strong>{inc['status']}</strong></div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            {render_status_badge(inc['priority'], p_badge)}
                        </div>
                    </div>
                    """
                )
                
            # Complete simulation incident clearing
            if st.session_state.incident_database:
                if st.button("🧹 Clear Completed Incidents Feed"):
                    st.session_state.incident_database = []
                    st.toast("Cleared backlog.")
                    st.rerun()
            else:
                st.info("Incident backlog clear. No outstanding security tickets.")

            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("### 📑 AI Pre-Shift Shift Briefing Compiler")
            st.caption("Synthesizes a cohesive briefings bulletin to align security teams and volunteers:")
            
            if st.button("📝 Compile Current Shift Briefing Sheet", type="secondary", use_container_width=True):
                with st.spinner("Analyzing active game-logs, queue indices, and transit grids..."):
                    time.sleep(1.5)
                    
                    render_html(
                        f"""
                        <div style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.2); padding: 20px; border-radius: 12px; font-family: 'Courier New', Courier, monospace;">
                            <div style="text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 15px;">
                                <strong style="color: #00FFCC; font-size: 1.1rem;">STADIUMLOGIQ CREW BRIEFING REPORT</strong><br/>
                                <span style="font-size: 0.75rem; color: #A0C4FF;">Shift: Matchday 14 Kickoff Operational Brief ({active_scenario.split(" (")[0]})</span>
                            </div>
                            <ul style="font-size: 0.8rem; color: #E0E1DD; line-height: 1.6; margin-left: -15px;">
                                <li><strong>GATE CONTROL:</strong> Gate B queue is heavily loaded ({crowd_context.get("overall_occupancy_pct", 91)}% overall stadium occupancy). Deploy ticket scanner assistants.</li>
                                <li><strong>ACCESSIBILITY:</strong> Elevator hosts stationed at Sector 112 (Ramp A) to support active routing.</li>
                                <li><strong>TRANSIT STRATEGY:</strong> Ensure dispatch of Red Line Metro guides to direct Sector 114 egress doors.</li>
                                <li><strong>UTILITIES TARGET:</strong> HVAC suite cooling setpoints optimized to shed grid energy loads.</li>
                                <li><strong>TACTICAL COMMANDS:</strong> Monitor dispatcher channels continuously. Active reports logged in {zone_location}.</li>
                            </ul>
                        </div>
                        """
                    )
