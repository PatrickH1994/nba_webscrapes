import time
import pandas as pd
from utils.fetch import fetch_url

def _process_boxscore(response, row, result_list):
    tables = pd.read_html(response.content)
    away = True
    for table in tables:
        # It throws an error at the 2nd if statement without the 1st if statement
        if table.columns.get_level_values(0)[1] == 'Advanced Box Score Stats': continue
        if table['Basic Box Score Stats'][-1:]['MP'].isna().max(): continue
        if int(table['Basic Box Score Stats']['MP'][-1:].max()) >= 240:
            teamStats = table['Basic Box Score Stats']
            teamStats['player_name'] = table['Unnamed: 0_level_0']
            teamStats['game_id'] = row.game_id
            if away:
                teamStats['team_name'] = row.away_team
                away = False
            else:
                teamStats['team_name'] = row.home_team
            result_list.append(teamStats)  # Append the team stats to the result list

def fetch_boxscore_data(games, start_index=0, chunk_size=500):
    df = pd.DataFrame(columns=['game_id', 'team_name', 'player_name', 'MP',
                               'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB',
                               'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-'])
    result_list = []
    for i, row in games.iloc[start_index:start_index+chunk_size].iterrows():
        year, month, day = row.datetime.split('-')
        url = f"https://www.basketball-reference.com/boxscores/{year}{month}{day}0{row.abbreviation}.html"
        print(f"{i}: Fetching data from {url}")
        game_data = fetch_url(url, _process_boxscore, (row, result_list))
        if game_data == 429:
            print('throttled')
            break
        if game_data is not None:
            result_list.append(game_data)
        time.sleep(2)
    # Define the columns
    columns = ['game_id', 'team_name', 'player_name', 'MP', 
               'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 
               'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']

    df = pd.concat(result_list, ignore_index=True)  # Concatenate all DataFrames at once
    df = df.reindex(columns=columns)  # Reindex to ensure the DataFrame has the desired columns

    return df