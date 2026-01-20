from abc import ABC, abstractmethod

class BaseDriver(ABC):
    """
    ABSTRACTION: Defines the contract for any browser automation tool.
    The Campaign scripts will ONLY interact with this interface.
    """

    @abstractmethod
    async def start(self, user_data_dir=None):
        """Starts the browser engine."""
        pass

    @abstractmethod
    async def stop(self):
        """Stops the engine and cleans up resources."""
        pass

    @abstractmethod
    async def navigate(self, url):
        """Visits a URL."""
        pass

    @abstractmethod
    async def get_state(self):
        """
        Returns the 'Perception' of the agent.
        Must return a tuple: (raw_html, visible_text_snapshot)
        """
        pass

    @abstractmethod
    async def execute_actions(self, action_list):
        """
        POLYMORPHISM: Receives generic JSON actions and translates
        them into tool-specific commands.
        """
        pass