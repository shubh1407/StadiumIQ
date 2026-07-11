import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from services.llm_chain import CrowdAnalysisChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html
from models.schemas import CrowdAnalysisResult

def render_crowd_intelligence() -> None:
    """Renders the Crowd Intelligence safety orchestration suite."""
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">👥 Crowd Intelligence & Safety</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Real-time stadium sensor feeds, security camera density logs, and LLM-powered safety risk hazard models.
            </p>
        </div>
        """
    )
    
    # 1. Fetch live contextual parameters
    raw_crowd_data = StadiumSimulator.get_crowd_context()
    
    # Run the intelligence chain to get parsed decisions (supports seamless demo fallback)
    chain = CrowdAnalysisChain()
    with st.spinner("Analyzing high-frequency camera frames..."):
        analysis: CrowdAnalysisResult = chain.analyze(raw_crowd_data)
        
    # 2. Key metrics display row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("🏟️ Total Fans Inside", f"{raw_crowd_data['total_fans_in_stadium']:,}", "Matchday 14")
    with m_col2:
        st.metric("📈 Gate Occupancy Rate", f"{raw_crowd_data['overall_occupancy_pct']}%", "+3.2% last 10m")
    with m_col3:
        st.metric("🔥 Average Density Score", f"{analysis.crowd_density_score:.1f}/10", "-0.4% dispersion")
    with m_col4:
        # Custom safety alert badge container
        render_html(
            f"""
            <div style="background: rgba(255,255,255,0.02); padding: 5px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); text-align: center; height: 70px;">
                <span style="font-size: 0.75rem; color: #A0C4FF; text-transform: uppercase;">AI Threat Rating</span><br/>
                <div style="margin-top: 6px;">{render_status_badge(analysis.overall_risk_level + ' Hazard', analysis.overall_risk_level)}</div>
            </div>
            """
        )

    st.markdown("---")

    # 3. Main content split: Left = Interactive Heatmaps & Trend Charts, Right = Bottleneck alerts & Dispatches
    col1, col2 = st.columns([1.8, 1.2], gap="medium")
    
    with col1:
        st.markdown("### 🗺️ Live Crowd Distribution Heatmap")
        
        # Generate simulated spatial coordinates for MetLife Stadium zones
        zones = ["Plaza-North", "Plaza-East", "Gate-A-Foyer", "Gate-B-Ingress", "Sector-112-Ramp", "Sector-205-Concourse", "VIP-Suites-Level-2"]
        x_coords = [10, 20, 30, 40, 25, 15, 35]
        y_coords = [15, 25, 12, 38, 42, 10, 22]
        # Map density indexes
        densities = [3.2, 5.1, 4.4, 8.7, 7.6, 2.1, 1.8]
        
        df_heatmap = pd.DataFrame({
            "Stadium Sector/Zone": zones,
            "X Position": x_coords,
            "Y Position": y_coords,
            "Crowd Density (0-10)": densities
        })
        
        # Plotly Scatter Density Bubble Map
        fig = px.scatter(
            df_heatmap,
            x="X Position",
            y="Y Position",
            size="Crowd Density (0-10)",
            color="Crowd Density (0-10)",
            text="Stadium Sector/Zone",
            color_continuous_scale="Jet",
            range_color=[0, 10],
            template="plotly_dark",
            labels={"X Position": "East-West (m)", "Y Position": "North-South (m)"}
        )
        fig.update_traces(textposition="top center", marker=dict(opacity=0.85, line=dict(width=1, color="white")))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="Density"),
            height=360,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Historical Influx trend plot
        st.markdown("### 🕒 Influx Rate Timeline (Cumulative Arrivals)")
        trends = raw_crowd_data["historical_trends"]
        df_trends = pd.DataFrame(trends)
        
        fig_line = px.area(
            df_trends,
            x="timestamp",
            y="density",
            template="plotly_dark",
            color_discrete_sequence=["#00FFCC"]
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Time relative to kickoff",
            yaxis_title="Normalized Influx Index",
            height=200,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown("### 🚨 High-Priority AI Alerts")
        
        # Render AI warning boxes
        for alert in analysis.system_alerts:
            st.warning(alert)
            
        st.markdown("### 🚧 Segmented Concourse Congestion")
        st.caption("Active monitoring of localized sectors:")
        
        for bn in analysis.active_bottlenecks:
            # Map status colors
            bar_color = "red" if bn.status == "Critical" else ("orange" if bn.status == "Warning" else "green")
            render_html(
                f"""
                <div style="margin-bottom: 12px; background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border-left: 4px solid {bar_color};">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <strong style="color: #FFFFFF;">{bn.zone_id}</strong>
                        <span style="color: #00FFCC; font-weight: bold;">{bn.density_index}/10 Index</span>
                    </div>
                    <div style="font-size: 0.75rem; color: #A0C4FF; margin-bottom: 6px;">Pacing: {bn.flow_rate} ({bn.status} flow)</div>
                </div>
                """
            )
            # Streamlit native progress bar
            st.progress(float(bn.density_index / 10.0))

        st.markdown("### 📋 Dispatch & Safety Strategy")
        st.caption("Central Operations safety directives recommended by LLM:")
        for rec in analysis.tactical_recommendations:
            render_html(
                f"""
                <div style="display: flex; gap: 10px; align-items: start; margin-bottom: 10px; font-size: 0.85rem; line-height: 1.4;">
                    <span style="color: #00FFCC; font-size: 1.1rem;">⚡</span>
                    <span style="color: #E0E1DD;">{rec}</span>
                </div>
                """
            )
            
        # Simulated manual alert broadcast trigger
        if st.button("📢 Broadcast Alert to Field Volunteers", type="primary", use_container_width=True):
            st.toast("Security bulletins broadcasted successfully to Sector 112 UHF radios!", icon="🚨")
