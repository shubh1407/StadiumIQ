import streamlit as st
import time
from services.llm_chain import AccessibilityChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html
from models.schemas import AccessibilityRouteResult

def render_accessibility_hub() -> None:
    """Renders the Accessibility Hub inclusive routing and aid platform."""
    # Apply active CSS changes before rendering anything
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">♿ Accessibility Hub</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Inclusive stadium navigation, step-free route narrations, visual beacons, sensory guides, and helper dispatches.
            </p>
        </div>
        """
    )
    
    # 1. Top Section: High-Visibility display customizers (Accessible preferences)
    st.markdown("### 👓 Inclusive UI Configuration")
    acc_col1, acc_col2 = st.columns(2)
    with acc_col1:
        large_font = st.toggle(
            "🔎 Enable Large Text Mode (115% Zoom)",
            value=st.session_state.get("accessibility_large_text", False),
            key="toggle_large_text"
        )
        if large_font != st.session_state.accessibility_large_text:
            st.session_state.accessibility_large_text = large_font
            st.rerun()
            
    with acc_col2:
        high_contrast = st.toggle(
            "🎨 Enable High Contrast Mode (Monochrome Dark)",
            value=st.session_state.get("accessibility_high_contrast", False),
            key="toggle_high_contrast"
        )
        if high_contrast != st.session_state.accessibility_high_contrast:
            st.session_state.accessibility_high_contrast = high_contrast
            st.rerun()

    st.markdown("---")

    # 2. Main layout divide
    col1, col2 = st.columns([1.2, 1.8], gap="medium")
    
    with col1:
        st.markdown("### 🧭 Step-Free Accessible Router")
        st.caption("Route step-by-step ADA-compliant stadium guidance:")
        
        # User input controls
        cur_loc = st.selectbox("Your Current Location:", ["Entrance Plaza A", "Gate B Ingress Lobby", "Ticket Office Concourse", "Sector 108 Food Court"])
        dest_loc = st.text_input("Target Seat/Sector Destination:", value="Sector 112 Row K Seat 14")
        
        service_type = st.radio(
            "Requested Assistance Program:",
            [
                "♿ Wheelchair Step-Free Route",
                "👓 Vision Impairment Assistant (Tactile & Verbal)",
                "👂 Hearing Impairment Visual Beacon Guide",
                "👵 Senior Citizens Easy-Paced Guide",
                "👶 Children & Family Support Guide"
            ],
            index=0
        )
        
        trigger_route = st.button("🗺️ Compute Inclusive Route", type="primary", use_container_width=True)
        
        # Companion dispatch fast simulator
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("### 🤝 On-Duty ADA Support Squad")
        ada_context = StadiumSimulator.get_accessibility_context()
        st.metric("Companion Hosts Available", f"{ada_context['companion_volunteers_available']} hosts", "Standby sector 112")
        
        if st.button("🦺 Dispatch Personal Helper to Seat Location", use_container_width=True):
            with st.spinner("Assigning closest available inclusion host..."):
                time.sleep(1.5)
                st.success("Companion host dispatched! Volunteer 'Elena G.' is en route with a spare transport wheelchair to Sector 112 foyer. Estimate: 3 mins.")
                st.toast("Host dispatched successfully.", icon="🤝")

    with col2:
        if trigger_route:
            st.markdown("### 🗺️ AI-Optimized Accessible Navigation Path")
            
            # Load accessibility variables and trigger chain
            chain = AccessibilityChain()
            with st.spinner("Calculating step-free matrices..."):
                route: AccessibilityRouteResult = chain.generate_route(
                    service_type=service_type,
                    current_location=cur_loc,
                    destination=dest_loc,
                    context=ada_context
                )
                
            # 1. Show descriptive voice narration
            render_html(
                f"""
                <div style="background: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.2); padding: 15px; border-radius: 12px; margin-bottom: 20px;">
                    <div style="font-weight: bold; color: #00FFCC; margin-bottom: 5px; font-size: 0.9rem;">📢 Screen-Reader Narration Stream</div>
                    <p style="color: #E0E1DD; font-size: 0.9rem; margin: 0; font-style: italic;">"{route.route_narration}"</p>
                </div>
                """
            )
            
            # 2. Display chronological navigation steps
            st.markdown("#### Chronological Route Steps:")
            for idx, step in enumerate(route.navigation_steps, 1):
                badge_text = "Step-Free Access" if step.is_step_free else "Assistance Suggested"
                badge_color = "safe" if step.is_step_free else "warning"
                
                # Check sensory loudness
                sensory_icon = "🔈" if step.sensory_rating == "Quiet" else ("🔉" if step.sensory_rating == "Moderate" else "🔊")
                
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <span style="background: #00FFCC; color: #000; font-weight: bold; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">{idx}</span>
                            <div>
                                <div style="font-size: 0.85rem; color: #FFFFFF; font-weight: 600;">{step.instruction}</div>
                                <div style="font-size: 0.75rem; color: #A0C4FF; margin-top: 2px;">{sensory_icon} Sensory Rating: {step.sensory_rating}</div>
                            </div>
                        </div>
                        <div>{render_status_badge(badge_text, badge_color)}</div>
                    </div>
                    """
                )
                
            # 3. Nearby ADA amenities & sensors
            st.markdown("#### Path Amenities & Milestones:")
            for amenity in route.nearby_ada_amenities:
                st.markdown(f"- 📍 {amenity}")
                
            if route.companion_team_notified:
                st.info("System Trigger: Central Inclusion Host Dispatch system was notified automatically during this search.")
                
            # 4. Explainable AI Section at the bottom of the result
            st.markdown("---")
            st.markdown("### 🔍 Explainable Route Guidance Trust Panel")
            st.caption("AI-justified routing explanation and confidence logs:")
            
            x_col1, x_col2 = st.columns(2)
            with x_col1:
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.06); padding: 15px; border-radius: 10px; height: 100%;">
                        <strong style="color: #00FFCC; font-size: 0.85rem;">🎯 Route Selection Rationale</strong>
                        <p style="color: #E0E1DD; font-size: 0.8rem; margin: 6px 0 0 0; line-height: 1.4;">{route.reason}</p>
                        <div style="margin-top: 10px; font-size: 0.8rem; color: #A0C4FF;">
                            Confidence Score: <span style="color: #00FFCC; font-weight: bold;">{route.confidence_score}%</span>
                        </div>
                    </div>
                    """
                )
            with x_col2:
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.06); padding: 15px; border-radius: 10px; height: 100%;">
                        <strong style="color: #00E5FF; font-size: 0.85rem;">⚡ Inclusive Impact & Fallbacks</strong>
                        <p style="color: #E0E1DD; font-size: 0.8rem; margin: 6px 0 0 0; line-height: 1.4;">
                            <strong>Expected Comfort Gain:</strong> {route.expected_impact}<br/>
                            <strong style="color: #FFEE58; display: inline-block; margin-top: 6px;">Fallback Path:</strong> {route.alternative_recommendation}
                        </p>
                    </div>
                    """
                )
                
        else:
            # Show default view before route trigger
            st.markdown("### 🧘 Sensory Calm Zones")
            st.caption("Active tranquil sanctuary zones mapped inside stadium:")
            
            for lounge in ada_context["sensory_quiet_lounges"]:
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); padding: 15px; border-radius: 12px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <strong style="color: #00FFCC;">{lounge['lounge_id']}</strong>
                            {render_status_badge(lounge['availability'], 'stable')}
                        </div>
                        <div style="font-size: 0.8rem; color: #E0E1DD;">Equipped Amenities: {lounge['amenities']}</div>
                    </div>
                    """
                )
            
            render_html(
                """
                <div style="border: 1px dashed rgba(255,255,255,0.1); padding: 25px; border-radius: 12px; text-align: center; color: rgba(255,255,255,0.4); margin-top: 40px;">
                    <span style="font-size: 2.5rem;">🧭</span>
                    <h5 style="margin-top: 10px; font-weight: 700; color: #E0E1DD;">Configure & Trigger Accessible Routing</h5>
                    <p style="font-size: 0.8rem; max-width: 320px; margin: 5px auto 0 auto;">
                        Enter your location on the left, pick an accessibility program, and hit 'Compute Route' to obtain your customized, voice-ready guide.
                    </p>
                </div>
                """
            )
