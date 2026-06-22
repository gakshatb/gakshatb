import requests
import datetime
import subprocess
import json
import sys

USERNAME = "gakshatb"

query = """
query userProfileCalendar($username: String!) {
  matchedUser(username: $username) {
    userCalendar {
      submissionCalendar
    }
  }
}
"""

url = "https://leetcode.com/graphql"

try:
    res = requests.post(
        url,
        json={"query": query, "variables": {"username": USERNAME}},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    res.raise_for_status()
    data = res.json()

    matched_user = data.get("data", {}).get("matchedUser")
    if matched_user is None:
        print(f"No LeetCode user found for '{USERNAME}', or API response shape changed.")
        sys.exit(0)

    calendar_raw = matched_user["userCalendar"]["submissionCalendar"]
    calendar = json.loads(calendar_raw)

except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
    print(f"LeetCode sync failed: {e}")
    sys.exit(0)

today_utc = datetime.datetime.now(datetime.timezone.utc).date()
today_ts = str(int(datetime.datetime(
    today_utc.year, today_utc.month, today_utc.day, tzinfo=datetime.timezone.utc
).timestamp()))

today_count = calendar.get(today_ts, 0)

if today_count > 0:
    with open("leetcode_commits.txt", "a") as f:
        f.write(f"{today_utc.isoformat()} : {today_count}\n")

    subprocess.run(["git", "add", "leetcode_commits.txt"], check=True)
    commit = subprocess.run(
        ["git", "commit", "-m", f"leetcode {today_utc.isoformat()}"]
    )
    if commit.returncode != 0:
        print("Nothing new to commit (already logged today).")
else:
    print("No LeetCode activity recorded for today yet.")
