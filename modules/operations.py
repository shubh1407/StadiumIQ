import streamlit as st
import time
from services.llm_chain import OpsCommandChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html
from models.schemas import OperationsCommandResult

def render_operations_command() -> None:
    """Renders the Operations Command control board."""
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">🛡️ Operations Command Center</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Live incident triage dashboards, automatic volunteer dispatch grids, and crew shift briefing compilers.
            </p>
        </div>
        """
    )
    
    # 1. Load active operations context
    ops_context = StadiumSimulator.get_operations_context()
    
    # Initialize active logged incidents list if not already present
    if "incident_database" not in st.session_state:
        st.session_state.incident_database = list(ops_context["active_incidents"])
        
    # 2. Split view: Left = Incident Logging Form & Dispatches, Right = Incident Feed & Shift Briefs
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
                
                # Show beautiful dispatch card
                st.markdown("---")
                st.markdown("### 📡 Active Dispatch Instructions")
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
                        <p style="color: #E0E1DD; font-size: 0.8rem; margin: 10px 0 0 0; line-height: 1.4;">
                            <strong>Playbook Directives:</strong> {result.incident_response_playbook}
                        </p>
                        <p style="color: #00FFCC; font-size: 0.8rem; margin-top: 10px; font-weight: bold;">
                            Assigned Closest Responder: {result.closest_volunteer_sector} Tactical Squad
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
            p_badge = "critical" if inc["priority"] == "High" else ("warning" if inc["priority"] == "Medium" else "low")
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

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("### 📑 AI Pre-Shift Shift Briefing Compiler")
        st.caption("Synthesizes a cohesive briefings bulletin to align security teams and volunteers:")
        
        if st.button("📝 Compile Current Shift Briefing Sheet", type="secondary", use_container_width=True):
            with st.spinner("Analyzing active game-logs, queue indices, and transit grids..."):
                time.sleep(2.0)
                
                render_html(
                    """
                    <div style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.2); padding: 20px; border-radius: 12px; font-family: 'Courier New', Courier, monospace;">
                        <div style="text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 15px;">
                            <strong style="color: #00FFCC; font-size: 1.1rem;">STADIUMLOGIQ CREW BRIEFING REPORT</strong><br/>
                            <span style="font-size: 0.75rem; color: #A0C4FF;">Shift: Matchday 14 Kickoff Operational Brief</span>
                        </div>
                        <ul style="font-size: 0.8rem; color: #E0E1DD; line-height: 1.6; margin-left: -15px;">
                            <li><strong>GATE CONTROL:</strong> Divert incoming pedestrian streams from Gate B turnstiles towards Gate C outer lanes.</li>
                            <li><strong>ACCESSIBILITY:</strong> Ensure elevator hosts are stationed at Elevator #3 near Sector 112 due to accessible route dispatches.</li>
                            <li><strong>TRANSIT STRATEGY:</strong> Highlight Red Line subway frequency (3 mins) to dispersing sectors.</li>
                            <li><strong>UTILITIES TARGET:</strong> Air conditioning setpoints for Suite level adjusted to 74°F for grid peak load optimization.</li>
                            <li><strong>TACTICAL COMMANDS:</strong> Maintain UHF channel 4 frequencies for active incident monitoring (Backlog ID: INC-882, INC-883).</li>
                        </ul>
                    </div>
                    """
                )
