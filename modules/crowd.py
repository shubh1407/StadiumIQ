import pandas as pd
import plotly.express as px
import streamlit as st

from services.llm_chain import CrowdAnalysisChain
from services.simulator import StadiumSimulator
from services.utils import apply_accessibility_filters, render_html, render_status_badge


def render_crowd_intelligence() -> None:
    """Renders the Crowd Intelligence safety orchestration suite."""
    apply_accessibility_filters()

    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">👥 Crowd Intelligence & Safety</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Real-time stadium sensor feeds, security camera density logs, predictive gate flow indicators, and explainable safety risk hazard models.
            </p>
        </div>
        """
    )

    # 1. Fetch live contextual parameters
    raw_crowd_data = StadiumSimulator.get_crowd_context()
    active_scenario = StadiumSimulator.get_active_scenario()

    # Run the intelligence chain to get parsed decisions (supports seamless demo fallback)
    if "cached_crowd_analysis" not in st.session_state:
        chain = CrowdAnalysisChain()
        with st.spinner("Analyzing high-frequency camera frames..."):
            st.session_state.cached_crowd_analysis = chain.analyze(raw_crowd_data)

    analysis = st.session_state.cached_crowd_analysis

    # Refresh panel for on-demand intelligence updates
    ref_col1, ref_col2 = st.columns([8, 2])
    with ref_col2:
        if st.button("🔄 Refresh Feeds", use_container_width=True):
            if "cached_crowd_analysis" in st.session_state:
                del st.session_state.cached_crowd_analysis
            st.rerun()

    # 2. Key metrics display row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("🏟️ Total Fans Inside", f"{raw_crowd_data['total_fans_in_stadium']:,}", active_scenario.split(" (")[0])
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

    # 3. Main content split: Left = Spatial Map & Predictive AI, Right = Bottlenecks & Explainable AI
    col1, col2 = st.columns([1.8, 1.2], gap="large")

    with col1:
        st.markdown("### 🗺️ Live Crowd Distribution Heatmap")

        # Generate simulated spatial coordinates for MetLife Stadium zones
        zones = ["Plaza-North", "Plaza-East", "Gate-A-Foyer", "Gate-B-Ingress", "Sector-112-Ramp", "Sector-205-Concourse", "VIP-Suites-Level-2"]
        x_coords = [10, 20, 30, 40, 25, 15, 35]
        y_coords = [15, 25, 12, 38, 42, 10, 22]
        densities = [3.2, 5.1, 4.4, 8.7, 7.6, 2.1, 1.8] if "Before Match" in active_scenario else [8.1, 7.5, 2.1, 1.5, 6.2, 9.4, 4.8]

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
            height=320,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Predictive AI Gate Flow Section
        st.markdown("### 🔮 Predictive Flow Intelligence Panel (15m/30m/60m Projections)")
        st.caption("Active neural-flow models predicting bottleneck probabilities across core turnstiles:")

        # Formulate dynamic predictive metrics based on active scenario
        if "Before Match" in active_scenario:
            pred_data = [
                {"Gate": "Gate A (Main North)", "Current": "45%", "Predicted 15m": "60%", "Predicted 30m": "78%", "Predicted 60m": "90%", "Risk": "HIGH", "badge": "high"},
                {"Gate": "Gate B (Concourse Ingress)", "Current": "72%", "Predicted 15m": "96%", "Predicted 30m": "99%", "Predicted 60m": "100%", "Risk": "CRITICAL", "badge": "critical"},
                {"Gate": "Gate C (West Plaza)", "Current": "20%", "Predicted 15m": "35%", "Predicted 30m": "48%", "Predicted 60m": "65%", "Risk": "LOW", "badge": "low"},
                {"Gate": "Gate D (VIP Only)", "Current": "10%", "Predicted 15m": "15%", "Predicted 30m": "20%", "Predicted 60m": "25%", "Risk": "LOW", "badge": "low"}
            ]
        elif "After Match" in active_scenario:
            pred_data = [
                {"Gate": "Gate A (Main North)", "Current": "95%", "Predicted 15m": "75%", "Predicted 30m": "45%", "Predicted 60m": "10%", "Risk": "HIGH", "badge": "high"},
                {"Gate": "Gate B (Concourse Ingress)", "Current": "98%", "Predicted 15m": "80%", "Predicted 30m": "50%", "Predicted 60m": "15%", "Risk": "HIGH", "badge": "high"},
                {"Gate": "Gate C (West Plaza)", "Current": "90%", "Predicted 15m": "70%", "Predicted 30m": "40%", "Predicted 60m": "8%", "Risk": "HIGH", "badge": "high"},
                {"Gate": "Gate D (VIP Only)", "Current": "35%", "Predicted 15m": "20%", "Predicted 30m": "10%", "Predicted 60m": "2%", "Risk": "LOW", "badge": "low"}
            ]
        elif "Weather Shift" in active_scenario:
            pred_data = [
                {"Gate": "Gate A (Main North)", "Current": "68%", "Predicted 15m": "85%", "Predicted 30m": "92%", "Predicted 60m": "95%", "Risk": "HIGH", "badge": "high"},
                {"Gate": "Gate B (Concourse Ingress)", "Current": "88%", "Predicted 15m": "98%", "Predicted 30m": "100%", "Predicted 60m": "100%", "Risk": "CRITICAL", "badge": "critical"},
                {"Gate": "Gate C (West Plaza)", "Current": "55%", "Predicted 15m": "70%", "Predicted 30m": "82%", "Predicted 60m": "88%", "Risk": "HIGH", "badge": "high"},
                {"Gate": "Gate D (VIP Only)", "Current": "15%", "Predicted 15m": "30%", "Predicted 30m": "45%", "Predicted 60m": "50%", "Risk": "MEDIUM", "badge": "medium"}
            ]
        elif "Critical Emergency" in active_scenario:
            pred_data = [
                {"Gate": "Gate A (Main North)", "Current": "99%", "Predicted 15m": "60%", "Predicted 30m": "20%", "Predicted 60m": "0%", "Risk": "CRITICAL", "badge": "critical"},
                {"Gate": "Gate B (Concourse Ingress)", "Current": "98%", "Predicted 15m": "55%", "Predicted 30m": "15%", "Predicted 60m": "0%", "Risk": "CRITICAL", "badge": "critical"},
                {"Gate": "Gate C (West Plaza)", "Current": "95%", "Predicted 15m": "50%", "Predicted 30m": "10%", "Predicted 60m": "0%", "Risk": "CRITICAL", "badge": "critical"},
                {"Gate": "Gate D (VIP Only)", "Current": "40%", "Predicted 15m": "10%", "Predicted 30m": "20%", "Predicted 60m": "0%", "Risk": "LOW", "badge": "low"}
            ]
        else: # Halftime
            pred_data = [
                {"Gate": "Gate A (Main North)", "Current": "5%", "Predicted 15m": "10%", "Predicted 30m": "15%", "Predicted 60m": "85%", "Risk": "LOW", "badge": "low"},
                {"Gate": "Gate B (Concourse Ingress)", "Current": "8%", "Predicted 15m": "12%", "Predicted 30m": "20%", "Predicted 60m": "98%", "Risk": "LOW", "badge": "low"},
                {"Gate": "Gate C (West Plaza)", "Current": "3%", "Predicted 15m": "8%", "Predicted 30m": "10%", "Predicted 60m": "75%", "Risk": "LOW", "badge": "low"},
                {"Gate": "Gate D (VIP Only)", "Current": "1%", "Predicted 15m": "2%", "Predicted 30m": "5%", "Predicted 60m": "30%", "Risk": "LOW", "badge": "low"}
            ]

        # Draw a beautiful responsive HTML table for predictions
        table_html = """
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; background: rgba(255,255,255,0.01); border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <th style="padding: 10px; color: #00FFCC; font-weight: bold;">Gate / turnstile</th>
                    <th style="padding: 10px; color: #FFFFFF;">Current</th>
                    <th style="padding: 10px; color: #FFFFFF;">In 15m</th>
                    <th style="padding: 10px; color: #FFFFFF;">In 30m</th>
                    <th style="padding: 10px; color: #FFFFFF;">In 60m</th>
                    <th style="padding: 10px; color: #FFFFFF; text-align: right;">Risk</th>
                </tr>
            </thead>
            <tbody>
        """
        for row in pred_data:
            badge_html = render_status_badge(row["Risk"], row["badge"])
            table_html += f"""
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); hover: background-color: rgba(255,255,255,0.02);">
                    <td style="padding: 12px; font-weight: 600; color: #FFFFFF;">{row['Gate']}</td>
                    <td style="padding: 12px; color: #E0E1DD;">{row['Current']}</td>
                    <td style="padding: 12px; color: #00E5FF; font-weight: bold;">{row['Predicted 15m']}</td>
                    <td style="padding: 12px; color: #00FFCC;">{row['Predicted 30m']}</td>
                    <td style="padding: 12px; color: #A0C4FF;">{row['Predicted 60m']}</td>
                    <td style="padding: 12px; text-align: right;">{badge_html}</td>
                </tr>
            """
        table_html += "</tbody></table>"
        render_html(table_html)

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

    # 4. Explainable AI Section at the bottom of the page
    st.markdown("---")
    st.markdown("### 🔍 Explainable AI (XAI) Safety Analysis")
    st.caption("To establish complete operational trust, the AI explains the underlying parameters and fallbacks supporting this safety calculation:")

    xai_col1, xai_col2 = st.columns(2)
    with xai_col1:
        render_html(
            f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 12px; height: 100%;">
                <strong style="color: #00FFCC; font-size: 0.9rem;">🎯 Recommendation Reasoning</strong>
                <p style="color: #E0E1DD; font-size: 0.85rem; margin: 8px 0 0 0; line-height: 1.5;">{analysis.reason}</p>
                <div style="margin-top: 15px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 0.85rem; color: #A0C4FF;">Model Confidence:</span>
                    <span style="background: rgba(0, 255, 204, 0.15); color: #00FFCC; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{analysis.confidence_score}%</span>
                </div>
            </div>
            """
        )
    with xai_col2:
        render_html(
            f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 12px; height: 100%;">
                <strong style="color: #00E5FF; font-size: 0.9rem;">⚡ Expected Impact & Alternative Protocols</strong>
                <p style="color: #E0E1DD; font-size: 0.85rem; margin: 8px 0 0 0; line-height: 1.5;">
                    <strong>Expected Flow Impact:</strong> {analysis.expected_impact}<br/>
                    <strong style="color: #FFEE58; display: inline-block; margin-top: 8px;">Fallback Recommendation:</strong> {analysis.alternative_recommendation}
                </p>
            </div>
            """
        )
