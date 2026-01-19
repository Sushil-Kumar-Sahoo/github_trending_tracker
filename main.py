import sys
import os 
import pprint

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# print(PROJECT_ROOT)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# print(PROJECT_ROOT)

from src.database import DatabaseManager
from src.utils import load_config,ensure_folder_exists,get_today_date,generate_stats_file
from src.scraper import GitHubScraper
from src.stats import sumarize_stats,top_repo_names_from_summary
from src.plotting import plot_top_repos

def main():
    cfg = load_config(os.path.join(PROJECT_ROOT,'config','config.yaml'))
    # print(cfg)
    data_folder = os.path.join(PROJECT_ROOT,"data")
    output_folder=os.path.join(PROJECT_ROOT,cfg["output"]["folder"])
    db_path = os.path.join(PROJECT_ROOT,cfg["database"]["path"])

    ensure_folder_exists(data_folder)
    ensure_folder_exists(output_folder)

    db = DatabaseManager(db_path)
    today = get_today_date()

    if db.date_exists(today):
        print(f"Data for today already exist .Skipping scrape and insert for data {today}")
    else:
        url = cfg["scraper"]["trending_url"]
        if cfg["scraper"].get('since'):
           sep = "&" if "?" in url else "?"
           url = f"{url}{sep}since={cfg['scraper'].get('since')}"
           
        headers = {"User-Agent": cfg["scraper"].get('user_agent',"Mozilla/5.0") }
        scraper = GitHubScraper(url,headers=headers) 
        try:
           repository = scraper.scrape_trending() 
           db.insert_repos(today,repos=repository)
           print(f"Insert/Updated {len(repository)} repository for {today}")
        except Exception as err:
            print(f"Exception occured while scrapping the data from GitHub Error :{err}") 

#to show data which are we analyzed in csv
    # to_show_csv = 

# Fetching :
    try:
        days = int(os.getenv("REPORT_DAYS", 7))
    except ValueError:
        days = 7
    print(f"Analyzing repository trends for last {days} days...")
    rows = db.fetch_last_n_days(days) 
    if not rows:
        print("No data found for the selected period . Exiting...")
        return
    else:
        stats = sumarize_stats(rows,cfg["plot"]["top_n"],min_presence_pct=0.3)

    stats_path = generate_stats_file(stats, output_folder)
    print(f"Analysis saved to {stats_path}")


    top_names = top_repo_names_from_summary(stats,fallback_top_n=10)

    if not top_names:
        print("No repos found to plot")
    else:
        plot_top_repos(rows,output_folder,top_names,cfg["plot"]["fig_size"])
        

if __name__ == '__main__' :
    main()