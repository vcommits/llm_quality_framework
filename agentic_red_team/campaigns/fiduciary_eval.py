# ... imports ...
from agentic_red_team.utils.telemetry import PhoenixRecorder  # <--- NEW


async def run_fiduciary_suite():
    # ... setup ...
    recorder = PhoenixRecorder()  # <--- Initialize

    # ... inside the loop ...
    for test_case in scenarios:
        # ... (brain decision) ...

        # ... (calculate status PASS/FAIL) ...

        # RECORD THE BLOB
        recorder.record_step(
            test_id=test_case['id'],
            goal=test_case['user_goal'],
            input_html=html_snapshot,
            output_actions=actions,
            status=status
        )

    # ... end of loop ...

    # PUBLISH TO PHOENIX
    recorder.publish_and_view()  # <--- Triggers the UI