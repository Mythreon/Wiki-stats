import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

WIKI_NAME = "nexusstation" 
URL = f"https://{WIKI_NAME}.wiki.gg/api.php"
FILENAME = "wiki_stats.csv"

def get_stats():
    headers = {"User-Agent": "StatsTrackerBot/1.0"}
    
    # 1. Get standard statistics
    params_stats = {"action": "query", "meta": "siteinfo", "siprop": "statistics", "format": "json"}
    
    # 2. Get CirrusSearch word count (article-words)
    # Note: CirrusSearch might not be enabled on every wiki, but common on wiki.gg
    params_cirrus = {
        "action": "query",
        "meta": "siteinfo",
        "siprop": "statistics",
        "format": "json",
        "extra": "cirrussearch-article-words-total" 
    }

    try:
        res = requests.get(URL, params=params_stats, headers=headers).json()
        stats = res['query']['statistics']
        
        # Try to fetch word count specifically
        # We use a separate call or specific siprop if the wiki supports it
        stats['word_count'] = stats.get('cirrussearch-article-words-total', 0)
        
        stats['date'] = datetime.now().strftime("%Y-%m-%d")
        return stats
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def create_charts(df):
    df['date'] = pd.to_datetime(df['date'])
    
    # Define the charts to generate: (DataFrame Column, Title, Filename, Color)
    metrics = [
        ('pages', 'Total Wiki Pages', 'growth_pages.png', '#3498db'),
        ('edits', 'Total Edits Over Time', 'total_edits.png', '#9b59b6'),
        ('edits_change', 'Daily Edits (Activity)', 'daily_activity.png', '#e67e22'),
        ('word_count', 'Total Word Count (CirrusSearch)', 'word_count.png', '#2ecc71')
    ]
    
    for column, title, filename, color in metrics:
        # Check if column exists and has data other than just zeros/NaNs
        if column in df.columns and df[column].notnull().any():
            plt.figure(figsize=(10, 5))
            plt.plot(df['date'], df[column], marker='o', linestyle='-', color=color)
            plt.title(title)
            plt.xlabel('Date')
            plt.ylabel('Count')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            print(f"Generated {filename}")

def update_csv(data):
    if not data: return
    df_new = pd.DataFrame([data])
    
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
        df = pd.concat([df, df_new], ignore_index=True).drop_duplicates(subset=['date'])
    else:
        df = df_new

    # --- CALCULATE DAILY CHANGE ---
    for col in ['pages', 'edits', 'activeusers', 'word_count']:
        if col in df.columns:
            df[f'{col}_change'] = df[col].diff().fillna(0).astype(int)

    df.to_csv(FILENAME, index=False)
    
    if len(df) > 1:
        create_charts(df)

if __name__ == "__main__":
    update_csv(get_stats())
