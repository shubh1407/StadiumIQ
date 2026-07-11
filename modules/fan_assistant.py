import streamlit as st
import time
from services.llm_chain import FanAssistantChain
from services.simulator import StadiumSimulator
from services.utils import render_status_badge, apply_accessibility_filters, render_html

def render_fan_assistant() -> None:
    """Renders the official multi-lingual Fan Assistant chatbot module."""
    # Apply global accessibility modes
    apply_accessibility_filters()
    
    render_html(
        """
        <div style="margin-bottom: 25px;">
            <h2 style="color: #00FFCC; font-weight: 800; margin-bottom: 5px;">💬 Fan Assistant</h2>
            <p style="color: #A0C4FF; margin: 0; font-size: 0.95rem;">
                Official multi-lingual concierge for the FIFA World Cup 2026. Get live navigation guides, concession wait-times, and assistance.
            </p>
        </div>
        """
    )
    
    # 1. Main visual split: Left sidebar column for Context & Suggested Actions, Right for Conversation
    col1, col2 = st.columns([1, 2.2], gap="large")
    
    with col1:
        st.markdown("### 🏟️ Stadium Live Status")
        
        # Load simulated context for the side widget
        status_text = StadiumSimulator.get_stadium_context()
        
        render_html(
            f"""
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: 600; color: #FFFFFF;">MetLife Stadium</span>
                    {render_status_badge("Match 14 LIVE", "active")}
                </div>
                <div style="font-size: 0.85rem; color: #E0E1DD; line-height: 1.6;">
                    {status_text.replace("- ", "• ")}
                </div>
            </div>
            """
        )
        
        st.markdown("### 💡 Quick Actions")
        st.caption("Click any preset query below to instantly route to StadiumIQ:")
        
        presets = [
            "🍔 Vegetarian food near Gate B",
            "🚽 Find a restroom with short queue",
            "🚗 Where is Lot Blue Overflow?",
            "🎟️ My mobile ticket won't scan!",
            "🚨 Medical Emergency near Sector 112"
        ]
        
        # Create small styled prompt buttons
        preset_clicked = None
        for preset in presets:
            if st.button(preset, use_container_width=True, key=f"preset_{preset}"):
                preset_clicked = preset[2:]  # Strip icon
                
    with col2:
        st.markdown("### 🗣️ Multi-Lingual Intelligence Portal")
        
        # Instantiate chain
        chain = FanAssistantChain()
        
        # Initialize conversation state if empty
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Draw previous chats
        chat_container = st.container(height=450, border=True)
        with chat_container:
            if not st.session_state.chat_history:
                render_html(
                    """
                    <div style="text-align: center; padding: 80px 20px; color: rgba(255, 255, 255, 0.4);">
                        <span style="font-size: 3rem;">👋</span>
                        <h4 style="margin-top: 15px; font-weight: 700; color: #00FFCC;">StadiumIQ Concierge</h4>
                        <p style="font-size: 0.85rem; max-width: 320px; margin: 5px auto 0 auto;">
                            Ask me any question in English, Spanish, French, German, or your preferred language.
                        </p>
                    </div>
                    """
                )
            else:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        
        # Handle message input
        user_input = st.chat_input("Ask StadiumIQ (e.g. 'Where is restroom Level 1 East?')")
        
        # Force submit if quick action was clicked
        if preset_clicked:
            user_input = preset_clicked

        if user_input:
            # 1. Show user message instantly
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)
            
            # 2. Add user turn to session state history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # 3. Stream AI answer
            with chat_container:
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    
                    # Construct serialized memory history
                    from services.memory import ConversationMemory
                    mem = ConversationMemory()
                    history_str = mem.get_history(st.session_state.chat_history[:-1])
                    
                    # Generate streaming output tokens
                    full_response = ""
                    for token in chain.run_streaming(
                        user_query=user_input,
                        history_buffer=history_str,
                        stadium_context=status_text
                    ):
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")
                    
                    # Render complete clean markdown output
                    response_placeholder.markdown(full_response)
                    
            # 4. Save response to state and rerun to preserve display
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            st.rerun()

        # Clear Conversation Button
        if st.session_state.chat_history:
            st.markdown("<div style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
            if st.button("🧹 Clear Chat History", type="secondary"):
                st.session_state.chat_history = []
                st.toast("Chat history cleared.")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
