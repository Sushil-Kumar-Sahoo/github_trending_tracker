import os
import yaml
from datetime import datetime
from typing import Dict
import pandas as pd

def load_config(path:str) -> dict :
    with open(path,'r',encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_folder_exists(path:str):
    os.makedirs(path,exist_ok=True)

def get_today_date() -> str :
    return datetime.now().strftime("%Y-%m-%d")
     
def generate_stats_file(stats: Dict, output_folder: str) -> str:
    rows = []

    for category in ("most_present", "consistent_repos", "top_by_avg_star"):
        for item in stats.get(category, []):
            row = item.copy()
            row["category"] = category
            rows.append(row)

    if not rows:
        raise ValueError("No statistics available to write")

    df = pd.DataFrame(rows)
    os.makedirs(output_folder, exist_ok=True)

    out_path = os.path.join(output_folder, "analysis.csv")
    df.to_csv(out_path, index=False)

    return out_path

