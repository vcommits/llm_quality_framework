import httpx
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

SENTRY_URL = "http://localhost:8001" # Assuming Node 1 runs on port 8001

def poll_for_jobs():
    logging.info("Node 2 Engine started. Polling for missions...")
    while True:
        try:
            # Get the next job
            response = httpx.get(f"{SENTRY_URL}/jobs/next")
            if response.status_code == 200 and response.json():
                mission = response.json()
                mission_id = mission['mission_id']
                logging.info(f"EXECUTING MISSION [{mission_id}] for target: {mission['target_url']}")
                
                # Simulate work
                time.sleep(5)
                
                # Report completion
                httpx.post(f"{SENTRY_URL}/jobs/complete/{mission_id}")
                logging.info(f"COMPLETED MISSION [{mission_id}]")
            else:
                # No job found, wait before polling again
                time.sleep(3)
        except httpx.RequestError as e:
            logging.error(f"Could not connect to Node 1 Sentry: {e}. Retrying in 10 seconds.")
            time.sleep(10)

if __name__ == "__main__":
    poll_for_jobs()
