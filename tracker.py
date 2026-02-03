import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

WIKI_NAME = "nexusstation" # Replace with your wiki subdomain
URL = f"https://{WIKI_NAME}.wiki.gg/api.php"
FILENAME = "wiki_stats.csv"

def get_stats():
    params = {"action": "query", "meta": "siteinfo", "siprop": "statistics", "format": "json"}
    headers = {"User-Agent": "StatsTrackerBot/1.0"}
    try:
        res = requests.get(URL, params=params, headers=headers).json()
        stats = res['query']['statistics']
        stats['date'] = datetime.now().strftime("%Y-%m-%d")
        return stats
    except: return None

def create_charts(df):
    df['date'] = pd.to_datetime(df['date'])
    # We'll plot the Total Pages and the Daily Change in Edits
    metrics = [
        ('pages', 'Total Wiki Pages', 'growth_pages.png'),
        ('edits_change', 'Daily Edits (Activity)', 'daily_activity.png')
    ]
    
    for column, title, filename in metrics:
        if column in df.columns and not df[column].isnull().all():
            plt.figure(figsize=(10, 5))
            plt.plot(df['date'], df[column], marker='o', linestyle='-', color='#e67e22' if 'change' in column else '#3498db')
            plt.title(title)
            plt.xlabel('Date')
            plt.ylabel('Count')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()

def update_csv(data):
    if not data: return
    df_new = pd.DataFrame([data])
    
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
        df = pd.concat([df, df_new], ignore_index=True).drop_duplicates(subset=['date'])
    else:
        df = df_new

    # --- CALCULATE DAILY CHANGE ---
    # This creates new columns showing the difference from the previous row
    for col in ['pages', 'edits', 'activeusers']:
        df[f'{col}_change'] = df[col].diff().fillna(0).astype(int)

    df.to_csv(FILENAME, index=False)
    
    if len(df) > 1:
        create_charts(df)

if __name__ == "__main__":
    update_csv(get_stats())
