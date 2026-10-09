import os
import time
import requests

USER_TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = "1438325162721415354"
MY_USER_ID = "1100570055915347968"

headers = {
    "Authorization": USER_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

base_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"

def purge_all():
    before_id = None
    total_deleted = 0
    scanned_total = 0

    print("Starting direct channel message purge...")

    while True:
        params = {"limit": 100}
        if before_id:
            params["before"] = before_id

        res = requests.get(base_url, headers=headers, params=params)

        if res.status_code == 429:
            wait = res.json().get("retry_after", 1.5)
            print(f"Rate limited on fetch. Pausing {wait}s...")
            time.sleep(wait)
            continue
        elif res.status_code != 200:
            print(f"Error fetching channel messages: {res.status_code} - {res.text}")
            break

        messages = res.json()
        if not messages or len(messages) == 0:
            print("Purge complete: Reached the beginning of the channel history.")
            break

        scanned_total += len(messages)
        # Advance the pointer to scan older messages
        before_id = messages[-1]["id"]

        for msg in messages:
            if msg.get("author", {}).get("id") == MY_USER_ID:
                msg_id = msg["id"]
                del_url = f"{base_url}/{msg_id}"

                while True:
                    del_res = requests.delete(del_url, headers=headers)

                    if del_res.status_code in (200, 204):
                        total_deleted += 1
                        if total_deleted % 25 == 0:
                            print(f"Deleted {total_deleted} messages (Scanned ~{scanned_total})...")
                        time.sleep(0.22)
                        break
                    elif del_res.status_code == 429:
                        wait = del_res.json().get("retry_after", 1.0)
                        time.sleep(wait)
                    elif del_res.status_code in (404, 403):
                        # Message already gone or permission denied
                        break
                    else:
                        time.sleep(0.5)
                        break

if __name__ == "__main__":
    purge_all()
