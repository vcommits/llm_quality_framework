from abc import ABC, abstractmethod

class BaseDriver(ABC):
    """
    ABSTRACTION: Defines the contract for any browser automation tool.
    The Campaign scripts will ONLY interact with this interface, never the concrete library.
    """

    @abstractmethod
    async def start(self, storage_state=None):
        """
        Starts the browser engine or connects to the app.
        :param storage_state: Optional path to a file containing auth cookies/state.
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Stops the engine, closes connections, and cleans up resources.
        """
        pass

    @abstractmethod
    async def navigate(self, url):
        """
        Visits a URL (Web Mode) or focuses the window (App Mode).
        """
        pass

    @abstractmethod
    async def get_state(self):
        """
        Returns the 'Perception' of the agent.
        Must return a tuple: (raw_html_content, visible_text_snapshot)
        """
        pass

    @abstractmethod
    async def execute_actions(self, actions):
        """
        POLYMORPHISM: Receives a generic list of JSON actions
        and translates them into tool-specific commands (Click, Fill, etc.)
        """
        pass