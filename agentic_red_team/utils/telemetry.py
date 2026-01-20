# File: agentic_red_team/utils/telemetry.py
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.litellm import LiteLLMInstrumentor
import os


class TelemetryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance.setup()
        return cls._instance

    def setup(self):
        """
        Starts the Phoenix server and wires up the listeners.
        """
        # 1. Start Local Server (The UI)
        # This will run on http://localhost:6006
        self.session = px.launch_app()
        print(f"🔥 [Telemetry] Phoenix Active: {self.session.url}")

        # 2. Register the Tracer (The Listener)
        # This connects standard Python logging to Phoenix
        self.tracer_provider = register(
            project_name="agentic_red_team_v1",
            endpoint="http://localhost:6006/v1/traces"
        )

        # 3. Auto-Instrument LiteLLM
        # This automatically captures every call 'brain.py' makes
        LiteLLMInstrumentor().instrument(tracer_provider=self.tracer_provider)