import streamlit as st
import pandas as pd
import plotly.express as px
from services.llm_chain import SustainabilityChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html
from models.schemas import SustainabilityResult

def render_sustainability_monitor() -> None:
    """Renders the Sustainability Monitor dashboard."""
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">♻️ Sustainability Monitor</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Live stadium power-grid loads, real-time waste diversion counts, and fan-incentive recycling gamification.
            </p>
        </div>
        """
    )
    
    # 1. Fetch live metrics
    eco_context = StadiumSimulator.get_sustainability_context()
    
    # Run Chain (cached in session-state for instant reruns)
    if "cached_sustainability_result" not in st.session_state:
        chain = SustainabilityChain()
        with st.spinner("Monitoring micro-grid power configurations..."):
            st.session_state.cached_sustainability_result = chain.monitor_utilities(eco_context)
            
    result: SustainabilityResult = st.session_state.cached_sustainability_result

    # On-demand refresh button for utility tracking
    ref_col1, ref_col2 = st.columns([8, 2])
    with ref_col2:
        if st.button("🔄 Refresh Grid", use_container_width=True):
            if "cached_sustainability_result" in st.session_state:
                del st.session_state.cached_sustainability_result
            st.rerun()
        
    # 2. Top-level status indicators
    sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)
    with sc_col1:
        st.metric("🔋 Active Power Grid Load", f"{eco_context['power_grid_load_kw']} kW", "Grid Optimal")
    with sc_col2:
        st.metric("☀️ Clean Solar Generation", f"{eco_context['solar_generation_pct']}% of total", "+5.4% solar peak")
    with sc_col3:
        st.metric("💧 Water Recycled Today", f"{eco_context['water_recycled_liters']:,} Liters", "Sanitation line B")
    with sc_col4:
        render_html(
            f"""
            <div style="background: rgba(255,255,255,0.02); padding: 5px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); text-align: center; height: 70px;">
                <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase;">Grid Load Rating</span><br/>
                <div style="margin-top: 6px;">{render_status_badge(result.grid_power_status, "stable")}</div>
            </div>
            """
        )

    st.markdown("---")

    # 3. Content layout: Left = Waste analytics, Right = Leaderboard & Fan Gamification
    col1, col2 = st.columns([1.6, 1.4], gap="medium")
    
    with col1:
        st.markdown("### 📊 Waste Diversion Analytics")
        st.caption("Active weights of categorized waste diverted from regional landfill sites:")
        
        # Plotly Pie chart for waste segregation ratios
        waste_data = eco_context["waste_segregation"]
        df_waste = pd.DataFrame({
            "Waste Classification": ["Organic Compostable", "Recyclable Plastics", "Residual Landfill"],
            "Weight (Kilograms)": [waste_data["organic_kg"], waste_data["recyclable_plastic_kg"], waste_data["landfill_kg"]]
        })
        
        fig = px.pie(
            df_waste,
            values="Weight (Kilograms)",
            names="Waste Classification",
            hole=0.45,
            color_discrete_sequence=["#4CAF50", "#2196F3", "#F44336"],
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Energy load balance alert
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("### 💡 Operator Grid Insight")
        st.info(f"⚡ **Grid Optimization Directives**: {result.operator_grid_insight}")
        
    with col2:
        st.markdown("### 🏆 Active Fan Eco Leaderboard")
        st.caption("Tracking plastic-sorting counts across stadium zones:")
        
        for idx, leader in enumerate(eco_context["active_eco_leaderboard"], 1):
            render_html(
                f"""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <span style="background: #4CAF50; color: #FFFFFF; font-weight: bold; border-radius: 40%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem;">#{idx}</span>
                        <div>
                            <strong style="color: #FFFFFF; font-size: 0.85rem;">{leader['group_id']}</strong>
                            <div style="font-size: 0.75rem; color: #A0C4FF;">Bottles recycled: {leader['recycled_bottles']} units</div>
                        </div>
                    </div>
                    <div style="color: #00FFCC; font-weight: bold; font-size: 0.9rem;">{leader['points']} Pts</div>
                </div>
                """
            )
            
        st.markdown("### ♻️ Fan Eco Gamification Challenges")
        st.caption("Help reduce FIFA World Cup carbon footprint to claim souvenir badges:")
        
        for ch in result.fan_challenges:
            render_html(
                f"""
                <div style="background: rgba(0, 168, 107, 0.05); border: 1px solid rgba(0, 168, 107, 0.2); border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <strong style="color: #00FFCC; font-size: 0.85rem;">🌱 {ch.challenge_title}</strong>
                        <span style="color: #4CAF50; font-size: 0.8rem; font-weight: bold;">+{ch.points_reward} Pts</span>
                    </div>
                    <p style="color: #E0E1DD; font-size: 0.75rem; margin-top: 5px; line-height: 1.4;">{ch.instructions}</p>
                </div>
                """
            )
            
        # Simulation input to check custom carbon calculators
        st.markdown("---")
        st.markdown("#### Calculate Your Travel Footprint:")
        p_dist = st.number_input("Est. Travel Distance to MetLife (Miles):", min_value=1.0, value=15.0)
        calc_carbon = p_dist * 0.404  # average co2 in kg per mile
        st.success(f"🌱 Your travel carbon footprint estimate: **{calc_carbon:.2f} kg of CO2**.")

    # 4. Explainable AI Section
    st.markdown("---")
    st.markdown("### 🔍 Explainable Utility Optimization Trust Panel")
    st.caption("Auditable metrics describing the AI's environmental recommendations:")
    
    x_col1, x_col2 = st.columns(2)
    with x_col1:
        render_html(
            f"""
            <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.06); padding: 15px; border-radius: 10px; height: 100%;">
                <strong style="color: #00FFCC; font-size: 0.85rem;">🎯 Grid Load Reduction Rationale</strong>
                <p style="color: #E0E1DD; font-size: 0.8rem; margin: 6px 0 0 0; line-height: 1.4;">{result.reason}</p>
                <div style="margin-top: 10px; font-size: 0.8rem; color: #A0C4FF;">
                    Optimized Accuracy Confidence: <span style="color: #00FFCC; font-weight: bold;">{result.confidence_score}%</span>
                </div>
            </div>
            """
        )
    with x_col2:
        render_html(
            f"""
            <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.06); padding: 15px; border-radius: 10px; height: 100%;">
                <strong style="color: #00E5FF; font-size: 0.85rem;">⚡ Sustainability Impact & Backup Actions</strong>
                <p style="color: #E0E1DD; font-size: 0.8rem; margin: 6px 0 0 0; line-height: 1.4;">
                    <strong>Expected Savings:</strong> {result.expected_impact}<br/>
                    <strong style="color: #FFEE58; display: inline-block; margin-top: 6px;">Micro-Grid Fallback:</strong> {result.alternative_recommendation}
                </p>
            </div>
            """
        )
