import json
import os
import datetime
from agentic_red_team import config

HISTORY_FILE = os.path.join(config.EVIDENCE_DIR, "run_history.json")


def save_run(target, campaign, results):
    if not os.path.exists(HISTORY_FILE):
        history = []
    else:
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []

    run_record = {
        "run_id": f"{target}_{int(datetime.datetime.now().timestamp())}",
        "timestamp": str(datetime.datetime.now()),
        "target": target,
        "campaign": campaign,
        "results": results
    }

    history.append(run_record)

    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"💾 Evaluation saved to History.")