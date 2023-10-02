### this script web scape through seasons 1970 - 2022 and return the teams, divisions, and conferences
### the script is checked against the Elo csv (line ~45)
### team_reference list can be updated to include other teams where pro-football-references != Elo file

import time
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

# list of seasons to get team information from
season_list = np.arange(1970,2023,1)

# function to parse season web page and return AFC & NFC teams and divisions
def teams(yr : int):
    url = f'https://www.pro-football-reference.com/years/{yr}/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'html.parser')
    nfc_table = soup.find('table',id='NFC').find('tbody').findChildren('tr')
    afc_table = soup.find('table',id='AFC').find('tbody').findChildren('tr')
    return ([[yr,'NFC',x.get_text()[1:],None] if x.find('a') == None else [yr,'NFC',None,x.find('a')['href'][7:10]] for x in nfc_table] +
             [[yr,'AFC',x.get_text()[1:],None] if x.find('a') == None else [yr,'AFC',None,x.find('a')['href'][7:10]] for x in afc_table])

# function to clean the dataframe
# need to forward fill division given 'None' from elements
def clean_df(df):
    df['division'].ffill(inplace=True)
    df.dropna(axis=0, how='any', inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['team'] = df['team'].str.upper()
    return df

# loop through each season to create a list of each team & season div/conf
# add the list to a DF
# pro-football-reference allows 20 requests/minute
# adding one second buffer to time.sleep()
data = [teams(year) for year in season_list if time.sleep(3.5) == None]
data2 = [data[i][j] for i in range(len(data)) for j in range(len(data[i]))]
div_df = pd.DataFrame(data2, columns=['season','conference','division','team'])

div_df = clean_df(div_df)

# bring in elo DF to match issue team names
### you will need to update the file path to whatever your path to the .csv is
elo = pd.read_csv(r'C:\Users\bkors\OneDrive\Desktop\School\CS 620\Data Project\nfl_elo.csv')

# clean the elo DF to get just team names
def clean_elo(df):
    df = df[df['season'] >= 1970]
    df = pd.concat([df['team1'],df['team2']],ignore_index=True)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True,inplace=True)
    df = pd.DataFrame(df,columns=['elo team name'])
    return df.copy()

elo_name_index = clean_elo(elo)

# list of team names that don't match pro-football-reference and elo
team_reference = [['CRD','ARI'],
                ['WAS','WSH'],
                ['GNB','GB'],
                ['SFO','SF'],
                ['RAM','LAR'],
                ['NOR','NO'],
                ['CLT','IND'],
                ['NWE','NW'],
                ['OTI','TEN'],
                ['RAI','OAK'],
                ['KAN','KC'],
                ['SDG','LAC'],
                ['TAM','TB'],
                ['RAV','BAL'],
                ['HTX','HOU']]
# convert list to DF
team_fix = pd.DataFrame(team_reference,columns=['pfr name','matching elo name'])

# merge div_df with elo team names for primary df reference
div_df = div_df.merge(team_fix, how='left', left_on='team', right_on='pfr name')
div_df['team name'] = np.where(pd.isna(div_df['matching elo name']),div_df['team'],div_df['matching elo name'])
div_df.drop(['team','pfr name','matching elo name'],axis=1,inplace=True)

print(f'First five rows:\n{div_df.head()}\nLast five rows:\n{div_df.tail()}')
