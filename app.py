import os

import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Set Streamlit page configurations
st.set_page_config(
    page_title="StadiumIQ | FIFA World Cup 2026",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Glassmorphic Stylesheet Loader
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback styles
        st.markdown(
            """
            <style>
                .main {
                    background: radial-gradient(circle at top left, #0D1B2A, #1B263B, #0D1B2A);
                    color: #E0E1DD;
                    font-family: 'Inter', sans-serif;
                }
                .stAppHeader {
                    background-color: rgba(13, 27, 42, 0.8) !important;
                    backdrop-filter: blur(10px);
                }
                [data-testid="stSidebar"] {
                    background-color: rgba(27, 38, 59, 0.4) !important;
                    backdrop-filter: blur(15px);
                    border-right: 1px solid rgba(255, 255, 255, 0.1);
                }
                .glass-card {
                    background: rgba(255, 255, 255, 0.04);
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(8px);
                    padding: 24px;
                    margin-bottom: 20px;
                }
                .world-cup-banner {
                    background: linear-gradient(135deg, #00A86B, #0066CC);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 30px;
                    box-shadow: 0 8px 32px 0 rgba(0, 168, 107, 0.3);
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

# Initialize global state variables
def init_session_states():
    if "api_key_valid" not in st.session_state:
        st.session_state.api_key_valid = bool(os.getenv("GROQ_API_KEY"))
    if "current_module" not in st.session_state:
        st.session_state.current_module = "Fan Assistant"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "accessibility_large_text" not in st.session_state:
        st.session_state.accessibility_large_text = False
    if "accessibility_high_contrast" not in st.session_state:
        st.session_state.accessibility_high_contrast = False

def render_sidebar():
    with st.sidebar:
        # Header banner inside Sidebar
        st.markdown(
            """
            <div role="banner" style="text-align: center; padding: 15px 0;">
                <h1 style="color: #00FFCC; font-size: 2rem; margin: 0; font-weight: 800; letter-spacing: 1px;">
                    <span aria-hidden="true">🏟️</span> StadiumIQ
                </h1>
                <p style="color: #A0C4FF; font-size: 0.9rem; margin-top: 5px;">AI Stadium Intelligence Platform</p>
                <div style="background-color: #00E676; color: #000; font-size: 0.75rem; font-weight: bold; padding: 3px 8px; border-radius: 20px; display: inline-block; margin-top: 5px;">
                    <span aria-hidden="true">🏆</span> FIFA WORLD CUP 2026
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1); margin-top: 10px; margin-bottom: 15px;' />", unsafe_allow_html=True)

        # Navigation option menu
        selected = option_menu(
            menu_title="Intelligence Suites",
            options=[
                "Fan Assistant",
                "Crowd Intelligence",
                "Accessibility Hub",
                "Transport Nexus",
                "Sustainability Monitor",
                "Operations Command"
            ],
            icons=[
                "chat-dots-fill",
                "people-fill",
                "universal-access",
                "bus-front-fill",
                "recycle",
                "shield-fill-check"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px !important", "background-color": "transparent"},
                "icon": {"color": "#00FFCC", "font-size": "1.1rem"},
                "nav-link": {
                    "font-size": "0.95rem",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#E0E1DD",
                    "--hover-color": "rgba(255, 255, 255, 0.08)",
                    "border-radius": "10px",
                    "padding": "10px 15px"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, rgba(0, 168, 107, 0.2), rgba(0, 102, 204, 0.3))",
                    "border-left": "4px solid #00FFCC",
                    "font-weight": "600",
                    "color": "#FFFFFF"
                }
            }
        )

        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1);' />", unsafe_allow_html=True)

        # 🎮 Live Simulation Controller
        st.markdown('### <span aria-hidden="true">🎮</span> Live Simulation Controller', unsafe_allow_html=True)
        st.caption("Alter stadium-wide state variables instantly:")

        scenarios = [
            "🎟️ Before Match (High Entry Crowd)",
            "🍔 Halftime (Food Court Rush)",
            "🏃 After Match (Exit Congestion)",
            "⛈️ Sudden Weather Shift (Rain/Storm)",
            "🚨 Critical Emergency Event"
        ]

        if "stadium_scenario" not in st.session_state:
            st.session_state.stadium_scenario = "🎟️ Before Match (High Entry Crowd)"

        try:
            default_idx = scenarios.index(st.session_state.stadium_scenario)
        except ValueError:
            default_idx = 0

        scenario_select = st.sidebar.radio(
            "Select Stadium Phase:",
            scenarios,
            index=default_idx,
            key="stadium_scenario_selector",
            help="Switch the simulated stadium phase to see how live data changes across every module.",
        )

        if scenario_select != st.session_state.stadium_scenario:
            st.session_state.stadium_scenario = scenario_select
            # Clear analysis caches so models are forced to evaluate the new context in real-time
            if "cached_crowd_analysis" in st.session_state:
                del st.session_state.cached_crowd_analysis
            if "cached_sustainability_result" in st.session_state:
                del st.session_state.cached_sustainability_result
            st.toast(f"Stadium transitioned to: {scenario_select.split(' ', 1)[1]}!", icon="🔄")
            st.rerun()

        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1);' />", unsafe_allow_html=True)

    return selected

def main():
    load_custom_css()
    init_session_states()

    # Skip link lets keyboard/screen-reader users jump straight past the
    # sidebar navigation into the main module content.
    st.markdown(
        '<a href="#main-content" style="position:absolute;left:-9999px;" '
        'class="skip-link">Skip to main content</a>',
        unsafe_allow_html=True,
    )

    selected_module = render_sidebar()
    st.session_state.current_module = selected_module

    st.markdown('<div id="main-content" role="main"></div>', unsafe_allow_html=True)

    # Render correct module view dynamically with defensive import guards
    try:
        if selected_module == "Fan Assistant":
            from modules.fan_assistant import render_fan_assistant
            render_fan_assistant()

        elif selected_module == "Crowd Intelligence":
            from modules.crowd import render_crowd_intelligence
            render_crowd_intelligence()

        elif selected_module == "Accessibility Hub":
            from modules.accessibility import render_accessibility_hub
            render_accessibility_hub()

        elif selected_module == "Transport Nexus":
            from modules.transport import render_transport_nexus
            render_transport_nexus()

        elif selected_module == "Sustainability Monitor":
            from modules.sustainability import render_sustainability_monitor
            render_sustainability_monitor()

        elif selected_module == "Operations Command":
            from modules.operations import render_operations_command
            render_operations_command()

    except ImportError as e:
        # Fallback view for uncompleted files so the application remains runnable at each step
        st.markdown(f"### ⚙️ Module '{selected_module}' is currently loading...")
        st.info("The production-ready components are being written step-by-step. Hang tight!")
        st.caption(f"Error trace (expected during build order): {str(e)}")

if __name__ == "__main__":
    main()
