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

search_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/search?author_id={MY_USER_ID}"
base_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"

def purge():
    total_deleted = 0
    print("Beginning purge via author search...")

    while True:
        res = requests.get(search_url, headers=headers)

        if res.status_code == 202:
            # Discord is indexing messages
            time.sleep(2)
            continue
        elif res.status_code == 429:
            wait = res.json().get("retry_after", 2.0)
            time.sleep(wait)
            continue
        elif res.status_code != 200:
            print(f"Halted: Status {res.status_code}")
            break

        data = res.json()
        messages = data.get("messages", [])

        if not messages:
            print("Purge complete: No matching messages found.")
            break

        for hit in messages:
            msg = hit[0] if isinstance(hit, list) else hit
            msg_id = msg["id"]
            del_url = f"{base_url}/{msg_id}"

            while True:
                del_res = requests.delete(del_url, headers=headers)

                if del_res.status_code in (200, 204):
                    total_deleted += 1
                    if total_deleted % 50 == 0:
                        print(f"Deleted {total_deleted} messages...")
                    time.sleep(0.25)
                    break
                elif del_res.status_code == 429:
                    wait = del_res.json().get("retry_after", 1.5)
                    time.sleep(wait)
                elif del_res.status_code == 404:
                    break
                else:
                    time.sleep(0.5)
                    break

        time.sleep(1.0)

if __name__ == "__main__":
    purge()
