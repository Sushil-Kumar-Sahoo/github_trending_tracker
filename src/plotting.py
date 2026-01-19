import os
import pandas as pd
from pandas import pivot_table
import matplotlib.pyplot as plt
from typing import List,Tuple,Optional
from src.utils import ensure_folder_exists

def plot_top_repos(rows:List[Tuple[str,str,int]],output_folder:str,top_repos:List[str],fig_size:tuple=(10,6)) -> Optional[str]:

    df = pd.DataFrame(rows,columns=["date","repo_name","stars"])
    if df.empty:
        print("No rows to plot")
        return None
    
    df["date"] = pd.to_datetime(df["date"])
    pivot = df.pivot_table(index="date",columns="repo_name",values="stars",aggfunc="first")
    present = [r for r in top_repos if r in pivot.columns]
    if not present:
        print("No matching repos to plot")
        return None
    
    plot_df = pivot[present].ffill().fillna(0)
    print(plot_df)

    plt.figure(figsize=fig_size)
    for col in plot_df.columns:
        plt.plot(plot_df.index,plot_df[col],marker="o",label=col)
    plt.xlabel("date")
    plt.xticks(rotation=45)
    plt.ylabel("stars")
    plt.legend(loc="best",fontsize="small")
    plt.ylabel("Stars")
    plt.title(f"GitHub Trending Stars ({len(plot_df.columns)} repos)")

    plt.grid(True)
    ensure_folder_exists(output_folder)
    out_path = os.path.join(output_folder,"github_trends.png")
    plt.savefig(out_path,bbox_inches="tight")
    plt.close()

    print(f"Figure is saved in {out_path}")
    return out_path
    

