import pandas as pd
from utils.fetch import fetch_url

def _process_monthly_games(response, df, year, month):
    yearMonth_table = pd.read_html(response.content)[0]
    yearMonth_table['season_start_year'] = year - 1
    return pd.concat([df, yearMonth_table])

def fetch_monthly_games(df, start_year, end_year, months, blacklist):
    for year in range(start_year, end_year):
        for month in months:
            if (year, month) in blacklist: continue
            url = f'https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html'
            print(f'Processing games for year, month: ({year}, {month})')
            fetch_url(url, _process_monthly_games, (df, year, month))
    return df
