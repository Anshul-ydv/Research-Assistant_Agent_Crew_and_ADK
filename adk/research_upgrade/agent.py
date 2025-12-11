import google.generativeai as genai
from src.agents.base import Agent

class RootAgent(Agent):
    """Root agent for handling user queries."""
    def __init__(self, api_key: str):
        super().__init__("RootAgent", "Main Assistant", None, None)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
