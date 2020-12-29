import pandas as pd
import numpy as np
from datetime import datetime

import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from urllib.request import urlopen
import json # library to handle JSON files
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Read in data that we scraped and created
NBA_long = pd.read_csv('https://raw.githubusercontent.com/hrishipoola/NBA_dashboard/main/data/NBA_long.csv', index_col=['team', 'year'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

markdown_text_1 = '''
## NBA Team Dashboard

Welcome! The NBA Team Dashboard lets fans explore how their favorite teams have evolved and how they compare
over the past 20 seasons in terms of:

**Win-loss %** \n
**Offensive rating (adj)**: points scored per 100 possessions adjusted for strength of opponent defense \n
**Defensive rating (adj)**: points allowed per 100 possessions adjusted for strength of opponent offense \n
**Net rating (adj)**: point differential per 100 possessions adjusted for strength of opponent

You can select teams and seasons you'd like to explore and dig deeper using hover, box & lasso select, zoom, and download tooltips. Metrics are scraped from [Basketball Reference](https://www.basketball-reference.com/). If you'd like, you can learn more
about how ratings are [calculated](https://www.basketball-reference.com/about/ratings.html). Each year refers to the year the season ended. What's fascinating is how dramatically a team's success and offensive and defensive prowess can change and how teams
and divisions compare with one another over time. The goal is continuity, tracking how a group of players performed over time regardless of franchise changes.

When collecting, shaping, and cleaning the data, care was taken to
account for franchise changes, either permanent or temporary, and expansion teams to ensure that today's 30 teams
map back to their original set of players. Some changes, like the Vancouver Grizzlies becoming the Memphis Grizzlies
from 2002-onward, the Seattle SuperSonics becoming the Oklahoma City Thunder from 2009-onward, and the New Jersey Nets becoming the
Brooklyn Nets from 2013-onward, are relatively straightforward. More complicated are those behind today's New Orleans Pelicans and
Charlotte Hornets, which have both undergone multiple transitions, name changes, and expansions. For example, the Charlotte Hornets became the New Orleans Hornets from 2003 onward, while the
Charlotte Bobcats were added as an expansion team from 2005 onward. Due to Hurricane Katrina, the New Orleans Hornets
transitioned to the New Orleans/Oklahoma City Hornets from 2006-2007 and relocated back to New Orleans
in 2008. The New Orleans Hornets became the New Orleans Pelicans from 2014 onward, while the
expansion Charlotte Bobcats became the Charlotte Hornets from 2015 onward. Today's New Orleans Pelicans trace back
to the original Charlotte Hornets from 2000-2002 (and before) and the New Orleans Hornets from 2003-2013. Today's Charlotte Hornets trace back to the
Charlotte Bobcats expansion team from 2005. We've mapped out the NBA's franchise changes and the logic
we've used to create today's teams in the 2nd tab. You can find code for the scrape and dashboard [here](https://github.com/hrishipoola/NBA_dashboard).

We hope you have fun with it and learn more about how your favorite teams have evolved over the past 20 seasons and how their offense and defense stack up.
If you'd like to learn more, give us a shout at info@crawstat.com!
'''


markdown_text_2 = '''
Today's New Orleans Pelicans trace back to the original Charlotte Hornets from 2000-2002 (and before) and the New Orleans Hornets from 2003-2013. Records from the
Charlotte Hornets 2000-2002, New Orleans Hornets, New Orleans/Oklahoma City Hornets, and New Orleans Pelicans were combined to create today's New Orleans Pelicans.
Today's Charlotte Hornets trace back to the Charlotte Bobcats expansion team from 2005. To avoid double-counting in creating today's Charlotte Hornets, records from the
Charlotte Hornets before the addition of the Charlotte Bobcats in 2005 were excluded (the Charlotte Hornets already transitioned to the New Orleans Hornets in 2003).
'''

default_teams = ['Los Angeles Lakers', 'Toronto Raptors', 'Golden State Warriors', 'Dallas Mavericks', 'Oklahoma City Thunder', 'Miami Heat']

# Create empty date time dataframe
team_changes = pd.DataFrame(dict(year = pd.date_range(start='2000-1-1', periods=21, freq='Y').year, height = 0))

# Plotly express plot
global fig
fig = px.bar(team_changes,
             x='year',
             y='height',
             title='NBA Franchise Changes 2000-2020',
             width=1200,
             height=450)

fig.update_xaxes(title='Season')
fig.update_yaxes(title='', matches=None, showticklabels=False, visible=False)
fig.update_layout(yaxis_range=[0,1])

fig.add_shape(type="line",
              x0=2002, y0=0, x1=2002, y1=0.9,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2002, y=0.9,
                   text='2002: Vancouver Grizzles become Memphis Grizzlies',
                   showarrow=False,
                   xshift=165)

fig.add_shape(type="line",
              x0=2003, y0=0, x1=2003, y1=0.8,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2003, y=0.8,
                   text='2003: Charlotte Hornets become New Orleans Hornets',
                   showarrow=False,
                   xshift=170)

fig.add_shape(type="line",
              x0=2005, y0=0, x1=2005, y1=0.7,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2005, y=0.7,
                   text='2005: Charlotte Bobcats added as expansion team',
                   showarrow=False,
                   xshift=160)


fig.add_shape(type="line",
              x0=2006, y0=0, x1=2006, y1=0.6,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2006, y=0.6,
                   text='2006: New Orleans Hornets relocate to Oklahoma City (Hurricane Katrina)',
                   showarrow=False,
                   xshift=230)


fig.add_shape(type="line",
              x0=2008, y0=0, x1=2008, y1=0.5,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2008, y=0.5,
                   text='2008: Hornets relocate back to New Orleans',
                   showarrow=False,
                   xshift=140)


fig.add_shape(type="line",
              x0=2009, y0=0, x1=2009, y1=0.4,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2009, y=0.4,
                   text='2009: Seattle SuperSonics become Oklahoma City Thunder',
                   showarrow=False,
                   xshift=185)


fig.add_shape(type="line",
              x0=2013, y0=0, x1=2013, y1=0.3,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2013, y=0.3,
                   text='2013: New Jersey Nets become Brooklyn Nets',
                   showarrow=False,
                   xshift=145)

fig.add_shape(type="line",
              x0=2014, y0=0, x1=2014, y1=0.2,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2014, y=0.2,
                   text='2014: New Orleans Hornets become New Orleans Pelicans',
                   showarrow=False,
                   xshift=180)


fig.add_shape(type="line",
              x0=2015, y0=0, x1=2015, y1=0.1,
              line=dict(width=2,dash='dash'))

fig.add_annotation(x=2015, y=0.1,
                   text='2015: Charlotte Bobcats become Charlotte Hornets',
                   showarrow=False,
                   xshift=160)

fig.update_layout(xaxis = dict(tickmode='linear', dtick=1))
fig.update_xaxes(tickangle=320)



app.layout = html.Div([
    dcc.Tabs(id='dash-tabs', value='tab-1', children=[
        dcc.Tab(label='NBA Dashboard', value='tab-1'),
        dcc.Tab(label='Franchise Changes', value='tab-2'),
        dcc.Tab(label='W-L %', value='tab-3'),
        dcc.Tab(label='Ratings', value='tab-4'),
        dcc.Tab(label='Off. vs. Def. (Division)', value='tab-5'),
        dcc.Tab(label='Off. vs. Def. (Team)', value='tab-6')
       ], colors={'border': 'white',
               'primary': 'darkturquoise',
               'background': 'whitesmoke'}, style={'fontFamily':'Helvetica'}),
    html.Div(id='dash-tabs-content')
])

@app.callback(Output('dash-tabs-content', 'children'),
              Input('dash-tabs', 'value'))


def render_content(tab):
    if tab == 'tab-1':
        return html.Div([dcc.Markdown(children=markdown_text_1)
                              ], style={'fontFamily':'Helvetica'})

    if tab == 'tab-2':
        return html.Div([
                    html.Div([
                              dcc.Graph(figure=fig)
                    ]),
                    html.Div([
                              dcc.Markdown(children=markdown_text_2)
                    ], style={'fontFamily':'Helvetica'})
                ])

    if tab == 'tab-3':
        return html.Div([
                     html.H4('Win-Loss%'),
                     html.Div([
                               html.Div('Teams', style={'paddingRight':'20px'}),
                               dcc.Dropdown(id='team-picker-1',
                                            options=[{'label': i, 'value': i} for i in NBA_long.index.get_level_values(0).unique()],
                                            value=default_teams,
                                            multi=True)
                              ],style={'display':'inline-block', 'verticalAlign':'top','width':'45%'}),
                      html.Div([
                                html.Div('Start Year', style={'paddingRight':'30px'}),
                                dcc.Dropdown(id='start-year-picker-1',
                                             options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                             value=NBA_long.index.get_level_values(1).min())
                               ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                      html.Div([
                                html.Div('End Year', style={'paddingRight':'30px'}),
                                dcc.Dropdown(id='end-year-picker-1',
                                             options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                             value=NBA_long.index.get_level_values(1).max())
                               ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                     html.Div([
                              html.Button(id='submit-button-1',
                                          n_clicks=0,
                                          children='Submit',
                                          style={'fontSize':14})
                              ],style={'display':'inline-block',
                                       'verticalAlign':'middle'}),
                     html.Div([
                              dcc.Graph(id='line-graph-1')
                              ])
        ], style={'fontFamily':'Helvetica'})

    if tab == 'tab-4':
        return html.Div([
                    html.H4('Ratings'),
                    html.Div([
                              html.Div('Teams', style={'paddingRight':'20px'}),
                              dcc.Dropdown(id='team-picker-2',
                                        options=[{'label': i, 'value': i} for i in NBA_long.index.get_level_values(0).unique()],
                                        value=default_teams,
                                        multi=True)
                              ],style={'display':'inline-block', 'verticalAlign':'top','width':'45%'}),
                    html.Div([
                              html.Div('Rating', style={'paddingRight':'20px'}),
                              dcc.Dropdown(id='rating-picker',
                                         options=[
                                                  {'label': 'Offensive', 'value': 'ortg_a'},
                                                  {'label': 'Defensive', 'value': 'drtg_a'},
                                                  {'label': 'Net', 'value': 'nrtg_a'}
                                                  ],
                                         value='nrtg_a')
                           ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                    html.Div([
                              html.Div('Start Year', style={'paddingRight':'30px'}),
                              dcc.Dropdown(id='start-year-picker-2',
                                         options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                         value=NBA_long.index.get_level_values(1).min())
                           ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                    html.Div([
                              html.Div('End Year', style={'paddingRight':'30px'}),
                              dcc.Dropdown(id='end-year-picker-2',
                                         options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                         value=NBA_long.index.get_level_values(1).max())
                           ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                    html.Div([
                              html.Button(id='submit-button-2',
                                      n_clicks=0,
                                      children='Submit',
                                      style={'fontSize':14})
                          ],style={'display':'inline-block',
                                   'verticalAlign':'top'}),
                    html.Div([
                              dcc.Graph(id='line-graph-2')
                          ])
    ], style={'fontFamily':'Helvetica'})

    if tab == 'tab-5':
        return html.Div([
                    html.H4('Offensive vs. Defensive Ratings by Division'),
                    html.Div([
                              html.Div('Teams', style={'paddingRight':'20px'}),
                              dcc.Dropdown(id='team-picker-3',
                                        options=[{'label': i, 'value': i} for i in NBA_long.index.get_level_values(0).unique()],
                                        value=default_teams,
                                        multi=True)
                             ],style={'display':'inline-block', 'verticalAlign':'top','width':'45%'}),
                    html.Div([
                              html.Div('Start Year', style={'paddingRight':'30px'}),
                              dcc.Dropdown(id='start-year-picker-3',
                                         options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                         value=NBA_long.index.get_level_values(1).min())
                             ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                    html.Div([
                              html.Div('End Year', style={'paddingRight':'30px'}),
                              dcc.Dropdown(id='end-year-picker-3',
                                         options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                         value=NBA_long.index.get_level_values(1).max())
                             ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                    html.Div([
                              html.Button(id='submit-button-3',
                                      n_clicks=0,
                                      children='Submit',
                                      style={'fontSize':14})
                             ],style={'display':'inline-block',
                                   'verticalAlign':'top'}),
                    html.Div([
                              dcc.Graph(id='scatter-graph-1')
                             ])
    ], style={'fontFamily':'Helvetica'})

    if tab == 'tab-6':
        return html.Div([
                         html.H4('Offensive vs. Defensive Ratings by Team'),
                         html.Div([
                                   html.Div('Teams', style={'paddingRight':'20px'}),
                                   dcc.Dropdown(id='team-picker-4',
                                        options=[{'label': i, 'value': i} for i in NBA_long.index.get_level_values(0).unique()],
                                        value=default_teams,
                                        multi=True)
                                  ],style={'display':'inline-block', 'verticalAlign':'top','width':'45%'}),
                        html.Div([
                                   html.Div('Start Year', style={'paddingRight':'30px'}),
                                   dcc.Dropdown(id='start-year-picker-4',
                                         options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                         value=NBA_long.index.get_level_values(1).min())
                                 ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                        html.Div([
                                  html.Div('End Year', style={'paddingRight':'30px'}),
                                  dcc.Dropdown(id='end-year-picker-4',
                                         options=[{'label': str(i), 'value': i} for i in NBA_long.index.get_level_values(1).unique()],
                                         value=NBA_long.index.get_level_values(1).max())
                                  ],style={'display':'inline-block', 'verticalAlign':'top','width':'10%'}),
                        html.Div([
                                  html.Button(id='submit-button-4',
                                      n_clicks=0,
                                      children='Submit',
                                      style={'fontSize':14})
                                 ],style={'display':'inline-block',
                                   'verticalAlign':'top'}),
                         html.Div([
                                   dcc.Graph(id='scatter-graph-2')
                          ])
    ], style={'fontFamily':'Helvetica'})


# Tab 2 callback

@app.callback(Output('line-graph-1', 'figure'),
             [Input('submit-button-1','n_clicks')],
             [State('team-picker-1','value'),
              State('start-year-picker-1','value'),
              State('end-year-picker-1','value')])

def update_line_graph_1(n_clicks, teams, start_year, end_year):
    years = list(range(start_year,end_year+1))

    filtered_df = NBA_long.loc[(teams, years), :]

    fig1 = px.line(filtered_df.reset_index(),
                 x='year',
                 y='w_l_percent',
                 color='team',
                 line_shape='spline',
                 title='Win-Loss %',
                 hover_name='team',
                 hover_data={'team':False,
                             'year':True,
                             'conf':True,
                             'div':True,
                             'w_l_percent':':.2%'},
                 width=1250,
                 height=600)

    fig1.update_xaxes(title='Season')
    fig1.update_yaxes(title='')
    fig1.update_layout(yaxis_tickformat = '%', legend_title='Team', hovermode='closest')

    return fig1

# Tab 3 callback

@app.callback(Output('line-graph-2', 'figure'),
             [Input('submit-button-2','n_clicks')],
             [State('team-picker-2','value'),
              State('rating-picker','value'),
              State('start-year-picker-2','value'),
              State('end-year-picker-2','value')])

def update_line_graph_2(n_clicks, teams, rating, start_year, end_year):
    years = list(range(start_year,end_year+1))

    filtered_df = NBA_long.loc[(teams, years), rating]

    fig2 = px.line(filtered_df.reset_index(),
                 x='year',
                 y=rating,
                 color='team',
                 line_shape='spline',
                 title='Rating',
                 hover_name='team',
                 hover_data={'team':False,
                             'year':True,
                             rating:':.2f'},
                 width=1250,
                 height=600)

    fig2.update_xaxes(title='Season')
    fig2.update_yaxes(title='Points')
    fig2.update_layout(legend_title='Team', hovermode='closest')

    return fig2

# Tab 4 callback

@app.callback(Output('scatter-graph-1', 'figure'),
             [Input('submit-button-3','n_clicks')],
             [State('team-picker-3','value'),
              State('start-year-picker-3','value'),
              State('end-year-picker-3','value')])

def update_scatter_graph_1(n_clicks, teams, start_year, end_year):
    years = list(range(start_year,end_year+1))

    filtered_df = NBA_long.loc[(teams, years), :]

    fig3 = px.scatter(filtered_df.fillna(0).reset_index(), #first five years of Charlotte Hornets is 0 as they're an expansion team
             x='drtg_a',
             y='ortg_a',
             color='div',
             size='w_l_percent',
             title='Offensive vs. Defensive Rating (Adjusted)',
             color_discrete_sequence=px.colors.qualitative.Vivid_r,
             opacity=0.7,
             hover_name='div',
             hover_data={'team':True,
                         'year':True,
                         'conf':True,
                         'div':False,
                         'w_l_percent':':.2%',
                         'ortg_a':':.2f',
                         'drtg_a':':.2f',
                         'nrtg_a':':.2f'},
             width=1000,
             height=800)

    fig3.update_xaxes(title='Defensive Rating (Adj)')
    fig3.update_yaxes(title='Offensive Rating (Adj)')
    fig3.update_layout(legend_title='Division')
    fig3.update_layout(yaxis_range=[90,122])
    fig3.update_layout(xaxis_range=[90,120])

    return fig3

# Tab 5 callback

@app.callback(Output('scatter-graph-2', 'figure'),
             [Input('submit-button-4','n_clicks')],
             [State('team-picker-4','value'),
              State('start-year-picker-4','value'),
              State('end-year-picker-4','value')])

def update_scatter_graph_2(n_clicks, teams, start_year, end_year):
    years = list(range(start_year,end_year+1))

    filtered_df = NBA_long.loc[(teams, years), :]

    fig4= px.scatter(filtered_df.fillna(0).reset_index(), #first five years of Charlotte Hornets is 0 as they're an expansion team
             x='drtg_a',
             y='ortg_a',
             color='team',
             size='w_l_percent',
             title='Offensive vs. Defensive Rating (Adjusted)',
             color_discrete_sequence=px.colors.qualitative.Bold_r,
             opacity=0.7,
             hover_name='team',
             hover_data={'team':False,
                         'year':True,
                         'conf':True,
                         'div':True,
                         'w_l_percent':':.2%',
                         'ortg_a':':.2f',
                         'drtg_a':':.2f',
                         'nrtg_a':':.2f'},
             width=1000,
             height=800)

    fig4.update_xaxes(title='Defensive Rating (Adj)')
    fig4.update_yaxes(title='Offensive Rating (Adj)')
    fig4.update_layout(legend_title='Team')
    fig4.update_layout(yaxis_range=[90,122])
    fig4.update_layout(xaxis_range=[90,120])

    return fig4


if __name__ == '__main__':
    app.run_server()
