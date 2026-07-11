from typing import List, Dict

class ConversationMemory:
    """
    Manages conversational memory thread state stored inside Streamlit's session_state.
    Provides simple mechanisms to query, insert, and serialize histories without token overflow.
    """

    def __init__(self, max_turns: int = 10) -> None:
        self.max_turns = max_turns

    def get_history(self, history_list: List[Dict[str, str]]) -> str:
        """Serializes current history list to a raw string representation for LLM ingestion."""
        if not history_list:
            return "No previous conversation history. This is the first interaction."

        # Keep only the last N turns to avoid context blowing up
        trimmed_history = history_list[-self.max_turns:]
        
        serialized = []
        for message in trimmed_history:
            role = "Fan" if message["role"] == "user" else "Assistant"
            content = message["content"]
            serialized.append(f"{role}: {content}")
            
        return "\n".join(serialized)

    def add_turn(self, history_list: List[Dict[str, str]], role: str, content: str) -> List[Dict[str, str]]:
        """Appends a new turn directly into the referenced session_state history list."""
        history_list.append({"role": role, "content": content})
        # Prevent memory leaks or gigantic payloads
        if len(history_list) > self.max_turns * 2:
            history_list[:] = history_list[-(self.max_turns * 2):]
        return history_list
