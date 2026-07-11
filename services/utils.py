import streamlit as st


def inject_glassmorphic_card(title: str, content_html: str, border_color: str = "rgba(255, 255, 255, 0.1)") -> None:
    """Renders a beautiful glassmorphic container with custom inner HTML contents."""
    card_style = f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid {border_color};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    ">
        <h4 style="color: #00FFCC; margin-top: 0; margin-bottom: 12px; font-weight: 700; font-size: 1.15rem; letter-spacing: 0.5px;">{title}</h4>
        <div style="color: #E0E1DD; font-size: 0.95rem; line-height: 1.6;">
            {content_html}
        </div>
    </div>
    """
    st.markdown(card_style, unsafe_allow_html=True)

def render_html(html_str: str) -> None:
    """Renders HTML cleanly using st.markdown by stripping leading indentation and formatting to avoid markdown code-block issues."""
    import inspect
    cleaned = inspect.cleandoc(html_str)
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    st.markdown(" ".join(lines), unsafe_allow_html=True)

def render_status_badge(label: str, status_type: str) -> str:
    """Generates a clean HTML status badge colored dynamically based on status type."""
    colors = {
        "critical": {"bg": "rgba(244, 67, 54, 0.15)", "text": "#FF5252", "border": "rgba(244, 67, 54, 0.4)"},
        "high": {"bg": "rgba(255, 152, 0, 0.15)", "text": "#FF9800", "border": "rgba(255, 152, 0, 0.4)"},
        "medium": {"bg": "rgba(255, 235, 59, 0.12)", "text": "#FFEE58", "border": "rgba(255, 235, 59, 0.4)"},
        "low": {"bg": "rgba(33, 150, 243, 0.15)", "text": "#42A5F5", "border": "rgba(33, 150, 243, 0.4)"},
        "active": {"bg": "rgba(76, 175, 80, 0.15)", "text": "#66BB6A", "border": "rgba(76, 175, 80, 0.4)"},
        "safe": {"bg": "rgba(76, 175, 80, 0.15)", "text": "#66BB6A", "border": "rgba(76, 175, 80, 0.4)"},
        "warning": {"bg": "rgba(255, 152, 0, 0.15)", "text": "#FF9800", "border": "rgba(255, 152, 0, 0.4)"},
        "stable": {"bg": "rgba(0, 188, 212, 0.15)", "text": "#26C6DA", "border": "rgba(0, 188, 212, 0.4)"},
    }
    cfg = colors.get(status_type.lower(), {"bg": "rgba(255,255,255,0.08)", "text": "#E0E1DD", "border": "rgba(255,255,255,0.2)"})

    return f'<span style="background-color: {cfg["bg"]}; color: {cfg["text"]}; border: 1px solid {cfg["border"]}; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; display: inline-block; letter-spacing: 0.5px;">{label}</span>'

def apply_accessibility_filters() -> None:
    """Applies high contrast or large font stylesheets globally using streamlit session states."""
    css_override = ""
    if st.session_state.get("accessibility_large_text", False):
        css_override += """
            html, body, [class*="st-"] {
                font-size: 1.15rem !important;
            }
            h1, h2, h3 {
                font-size: 2.2rem !important;
            }
            p, span, li, button, input {
                font-size: 1.1rem !important;
            }
        """
    if st.session_state.get("accessibility_high_contrast", False):
        css_override += """
            html, body, .main {
                background: #000000 !important;
                color: #FFFFFF !important;
            }
            .glass-card, div[style*="background"] {
                background: #111111 !important;
                border: 2px solid #FFFFFF !important;
                color: #FFFFFF !important;
            }
            h1, h2, h3, h4, h5, h6, span, p, li, strong {
                color: #FFFFFF !important;
                text-shadow: none !important;
            }
            button, .stButton>button {
                background-color: #00FFCC !important;
                color: #000000 !important;
                font-weight: 900 !important;
                border: 2px solid #FFFFFF !important;
            }
        """
    if css_override:
        st.markdown(f"<style>{css_override}</style>", unsafe_allow_html=True)

def render_world_cup_header() -> None:
    """Renders the official World Cup responsive title card."""
    st.markdown(
        """
        <div class="world-cup-banner">
            <span style="font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; color: #A0C4FF;">
                FIFA World Cup 2026 Live Operations Dashboard
            </span>
            <h2 style="margin: 5px 0 0 0; color: #FFFFFF; font-weight: 800; font-size: 2.2rem; letter-spacing: -0.5px;">
                STADIUMLOGIQ STADIUM OPERATIONS TERMINAL
            </h2>
            <p style="margin: 5px 0 0 0; font-size: 0.95rem; color: #00FFCC; font-weight: 500;">
                MetLife Stadium (Zone A) • Boston, MA • Capacity 82,500
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
