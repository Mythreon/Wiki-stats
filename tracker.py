import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

WIKI_NAME = "nexusstation" # Remember to keep your wiki name here!
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
    # Convert date column to actual dates for better scaling
    df['date'] = pd.to_datetime(df['date'])
    
    # List of charts to make: (Column Name, Chart Title, File Name)
    metrics = [
        ('pages', 'Total Wiki Pages', 'growth_pages.png'),
        ('edits', 'Total Wiki Edits', 'growth_edits.png'),
        ('activeusers', 'Active Users (30 Days)', 'active_users.png')
    ]
    
    for column, title, filename in metrics:
        plt.figure(figsize=(10, 5))
        plt.plot(df['date'], df[column], marker='o', linestyle='-', color='#3498db')
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
        df_old = pd.read_csv(FILENAME)
        df = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['date'])
    else:
        df = df_new
    
    df.to_csv(FILENAME, index=False)
    # Generate the charts based on the updated data
    if len(df) > 1: # Charts only make sense with 2+ days of data
        create_charts(df)

if __name__ == "__main__":
    update_csv(get_stats())
