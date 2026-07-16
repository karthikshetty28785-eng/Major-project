import subprocess
import time
import os
import datetime

LOG_FILE = "oob/captured_sessions.log"
HONEYTOKEN_ALERT = "oob/honeytoken_alerts.log"
CONTAINER_LOG = "/tmp/session_log.txt"
HONEYTOKEN_CONTAINER = "/tmp/honeytoken_alert.txt"

def get_container_id():
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=honeypot_app", "--format", "{{.ID}}"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def copy_log_from_container(container_id, src, dst):
    subprocess.run(
        ["docker", "cp", f"{container_id}:{src}", dst],
        capture_output=True
    )

def record(container_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Copy session log from inside container to OOB
    tmp_session = "oob/tmp_session.log"
    copy_log_from_container(container_id, CONTAINER_LOG, tmp_session)

    if os.path.exists(tmp_session):
        with open(tmp_session, "r") as f:
            content = f.read()
        if content.strip():
            with open(LOG_FILE, "a") as out:
                out.write(f"\n--- Snapshot at {timestamp} ---\n")
                out.write(content)

    # Copy honeytoken alerts
    tmp_honey = "oob/tmp_honey.log"
    copy_log_from_container(container_id, HONEYTOKEN_CONTAINER, tmp_honey)

    if os.path.exists(tmp_honey):
        with open(tmp_honey, "r") as f:
            content = f.read()
        if content.strip():
            with open(HONEYTOKEN_ALERT, "a") as out:
                out.write(content)
            print(f"[ALERT] HONEYTOKEN TRIGGERED — check {HONEYTOKEN_ALERT}")

def main():
    print("OOB Recorder started. Monitoring honeypot container...")
    os.makedirs("oob", exist_ok=True)

    while True:
        container_id = get_container_id()
        if container_id:
            record(container_id)
        else:
            print(f"[{datetime.datetime.now()}] Container not found. Waiting...")
        time.sleep(10)

if __name__ == "__main__":
    main()
