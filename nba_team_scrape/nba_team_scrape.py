#!/usr/bin/env python
# coding: utf-8

# ## NBA Team Scrape 2000-2020

#
#
# The NBA is rich with team and player data. After having challenges working with NBA API, we decided to scrape directly from Basketball Reference (https://www.basketball-reference.com/), a source of NBA data and analytics used widely in the industry.
#
# First, we'll scrape team data, including team name, conference, win-loss percentage, and unadjusted and adjusted offensive, defensive, and net ratings from 2016 through 2020. Next, we'll scrape player data for total season, per game, per 36 minute, per 100 possession, and advance analytics from 2016 through 2020. To build up our data set, we'll define and bundle together functions that scrape data, build, format, and save dataframes, and loop over each year (and stat type for player data). In scraping, we'll make us of list comprehension, which is arguably one of the most beautiful techniques in Python. We'll merge together team data for each year and player data for all stat types for each year to create massive team and player csv files, respectively.
#

# In[1]:


import pandas as pd
import numpy as np
import io
import os

# Web scraping using BeautifulSoup and converting to pandas dataframe
import requests
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup

from time import sleep
from warnings import warn
from random import randint

# Merging dataframes in dictionary of dataframes
from functools import partial, reduce

from pandas import MultiIndex

import plotly.express as px

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# ## Scrape Team Stats 2000-2020

# In[2]:

# Variables to direct scrape
directory = '/users/hpoola/Desktop/nba_team_scrape/'
start_year = 2000
end_year = 2020

# Get website and create BeautifulSoup object
def get_html(year):
    url = ('https://www.basketball-reference.com/leagues/NBA_{}_ratings.html'.format(year))
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    return soup

# Get variable headers for the statistics from the page
def get_header(soup):
    header = [th.get_text() for th in soup.find_all('tr')[1].find_all('th')]
    header = header[1:] # Don't need rank column
    header = [item.replace('%', '_percent').replace('/', '_').lower() for item in header] # replace special characters and convert to lower case
    return header

# Get the team statistics
def get_stats(soup, headers):
    stats = []
    rows = soup.find_all('tr', class_=None)
    for i in range(len(rows)):
        stats.append([j.text for j in rows[i].find_all('td')]) # list comprehension: get the text of the table data (td) for each row
    stats = pd.DataFrame(stats, columns=headers)
    return stats

# Format dataframe
def format_dataframe(team_stats):
    team_stats = team_stats.copy()

    #Drop empty columns
    drop_cols = []
    for col in team_stats.columns:
        if (len(col) <= 1): # if length of column is <=1
            drop_cols.append(col)
    team_stats = team_stats.drop(columns=drop_cols)

    # Convert numerical columns to numeric
    cols = [i for i in team_stats.columns if i not in ['team', 'conf', 'div']] # list comprehension: columns that aren't non-numer columns player, pos, team
    for col in cols:
        team_stats[col] = pd.to_numeric(team_stats[col])

    # Fill blanks
    team_stats = team_stats.fillna(0)

    # Save to csv
    team_stats.to_csv('{}/nba_team_stats_{}.csv'.format(directory, year), index=False)

# Main loop to get team statistics for years of interest

# Loop through the years
for year in range(start_year, end_year + 1):
    team_stats = pd.DataFrame() # team_stats dataframe for each year (make sure that it's inside the for loop!)

    # Slow down the web scrape to avoid server getting overloaded
    sleep(randint(1, 4))

    # Get website
    html_soup = get_html(year)

    # Get header
    if year == start_year:
        headers = get_header(html_soup)

    # Get team stats
    team_stats = team_stats.append(get_stats(html_soup, headers), ignore_index=True)

    team_stats = team_stats.drop([0]) # drop the first row with blank data

    print('{} table completed.'.format(year))

    # Format the datatframe
    format_dataframe(team_stats)


# Create multiple dataframes using dict comprehension - https://stackoverflow.com/questions/28143573/generate-multiple-pandas-data-frames

# In[3]:


# Create list of years as strings
a = range(start_year,end_year+1)
years = list(map(str,a))

# Create suffix for each year for column names (e.g., '_2020')
suffix = list(map('_'.__add__, str(years)))

# Dict comprehension to create dictionary of dataframes (by year) from each csv
filepath = '/users/hpoola/Desktop/nba_team_scrape/nba_team_stats_{}.csv'
dfs = {year: pd.read_csv(filepath.format(year)) for year in years}

# Add suffix for the column headings we need for each year's dataframe in dictionary of dataframes
for year in years:
    dfs[year].columns = dfs[year].columns.map(lambda x: x + '_'+str(year) if x != 'team' and x != 'conf' and x != 'div' else x)


# In[4]:


def merged_df(dfs):
    merged = reduce(lambda left, right: pd.merge(left,
                                                 right,
                                                 on = ['team', 'conf', 'div'],
                                                 how='outer'),
                                                 dfs)
    return merged

NBA = merged_df(dfs.values()).groupby('team').first().reset_index()


# In[5]:


NBA

# Names of divisions have changed for select teams in the time period, let's update with most current
NBA.iloc[0,2] = 'SE'
NBA.iloc[4,2] = 'SE'
NBA.iloc[7,2] = 'SW'
NBA.iloc[8,2] = 'NW'
NBA.iloc[11,2] = 'SW'
NBA.iloc[15,2] = 'SW'
NBA.iloc[16,2] = 'SE'
NBA.iloc[18,2] = 'NW'
NBA.iloc[25,2] = 'SE'
NBA.iloc[28,2] = 'NW'
NBA.iloc[30,2] = 'SW'
NBA.iloc[32,2] = 'A'
NBA.iloc[33,2] = 'NW'
NBA.iloc[35,2] = 'SE'

# Let's look at the current 30 teams
dfs['2020'].team.to_frame()


# All teams from 2000 to 2020 - 36 teams
NBA.team.to_frame()

# Create dataframe with rows that include null values
null_mask = NBA.isnull()
row_has_null = null_mask.any(axis=1)
null_df = NBA[row_has_null]
null_df


# These are the teams that have undergone city or franchise changes, either permanent or temporary, or are expansion teams.

# http://practicallypredictable.com/2017/12/21/web-scraping-nba-team-matchups-box-scores/
#
# https://en.wikipedia.org/wiki/List_of_National_Basketball_Association_seasons
#
# https://en.wikipedia.org/wiki/Charlotte_Hornets
#
# https://en.wikipedia.org/wiki/Effect_of_Hurricane_Katrina_on_the_New_Orleans_Hornets
#
#
# Goal is to track a group of players even as franchise changes cities
#
# 1) Seattle SuperSonics became the Oklahoma City Thunder starting from the 2009 season onward - Oklahoma City Thunder takes precedence
#
# 2) Vancouver Grizzlies became the Memphis Grizzlies from 2002 onward - Memphis Grizzlies takes precedence
#
# 3) New Jersey Nets became the Brooklyn Nets from 2013 onward - Brooklyn Nets takes precedence
#
# 4) Hornets and Pelicans
# - Charlotte Hornets became New Orleans Hornets from 2003 onward
# - Charlotte Bobcats joined as expansion team from 2005 onward
# - New Orleans Hornets became New Orleans/Oklahoma City Hornets from 2006 through 2007
# - New Orleans Hornets became New Orleans Pelicans from 2014 onward
# - Charlotte Bobcats became Charlotte Hornets from 2015 onward
#
# - Current teams are Charlotte Hornets and New Orleans Pelicans
# -- Combine Charlotte Bobcats with Charlotte Hornets from 2015 onward
# -- Combine Charlotte Bobcats from 2005 through 2014 with above row
# -- Combine New Orleans Hornets with New Orleans Pelicans from 2008 onward
# -- Combine New Orleans/Oklahoma City Hornets with New Orleans Hornets from 2006 through 2007
# -- Combine Charlotte Hornets with New Orleans Hornets above
#
# https://stackoverflow.com/questions/44799264/merging-two-rows-one-with-a-value-the-other-nan-in-pandas
#
#
#
# The most complicated situation is with Charlotte and New Orleans.
#
# Hornets and Pelicans
#
# As descibed in detail here, the Charlotte Hornets moved to New Orleans in 2002. The Charlotte Bobcats joined the NBA as an expansion team in 2004. Prior to the 2014-15 season, the Charlotte Bobcats and the New Orleans Hornets agreed to a deal whereby New Orleans would become the Pelicans and the Hornets name and history would revert to Charlotte. This explains why the abbreviation ‘CHA’ is used for both the Charlotte Bobcats and the Charlotte Hornets, in addition to the ‘CHH’ abbreviation for the other Charlotte Hornets (the team that moved in 2002 and ultimately became the Pelicans).
#
# Another complication is that because of Hurricane Katrina, the New Orleans Hornets had to relocate for much of the 2005-6 and 2006-7 seasons to Oklahoma City. That’s why there is an abbreviation ‘NOK’ to represent the games that were played under the label New Orleans/Oklahoma City Hornets.
#
# Let’s sort this out and make sure we understand this in detail.
#
# First, let build a table with the current 30 NBA teams, so we can keep track of historical abbreviations and how they map to current teams. Remember that the ‘team_id’ is meant to be a unique identifier for each team, even if the abbreviation or team name changes.
#
# This table makes it clear that ‘CHH’ is the original Charlotte Hornets, who became the New Orleans Hornets (and the New Orleans/Oklahoma City Hornets), before becoming the New Orleans Pelicans (‘NOP’). The abbreviation ‘CHA’ refers to the Bobcats, who then became the new Charlotte Hornets in the 2014-15 season.
#
#
# “Fixing” the Team Data
#
# What might surprise you about this, is that the NBA team data are wrong!
#
# If you look at the team table above, you’ll see that ‘CHH’ has the same ‘team_id’ as ‘CHA’. Now, you may think this is correct, since the Bobcats and the New Orleans Hornets did a deal returning the history of the original Charlotte Hornets (‘CHH’) to Charlotte. That’s why ‘CHH’ and ‘CHA’ have the same ‘team_id’.
#
# On the other hand, if you goal is to track the performance of group of players, as their franchise changed cities, this is incorrect. The guys who played on the ‘CHH’ squad in the 2001-2 season should be connected with the ‘NOH’ squad in the 2002-3 season.
#
# The NBA team data as recorded don’t reflect that.
#
# To keep track of this, we will do something that you should never do lightly. We are going to override our team data table to make sure the ‘CHH’ games are grouped with the current Pelicans franchise. We are effectively going to undo the Charlotte/New Orleans deal to transfer the Hornets history.


NBA.shape


# ## Convert from Wide to Long format


NBA_long = pd.wide_to_long(NBA, stubnames=['w_l_percent','mov','ortg','drtg','nrtg','mov_a','ortg_a','drtg_a','nrtg_a'], i='team', j='year', sep='_', suffix='\d+')
NBA_long.head(40)


# ## Oklahoma City Thunder


thunder = NBA_long.loc[['Oklahoma City Thunder', 'Seattle SuperSonics'],:]

# Change Seattle SuperSonics to Oklahoma City Thunder in index
teams = thunder.index.get_level_values('team').to_list()
teams = ['Oklahoma City Thunder' if x=='Seattle SuperSonics' else x for x in teams]
new_index = zip(teams, thunder.index.get_level_values('year'))
thunder.index = pd.MultiIndex.from_tuples(new_index, names = thunder.index.names)

thunder = thunder.groupby(['team','year']).sum().assign(conf='W', div='NW')

cols = list(thunder.columns.values) #Make a list of all of the columns in the df
cols.pop(cols.index('conf')) #Remove conf from list
cols.pop(cols.index('div')) #

thunder = thunder[['conf','div'] + cols]
thunder


# ## Memphis Grizzlies


grizzlies = NBA_long.loc[['Memphis Grizzlies', 'Vancouver Grizzlies'],:]

# Change Vancouver Grizzlies to Memphis Grizzlies in index
teams = grizzlies.index.get_level_values('team').to_list()
teams = ['Memphis Grizzlies' if x=='Vancouver Grizzlies' else x for x in teams]
new_index = zip(teams, grizzlies.index.get_level_values('year'))
grizzlies.index = pd.MultiIndex.from_tuples(new_index, names = grizzlies.index.names)

grizzlies = grizzlies.groupby(['team','year']).sum().assign(conf='W', div='M')

cols = list(grizzlies.columns.values) #Make a list of all of the columns in the df
cols.pop(cols.index('conf')) #Remove conf from list
cols.pop(cols.index('div')) #

grizzlies = grizzlies[['conf','div'] + cols]
grizzlies


# ## Brooklyn Nets


nets = NBA_long.loc[['Brooklyn Nets', 'New Jersey Nets'],:]

# Change New Jersey Nets to Brooklyn Nets in index
teams = nets.index.get_level_values('team').to_list()
teams = ['Brooklyn Nets' if x=='New Jersey Nets' else x for x in teams]
new_index = zip(teams, nets.index.get_level_values('year'))
nets.index = pd.MultiIndex.from_tuples(new_index, names = nets.index.names)

nets = nets.groupby(['team','year']).sum().assign(conf='E', div='A')

cols = list(nets.columns.values) #Make a list of all of the columns in the df
cols.pop(cols.index('conf')) #Remove conf from list
cols.pop(cols.index('div')) #

nets = nets[['conf','div'] + cols]
nets


# ## Charlotte Hornets

# - Charlotte Hornets became New Orleans Hornets from 2003 onward
# - Charlotte Bobcats joined as expansion team from 2005 onward
# - New Orleans Hornets became New Orleans/Oklahoma City Hornets from 2006 through 2007
# - New Orleans Hornets became New Orleans Pelicans from 2014 onward
# - Charlotte Bobcats became Charlotte Hornets from 2015 onward
#
# Charlotte Hornets:
# - Combine Charlotte Bobcats with only 2003-onward Charlotte Hornets (original Charlotte Hornets from 2000 through 2002 are actually today's New Orleans Pelicans)
#


hornets = NBA_long.loc[['Charlotte Hornets', 'Charlotte Bobcats'],:]

# Replace Charlotte Hornets 2000,2001,2002 numeric values with NaN (this cohort of players actually maps to today's New Orleans Pelicans)
hornets.loc[('Charlotte Hornets', [2000,2001,2002]), :] = hornets.loc[('Charlotte Hornets', [2000,2001,2002]), :]                                                                 .astype('str')                                                                 .replace({'\d+': np.nan}, regex=True)

# Change Charlotte Bobcats to Charlotte Hornets in index
teams = hornets.index.get_level_values('team').to_list()
teams = ['Charlotte Hornets' if x=='Charlotte Bobcats' else x for x in teams]
new_index = zip(teams, hornets.index.get_level_values('year'))
hornets.index = pd.MultiIndex.from_tuples(new_index, names = hornets.index.names)

hornets = hornets.groupby(['team','year']).sum().assign(conf='E', div='C')

cols = list(hornets.columns.values) #Make a list of all of the columns in the df
cols.pop(cols.index('conf')) #Remove conf from list
cols.pop(cols.index('div')) #

hornets = hornets[['conf','div'] + cols]
hornets


# ## New Orleans Pelicans

#
# New Orleans Pelicans:
# - Combine New Orleans Hornets, New Orleans/Oklahoma City Hornets, New Orleans Pelicans
# - Combine Charlotte Hornets 2000 through 2002 with above


pelicans = NBA_long.loc[['Charlotte Hornets', 'New Orleans Hornets', 'New Orleans/Oklahoma City Hornets', 'New Orleans Pelicans'],:]

# Replace Charlotte Hornets 2003-2020 numeric values with NaN (this cohort of players actually map to today's Charlotte Hornets, not thePelicans)
non_hornets_years = list(range(2003,2021))
pelicans.loc[('Charlotte Hornets', non_hornets_years), :] = hornets.loc[('Charlotte Hornets', non_hornets_years), :]                                                                   .astype('str')                                                                   .replace({'\d+': np.nan}, regex=True)

# Change New Orleans Hornets, Charlotte Hornets, New Orleans/Oklahoma City Hornets to New Orleans Pelicans
teams = pelicans.index.get_level_values('team').to_list()
teams = ['New Orleans Pelicans' if x=='New Orleans Hornets' or x=='Charlotte Hornets' or x=='New Orleans/Oklahoma City Hornets' else x for x in teams]
new_index = zip(teams, pelicans.index.get_level_values('year'))
pelicans.index = pd.MultiIndex.from_tuples(new_index, names = pelicans.index.names)

pelicans = pelicans.groupby(['team','year']).sum().assign(conf='W', div='SW')

cols = list(pelicans.columns.values) #Make a list of all of the columns in the df
cols.pop(cols.index('conf')) #Remove conf from list
cols.pop(cols.index('div')) #

pelicans = pelicans[['conf','div'] + cols]
pelicans


# # NBA Dataframe with updated teams

NBA_long.drop(['Oklahoma City Thunder', 'Seattle SuperSonics', 'Memphis Grizzlies', 'Vancouver Grizzlies','Brooklyn Nets', 'New Jersey Nets',
               'Charlotte Hornets', 'Charlotte Bobcats', 'New Orleans Hornets', 'New Orleans/Oklahoma City Hornets', 'New Orleans Pelicans'],
               level=0, inplace=True)



# Concat NBA long with updated team dataframes, sort rows by year (level 1 index, axis 0)
NBA_long = pd.concat([NBA_long, thunder, grizzlies, nets, hornets, pelicans], axis=0).sort_index(level=1, axis=0)
NBA_long



#Since today's Charlotte Hornets maps back to the expansion team Chatlotte Bobcats, which joined from 2005 onward, we'll replace values before with NaN
NBA_long.loc[('Charlotte Hornets', [2000,2001,2002, 2003, 2004]), :] = NBA_long.loc[('Charlotte Hornets', [2000,2001,2002,2003,2004]), :]                                                                               .astype('str')                                                                               .replace({'\d+': np.nan}, regex=True)




# We see that each year has exactly 30 teams, which is what we want. They also map to today's franchises
NBA_long.groupby(level='year').size()

NBA_long.info()

# Check data type of the year index
NBA_long.index.get_level_values(1).dtype

NBA_long.to_csv('/users/hpoola/Desktop/nba_team_scrape/NBA_long.csv')

#
# 4) Hornets and Pelicans
#
#
# <br>- Current teams are Charlotte Hornets and New Orleans Pelicans
# -- Combine Charlotte Bobcats with Charlotte Hornets from 2015 onward
# -- Combine Charlotte Bobcats from 2005 through 2014 with above row
# -- Combine New Orleans Hornets with New Orleans Pelicans from 2008 onward
# -- Combine New Orleans/Oklahoma City Hornets with New Orleans Hornets from 2006 through 2007
# -- Combine Charlotte Hornets with New Orleans Hornets above

#
# http://practicallypredictable.com/2017/12/21/web-scraping-nba-team-matchups-box-scores/
#
#
#
# Add suffix to each dataframe
# https://stackoverflow.com/questions/48236438/merge-multiple-dataframe-with-specified-suffix
#
# Merge dfs with suffixes
# https://stackoverflow.com/questions/48236438/merge-multiple-dataframe-with-specified-suffix
#
#
# https://stackoverflow.com/questions/42725315/nested-merges-in-pandas-with-suffixes
#
# https://stackoverflow.com/questions/8091303/simultaneously-merge-multiple-data-frames-in-a-list
#
# https://stackoverflow.com/questions/38978214/merge-a-list-of-dataframes-to-create-one-dataframe
#
# https://www.kite.com/python/answers/how-to-merge-a-list-of-pandas-dataframes-into-a-single-dataframe-in-python
#
#
#
