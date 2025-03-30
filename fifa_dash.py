import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

#SCRAPING DATA
url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table", {"class": "wikitable"})


target_table = None
for table in tables:
    df_test = pd.read_html(StringIO(str(table)))[0]
    if "Winners" in df_test.columns and "Runners-up" in df_test.columns:
        target_table = df_test
        break

if target_table is None:
    raise Exception("Couldn't find the correct table!")

#wiki column
df = target_table
df.columns = ['Year', 'Winners', 'Score', 'Runners-up', 'Venue', 'Location', 'Attendance', 'Ref']
df = df[['Year', 'Winners', 'Runners-up']]
df = df.dropna(subset=['Winners', 'Runners-up'])

#West Germany into Germany
df.loc[:, 'Winners'] = df['Winners'].replace({'West Germany': 'Germany'})
df.loc[:, 'Runners-up'] = df['Runners-up'].replace({'West Germany': 'Germany'})

#Print preview
print(df.head())



from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# App instance
app = Dash(__name__)

# 1. World Cup Wins by Country
win_counts = df['Winners'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

# 2. App Layout
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),
    
    # Choropleth Map
    dcc.Graph(id='choropleth',
              figure=px.choropleth(
                  win_counts,
                  locations='Country',
                  locationmode='country names',
                  color='Wins',
                  color_continuous_scale='Blues',
                  title='World Cup Wins by Country',
              )),
    
    html.Div([
        html.Label("Select a Country:"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in sorted(df['Winners'].unique())],
            value='Brazil'
        ),
        html.Div(id='country-output', style={'marginTop': 20, 'fontWeight': 'bold'})
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label("Select a Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': int(y), 'value': int(y)} for y in sorted(df['Year'].unique())],
            value=2022
        ),
        html.Div(id='year-output', style={'marginTop': 20, 'fontWeight': 'bold'})
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
])

@app.callback(
    Output('country-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_output(selected_country):
    count = df[df['Winners'] == selected_country].shape[0]
    return f"{selected_country} has won the World Cup {count} time(s)."

@app.callback(
    Output('year-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_output(selected_year):
    row = df[df['Year'] == selected_year]
    if not row.empty:
        winner = row.iloc[0]['Winners']
        runner_up = row.iloc[0]['Runners-up']
        return f"In {selected_year}, {winner} won against {runner_up}."
    return "No data for this year."

if __name__ == '__main__':
    app.run(debug=True)
