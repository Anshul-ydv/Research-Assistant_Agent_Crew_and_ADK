# src/agents/base.py

from typing import Dict, Any

class Agent:
    """
    Base class for all ADK agents.
    
    This conceptual class provides a common structure for all agents in the system.
    In a real ADK implementation, this might be provided by the framework itself.
    """
    def __init__(self, name: str, role: str, memory, logger):
        """
        Initializes the base agent.
        
        Args:
            name (str): The unique name of the agent.
            role (str): A description of the agent's function.
            memory: An instance of the memory system to share state.
            logger: An instance of the workflow logger for monitoring.
        """
        self.name = name
        self.role = role
        self.memory = memory
        self.logger = logger

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        The main execution method for the agent. This should be overridden by subclasses.
        
        Raises:
            NotImplementedError: If the subclass does not implement this method.
            
        Returns:
            A dictionary containing the agent's results.
        """
        raise NotImplementedError("Each agent must implement the execute method.")