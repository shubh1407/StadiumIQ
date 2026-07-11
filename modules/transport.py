import streamlit as st
import pandas as pd
import plotly.express as px
from services.llm_chain import TransportChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html
from models.schemas import TransportnexusResult

def render_transport_nexus() -> None:
    """Renders the Transport Nexus transit orchestration system."""
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">🚌 Transport Nexus</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Optimized stadium dispersion algorithms, metro delays tracking, shuttle wait times, and rideshare surge guides.
            </p>
        </div>
        """
    )
    
    # 1. Fetch transport simulation context
    trans_context = StadiumSimulator.get_transport_context()
    
    # 2. Main columns layout: Input/Controls & Lot Occupancy Left, Dynamic Recommendation Right
    col1, col2 = st.columns([1.1, 1.9], gap="medium")
    
    with col1:
        st.markdown("### 🗺️ Live Dispatch Terminal")
        st.caption("Enter fan seat sector and destination zone:")
        
        sector_id = st.selectbox("Current Seating Sector (e.g. Sector 114):", ["114", "202", "305", "VIP Suite B"])
        destination_zone = st.text_input("Destination Zone / Regional Hub:", value="Central Station (Downtown Hub)")
        
        trigger_search = st.button("🗺️ Compute Optimized Transit Path", type="primary", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### 🅿️ Parking Lot Occupancy")
        for lot in trans_context["parking_lots"]:
            badge_type = "critical" if "FULL" in lot["recommendation"] else "active"
            render_html(
                f"""
                <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <strong style="color: #FFFFFF; font-size: 0.85rem;">{lot['lot_id']}</strong>
                        {render_status_badge(f"{lot['occupancy_pct']}% Full", badge_type)}
                    </div>
                    <div style="font-size: 0.75rem; color: #A0C4FF;">Advice: {lot['recommendation']}</div>
                </div>
                """
            )
            
    with col2:
        if trigger_search:
            st.markdown("### 💡 StadiumIQ Smart Transit Recommendations")
            
            # Fire chain
            chain = TransportChain()
            with st.spinner("Crunching post-match transit timelines..."):
                result: TransportnexusResult = chain.get_recommendation(
                    sector_id=sector_id,
                    destination_zone=destination_zone,
                    context=trans_context
                )
                
            # Render best transit choice
            render_html(
                f"""
                <div style="background: linear-gradient(135deg, rgba(0, 168, 107, 0.15), rgba(0, 102, 204, 0.15)); border: 1px solid #00FFCC; padding: 18px; border-radius: 16px; margin-bottom: 25px;">
                    <span style="font-size: 0.75rem; font-weight: bold; text-transform: uppercase; color: #00FFCC; letter-spacing: 1px;">🥇 AI Top Recommendation</span>
                    <h3 style="margin: 5px 0 0 0; color: #FFFFFF; font-weight: 800;">Take the {result.recommended_option_mode} Express</h3>
                    <p style="margin: 5px 0 0 0; color: #E0E1DD; font-size: 0.9rem;">{result.travel_time_summary}</p>
                </div>
                """
            )
            
            # Show multi-transit options
            st.markdown("#### Travel Option Alternatives Comparison:")
            
            # Convert list of Pydantic models to Pandas dataframe for quick chart render
            raw_options = [opt.model_dump() for opt in result.all_transit_options]
            df_opt = pd.DataFrame(raw_options)
            
            # Display custom table
            for opt in result.all_transit_options:
                con_color = "low" if opt.congestion_level == "Low" else ("warning" if opt.congestion_level == "Medium" else "critical")
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #FFFFFF; font-size: 0.9rem;">🚇 {opt.mode}</strong>
                            <div style="font-size: 0.75rem; color: #A0C4FF; margin-top: 3px;">
                                Duration: {opt.estimated_duration_mins} mins • Est. Cost: ${opt.estimated_cost_usd:.2f} • CO2 offset: {opt.carbon_footprint_kg}kg
                            </div>
                        </div>
                        <div>{render_status_badge(f"{opt.congestion_level} Traffic", con_color)}</div>
                    </div>
                    """
                )
                
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("#### 📊 Alternate Routes: Travel Time vs. CO2 Footprint")
            
            # Draw Comparison bar chart using Plotly Express
            fig = px.bar(
                df_opt,
                x="mode",
                y=["estimated_duration_mins", "carbon_footprint_kg"],
                title="Duration (Minutes) and Carbon Footprint (kg Co2 Equivalent)",
                barmode="group",
                template="plotly_dark",
                color_discrete_map={"estimated_duration_mins": "#00FFCC", "carbon_footprint_kg": "#2196F3"},
                labels={"mode": "Transit Mode", "value": "Metric Index"}
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend_title_text="Transit Indicator",
                height=260,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Dispatch guide
            st.markdown("<br/>", unsafe_allow_html=True)
            render_html(
                f"""
                <div style="background: rgba(33, 150, 243, 0.05); border: 1px solid rgba(33, 150, 243, 0.2); border-radius: 12px; padding: 15px; font-size: 0.85rem; color: #E0E1DD;">
                    <strong>ℹ️ Operational Directive for Sector Volunteers:</strong><br/>
                    {result.operator_guideline}
                </div>
                """
            )
            
        else:
            # Render general live shuttle schedules
            st.markdown("### 🚌 Real-Time Charter Shuttle Timelines")
            shuttles = trans_context["shuttle_bus"]
            
            sc1, sc2 = st.columns(2)
            with sc1:
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 15px; border-radius: 12px;">
                        <strong style="color: #00FFCC;">Route A (Airport Loop)</strong>
                        <div style="font-size: 1.5rem; font-weight: bold; margin: 5px 0;">{shuttles['route_a_airport']['wait_time_mins']} mins</div>
                        <div style="font-size: 0.75rem; color: #A0C4FF;">Buses Running: {shuttles['route_a_airport']['buses_active']} • Current Load: {shuttles['route_a_airport']['load']}</div>
                    </div>
                    """
                )
            with sc2:
                render_html(
                    f"""
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 15px; border-radius: 12px;">
                        <strong style="color: #00FFCC;">Route B (Downtown Loop)</strong>
                        <div style="font-size: 1.5rem; font-weight: bold; margin: 5px 0;">{shuttles['route_b_downtown']['wait_time_mins']} mins</div>
                        <div style="font-size: 0.75rem; color: #A0C4FF;">Buses Running: {shuttles['route_b_downtown']['buses_active']} • Current Load: {shuttles['route_b_downtown']['load']}</div>
                    </div>
                    """
                )
                
            render_html(
                """
                <div style="border: 1px dashed rgba(255,255,255,0.1); padding: 30px; border-radius: 12px; text-align: center; color: rgba(255,255,255,0.4); margin-top: 30px;">
                    <span style="font-size: 2.5rem;">🚌</span>
                    <h5 style="margin-top: 10px; font-weight: 700; color: #E0E1DD;">Post-Match Dispersion Calculator</h5>
                    <p style="font-size: 0.8rem; max-width: 340px; margin: 5px auto 0 auto;">
                        Enter seating sectors and targets to generate immediate multi-modal options and carbon charts.
                    </p>
                </div>
                """
            )
    pre_match_delay = trans_context["metro"]
    st.info(f"🚇 **{pre_match_delay['line_name']}**: {pre_match_delay['status']} with zero delay. Operating at {pre_match_delay['current_load_pct']}% load.")

