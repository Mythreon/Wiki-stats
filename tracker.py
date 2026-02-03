import requests
import pandas as pd
from datetime import datetime
import os

WIKI_NAME = "nexusstation" 
URL = f"https://{WIKI_NAME}.wiki.gg/api.php"
FILENAME = "wiki_stats.csv"

def get_stats():
    params = {"action": "query", "meta": "siteinfo", "siprop": "statistics", "format": "json"}
    headers = {"User-Agent": "StatsTrackerBot/1.0 (Contact: via GitHub)"}
    
    try:
        res = requests.get(URL, params=params, headers=headers).json()
        stats = res['query']['statistics']
        stats['date'] = datetime.now().strftime("%Y-%m-%d")
        return stats
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_csv(data):
    if not data: return
    df_new = pd.DataFrame([data])
    if os.path.exists(FILENAME):
        df_old = pd.read_csv(FILENAME)
        df_combined = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['date'])
        df_combined.to_csv(FILENAME, index=False)
    else:
        df_new.to_csv(FILENAME, index=False)

if __name__ == "__main__":
    update_csv(get_stats())
