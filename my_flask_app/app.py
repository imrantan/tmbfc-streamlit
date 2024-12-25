import pandas as pd
from flask import Flask, render_template, request
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = Flask(__name__)

# Load the Excel file
file_path = 'data/tmb_fc_data.xlsx'
xl = pd.ExcelFile(file_path)

# Read the sheets into DataFrames
players_df = xl.parse('player_info')
goals_df = xl.parse('goals')
assists_df = xl.parse('assists')
club_info_df = xl.parse('club_info')

# Define the team lineup
team_positions = {
    'FWD': 'Forward',
    'MID': 'Midfielder',
    'DEF': 'Defender',
    'GK': 'Goalkeeper'
}

@app.route('/')
def index():
    # Get the list of players and their positions
    players = players_df[['player_name', 'primary_position', 'secondary_position']].sort_values(by='primary_position')
    
    # Render the home page with the team lineup
    return render_template('index.html', players=players)

@app.route('/player/<player_name>')
def player_stats(player_name):
    # Get the player's info
    player_info = players_df[players_df['player_name'] == player_name].iloc[0]
    
    # Get the goals and assists data for the player
    player_goals = goals_df[player_name].dropna()
    player_assists = assists_df[player_name].dropna()

    # Convert the indices to datetime if they are not already
    player_goals.index = pd.to_datetime(player_goals.index)
    player_assists.index = pd.to_datetime(player_assists.index)

    # Create time series charts for goals and assists
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)

    fig.add_trace(go.Scatter(
        x=player_goals.index, 
        y=player_goals.values, 
        mode='lines+markers', 
        name='Goals'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=player_assists.index, 
        y=player_assists.values, 
        mode='lines+markers', 
        name='Assists'
    ), row=2, col=1)

    # Update layout with better styling
    fig.update_layout(
        title=f'{player_name} - Goals and Assists Over Time',
        showlegend=True,
        xaxis=dict(
            tickformat="%d-%m-%Y",  # Format dates as DD-MM-YYYY
            tickvals=player_goals.index.union(player_assists.index).sort_values(),  # Ensure all dates are shown
        ),
        font=dict(family="Roboto, sans-serif"),  # Use a more appealing font
        template="plotly_dark"  # Apply a dark football theme
    )

    graph = pio.to_html(fig, full_html=False)

    return render_template('player_stats.html', player_info=player_info, graph=graph)


if __name__ == '__main__':
    app.run(debug=True)
