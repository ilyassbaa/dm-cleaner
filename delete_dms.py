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

def purge_fast():
    before_id = None
    total_deleted = 0

    print("Starting deletion process...")

    while True:
        params = {"limit": 100}
        if before_id:
            params["before"] = before_id

        res = requests.get(base_url, headers=headers, params=params)

        if res.status_code == 429:
            retry_after = res.json().get("retry_after", 1.5)
            print(f"Rate limited on fetch. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        elif res.status_code != 200:
            print(f"Error fetching messages: {res.status_code} - {res.text}")
            break

        messages = res.json()
        if not messages:
            print("Purge complete: No more messages found.")
            break

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
                            print(f"Deleted {total_deleted} messages...")
                        time.sleep(0.22)
                        break
                    elif del_res.status_code == 429:
                        data = del_res.json()
                        wait = data.get("retry_after", 1.0)
                        print(f"Hit rate limit. Pausing {wait}s...")
                        time.sleep(wait)
                    elif del_res.status_code == 404:
                        break
                    else:
                        print(f"Unexpected status: {del_res.status_code}")
                        break

if __name__ == "__main__":
    purge_fast()
